"""
prd_updater.py — PRD 状态回写 (T-106)

任务完成后自动将 PRD 中对应行从 `⏳ PENDING` 更新为 `✅ DONE`。

支持特性:
    - 按任务 ID 匹配并更新状态
    - 支持 PRD Markdown 表格格式
    - 批量更新
    - 变更日志记录
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from .core import TaskStatus

logger = logging.getLogger(__name__)


@dataclass
class UpdateResult:
    """PRD 更新结果。"""
    success: bool
    task_id: str
    old_status: str
    new_status: str
    line_number: int | None = None
    message: str = ""


class PRDUpdater:
    """PRD 状态回写器。

    使用方式:
        updater = PRDUpdater("docs/prd/axiom-v4-dev.md")
        result = updater.update_task_status("T-101", TaskStatus.DONE)
    """

    # PRD 表格中的状态标记
    STATUS_MARKERS = {
        TaskStatus.PENDING: "⏳ PENDING",
        TaskStatus.IN_PROGRESS: "🔄 IN_PROGRESS",
        TaskStatus.DONE: "✅ DONE",
        TaskStatus.BLOCKED: "🚫 BLOCKED",
        TaskStatus.RETRY: "🔁 RETRY",
        TaskStatus.FAILED: "❌ FAILED",
        TaskStatus.SKIPPED: "⏭️ SKIPPED",
    }

    def __init__(self, prd_path: str | Path) -> None:
        """
        Args:
            prd_path: PRD 文件路径
        """
        self.prd_path = Path(prd_path)
        self._update_log: list[UpdateResult] = []

    # ── 公开 API ────────────────────────────────────────

    def update_task_status(
        self,
        task_id: str,
        new_status: TaskStatus,
    ) -> UpdateResult:
        """更新 PRD 中指定任务的状态。

        Args:
            task_id: 任务 ID (e.g., "T-101")
            new_status: 新状态

        Returns:
            UpdateResult
        """
        if not self.prd_path.exists():
            return UpdateResult(
                success=False,
                task_id=task_id,
                old_status="",
                new_status=self.STATUS_MARKERS.get(new_status, str(new_status)),
                message=f"PRD file not found: {self.prd_path}",
            )

        try:
            content = self.prd_path.read_text(encoding="utf-8")
            new_content, old_status, line_num = self._replace_status(
                content, task_id, new_status
            )

            if new_content == content:
                return UpdateResult(
                    success=False,
                    task_id=task_id,
                    old_status=old_status or "unknown",
                    new_status=self.STATUS_MARKERS.get(new_status, str(new_status)),
                    message=f"Task {task_id} not found in PRD or status unchanged",
                )

            self.prd_path.write_text(new_content, encoding="utf-8")

            result = UpdateResult(
                success=True,
                task_id=task_id,
                old_status=old_status or "unknown",
                new_status=self.STATUS_MARKERS.get(new_status, str(new_status)),
                line_number=line_num,
                message=f"Updated {task_id}: {old_status} → {self.STATUS_MARKERS.get(new_status)}",
            )
            self._update_log.append(result)
            logger.info(result.message)
            return result

        except Exception as exc:
            logger.error("Failed to update PRD: %s", exc)
            return UpdateResult(
                success=False,
                task_id=task_id,
                old_status="",
                new_status=self.STATUS_MARKERS.get(new_status, str(new_status)),
                message=str(exc),
            )

    def batch_update(
        self,
        updates: list[tuple[str, TaskStatus]],
    ) -> list[UpdateResult]:
        """批量更新多个任务状态。

        Args:
            updates: [(task_id, new_status), ...]

        Returns:
            UpdateResult 列表
        """
        results: list[UpdateResult] = []
        for task_id, status in updates:
            result = self.update_task_status(task_id, status)
            results.append(result)
        return results

    def get_task_status(self, task_id: str) -> str | None:
        """查询 PRD 中指定任务的当前状态。

        Args:
            task_id: 任务 ID

        Returns:
            状态文本，或 None（未找到）
        """
        if not self.prd_path.exists():
            return None

        content = self.prd_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            if task_id in line:
                for status in self.STATUS_MARKERS.values():
                    if status in line:
                        return status
        return None

    @property
    def update_log(self) -> list[UpdateResult]:
        """历史更新日志。"""
        return list(self._update_log)

    # ── 内部方法 ────────────────────────────────────────

    def _replace_status(
        self,
        content: str,
        task_id: str,
        new_status: TaskStatus,
    ) -> tuple[str, str | None, int | None]:
        """在 PRD 内容中替换指定任务的状态。

        Returns:
            (new_content, old_status_text, line_number)
        """
        new_marker = self.STATUS_MARKERS.get(new_status, str(new_status))
        lines = content.splitlines(keepends=True)
        old_status: str | None = None
        line_num: int | None = None

        for i, line in enumerate(lines):
            if task_id not in line:
                continue

            # 找到包含 task_id 的行，替换其中的状态标记
            for status, marker in self.STATUS_MARKERS.items():
                if marker in line:
                    old_status = marker
                    lines[i] = line.replace(marker, new_marker)
                    line_num = i + 1
                    break

            if old_status:
                break

        return "".join(lines), old_status, line_num
