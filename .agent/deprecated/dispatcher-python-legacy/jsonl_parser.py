"""
jsonl_parser.py — JSONL 事件解析器 (T-102)

解析 Codex CLI `--json` 输出的五类事件:
    - agent_message: Agent 文本消息
    - tool_call: 工具调用 (write_file / run_command 等)
    - tool_result: 工具执行结果
    - error: 错误事件
    - session_end: 会话结束

支持特性:
    - 语义疑问检测（中英文混合支持）
    - 会话完成检测
    - 错误提取
    - 结构化内容摘要
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

from .core import JSONLEvent

logger = logging.getLogger(__name__)

# 疑问句检测模式
QUESTION_PATTERNS: list[re.Pattern[str]] = [
    # 中文疑问
    re.compile(r"[\?？]\s*$"),  # 以问号结尾
    re.compile(r"(请确认|请选择|请指定|请告诉|请问|你希望|你想要|需要我)"),
    re.compile(r"(是否|是不是|能否|可否|要不要|对不对)"),
    re.compile(r"(哪个|哪些|什么|怎么|如何|为什么|多少|几个)"),
    # 英文疑问
    re.compile(r"\b(should I|do you want|would you like|can I|shall I)\b", re.IGNORECASE),
    re.compile(r"\b(which|what|how|where|when|why)\b.*\?\s*$", re.IGNORECASE),
    # 选择请求
    re.compile(r"(选项|option)\s*[A-D1-9]", re.IGNORECASE),
    re.compile(r"\b(A\)|B\)|C\)|1\)|2\)|3\))"),
    # 阻塞声明
    re.compile(r"(无法继续|无法确定|不确定|blocked|stuck|need.*input)", re.IGNORECASE),
]

# 非疑问的例外模式（排除误报）
QUESTION_EXCLUDE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(已完成|已解决|已修复|没有问题|没问题)"),
    re.compile(r"(不需要|无需|跳过)"),
]


class JSONLParser:
    """JSONL 事件流解析器。

    将 Codex CLI 的 JSON Lines 输出解析为结构化的 JSONLEvent 序列，
    并提供语义分析功能（疑问检测、完成检测、错误提取）。

    使用方式:
        parser = JSONLParser()
        events = parser.parse_stream(file_handle)
        # 或逐行解析
        event = parser.parse_line(line)
    """

    def __init__(self) -> None:
        self._event_count: int = 0

    # ── 解析 API ────────────────────────────────────────

    def parse_line(self, line: str) -> JSONLEvent | None:
        """解析单行 JSONL，异常时返回 None 而非抛出。

        Args:
            line: 单行文本（可含换行符）

        Returns:
            JSONLEvent 或 None（解析失败时）
        """
        line = line.strip()
        if not line:
            return None

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            logger.debug("Non-JSON line skipped: %s", line[:80])
            return None

        if not isinstance(data, dict):
            logger.debug("Non-object JSON skipped: %s", type(data))
            return None

        event = JSONLEvent(
            type=data.get("type", "unknown"),
            timestamp=data.get("timestamp", time.time()),
            content=data,
        )
        self._event_count += 1
        return event

    def parse_stream(self, stream: TextIO) -> list[JSONLEvent]:
        """解析整个 JSONL 流。

        Args:
            stream: 可遍历行的文本流（文件对象或 StringIO）

        Returns:
            解析后的事件列表
        """
        events: list[JSONLEvent] = []
        for line in stream:
            event = self.parse_line(line)
            if event:
                events.append(event)
        return events

    def parse_file(self, path: str | Path) -> list[JSONLEvent]:
        """从文件解析 JSONL。

        Args:
            path: JSONL 文件路径

        Returns:
            解析后的事件列表
        """
        with open(path, "r", encoding="utf-8") as f:
            return self.parse_stream(f)

    # ── 语义检测 API ────────────────────────────────────

    def detect_question(self, event: JSONLEvent) -> str | None:
        """语义分析: 检测 agent_message 中是否包含疑问。

        检测模式:
            - 疑问句（中英文问号结尾）
            - 选择请求（选项 A/B/C）
            - 阻塞声明（无法继续、需要输入）
            - 确认请求（请确认、是否）

        Args:
            event: JSONL 事件

        Returns:
            检测到的问题文本，或 None
        """
        if event.type != "agent_message":
            return None

        message = event.content.get("message", "")
        if not message or len(message.strip()) < 3:
            return None

        # 排除误报
        for exclude in QUESTION_EXCLUDE_PATTERNS:
            if exclude.search(message):
                return None

        # 检查疑问模式
        for pattern in QUESTION_PATTERNS:
            if pattern.search(message):
                return message

        return None

    def detect_completion(self, event: JSONLEvent) -> bool:
        """检测 session_end 事件。

        Args:
            event: JSONL 事件

        Returns:
            是否为会话结束事件
        """
        return event.type == "session_end"

    def detect_error(self, event: JSONLEvent) -> str | None:
        """检测 error 事件并提取错误消息。

        Args:
            event: JSONL 事件

        Returns:
            错误消息文本，或 None
        """
        if event.type != "error":
            return None
        return event.content.get("message", str(event.content))

    # ── 批量分析 API ────────────────────────────────────

    def analyze_events(self, events: list[JSONLEvent]) -> EventSummary:
        """对一组事件进行综合分析。

        Args:
            events: 事件列表

        Returns:
            EventSummary — 包含分类统计、检测到的问题、错误等
        """
        summary = EventSummary()

        for event in events:
            # 计数
            summary.type_counts[event.type] = summary.type_counts.get(event.type, 0) + 1

            # 检测问题
            question = self.detect_question(event)
            if question:
                summary.questions.append(question)

            # 检测完成
            if self.detect_completion(event):
                summary.completed = True

            # 检测错误
            error = self.detect_error(event)
            if error:
                summary.errors.append(error)

            # 收集 agent 消息
            if event.type == "agent_message":
                msg = event.content.get("message", "")
                if msg:
                    summary.messages.append(msg)

            # 收集工具调用
            if event.type == "tool_call":
                tool_name = event.content.get("tool", "unknown")
                summary.tool_calls.append(tool_name)

        summary.total_events = len(events)
        summary.success = summary.completed and len(summary.errors) == 0

        return summary

    @property
    def event_count(self) -> int:
        """已解析的事件总数。"""
        return self._event_count


@dataclass
class EventSummary:
    """事件流的综合分析结果。"""

    total_events: int = 0
    type_counts: dict[str, int] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    completed: bool = False
    success: bool = False

    @property
    def has_questions(self) -> bool:
        return len(self.questions) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def __repr__(self) -> str:
        return (
            f"EventSummary(events={self.total_events}, "
            f"questions={len(self.questions)}, "
            f"errors={len(self.errors)}, "
            f"success={self.success})"
        )
