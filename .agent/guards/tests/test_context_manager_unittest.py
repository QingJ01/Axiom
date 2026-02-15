import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MEMORY_DIR = PROJECT_ROOT / ".agent" / "memory"
if str(MEMORY_DIR) not in sys.path:
    sys.path.insert(0, str(MEMORY_DIR))

from context_manager import ContextManager


class TestContextManager(unittest.TestCase):
    def _make_memory(self, base: Path) -> None:
        memory = base / ".agent" / "memory"
        memory.mkdir(parents=True, exist_ok=True)
        (memory / "active_context.md").write_text(
            """---
session_id: \"test-session\"
task_status: IDLE
last_checkpoint: cp-1
---

## 📝 任务队列 (Active Tasks)
- [x] **[DONE]** T-001: old
""",
            encoding="utf-8",
        )
        (memory / "state_machine.md").write_text(
            """## 1. 状态定义 (States)
| 状态 | 代码 | 对应阶段 | 描述 |
|-----|------|---------|-----|
| 空闲 | IDLE | - | - |
| 起草中 | DRAFTING | - | - |
| 待确认 | CONFIRMING | - | - |
| 开发中 | IMPLEMENTING | - | - |
| 阻塞 | BLOCKED | - | - |
""",
            encoding="utf-8",
        )
        (memory / "project_decisions.md").write_text(
            """# Project Decisions

## 5. 已知问题 (错误模式学习)
| 日期 | 错误类型 | 根因分析 | 修复方案 |
|------|---------|---------|---------|
| 2026-02-12 | X | Y | Z |
""",
            encoding="utf-8",
        )

    def test_update_state_valid_transition(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self._make_memory(base)
            mgr = ContextManager(base_dir=base)

            msg = mgr.update_state("DRAFTING")
            self.assertIn("IDLE", msg)
            self.assertIn("DRAFTING", msg)

            text = (base / ".agent" / "memory" / "active_context.md").read_text(encoding="utf-8")
            self.assertIn("task_status: DRAFTING", text)

    def test_update_state_invalid_transition_raises(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self._make_memory(base)
            mgr = ContextManager(base_dir=base)

            with self.assertRaises(ValueError):
                mgr.update_state("BLOCKED")

    def test_update_progress_appends_task_line(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self._make_memory(base)
            mgr = ContextManager(base_dir=base)

            mgr.update_progress("T-002", "PENDING", "new item")
            text = (base / ".agent" / "memory" / "active_context.md").read_text(encoding="utf-8")
            self.assertIn("T-002", text)
            self.assertIn("new item", text)

    def test_save_decision_appends_entry(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self._make_memory(base)
            mgr = ContextManager(base_dir=base)

            mgr.save_decision("Rule", "Use strict CI gate")
            text = (base / ".agent" / "memory" / "project_decisions.md").read_text(encoding="utf-8")
            self.assertIn("Use strict CI gate", text)

    def test_record_error_appends_known_issue_row(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self._make_memory(base)
            mgr = ContextManager(base_dir=base)

            mgr.record_error("BuildError", "bad dep", "pin version", "build")
            text = (base / ".agent" / "memory" / "project_decisions.md").read_text(encoding="utf-8")
            self.assertIn("BuildError", text)
            self.assertIn("pin version", text)


if __name__ == "__main__":
    unittest.main()
