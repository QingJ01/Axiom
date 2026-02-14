"""
worker.py — Worker 封装器 (T-101)

封装 `codex exec --json --full-auto` 调用:
- 子进程生命周期管理（启动 / 终止 / 超时）
- JSONL 事件流的实时读取
- 超时控制（默认 10 分钟，可配置 10/15/20 min）
"""

from __future__ import annotations

import json
import logging
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .core import JSONLEvent, TaskSpec, Timer, WorkerResult

logger = logging.getLogger(__name__)


@dataclass
class WorkerConfig:
    """Worker 运行配置。"""

    codex_bin: str = "codex"  # codex CLI 可执行文件路径
    default_timeout: int = 600  # 默认超时秒数（10 分钟）
    working_dir: str | None = None  # 工作目录，None 则使用当前目录
    env_vars: dict[str, str] = field(default_factory=dict)  # 额外环境变量
    # 2026-02-10: Windows 下必须使用 bypass 模式才能正常写入文件
    bypass_sandbox: bool = True  # 绕过沙箱限制 (Windows 必须为 True)
    approval_mode: str = "full-auto"  # 审批模式 (仅当 bypass_sandbox=False 时生效)


class Worker:
    """Worker 封装器 — 管理 Codex CLI 子进程的生命周期。

    使用方式:
        worker = Worker(config)
        result = worker.execute(task)

    支持特性:
        - 子进程超时终止
        - 实时 JSONL 事件流解析
        - 线程安全的事件收集
        - 进程状态查询
    """

    def __init__(self, config: WorkerConfig | None = None) -> None:
        self.config = config or WorkerConfig()
        self._process: subprocess.Popen | None = None
        self._events: list[JSONLEvent] = []
        self._lock = threading.Lock()
        self._running = False

    # ── 公开 API ────────────────────────────────────────────

    def execute(
        self,
        task: TaskSpec,
        prompt: str | None = None,
        on_event: Callable[[JSONLEvent], None] | None = None,
    ) -> WorkerResult:
        """执行一个任务并返回结果。

        Args:
            task: 任务规格
            prompt: 自定义 Prompt。若为 None，则自动从 task 生成。
            on_event: 事件回调，每收到一条 JSONL 事件时调用。

        Returns:
            WorkerResult — 包含执行结果、所有事件、提出的问题等。
        """
        effective_prompt = prompt or self._build_prompt(task)
        timeout = task.timeout_seconds or self.config.default_timeout

        timer = Timer()
        timer.start()

        try:
            self._start_process(effective_prompt)
            events = self._collect_events(timeout=timeout, on_event=on_event)
            success = self._check_success(events)
            questions = self._extract_questions(events)
            output = self._extract_output(events)
            error_msg = self._extract_error(events)

            duration = timer.stop()

            return WorkerResult(
                task_id=task.id,
                success=success and not questions,
                output=output,
                events=events,
                questions=questions,
                duration_seconds=duration,
                restart_count=0,
                error_message=error_msg,
            )

        except TimeoutError:
            duration = timer.stop()
            self.terminate()
            logger.warning(
                "Task %s timed out after %.1f seconds", task.id, duration
            )
            return WorkerResult(
                task_id=task.id,
                success=False,
                output="",
                events=list(self._events),
                questions=[],
                duration_seconds=duration,
                restart_count=0,
                error_message=f"Timeout after {timeout}s",
            )

        except Exception as exc:
            duration = timer.stop()
            self.terminate()
            logger.error("Task %s failed with exception: %s", task.id, exc)
            return WorkerResult(
                task_id=task.id,
                success=False,
                output="",
                events=list(self._events),
                questions=[],
                duration_seconds=duration,
                restart_count=0,
                error_message=str(exc),
            )

    def terminate(self) -> None:
        """强制终止 Worker 子进程。"""
        if self._process and self._process.poll() is None:
            logger.info("Terminating worker process (PID: %d)", self._process.pid)
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Force killing worker process")
                self._process.kill()
                self._process.wait()
        self._running = False

    @property
    def is_running(self) -> bool:
        """Worker 是否正在运行。"""
        return self._running and self._process is not None and self._process.poll() is None

    # ── 内部方法 ────────────────────────────────────────────

    def _build_prompt(self, task: TaskSpec) -> str:
        """根据 TaskSpec 构建执行 Prompt。"""
        return (
            f"请执行以下任务:\n\n"
            f"## 任务 {task.id}: {task.name}\n\n"
            f"{task.description}\n\n"
            f"---\n"
            f"要求:\n"
            f"1. 严格按照描述完成任务\n"
            f"2. 完成后输出简要总结\n"
            f"3. 如遇到无法自行决定的问题，清楚地提出问题\n"
        )

    def _build_command(self, prompt: str) -> list[str]:
        """构建 codex CLI 命令行参数。"""
        cmd = [
            self.config.codex_bin,
            "exec",
            "--json",
        ]
        
        # 2026-02-10: Windows 下必须使用 bypass 模式才能正常写入文件
        if self.config.bypass_sandbox:
            cmd.append("--dangerously-bypass-approvals-and-sandbox")
        else:
            cmd.append(f"--approval-mode={self.config.approval_mode}")
        
        cmd.append(prompt)
        return cmd

    def _start_process(self, prompt: str) -> None:
        """启动 Codex CLI 子进程。"""
        cmd = self._build_command(prompt)
        working_dir = self.config.working_dir or str(Path.cwd())

        logger.info("Starting worker: %s", " ".join(cmd[:4]) + " ...")
        logger.debug("Working dir: %s", working_dir)

        env = None
        if self.config.env_vars:
            import os
            env = {**os.environ, **self.config.env_vars}

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_dir,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self._events = []
        self._running = True

    def _collect_events(
        self,
        timeout: int,
        on_event: Callable[[JSONLEvent], None] | None = None,
    ) -> list[JSONLEvent]:
        """实时读取子进程 stdout 的 JSONL 流，收集事件。

        Args:
            timeout: 超时秒数
            on_event: 事件回调

        Returns:
            收集到的所有 JSONL 事件列表

        Raises:
            TimeoutError: 超时时抛出
        """
        if not self._process or not self._process.stdout:
            return []

        deadline = time.monotonic() + timeout
        events: list[JSONLEvent] = []

        def _read_stream() -> None:
            """在子线程中读取 stdout。"""
            assert self._process is not None and self._process.stdout is not None
            for line in self._process.stdout:
                line = line.strip()
                if not line:
                    continue
                event = self._parse_jsonl_line(line)
                if event:
                    with self._lock:
                        events.append(event)
                        self._events.append(event)
                    if on_event:
                        try:
                            on_event(event)
                        except Exception as e:
                            logger.warning("Event callback error: %s", e)

        reader_thread = threading.Thread(target=_read_stream, daemon=True)
        reader_thread.start()

        # 等待进程完成或超时
        while reader_thread.is_alive():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"Worker exceeded {timeout}s timeout")
            reader_thread.join(timeout=min(1.0, remaining))

        # 确保进程已结束
        if self._process.poll() is None:
            self._process.wait(timeout=5)

        self._running = False
        return events

    def _parse_jsonl_line(self, line: str) -> JSONLEvent | None:
        """解析单条 JSONL 行。"""
        try:
            data = json.loads(line)
            return JSONLEvent(
                type=data.get("type", "unknown"),
                timestamp=data.get("timestamp", time.time()),
                content=data,
            )
        except json.JSONDecodeError:
            logger.debug("Skipping non-JSON line: %s", line[:100])
            return None

    def _check_success(self, events: list[JSONLEvent]) -> bool:
        """根据事件流判断任务是否成功完成。"""
        has_error = any(e.type == "error" for e in events)
        has_session_end = any(e.type == "session_end" for e in events)
        return has_session_end and not has_error

    def _extract_questions(self, events: list[JSONLEvent]) -> list[str]:
        """从事件流中提取 Worker 提出的问题。"""
        questions: list[str] = []
        question_indicators = ["?", "？", "请确认", "请选择", "是否", "需要"]

        for event in events:
            if event.type == "agent_message":
                message = event.content.get("message", "")
                if any(ind in message for ind in question_indicators):
                    questions.append(message)

        return questions

    def _extract_output(self, events: list[JSONLEvent]) -> str:
        """从事件流中提取最终输出文本。"""
        messages: list[str] = []
        for event in events:
            if event.type == "agent_message":
                msg = event.content.get("message", "")
                if msg:
                    messages.append(msg)
        return "\n".join(messages) if messages else ""

    def _extract_error(self, events: list[JSONLEvent]) -> str | None:
        """提取错误信息。"""
        errors: list[str] = []
        for event in events:
            if event.type == "error":
                msg = event.content.get("message", str(event.content))
                errors.append(msg)
        return "; ".join(errors) if errors else None
