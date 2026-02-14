"""
Learning Queue Processor — 学习队列处理器 (T-207)

管理 learning_queue.md 的完整生命周期：
  - 入队 (add_item): 任务完成/错误修复时自动添加素材
  - 按优先级处理 (process_queue): P0 > P1 > P2 > P3
  - 输出知识/模式
  - 标记已处理
  - 7 天后清理

Usage:
    from evolution.learning_queue import LearningQueue
    queue = LearningQueue(base_dir=".agent/memory")
    queue.add_item(source_type="code_change", source_id="T-201", priority="P1")
    queue.process_queue()
    queue.cleanup(days=7)
"""

from __future__ import annotations

import re
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class QueueItem:
    """学习队列条目"""
    id: str
    source_type: str       # code_change | error_fix | workflow_run | user_feedback
    source_id: str         # e.g. "T-201", "error-xxx"
    priority: str          # P0 | P1 | P2 | P3
    created: str = ""
    status: str = "pending"  # pending | processing | done
    description: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.created:
            self.created = datetime.date.today().isoformat()


PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


class LearningQueue:
    """
    学习队列处理器。

    职责：
    1. 管理待学习素材队列
    2. 按优先级处理
    3. 清理过期条目
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.queue_file = self.base_dir / "evolution" / "learning_queue.md"

    # ── Public API ──

    def add_item(
        self,
        source_type: str,
        source_id: str,
        priority: str = "P2",
        description: str = "",
        metadata: dict | None = None,
    ) -> QueueItem:
        """
        向队列添加一条学习素材。

        Parameters
        ----------
        source_type : str
            来源类型 (code_change | error_fix | workflow_run | user_feedback)
        source_id : str
            来源 ID (e.g. "T-201")
        priority : str
            优先级 (P0 > P1 > P2 > P3)
        description : str
            素材描述
        metadata : dict
            附加元数据

        Returns
        -------
        QueueItem
            添加的队列条目
        """
        items = self._load_items()
        next_id = f"LQ-{len(items) + 1:03d}"

        item = QueueItem(
            id=next_id,
            source_type=source_type,
            source_id=source_id,
            priority=priority,
            description=description,
            metadata=metadata or {},
        )

        items.append(item)
        self._save_queue(items)
        return item

    def process_queue(self, max_items: int = 10) -> list[QueueItem]:
        """
        按优先级处理队列中的待处理素材。

        Parameters
        ----------
        max_items : int
            最多处理几条

        Returns
        -------
        list[QueueItem]
            已处理的素材列表
        """
        items = self._load_items()
        pending = [i for i in items if i.status == "pending"]

        # 按优先级排序
        pending.sort(key=lambda x: PRIORITY_ORDER.get(x.priority, 99))

        processed = []
        for item in pending[:max_items]:
            item.status = "done"
            processed.append(item)

        self._save_queue(items)
        return processed

    def get_pending_count(self) -> int:
        """获取待处理素材数量"""
        items = self._load_items()
        return sum(1 for i in items if i.status == "pending")

    def get_stats(self) -> dict:
        """获取队列统计"""
        items = self._load_items()
        return {
            "pending": sum(1 for i in items if i.status == "pending"),
            "processing": sum(1 for i in items if i.status == "processing"),
            "done": sum(1 for i in items if i.status == "done"),
            "total": len(items),
        }

    def cleanup(self, days: int = 7) -> int:
        """
        清理已处理超过 {days} 天的条目。

        Returns
        -------
        int
            清理的条目数量
        """
        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        items = self._load_items()
        original_count = len(items)

        items = [
            i for i in items
            if not (i.status == "done" and self._parse_date(i.created) and self._parse_date(i.created) <= cutoff)
        ]

        cleaned = original_count - len(items)
        self._save_queue(items)
        return cleaned

    # ── Private Methods ──

    def _load_items(self) -> list[QueueItem]:
        """从 learning_queue.md 加载队列条目"""
        if not self.queue_file.exists():
            return []

        text = self.queue_file.read_text(encoding="utf-8")
        items = []

        # 解析 Pending Items 表
        in_table = False
        for line in text.split("\n"):
            if "| ID | Source Type |" in line:
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 7 and parts[1] != "-":
                    items.append(QueueItem(
                        id=parts[1],
                        source_type=parts[2],
                        source_id=parts[3],
                        priority=parts[4],
                        created=parts[5],
                        status=parts[6] if len(parts) > 6 else "pending",
                    ))
            elif in_table and not line.startswith("|"):
                break

        return items

    def _save_queue(self, items: list[QueueItem]) -> None:
        """重建 learning_queue.md"""
        today = datetime.date.today().isoformat()

        pending_count = sum(1 for i in items if i.status == "pending")
        processing_count = sum(1 for i in items if i.status == "processing")
        done_today = sum(1 for i in items if i.status == "done" and i.created == today)

        lines = [
            "---",
            "description: 待学习队列 - 记录待提取和处理的学习素材",
            "version: 1.0",
            f"last_updated: {today}",
            "---",
            "",
            "# Learning Queue (待学习队列)",
            "",
            "记录待处理的学习素材，由 Knowledge Harvester 在空闲时处理。",
            "",
            "## 1. 队列状态",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| 待处理 | {pending_count} |",
            f"| 处理中 | {processing_count} |",
            f"| 今日已处理 | {done_today} |",
            "",
            "## 2. 待学习素材 (Pending Items)",
            "",
            "| ID | Source Type | Source ID | Priority | Created | Status |",
            "|----|-------------|-----------|----------|---------|--------|",
        ]

        if items:
            for item in items:
                lines.append(
                    f"| {item.id} | {item.source_type} | {item.source_id} "
                    f"| {item.priority} | {item.created} | {item.status} |"
                )
        else:
            lines.append("| - | - | - | - | - | 队列为空 |")

        lines += [
            "",
            "### Source Types",
            "- `conversation`: 对话记录",
            "- `code_change`: 代码变更",
            "- `error_fix`: 错误修复",
            "- `workflow_run`: 工作流执行",
            "- `user_feedback`: 用户反馈",
            "",
            "### Priority Levels",
            "- `P0`: 立即处理（重大发现）",
            "- `P1`: 高优先级（成功经验）",
            "- `P2`: 正常处理",
            "- `P3`: 低优先级（可选）",
            "",
            "## 3. 处理规则",
            "",
            "### 3.1 自动入队触发器",
            "- 任务完成后 → 添加 `code_change` 素材",
            "- 错误修复后 → 添加 `error_fix` 素材",
            "- 工作流完成 → 添加 `workflow_run` 素材",
            "",
            "### 3.2 处理时机",
            "- 状态变为 IDLE 时处理队列",
            "- `/evolve` 命令强制处理",
            "",
            "### 3.3 处理流程",
            "```",
            "1. 按优先级排序 (P0 > P1 > P2 > P3)",
            "2. 逐条分析素材内容",
            "3. 提取知识条目或代码模式",
            "4. 标记为已处理",
            "5. 7 天后自动清理已处理条目",
            "```",
            "",
        ]

        self.queue_file.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime.date]:
        """解析日期字符串"""
        try:
            return datetime.date.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None
