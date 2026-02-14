"""
test_e2e.py — 端到端集成测试 (T-107)

使用 Mini PRD (3 任务) 验证完整流程:
    1. parse_prd() → 正确提取任务列表
    2. 依赖顺序调度
    3. Worker 执行 (Mock)
    4. 重启注入
    5. PM 决策引擎集成
    6. Git 自动提交 (Mock git)
    7. PRD 状态回写
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

from dispatcher.core import TaskSpec, TaskStatus, WorkerResult
from dispatcher.decision_engine import DecisionEngine, DecisionType
from dispatcher.git_ops import GitOps, GitResult
from dispatcher.jsonl_parser import JSONLParser
from dispatcher.main import Dispatcher, DispatchReport
from dispatcher.prd_updater import PRDUpdater
from dispatcher.restart_injector import RestartInjector
from dispatcher.worker import Worker, WorkerConfig


# ──────────────────────────────────────────────────────
# Mini PRD 样本
# ──────────────────────────────────────────────────────

MINI_PRD = textwrap.dedent("""\
    # Mini PRD — 端到端测试

    ## Tasks

    | ID | 任务 | 状态 | 描述 | 预估 | 依赖 | 验收标准 |
    |----|------|------|------|-----|------|---------|
    | T-001 | **创建配置文件** | ⏳ PENDING | 创建 config.yaml 并写入基本配置 | 1h | - | 文件存在 |
    | T-002 | **实现工具类** | ⏳ PENDING | 创建 utils.py 包含 helper 函数 | 2h | T-001 | 函数可调用 |
    | T-003 | **编写测试** | ⏳ PENDING | 为工具类编写单元测试 | 1h | T-001, T-002 | 测试通过 |
""")

# 已全部完成的 PRD（用于验证不重复执行）
COMPLETED_PRD = textwrap.dedent("""\
    # Completed PRD

    | ID | 任务 | 状态 | 描述 | 预估 | 依赖 | 验收标准 |
    |----|------|------|------|-----|------|---------|
    | T-001 | **已完成的任务** | ✅ DONE | 已完成 | 1h | - | 已通过 |
""")


# ──────────────────────────────────────────────────────
# 1. PRD 解析测试
# ──────────────────────────────────────────────────────


class TestParsePRD:
    """测试 Dispatcher.parse_prd() 的 PRD 解析能力。"""

    def test_parse_mini_prd(self, tmp_path: Path) -> None:
        prd = tmp_path / "mini.md"
        prd.write_text(MINI_PRD, encoding="utf-8")

        dispatcher = Dispatcher(prd_path=prd, dry_run=True)
        tasks = dispatcher.parse_prd()

        assert len(tasks) == 3
        assert tasks[0].id == "T-001"
        assert tasks[0].name == "创建配置文件"
        assert tasks[0].dependencies == []
        assert tasks[1].id == "T-002"
        assert tasks[1].dependencies == ["T-001"]
        assert tasks[2].id == "T-003"
        assert "T-001" in tasks[2].dependencies
        assert "T-002" in tasks[2].dependencies

    def test_parse_no_pending(self, tmp_path: Path) -> None:
        prd = tmp_path / "done.md"
        prd.write_text(COMPLETED_PRD, encoding="utf-8")

        dispatcher = Dispatcher(prd_path=prd, dry_run=True)
        tasks = dispatcher.parse_prd()
        assert len(tasks) == 0

    def test_parse_nonexistent(self, tmp_path: Path) -> None:
        dispatcher = Dispatcher(prd_path=tmp_path / "no.md", dry_run=True)
        tasks = dispatcher.parse_prd()
        assert len(tasks) == 0

    def test_timeout_estimation(self, tmp_path: Path) -> None:
        prd = tmp_path / "mini.md"
        prd.write_text(MINI_PRD, encoding="utf-8")

        dispatcher = Dispatcher(prd_path=prd, dry_run=True)
        tasks = dispatcher.parse_prd()

        # 1h → 1 * 3 * 3600 + 600 = 11400
        assert tasks[0].timeout_seconds == 11400
        # 2h → 2 * 3 * 3600 + 600 = 22200
        assert tasks[1].timeout_seconds == 22200


# ──────────────────────────────────────────────────────
# 2. Dry Run 测试
# ──────────────────────────────────────────────────────


class TestDryRun:
    """dry_run=True 时只解析不执行。"""

    def test_dry_run_no_execution(self, tmp_path: Path) -> None:
        prd = tmp_path / "mini.md"
        prd.write_text(MINI_PRD, encoding="utf-8")

        dispatcher = Dispatcher(prd_path=prd, dry_run=True)
        report = dispatcher.run()

        assert report.total_tasks == 3
        assert report.done == 0
        assert report.skipped == 3
        assert len(report.results) == 0


# ──────────────────────────────────────────────────────
# 3. 端到端集成测试 (Mock Worker)
# ──────────────────────────────────────────────────────


class TestE2EWithMock:
    """模拟 Worker 输出，验证完整调度流程。"""

    def test_all_tasks_succeed(self, tmp_path: Path) -> None:
        """3 个任务全部成功完成。"""
        prd = tmp_path / "mini.md"
        prd.write_text(MINI_PRD, encoding="utf-8")

        dispatcher = Dispatcher(prd_path=prd, repo_path=tmp_path)

        # Mock Worker.execute → 全部成功
        success_result = WorkerResult(
            task_id="", success=True, output="任务完成",
        )

        def mock_execute(task, prompt=None, on_event=None):
            return WorkerResult(
                task_id=task.id, success=True, output=f"{task.name} 完成",
            )

        dispatcher.worker.execute = mock_execute
        dispatcher.injector.worker = dispatcher.worker

        # Mock Git （避免真实 git 操作）
        dispatcher.git.auto_commit = MagicMock(
            return_value=GitResult(success=True, message="committed", commit_hash="abc123")
        )

        report = dispatcher.run()

        assert report.total_tasks == 3
        assert report.done == 3
        assert report.failed == 0
        assert report.blocked == 0

        # 验证 PRD 被正确更新
        content = prd.read_text(encoding="utf-8")
        assert content.count("✅ DONE") == 3
        assert "⏳ PENDING" not in content

        # 验证 Git 被调用了 3 次
        assert dispatcher.git.auto_commit.call_count == 3

    def test_task_with_question_auto_answered(self, tmp_path: Path) -> None:
        """Worker 提问 → 决策引擎自动回答 → 重启 → 完成。"""
        prd = tmp_path / "mini.md"
        prd.write_text(MINI_PRD, encoding="utf-8")

        dispatcher = Dispatcher(prd_path=prd, repo_path=tmp_path)

        call_counts: dict[str, int] = {}

        def mock_execute(task, prompt=None, on_event=None):
            call_counts[task.id] = call_counts.get(task.id, 0) + 1
            # T-001 第一次提问，第二次成功
            if task.id == "T-001" and call_counts[task.id] == 1:
                return WorkerResult(
                    task_id=task.id, success=False, output="",
                    questions=["文件名用什么规范？"],
                )
            return WorkerResult(
                task_id=task.id, success=True, output=f"{task.name} 完成",
            )

        dispatcher.worker.execute = mock_execute
        dispatcher.injector.worker = dispatcher.worker

        dispatcher.git.auto_commit = MagicMock(
            return_value=GitResult(success=True, message="ok", commit_hash="x")
        )

        report = dispatcher.run()

        assert report.done == 3
        assert report.failed == 0
        # T-001 被调用了 2 次（1 次提问 + 1 次重启后成功）
        assert call_counts["T-001"] == 2

    def test_dependency_order(self, tmp_path: Path) -> None:
        """验证依赖顺序: T-001 → T-002 → T-003。"""
        prd = tmp_path / "mini.md"
        prd.write_text(MINI_PRD, encoding="utf-8")

        dispatcher = Dispatcher(prd_path=prd, repo_path=tmp_path)

        execution_order: list[str] = []

        def mock_execute(task, prompt=None, on_event=None):
            execution_order.append(task.id)
            return WorkerResult(
                task_id=task.id, success=True, output="ok",
            )

        dispatcher.worker.execute = mock_execute
        dispatcher.injector.worker = dispatcher.worker

        dispatcher.git.auto_commit = MagicMock(
            return_value=GitResult(success=True, message="ok", commit_hash="x")
        )

        report = dispatcher.run()

        assert execution_order == ["T-001", "T-002", "T-003"]

    def test_dependency_skip_when_unmet(self, tmp_path: Path) -> None:
        """T-001 失败时，T-002 和 T-003 应被跳过（依赖未满足）。"""
        prd = tmp_path / "mini.md"
        prd.write_text(MINI_PRD, encoding="utf-8")

        dispatcher = Dispatcher(prd_path=prd, repo_path=tmp_path)

        def mock_execute(task, prompt=None, on_event=None):
            if task.id == "T-001":
                return WorkerResult(
                    task_id=task.id, success=False, output="",
                    error_message="模拟失败",
                )
            return WorkerResult(
                task_id=task.id, success=True, output="ok",
            )

        dispatcher.worker.execute = mock_execute
        dispatcher.injector.worker = dispatcher.worker

        dispatcher.git.auto_commit = MagicMock(
            return_value=GitResult(success=True, message="ok", commit_hash="x")
        )

        report = dispatcher.run()

        assert report.failed == 1  # T-001
        assert report.skipped == 2  # T-002, T-003
        assert report.done == 0

    def test_blocked_task(self, tmp_path: Path) -> None:
        """Worker 提出需求歧义问题 → 决策引擎返回 BLOCKED。"""
        prd = tmp_path / "mini.md"
        prd.write_text(MINI_PRD, encoding="utf-8")

        dispatcher = Dispatcher(prd_path=prd, repo_path=tmp_path)

        def mock_execute(task, prompt=None, on_event=None):
            if task.id == "T-001":
                return WorkerResult(
                    task_id=task.id, success=False, output="",
                    questions=["这个需求到底是什么意思？"],
                )
            return WorkerResult(
                task_id=task.id, success=True, output="ok",
            )

        dispatcher.worker.execute = mock_execute
        dispatcher.injector.worker = dispatcher.worker

        dispatcher.git.auto_commit = MagicMock(
            return_value=GitResult(success=True, message="ok", commit_hash="x")
        )

        report = dispatcher.run()

        # T-001 BLOCKED，T-002/T-003 依赖未满足被跳过
        assert report.blocked == 1
        assert report.skipped == 2

        # 验证 PRD 中 T-001 被标记为 BLOCKED
        content = prd.read_text(encoding="utf-8")
        assert "🚫 BLOCKED" in content


# ──────────────────────────────────────────────────────
# 4. DispatchReport 测试
# ──────────────────────────────────────────────────────


class TestDispatchReport:
    def test_success_rate(self) -> None:
        report = DispatchReport(total_tasks=10, done=7, failed=2, blocked=1)
        assert report.success_rate == 0.7

    def test_summary_output(self) -> None:
        report = DispatchReport(total_tasks=3, done=3)
        s = report.summary()
        assert "3" in s
        assert "100%" in s

    def test_zero_tasks(self) -> None:
        report = DispatchReport()
        assert report.success_rate == 0.0


# ──────────────────────────────────────────────────────
# 5. 组件集成验证
# ──────────────────────────────────────────────────────


class TestComponentIntegration:
    """验证各组件的接口兼容性。"""

    def test_decision_engine_as_callback(self) -> None:
        engine = DecisionEngine()
        callback = engine.as_answer_callback()

        # 技术问题 → 返回答案
        answer = callback("T-001", "文件名用什么命名规范？")
        assert answer is not None

        # 需求问题 → 返回 None
        answer = callback("T-001", "这个需求要不要做？")
        assert answer is None

    def test_prd_updater_batch(self, tmp_path: Path) -> None:
        prd = tmp_path / "mini.md"
        prd.write_text(MINI_PRD, encoding="utf-8")

        updater = PRDUpdater(prd)
        results = updater.batch_update([
            ("T-001", TaskStatus.DONE),
            ("T-002", TaskStatus.DONE),
            ("T-003", TaskStatus.DONE),
        ])

        assert all(r.success for r in results)
        content = prd.read_text(encoding="utf-8")
        assert content.count("✅ DONE") == 3

    def test_parser_analyze_full_session(self) -> None:
        from dispatcher.core import JSONLEvent

        parser = JSONLParser()
        events = [
            JSONLEvent("agent_message", 1.0, {"message": "开始执行"}),
            JSONLEvent("tool_call", 2.0, {"tool": "write_file"}),
            JSONLEvent("tool_result", 3.0, {"result": "ok"}),
            JSONLEvent("agent_message", 4.0, {"message": "完成任务"}),
            JSONLEvent("session_end", 5.0, {}),
        ]
        summary = parser.analyze_events(events)

        assert summary.total_events == 5
        assert summary.success is True
        assert summary.has_questions is False
        assert "write_file" in summary.tool_calls


# ──────────────────────────────────────────────────────
# 运行入口
# ──────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
