"""
test_injector.py — 重启注入机制单元测试 (T-103)

测试覆盖:
  - build_injected_prompt: QA 对注入格式
  - compress_context: Prompt 压缩
  - should_restart: 重启条件判断（次数上限 / 风险检测）
  - execute_with_injection: Mock Worker 提问 → 注入答案 → 重启
  - BLOCKED 场景: 无法回答 / 超过重启上限
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_dispatcher_parent = str(Path(__file__).resolve().parent.parent.parent)
if _dispatcher_parent not in sys.path:
    sys.path.insert(0, _dispatcher_parent)

from dispatcher.core import JSONLEvent, TaskSpec, TaskStatus, WorkerResult
from dispatcher.jsonl_parser import JSONLParser
from dispatcher.restart_injector import (
    InjectionContext,
    QAPair,
    RestartInjector,
    MAX_PROMPT_CHARS,
)
from dispatcher.worker import Worker, WorkerConfig


# ──────────────────────────────────────────────────────
# 1. QAPair 和 InjectionContext
# ──────────────────────────────────────────────────────


class TestQAPair:
    def test_basic_creation(self) -> None:
        qa = QAPair(question="问题", answer="回答", restart_index=0)
        assert qa.question == "问题"
        assert qa.answer == "回答"
        assert qa.restart_index == 0


class TestInjectionContext:
    def test_total_restarts(self) -> None:
        ctx = InjectionContext(task_id="T-001", original_prompt="test")
        assert ctx.total_restarts == 0
        ctx.restart_count = 2
        assert ctx.total_restarts == 2


# ──────────────────────────────────────────────────────
# 2. build_injected_prompt
# ──────────────────────────────────────────────────────


class TestBuildInjectedPrompt:
    def setup_method(self) -> None:
        self.worker = Worker(WorkerConfig())
        self.injector = RestartInjector(self.worker)

    def test_no_qa_pairs(self) -> None:
        prompt = self.injector.build_injected_prompt("原始Prompt", [])
        assert prompt == "原始Prompt"

    def test_single_qa_pair(self) -> None:
        qa = [QAPair("数据库用哪个？", "用 PostgreSQL", 0)]
        prompt = self.injector.build_injected_prompt("执行任务", qa)
        assert "补充信息 1" in prompt
        assert "数据库用哪个？" in prompt
        assert "PostgreSQL" in prompt

    def test_multiple_qa_pairs(self) -> None:
        qa = [
            QAPair("问题1？", "答案1", 0),
            QAPair("问题2？", "答案2", 1),
            QAPair("问题3？", "答案3", 2),
        ]
        prompt = self.injector.build_injected_prompt("原始", qa)
        assert "补充信息 1" in prompt
        assert "补充信息 2" in prompt
        assert "补充信息 3" in prompt

    def test_original_preserved(self) -> None:
        qa = [QAPair("Q?", "A", 0)]
        prompt = self.injector.build_injected_prompt("重要指令不能丢", qa)
        assert "重要指令不能丢" in prompt


# ──────────────────────────────────────────────────────
# 3. compress_context
# ──────────────────────────────────────────────────────


class TestCompressContext:
    def setup_method(self) -> None:
        self.worker = Worker(WorkerConfig())
        self.injector = RestartInjector(self.worker)

    def test_no_compression_needed(self) -> None:
        short = "短文本" * 100
        assert self.injector.compress_context(short) == short

    def test_compression_applied(self) -> None:
        # 生成超长 Prompt
        long_prompt = "X" * (MAX_PROMPT_CHARS + 5000)
        compressed = self.injector.compress_context(long_prompt)
        assert len(compressed) < len(long_prompt)
        assert "上下文已压缩" in compressed

    def test_head_preserved(self) -> None:
        head = "重要头部" * 400  # 确保超过 2000 字符
        long_prompt = head + "Y" * (MAX_PROMPT_CHARS + 1000)
        compressed = self.injector.compress_context(long_prompt)
        assert compressed.startswith("重要头部重要头部")


# ──────────────────────────────────────────────────────
# 4. should_restart
# ──────────────────────────────────────────────────────


class TestShouldRestart:
    def setup_method(self) -> None:
        self.worker = Worker(WorkerConfig())
        self.injector = RestartInjector(self.worker)

    def test_first_restart_allowed(self) -> None:
        # 无上下文时，首次允许重启
        assert self.injector.should_restart("T-001", "普通问题？") is True

    def test_within_limit(self) -> None:
        ctx = InjectionContext(task_id="T-001", original_prompt="p", restart_count=2)
        self.injector._contexts["T-001"] = ctx
        assert self.injector.should_restart("T-001", "普通问题？") is True

    def test_exceeds_limit(self) -> None:
        ctx = InjectionContext(task_id="T-001", original_prompt="p", restart_count=3)
        self.injector._contexts["T-001"] = ctx
        assert self.injector.should_restart("T-001", "普通问题？") is False

    def test_risk_keyword_blocked(self) -> None:
        ctx = InjectionContext(task_id="T-001", original_prompt="p", restart_count=0)
        self.injector._contexts["T-001"] = ctx
        assert self.injector.should_restart("T-001", "要不要删除数据库？") is False

    def test_risk_keyword_production(self) -> None:
        ctx = InjectionContext(task_id="T-001", original_prompt="p", restart_count=0)
        self.injector._contexts["T-001"] = ctx
        assert self.injector.should_restart("T-001", "deploy to production?") is False

    def test_risk_keyword_rm_rf(self) -> None:
        ctx = InjectionContext(task_id="T-001", original_prompt="p", restart_count=0)
        self.injector._contexts["T-001"] = ctx
        assert self.injector.should_restart("T-001", "执行 rm -rf /tmp/data") is False

    def test_safe_question(self) -> None:
        ctx = InjectionContext(task_id="T-001", original_prompt="p", restart_count=0)
        self.injector._contexts["T-001"] = ctx
        assert self.injector.should_restart("T-001", "用什么命名规范？") is True


# ──────────────────────────────────────────────────────
# 5. execute_with_injection (集成测试, Mock Worker)
# ──────────────────────────────────────────────────────


class TestExecuteWithInjection:
    """使用 Mock Worker.execute 模拟提问 → 注入 → 重启的完整流程。"""

    def _make_task(self) -> TaskSpec:
        return TaskSpec(id="T-TEST", name="测试任务", description="注入测试")

    def test_no_question_no_restart(self) -> None:
        """Worker 不提问，直接完成。"""
        worker = Worker(WorkerConfig())
        worker.execute = MagicMock(return_value=WorkerResult(
            task_id="T-TEST", success=True, output="完成",
            questions=[], restart_count=0,
        ))

        injector = RestartInjector(worker)
        result = injector.execute_with_injection(self._make_task())

        assert result.success is True
        assert result.restart_count == 0
        assert worker.execute.call_count == 1

    def test_one_question_one_restart(self) -> None:
        """Worker 提问一次 → 注入答案 → 重启 → 完成。"""
        worker = Worker(WorkerConfig())

        call_count = [0]

        def mock_execute(task, prompt=None, on_event=None):
            call_count[0] += 1
            if call_count[0] == 1:
                return WorkerResult(
                    task_id="T-TEST", success=False, output="",
                    questions=["用什么框架？"],
                )
            else:
                return WorkerResult(
                    task_id="T-TEST", success=True, output="完成",
                    questions=[],
                )

        worker.execute = mock_execute
        worker._build_prompt = MagicMock(return_value="执行任务")

        injector = RestartInjector(worker)

        def answer_func(task_id: str, question: str) -> str:
            return "用 Flask"

        result = injector.execute_with_injection(self._make_task(), answer_func=answer_func)

        assert result.success is True
        assert result.restart_count == 1
        assert call_count[0] == 2

    def test_max_restart_limit(self) -> None:
        """超过 3 次重启后标记失败。"""
        worker = Worker(WorkerConfig())

        def mock_execute(task, prompt=None, on_event=None):
            return WorkerResult(
                task_id="T-TEST", success=False, output="",
                questions=["再问一次？"],
            )

        worker.execute = mock_execute
        worker._build_prompt = MagicMock(return_value="执行任务")

        injector = RestartInjector(worker)

        def answer_func(task_id: str, question: str) -> str:
            return "回答"

        result = injector.execute_with_injection(self._make_task(), answer_func=answer_func)

        # 应该在第 4 次时停止 (0,1,2 OK → 3 触发上限)
        assert result.success is False
        assert "max restarts" in (result.error_message or "").lower() or "exceeded" in (result.error_message or "").lower()

    def test_blocked_when_no_answer(self) -> None:
        """answer_func 返回 None → 标记 BLOCKED。"""
        worker = Worker(WorkerConfig())
        worker.execute = MagicMock(return_value=WorkerResult(
            task_id="T-TEST", success=False, output="",
            questions=["这是什么需求？"],
        ))
        worker._build_prompt = MagicMock(return_value="执行任务")

        injector = RestartInjector(worker)

        def answer_func(task_id: str, question: str) -> str | None:
            return None

        result = injector.execute_with_injection(self._make_task(), answer_func=answer_func)

        assert result.success is False
        assert "BLOCKED" in (result.error_message or "")

    def test_risk_question_blocked(self) -> None:
        """涉及风险操作的问题无法重启。"""
        worker = Worker(WorkerConfig())
        worker.execute = MagicMock(return_value=WorkerResult(
            task_id="T-TEST", success=False, output="",
            questions=["要不要删除数据库？"],
        ))
        worker._build_prompt = MagicMock(return_value="执行任务")

        injector = RestartInjector(worker)

        def answer_func(task_id: str, question: str) -> str:
            return "是的"

        result = injector.execute_with_injection(self._make_task(), answer_func=answer_func)

        assert result.success is False

    def test_qa_history_tracked(self) -> None:
        """验证 QA 历史被正确追踪。"""
        worker = Worker(WorkerConfig())
        call_count = [0]

        def mock_execute(task, prompt=None, on_event=None):
            call_count[0] += 1
            if call_count[0] <= 2:
                return WorkerResult(
                    task_id="T-TEST", success=False, output="",
                    questions=[f"问题{call_count[0]}？"],
                )
            return WorkerResult(
                task_id="T-TEST", success=True, output="完成", questions=[],
            )

        worker.execute = mock_execute
        worker._build_prompt = MagicMock(return_value="执行任务")

        injector = RestartInjector(worker)

        def answer_func(task_id: str, question: str) -> str:
            return f"回答: {question}"

        result = injector.execute_with_injection(self._make_task(), answer_func=answer_func)

        ctx = injector.get_context("T-TEST")
        assert ctx is not None
        assert len(ctx.qa_pairs) == 2
        assert ctx.restart_count == 2


# ──────────────────────────────────────────────────────
# 运行入口
# ──────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
