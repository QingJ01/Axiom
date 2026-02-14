"""
test_parser.py — JSONL 事件解析器单元测试 (T-102)

测试覆盖:
  - 单行解析 (有效 JSON / 无效 JSON / 空行)
  - 五类事件类型正确解析
  - 疑问检测 (中文 / 英文 / 选择 / 阻塞 / 排除误报)
  - session_end 完成检测
  - error 错误提取
  - 流式解析 / 文件解析
  - 批量分析 EventSummary
"""

from __future__ import annotations

import json
import sys
import tempfile
from io import StringIO
from pathlib import Path

import pytest

_dispatcher_parent = str(Path(__file__).resolve().parent.parent.parent)
if _dispatcher_parent not in sys.path:
    sys.path.insert(0, _dispatcher_parent)

from dispatcher.core import JSONLEvent
from dispatcher.jsonl_parser import JSONLParser, EventSummary


# ──────────────────────────────────────────────────────
# 1. 单行解析
# ──────────────────────────────────────────────────────


class TestParseLine:
    def setup_method(self) -> None:
        self.parser = JSONLParser()

    def test_valid_agent_message(self) -> None:
        line = json.dumps({"type": "agent_message", "timestamp": 1.0, "message": "hello"})
        event = self.parser.parse_line(line)
        assert event is not None
        assert event.type == "agent_message"
        assert event.content["message"] == "hello"

    def test_valid_tool_call(self) -> None:
        line = json.dumps({"type": "tool_call", "timestamp": 2.0, "tool": "write_file", "args": {"path": "test.py"}})
        event = self.parser.parse_line(line)
        assert event is not None
        assert event.type == "tool_call"
        assert event.content["tool"] == "write_file"

    def test_valid_tool_result(self) -> None:
        line = json.dumps({"type": "tool_result", "timestamp": 3.0, "result": "ok"})
        event = self.parser.parse_line(line)
        assert event is not None
        assert event.type == "tool_result"

    def test_valid_error(self) -> None:
        line = json.dumps({"type": "error", "timestamp": 4.0, "message": "something failed"})
        event = self.parser.parse_line(line)
        assert event is not None
        assert event.type == "error"

    def test_valid_session_end(self) -> None:
        line = json.dumps({"type": "session_end", "timestamp": 5.0})
        event = self.parser.parse_line(line)
        assert event is not None
        assert event.type == "session_end"

    def test_missing_type_defaults_to_unknown(self) -> None:
        line = json.dumps({"timestamp": 1.0, "data": "foo"})
        event = self.parser.parse_line(line)
        assert event is not None
        assert event.type == "unknown"

    def test_invalid_json(self) -> None:
        assert self.parser.parse_line("not-json") is None

    def test_empty_line(self) -> None:
        assert self.parser.parse_line("") is None
        assert self.parser.parse_line("   ") is None

    def test_non_object_json(self) -> None:
        assert self.parser.parse_line("[1, 2, 3]") is None
        assert self.parser.parse_line('"string"') is None

    def test_event_count_increments(self) -> None:
        parser = JSONLParser()
        assert parser.event_count == 0
        parser.parse_line(json.dumps({"type": "agent_message"}))
        assert parser.event_count == 1
        parser.parse_line(json.dumps({"type": "session_end"}))
        assert parser.event_count == 2
        parser.parse_line("bad line")
        assert parser.event_count == 2  # 无效行不计数


# ──────────────────────────────────────────────────────
# 2. 疑问检测
# ──────────────────────────────────────────────────────


class TestDetectQuestion:
    def setup_method(self) -> None:
        self.parser = JSONLParser()

    def _make_msg_event(self, message: str) -> JSONLEvent:
        return JSONLEvent(type="agent_message", timestamp=1.0, content={"message": message})

    def test_chinese_question_mark(self) -> None:
        e = self._make_msg_event("这个配置文件放在哪里？")
        assert self.parser.detect_question(e) is not None

    def test_english_question_mark(self) -> None:
        e = self._make_msg_event("Should I use the default config?")
        assert self.parser.detect_question(e) is not None

    def test_please_confirm(self) -> None:
        e = self._make_msg_event("请确认以下方案是否正确")
        assert self.parser.detect_question(e) is not None

    def test_yes_or_no(self) -> None:
        e = self._make_msg_event("是否需要添加单元测试")
        assert self.parser.detect_question(e) is not None

    def test_choice_pattern(self) -> None:
        e = self._make_msg_event("请选择: 选项A 或 选项B")
        assert self.parser.detect_question(e) is not None

    def test_blocked_statement(self) -> None:
        e = self._make_msg_event("无法继续，需要更多信息")
        assert self.parser.detect_question(e) is not None

    def test_english_should_i(self) -> None:
        e = self._make_msg_event("Should I create the file in src/ directory?")
        assert self.parser.detect_question(e) is not None

    def test_not_a_question(self) -> None:
        e = self._make_msg_event("任务已完成，文件已创建")
        assert self.parser.detect_question(e) is None

    def test_exclude_false_positive(self) -> None:
        e = self._make_msg_event("没有问题，已经全部处理完毕")
        assert self.parser.detect_question(e) is None

    def test_non_agent_message_ignored(self) -> None:
        e = JSONLEvent(type="tool_call", timestamp=1.0, content={"message": "这是什么？"})
        assert self.parser.detect_question(e) is None

    def test_empty_message(self) -> None:
        e = self._make_msg_event("")
        assert self.parser.detect_question(e) is None

    def test_short_message(self) -> None:
        e = self._make_msg_event("好")
        assert self.parser.detect_question(e) is None


# ──────────────────────────────────────────────────────
# 3. 完成 & 错误检测
# ──────────────────────────────────────────────────────


class TestDetectCompletionAndError:
    def setup_method(self) -> None:
        self.parser = JSONLParser()

    def test_detect_completion(self) -> None:
        e = JSONLEvent(type="session_end", timestamp=1.0, content={})
        assert self.parser.detect_completion(e) is True

    def test_non_session_end(self) -> None:
        e = JSONLEvent(type="agent_message", timestamp=1.0, content={})
        assert self.parser.detect_completion(e) is False

    def test_detect_error(self) -> None:
        e = JSONLEvent(type="error", timestamp=1.0, content={"message": "crash"})
        error = self.parser.detect_error(e)
        assert error == "crash"

    def test_detect_error_no_message(self) -> None:
        e = JSONLEvent(type="error", timestamp=1.0, content={"code": 500})
        error = self.parser.detect_error(e)
        assert error is not None  # 使用 str(content) 兜底

    def test_non_error_event(self) -> None:
        e = JSONLEvent(type="agent_message", timestamp=1.0, content={})
        assert self.parser.detect_error(e) is None


# ──────────────────────────────────────────────────────
# 4. 流式解析 & 文件解析
# ──────────────────────────────────────────────────────


class TestStreamAndFileParsing:
    def setup_method(self) -> None:
        self.parser = JSONLParser()

    def test_parse_stream(self) -> None:
        lines = "\n".join([
            json.dumps({"type": "agent_message", "timestamp": 1.0, "message": "hi"}),
            json.dumps({"type": "tool_call", "timestamp": 2.0, "tool": "test"}),
            "bad line",
            json.dumps({"type": "session_end", "timestamp": 3.0}),
        ])
        stream = StringIO(lines)
        events = self.parser.parse_stream(stream)
        assert len(events) == 3
        assert events[0].type == "agent_message"
        assert events[2].type == "session_end"

    def test_parse_file(self, tmp_path: Path) -> None:
        content = "\n".join([
            json.dumps({"type": "agent_message", "timestamp": 1.0, "message": "开始"}),
            json.dumps({"type": "session_end", "timestamp": 2.0}),
        ])
        file_path = tmp_path / "test.jsonl"
        file_path.write_text(content, encoding="utf-8")

        events = self.parser.parse_file(file_path)
        assert len(events) == 2


# ──────────────────────────────────────────────────────
# 5. 批量分析
# ──────────────────────────────────────────────────────


class TestAnalyzeEvents:
    def setup_method(self) -> None:
        self.parser = JSONLParser()

    def _make_events(self) -> list[JSONLEvent]:
        return [
            JSONLEvent("agent_message", 1.0, {"message": "分析开始"}),
            JSONLEvent("agent_message", 2.0, {"message": "这个接口应该用什么协议？"}),
            JSONLEvent("tool_call", 3.0, {"tool": "write_file"}),
            JSONLEvent("tool_result", 4.0, {"result": "ok"}),
            JSONLEvent("tool_call", 5.0, {"tool": "run_command"}),
            JSONLEvent("tool_result", 6.0, {"result": "ok"}),
            JSONLEvent("agent_message", 7.0, {"message": "完成"}),
            JSONLEvent("session_end", 8.0, {}),
        ]

    def test_summary_counts(self) -> None:
        events = self._make_events()
        summary = self.parser.analyze_events(events)

        assert summary.total_events == 8
        assert summary.type_counts["agent_message"] == 3
        assert summary.type_counts["tool_call"] == 2
        assert summary.type_counts["tool_result"] == 2
        assert summary.type_counts["session_end"] == 1

    def test_summary_questions(self) -> None:
        events = self._make_events()
        summary = self.parser.analyze_events(events)

        assert summary.has_questions is True
        assert len(summary.questions) == 1
        assert "协议" in summary.questions[0]

    def test_summary_tool_calls(self) -> None:
        events = self._make_events()
        summary = self.parser.analyze_events(events)

        assert "write_file" in summary.tool_calls
        assert "run_command" in summary.tool_calls

    def test_summary_success(self) -> None:
        events = self._make_events()
        summary = self.parser.analyze_events(events)
        assert summary.completed is True
        assert summary.success is True

    def test_summary_with_error(self) -> None:
        events = [
            JSONLEvent("agent_message", 1.0, {"message": "开始"}),
            JSONLEvent("error", 2.0, {"message": "crash"}),
            JSONLEvent("session_end", 3.0, {}),
        ]
        summary = self.parser.analyze_events(events)
        assert summary.completed is True
        assert summary.success is False
        assert summary.has_errors is True

    def test_summary_repr(self) -> None:
        summary = EventSummary(total_events=5, success=True)
        assert "5" in repr(summary)

    def test_empty_events(self) -> None:
        summary = self.parser.analyze_events([])
        assert summary.total_events == 0
        assert summary.success is False
        assert summary.completed is False


# ──────────────────────────────────────────────────────
# 运行入口
# ──────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
