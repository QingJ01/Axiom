"""
Reflection Engine — 反思引擎 (T-205)

任务完成后自动反思：
  - 读取 active_context.md 解析任务完成情况
  - 生成结构化反思报告 (WWW / WCI / Learnings / Action Items)
  - 追加到 reflection_log.md
  - 提取知识条目和 Action Items

Usage:
    from evolution.reflection import ReflectionEngine
    engine = ReflectionEngine(base_dir=".agent/memory")
    report = engine.reflect(session_name="Feature X", duration=15,
                            went_well=["快速完成"], could_improve=["测试不足"],
                            learnings=["..."], action_items=["..."])
"""

from __future__ import annotations

import re
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ReflectionReport:
    """反思报告数据结构"""
    session_name: str
    date: str
    duration_min: int = 0
    tasks_completed: int = 0
    tasks_total: int = 0
    auto_fix_count: int = 0
    rollback_count: int = 0
    went_well: list[str] = field(default_factory=list)
    could_improve: list[str] = field(default_factory=list)
    learnings: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"### {self.date} Session: {self.session_name}",
            "",
            "#### 📊 Quick Stats",
            f"- Duration: ~{self.duration_min} min",
            f"- Tasks Completed: {self.tasks_completed}/{self.tasks_total}",
            f"- Auto-Fix: {self.auto_fix_count} times",
            f"- Rollbacks: {self.rollback_count} times",
            "",
            "#### ✅ What Went Well (做得好)",
        ]
        for item in self.went_well:
            lines.append(f"- [x] {item}")
        if not self.went_well:
            lines.append("- (无)")
        lines += ["", "#### ⚠️ What Could Improve (待改进)"]
        for item in self.could_improve:
            lines.append(f"- [ ] {item}")
        if not self.could_improve:
            lines.append("- (无)")
        lines += ["", "#### 💡 Learnings (学到的)"]
        for item in self.learnings:
            lines.append(f"- {item}")
        if not self.learnings:
            lines.append("- (无)")
        lines += ["", "#### 🎯 Action Items (后续行动)"]
        for item in self.action_items:
            lines.append(f"- [ ] {item}")
        if not self.action_items:
            lines.append("- (无)")
        lines.append("")
        return "\n".join(lines)


class ReflectionEngine:
    """
    反思引擎：生成结构化反思报告并持久化到 reflection_log.md

    工作流：
    1. 读取 active_context.md → 解析任务完成情况
    2. 生成反思报告 (输入: 主观评估)
    3. 追加到 reflection_log.md
    4. 更新反思统计
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.active_context = self.base_dir / "active_context.md"
        self.reflection_log = self.base_dir / "evolution" / "reflection_log.md"

    # ── Public API ──

    def reflect(
        self,
        session_name: str,
        duration: int = 0,
        went_well: list[str] | None = None,
        could_improve: list[str] | None = None,
        learnings: list[str] | None = None,
        action_items: list[str] | None = None,
        auto_fix_count: int = 0,
        rollback_count: int = 0,
    ) -> ReflectionReport:
        """
        生成反思报告并追加到日志。

        Parameters
        ----------
        session_name : str
            会话名称
        duration : int
            耗时 (分钟)
        went_well : list[str]
            做得好的事项
        could_improve : list[str]
            待改进事项
        learnings : list[str]
            学到的知识
        action_items : list[str]
            后续行动计划
        auto_fix_count : int
            自动修复次数
        rollback_count : int
            回滚次数

        Returns
        -------
        ReflectionReport
            生成的反思报告
        """
        # 解析 active_context 获取任务统计
        task_stats = self.parse_active_context()

        report = ReflectionReport(
            session_name=session_name,
            date=datetime.date.today().isoformat(),
            duration_min=duration,
            tasks_completed=task_stats.get("completed", 0),
            tasks_total=task_stats.get("total", 0),
            auto_fix_count=auto_fix_count,
            rollback_count=rollback_count,
            went_well=went_well or [],
            could_improve=could_improve or [],
            learnings=learnings or [],
            action_items=action_items or [],
        )

        self._append_to_log(report)
        self._update_stats(report)

        return report

    def parse_active_context(self) -> dict:
        """解析 active_context.md，提取任务完成统计"""
        if not self.active_context.exists():
            return {"completed": 0, "total": 0}

        text = self.active_context.read_text(encoding="utf-8")
        completed = len(re.findall(r"\[✅ DONE\]", text))
        pending = len(re.findall(r"\[⏳ PENDING\]", text))
        blocked = len(re.findall(r"\[🔴 BLOCKED\]", text))
        total = completed + pending + blocked

        return {
            "completed": completed,
            "pending": pending,
            "blocked": blocked,
            "total": total,
        }

    def get_pending_action_items(self) -> list[str]:
        """从反思日志中提取未完成的 Action Items"""
        if not self.reflection_log.exists():
            return []

        text = self.reflection_log.read_text(encoding="utf-8")
        items = re.findall(r"- \[ \] (.+)", text)
        return items

    def get_reflection_summary(self, last_n: int = 5) -> str:
        """获取最近 N 次反思的摘要"""
        if not self.reflection_log.exists():
            return "暂无反思记录"

        text = self.reflection_log.read_text(encoding="utf-8")
        # 提取 session headers
        sessions = re.findall(
            r"### (\d{4}-\d{2}-\d{2}) Session: (.+?)(?=\n###|\Z)",
            text,
            re.DOTALL,
        )
        if not sessions:
            return "暂无反思记录"

        lines = [f"最近 {min(last_n, len(sessions))} 次反思:\n"]
        for date, content in sessions[-last_n:]:
            # 提取 session name
            name = content.split("\n")[0].strip()
            lines.append(f"- {date}: {name}")

        return "\n".join(lines)

    # ── Private Methods ──

    def _append_to_log(self, report: ReflectionReport) -> None:
        """追加反思报告到 reflection_log.md"""
        if not self.reflection_log.exists():
            return

        text = self.reflection_log.read_text(encoding="utf-8")
        report_md = report.to_markdown()

        # 在 "## Session History" 后插入
        marker = "## Session History"
        if marker in text:
            idx = text.index(marker) + len(marker)
            text = text[:idx] + "\n\n" + report_md + text[idx:]
        else:
            # Fallback: 追加到文件末尾
            text += "\n\n" + report_md

        self.reflection_log.write_text(text, encoding="utf-8")

    def _update_stats(self, report: ReflectionReport) -> None:
        """更新反思统计"""
        if not self.reflection_log.exists():
            return

        text = self.reflection_log.read_text(encoding="utf-8")

        # 更新月度统计
        month = report.date[:7]
        stats_pattern = rf"\| {month} \| (\d+) \| (\d+) \| (\d+) \|"
        match = re.search(stats_pattern, text)

        if match:
            sessions = int(match.group(1)) + 1
            learnings = int(match.group(2)) + len(report.learnings)
            completed = int(match.group(3))
            text = re.sub(
                stats_pattern,
                f"| {month} | {sessions} | {learnings} | {completed} |",
                text,
            )
        else:
            # 新增月度行
            new_row = f"| {month} | 1 | {len(report.learnings)} | 0 |"
            # 在统计表末尾插入
            stats_marker = "## 反思统计 (Reflection Stats)"
            if stats_marker in text:
                # 找到表格最后一行
                idx = text.index(stats_marker)
                rest = text[idx:]
                lines = rest.split("\n")
                insert_at = None
                for i, line in enumerate(lines):
                    if line.startswith("|") and "Month" not in line and "---" not in line:
                        insert_at = i
                if insert_at:
                    lines.insert(insert_at + 1, new_row)
                    text = text[:idx] + "\n".join(lines)

        self.reflection_log.write_text(text, encoding="utf-8")
