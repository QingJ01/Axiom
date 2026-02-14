"""
test_worker.py — Worker 封装器单元测试 (T-101)

测试覆盖:
  - TaskSpec / WorkerResult / Timer 数据类
  - Worker 启动 Mock 子进程
  - JSONL 行解析
  - 超时终止
  - 问题检测
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import time
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# 将 dispatcher 的父目录加入 path，以支持包内相对导入
_dispatcher_parent = str(Path(__file__).resolve().parent.parent.parent)
if _dispatcher_parent not in sys.path:
    sys.path.insert(0, _dispatcher_parent)

from dispatcher.core import JSONLEvent, TaskSpec, TaskStatus, Timer, WorkerResult
from dispatcher.worker import Worker, WorkerConfig


# ──────────────────────────────────────────────────────
# 1. 数据类测试
# ──────────────────────────────────────────────────────


class TestTaskStatus:
    def test_all_statuses_exist(self) -> None:
        assert TaskStatus.PENDING.value == "⏳"
        assert TaskStatus.DONE.value == "✅"
        assert TaskStatus.FAILED.value == "❌"
        assert TaskStatus.BLOCKED.value == "🚫"
        assert TaskStatus.IN_PROGRESS.value == "🔄"
        assert TaskStatus.RETRY.value == "🔁"
        assert TaskStatus.SKIPPED.value == "⏭️"


class TestTaskSpec:
    def test_default_values(self) -> None:
        task = TaskSpec(id="T-001", name="测试任务", description="描述")
        assert task.status == TaskStatus.PENDING
        assert task.timeout_seconds == 600
        assert task.dependencies == []
        assert task.is_ready is True

    def test_not_ready_when_done(self) -> None:
        task = TaskSpec(
            id="T-001", name="测试", description="描述",
            status=TaskStatus.DONE,
        )
        assert task.is_ready is False

    def test_not_ready_when_blocked(self) -> None:
        task = TaskSpec(
            id="T-001", name="测试", description="描述",
            status=TaskStatus.BLOCKED,
        )
        assert task.is_ready is False


class TestWorkerResult:
    def test_has_questions(self) -> None:
        r = WorkerResult(task_id="T-001", success=True, output="ok")
        assert r.has_questions is False

        r.questions = ["这个文件放哪里？"]
        assert r.has_questions is True


class TestTimer:
    def test_basic_timing(self) -> None:
        t = Timer()
        t.start()
        time.sleep(0.05)
        elapsed = t.stop()
        assert elapsed >= 0.04  # 允许少量误差

    def test_elapsed_without_stop(self) -> None:
        t = Timer()
        t.start()
        time.sleep(0.05)
        assert t.elapsed >= 0.04

    def test_elapsed_before_start(self) -> None:
        t = Timer()
        assert t.elapsed == 0.0

    def test_stop_without_start(self) -> None:
        t = Timer()
        with pytest.raises(RuntimeError, match="Timer not started"):
            t.stop()


class TestJSONLEvent:
    def test_repr(self) -> None:
        e = JSONLEvent(type="agent_message", timestamp=1000.0, content={})
        assert "agent_message" in repr(e)


# ──────────────────────────────────────────────────────
# 2. Worker 内部方法测试
# ──────────────────────────────────────────────────────


class TestWorkerInternals:
    def setup_method(self) -> None:
        self.worker = Worker(WorkerConfig())

    def test_build_prompt(self) -> None:
        task = TaskSpec(id="T-001", name="测试任务", description="这是一个测试任务")
        prompt = self.worker._build_prompt(task)
        assert "T-001" in prompt
        assert "测试任务" in prompt
        assert "这是一个测试任务" in prompt

    def test_build_command(self) -> None:
        cmd = self.worker._build_command("test prompt")
        assert cmd[0] == "codex"
        assert "exec" in cmd
        assert "--json" in cmd
        assert "--approval-mode=full-auto" in cmd
        assert "test prompt" in cmd

    def test_parse_jsonl_line_valid(self) -> None:
        line = json.dumps({
            "type": "agent_message",
            "timestamp": 1000.0,
            "message": "hello",
        })
        event = self.worker._parse_jsonl_line(line)
        assert event is not None
        assert event.type == "agent_message"
        assert event.timestamp == 1000.0

    def test_parse_jsonl_line_invalid(self) -> None:
        event = self.worker._parse_jsonl_line("not-a-json")
        assert event is None

    def test_parse_jsonl_line_missing_type(self) -> None:
        line = json.dumps({"timestamp": 1000.0})
        event = self.worker._parse_jsonl_line(line)
        assert event is not None
        assert event.type == "unknown"

    def test_check_success(self) -> None:
        # 成功: 有 session_end，无 error
        events = [
            JSONLEvent("agent_message", 1.0, {}),
            JSONLEvent("session_end", 2.0, {}),
        ]
        assert self.worker._check_success(events) is True

        # 失败: 有 error
        events_err = [
            JSONLEvent("error", 1.0, {"message": "crash"}),
            JSONLEvent("session_end", 2.0, {}),
        ]
        assert self.worker._check_success(events_err) is False

        # 失败: 无 session_end
        events_no_end = [JSONLEvent("agent_message", 1.0, {})]
        assert self.worker._check_success(events_no_end) is False

    def test_extract_questions(self) -> None:
        events = [
            JSONLEvent("agent_message", 1.0, {"message": "开始执行"}),
            JSONLEvent("agent_message", 2.0, {"message": "这个配置文件放哪里？"}),
            JSONLEvent("agent_message", 3.0, {"message": "是否需要添加测试？"}),
            JSONLEvent("agent_message", 4.0, {"message": "任务完成"}),
        ]
        questions = self.worker._extract_questions(events)
        assert len(questions) == 2
        assert "放哪里？" in questions[0]
        assert "是否" in questions[1]

    def test_extract_output(self) -> None:
        events = [
            JSONLEvent("agent_message", 1.0, {"message": "第一行"}),
            JSONLEvent("tool_call", 2.0, {"tool": "write_file"}),
            JSONLEvent("agent_message", 3.0, {"message": "第二行"}),
        ]
        output = self.worker._extract_output(events)
        assert "第一行" in output
        assert "第二行" in output

    def test_extract_error(self) -> None:
        events = [
            JSONLEvent("error", 1.0, {"message": "file not found"}),
            JSONLEvent("error", 2.0, {"message": "permission denied"}),
        ]
        error = self.worker._extract_error(events)
        assert error is not None
        assert "file not found" in error
        assert "permission denied" in error

    def test_extract_error_none(self) -> None:
        events = [JSONLEvent("agent_message", 1.0, {})]
        assert self.worker._extract_error(events) is None


# ──────────────────────────────────────────────────────
# 3. Worker 集成测试 (Mock 子进程)
# ──────────────────────────────────────────────────────


# 辅助: 生成 Mock JSONL 输出的 Python 脚本
MOCK_WORKER_SUCCESS = textwrap.dedent("""\
    import json, sys, time
    events = [
        {"type": "agent_message", "timestamp": 1.0, "message": "开始执行任务"},
        {"type": "tool_call", "timestamp": 2.0, "tool": "write_file", "args": {}},
        {"type": "tool_result", "timestamp": 3.0, "result": "ok"},
        {"type": "agent_message", "timestamp": 4.0, "message": "任务完成"},
        {"type": "session_end", "timestamp": 5.0},
    ]
    for e in events:
        print(json.dumps(e), flush=True)
        time.sleep(0.01)
""")

MOCK_WORKER_WITH_QUESTION = textwrap.dedent("""\
    import json, sys, time
    events = [
        {"type": "agent_message", "timestamp": 1.0, "message": "分析中..."},
        {"type": "agent_message", "timestamp": 2.0, "message": "这个数据库连接字符串应该用什么？"},
        {"type": "session_end", "timestamp": 3.0},
    ]
    for e in events:
        print(json.dumps(e), flush=True)
        time.sleep(0.01)
""")

MOCK_WORKER_TIMEOUT = textwrap.dedent("""\
    import time, json, sys
    print(json.dumps({"type": "agent_message", "timestamp": 1.0, "message": "开始..."}), flush=True)
    time.sleep(30)  # 很久，会被超时终止
""")

MOCK_WORKER_ERROR = textwrap.dedent("""\
    import json, sys
    events = [
        {"type": "agent_message", "timestamp": 1.0, "message": "执行中"},
        {"type": "error", "timestamp": 2.0, "message": "RuntimeError: crash"},
        {"type": "session_end", "timestamp": 3.0},
    ]
    for e in events:
        print(json.dumps(e), flush=True)
""")


class TestWorkerExecute:
    """使用 Mock Python 脚本模拟 Codex CLI 子进程，测试 Worker.execute。"""

    def _make_worker_with_mock(self, mock_script: str) -> Worker:
        """创建一个使用 Python Mock 脚本替代 codex CLI 的 Worker。"""
        config = WorkerConfig(codex_bin=sys.executable)
        worker = Worker(config)

        # 覆盖 _build_command 让它运行 Python 脚本
        original_build = worker._build_command

        def mock_build_command(prompt: str) -> list[str]:
            return [sys.executable, "-c", mock_script]

        worker._build_command = mock_build_command  # type: ignore[assignment]
        return worker

    def test_successful_execution(self) -> None:
        worker = self._make_worker_with_mock(MOCK_WORKER_SUCCESS)
        task = TaskSpec(id="T-TEST", name="测试任务", description="成功场景")

        result = worker.execute(task)

        assert result.task_id == "T-TEST"
        assert result.success is True
        assert result.error_message is None
        assert len(result.events) >= 4
        assert result.duration_seconds > 0
        assert "任务完成" in result.output

    def test_question_detection(self) -> None:
        worker = self._make_worker_with_mock(MOCK_WORKER_WITH_QUESTION)
        task = TaskSpec(id="T-TEST", name="测试任务", description="提问场景")

        result = worker.execute(task)

        assert result.has_questions is True
        assert len(result.questions) >= 1
        assert result.success is False  # 有问题时 success 为 False

    def test_timeout_termination(self) -> None:
        worker = self._make_worker_with_mock(MOCK_WORKER_TIMEOUT)
        task = TaskSpec(
            id="T-TEST", name="测试任务", description="超时场景",
            timeout_seconds=2,
        )

        result = worker.execute(task)

        assert result.success is False
        assert result.error_message is not None
        assert "Timeout" in result.error_message
        assert result.duration_seconds >= 1.5

    def test_error_handling(self) -> None:
        worker = self._make_worker_with_mock(MOCK_WORKER_ERROR)
        task = TaskSpec(id="T-TEST", name="测试任务", description="错误场景")

        result = worker.execute(task)

        assert result.success is False
        assert result.error_message is not None
        assert "crash" in result.error_message

    def test_event_callback(self) -> None:
        worker = self._make_worker_with_mock(MOCK_WORKER_SUCCESS)
        task = TaskSpec(id="T-TEST", name="测试任务", description="回调场景")

        collected: list[JSONLEvent] = []
        result = worker.execute(task, on_event=lambda e: collected.append(e))

        assert len(collected) >= 4
        assert all(isinstance(e, JSONLEvent) for e in collected)

    def test_custom_prompt(self) -> None:
        worker = self._make_worker_with_mock(MOCK_WORKER_SUCCESS)
        task = TaskSpec(id="T-TEST", name="测试任务", description="自定义Prompt")

        result = worker.execute(task, prompt="自定义指令")

        assert result.success is True

    def test_worker_is_running_property(self) -> None:
        worker = self._make_worker_with_mock(MOCK_WORKER_TIMEOUT)
        assert worker.is_running is False

    def test_terminate_when_not_running(self) -> None:
        worker = Worker()
        # 不应抛出异常
        worker.terminate()


# ──────────────────────────────────────────────────────
# 运行入口
# ──────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
