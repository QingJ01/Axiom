"""
test_prd_updater.py — PRD 状态回写测试 (T-106)

测试覆盖:
  - 更新 PENDING → DONE
  - 更新 PENDING → BLOCKED / FAILED
  - 文件不存在的处理
  - 任务未找到的处理
  - 批量更新
  - 状态查询
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_dispatcher_parent = str(Path(__file__).resolve().parent.parent.parent)
if _dispatcher_parent not in sys.path:
    sys.path.insert(0, _dispatcher_parent)

from dispatcher.core import TaskStatus
from dispatcher.prd_updater import PRDUpdater

SAMPLE_PRD = """\
# Test PRD

## Tasks

| ID | 任务 | 状态 | 描述 | 预估 | 依赖 | 验收标准 |
|----|------|------|------|-----|------|---------|
| T-101 | **Worker 封装器** | ⏳ PENDING | 封装 codex exec | 3h | - | 单元测试 |
| T-102 | **JSONL 解析器** | ⏳ PENDING | 解析事件流 | 2h | T-101 | 单元测试 |
| T-103 | **重启注入** | ⏳ PENDING | 检测提问并重启 | 3h | T-101, T-102 | 集成测试 |
"""


class TestPRDUpdater:
    def setup_method(self) -> None:
        pass

    def test_update_pending_to_done(self, tmp_path: Path) -> None:
        prd = tmp_path / "test.md"
        prd.write_text(SAMPLE_PRD, encoding="utf-8")

        updater = PRDUpdater(prd)
        result = updater.update_task_status("T-101", TaskStatus.DONE)

        assert result.success is True
        assert "PENDING" in result.old_status
        assert "DONE" in result.new_status

        # 验证文件内容
        content = prd.read_text(encoding="utf-8")
        assert "✅ DONE" in content
        assert content.count("⏳ PENDING") == 2  # 只有 T-101 被更新

    def test_update_to_blocked(self, tmp_path: Path) -> None:
        prd = tmp_path / "test.md"
        prd.write_text(SAMPLE_PRD, encoding="utf-8")

        updater = PRDUpdater(prd)
        result = updater.update_task_status("T-102", TaskStatus.BLOCKED)

        assert result.success is True
        content = prd.read_text(encoding="utf-8")
        assert "🚫 BLOCKED" in content

    def test_update_to_failed(self, tmp_path: Path) -> None:
        prd = tmp_path / "test.md"
        prd.write_text(SAMPLE_PRD, encoding="utf-8")

        updater = PRDUpdater(prd)
        result = updater.update_task_status("T-103", TaskStatus.FAILED)

        assert result.success is True
        content = prd.read_text(encoding="utf-8")
        assert "❌ FAILED" in content

    def test_file_not_found(self, tmp_path: Path) -> None:
        updater = PRDUpdater(tmp_path / "nonexistent.md")
        result = updater.update_task_status("T-101", TaskStatus.DONE)

        assert result.success is False
        assert "not found" in result.message

    def test_task_not_found(self, tmp_path: Path) -> None:
        prd = tmp_path / "test.md"
        prd.write_text(SAMPLE_PRD, encoding="utf-8")

        updater = PRDUpdater(prd)
        result = updater.update_task_status("T-999", TaskStatus.DONE)

        assert result.success is False
        assert "not found" in result.message.lower() or "unchanged" in result.message.lower()

    def test_batch_update(self, tmp_path: Path) -> None:
        prd = tmp_path / "test.md"
        prd.write_text(SAMPLE_PRD, encoding="utf-8")

        updater = PRDUpdater(prd)
        results = updater.batch_update([
            ("T-101", TaskStatus.DONE),
            ("T-102", TaskStatus.DONE),
        ])

        assert len(results) == 2
        assert all(r.success for r in results)

        content = prd.read_text(encoding="utf-8")
        assert content.count("✅ DONE") == 2

    def test_get_task_status(self, tmp_path: Path) -> None:
        prd = tmp_path / "test.md"
        prd.write_text(SAMPLE_PRD, encoding="utf-8")

        updater = PRDUpdater(prd)
        status = updater.get_task_status("T-101")
        assert status is not None
        assert "PENDING" in status

    def test_get_task_status_not_found(self, tmp_path: Path) -> None:
        prd = tmp_path / "test.md"
        prd.write_text(SAMPLE_PRD, encoding="utf-8")

        updater = PRDUpdater(prd)
        assert updater.get_task_status("T-999") is None

    def test_update_log(self, tmp_path: Path) -> None:
        prd = tmp_path / "test.md"
        prd.write_text(SAMPLE_PRD, encoding="utf-8")

        updater = PRDUpdater(prd)
        updater.update_task_status("T-101", TaskStatus.DONE)
        updater.update_task_status("T-102", TaskStatus.DONE)

        assert len(updater.update_log) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
