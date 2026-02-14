"""
core.py — 核心数据类定义

定义 TaskSpec / WorkerResult / JSONLEvent / TaskStatus 等基础类型，
作为 Dispatcher 各模块之间的通信契约。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """任务状态枚举，与 PRD 中的图标对应。"""

    PENDING = "⏳"
    IN_PROGRESS = "🔄"
    DONE = "✅"
    BLOCKED = "🚫"
    RETRY = "🔁"
    FAILED = "❌"
    SKIPPED = "⏭️"


@dataclass
class JSONLEvent:
    """Codex CLI --json 输出的单条 JSONL 事件。"""

    type: str  # agent_message / tool_call / tool_result / error / session_end
    timestamp: float
    content: dict[str, Any]  # 原始 JSON 内容

    def __repr__(self) -> str:
        return f"JSONLEvent(type={self.type!r}, ts={self.timestamp:.1f})"


@dataclass
class TaskSpec:
    """单个任务的规格描述，从 PRD 中解析得到。"""

    id: str  # e.g., "T-001"
    name: str  # e.g., "实现基础调度器"
    description: str  # 任务详细描述
    dependencies: list[str] = field(default_factory=list)  # e.g., ["T-001"]
    status: TaskStatus = TaskStatus.PENDING
    timeout_seconds: int = 600  # 默认 10 分钟

    @property
    def is_ready(self) -> bool:
        """当前任务是否可以执行（PENDING 且无未完成依赖）。
        注意: 依赖检查需在调度层完成，此处仅检查自身状态。"""
        return self.status == TaskStatus.PENDING


@dataclass
class WorkerResult:
    """Worker 执行完毕后的结果。"""

    task_id: str
    success: bool
    output: str  # Worker 最终输出
    events: list[JSONLEvent] = field(default_factory=list)  # 所有 JSONL 事件
    questions: list[str] = field(default_factory=list)  # Worker 提出的问题
    duration_seconds: float = 0.0
    restart_count: int = 0  # 重启次数
    error_message: str | None = None  # 错误信息

    @property
    def has_questions(self) -> bool:
        """Worker 是否提出了需要回答的问题。"""
        return len(self.questions) > 0


class Timer:
    """简易计时器，用于追踪任务执行耗时。"""

    def __init__(self) -> None:
        self._start: float | None = None
        self._end: float | None = None

    def start(self) -> None:
        self._start = time.monotonic()
        self._end = None

    def stop(self) -> float:
        if self._start is None:
            raise RuntimeError("Timer not started")
        self._end = time.monotonic()
        return self.elapsed

    @property
    def elapsed(self) -> float:
        if self._start is None:
            return 0.0
        end = self._end if self._end is not None else time.monotonic()
        return end - self._start
