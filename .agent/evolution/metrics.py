"""
Workflow Metrics Tracker — 工作流指标追踪 (T-208)

在工作流关键节点记录计时和状态，用于识别瓶颈和优化机会。

支持的工作流：
  - feature-flow: 全功能开发流程
  - analyze-error: 错误分析修复
  - start: 启动/上下文恢复

Usage:
    from evolution.metrics import WorkflowMetrics
    tracker = WorkflowMetrics(base_dir=".agent/memory")
    tracker.start_tracking("feature-flow")
    # ... 工作流执行 ...
    tracker.end_tracking("feature-flow", success=True, notes="完成 T-201")
    tracker.get_insights("feature-flow")
"""

from __future__ import annotations

import re
import time
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class WorkflowRun:
    """工作流执行记录"""
    workflow: str
    date: str
    duration_min: int = 0
    success: bool = True
    rollbacks: int = 0
    auto_fix: int = 0
    bottleneck: str = ""
    notes: str = ""

    def to_table_row(self) -> str:
        """生成 Markdown 表格行"""
        success_mark = "✓" if self.success else "✗"
        return (
            f"| {self.date} | {self.duration_min}min | {success_mark} "
            f"| {self.rollbacks} | {self.auto_fix} | {self.bottleneck} | {self.notes} |"
        )


@dataclass
class WorkflowInsight:
    """工作流洞察"""
    workflow: str
    avg_duration: float = 0.0
    success_rate: float = 0.0
    total_runs: int = 0
    common_bottleneck: str = ""
    suggestion: str = ""


class WorkflowMetrics:
    """
    工作流效能统计管理器。

    职责：
    1. 记录工作流执行指标
    2. 计算洞察 (平均耗时、成功率、瓶颈)
    3. 生成优化建议
    4. 更新全局统计
    """

    # 启动时间戳缓存 (workflow_name → start_time)
    _active_timers: dict[str, float] = {}

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.metrics_file = self.base_dir / "evolution" / "workflow_metrics.md"
        WorkflowMetrics._active_timers = {}

    # ── Public API ──

    def start_tracking(self, workflow: str) -> None:
        """开始追踪工作流"""
        WorkflowMetrics._active_timers[workflow] = time.time()

    def end_tracking(
        self,
        workflow: str,
        success: bool = True,
        rollbacks: int = 0,
        auto_fix: int = 0,
        bottleneck: str = "",
        notes: str = "",
        duration_override: int | None = None,
    ) -> WorkflowRun:
        """
        结束追踪并记录指标。

        Parameters
        ----------
        workflow : str
            工作流名称
        success : bool
            是否成功
        rollbacks : int
            回滚次数
        auto_fix : int
            自动修复次数
        bottleneck : str
            瓶颈环节
        notes : str
            备注
        duration_override : int | None
            手动指定耗时 (分钟), 覆盖计时器

        Returns
        -------
        WorkflowRun
            记录的工作流执行数据
        """
        if duration_override is not None:
            duration = duration_override
        elif workflow in WorkflowMetrics._active_timers:
            elapsed = time.time() - WorkflowMetrics._active_timers.pop(workflow)
            duration = max(1, int(elapsed / 60))
        else:
            duration = 0

        run = WorkflowRun(
            workflow=workflow,
            date=datetime.date.today().isoformat(),
            duration_min=duration,
            success=success,
            rollbacks=rollbacks,
            auto_fix=auto_fix,
            bottleneck=bottleneck,
            notes=notes,
        )

        self._append_run(run)
        self._update_global_stats(run)
        return run

    def record_run(
        self,
        workflow: str,
        duration_min: int,
        success: bool = True,
        rollbacks: int = 0,
        auto_fix: int = 0,
        bottleneck: str = "",
        notes: str = "",
    ) -> WorkflowRun:
        """直接记录一次工作流执行（不使用计时器）"""
        return self.end_tracking(
            workflow=workflow,
            success=success,
            rollbacks=rollbacks,
            auto_fix=auto_fix,
            bottleneck=bottleneck,
            notes=notes,
            duration_override=duration_min,
        )

    def get_insights(self, workflow: str) -> WorkflowInsight:
        """
        获取工作流洞察。

        Returns
        -------
        WorkflowInsight
            包含平均耗时、成功率、瓶颈分析
        """
        runs = self._load_runs(workflow)
        if not runs:
            return WorkflowInsight(workflow=workflow)

        durations = [r["duration"] for r in runs]
        successes = [r["success"] for r in runs]
        bottlenecks = [r["bottleneck"] for r in runs if r["bottleneck"]]

        avg_dur = sum(durations) / len(durations) if durations else 0
        success_rate = sum(1 for s in successes if s) / len(successes) if successes else 0

        # 最常见瓶颈
        common_bottleneck = ""
        if bottlenecks:
            from collections import Counter
            common_bottleneck = Counter(bottlenecks).most_common(1)[0][0]

        # 优化建议
        suggestion = ""
        if avg_dur > 30:
            suggestion = f"平均耗时 {avg_dur:.0f} min 偏高，考虑拆分工作流或缓存中间结果"
        if success_rate < 0.8:
            suggestion = f"成功率 {success_rate:.0%} 低于 80%，建议检查常见失败原因"

        return WorkflowInsight(
            workflow=workflow,
            avg_duration=round(avg_dur, 1),
            success_rate=round(success_rate, 2),
            total_runs=len(runs),
            common_bottleneck=common_bottleneck,
            suggestion=suggestion,
        )

    def get_all_insights(self) -> dict[str, WorkflowInsight]:
        """获取所有工作流的洞察"""
        workflows = ["feature-flow", "analyze-error", "start"]
        return {w: self.get_insights(w) for w in workflows}

    # ── Private Methods ──

    def _append_run(self, run: WorkflowRun) -> None:
        """追加一条执行记录到 workflow_metrics.md"""
        if not self.metrics_file.exists():
            return

        text = self.metrics_file.read_text(encoding="utf-8")
        row = run.to_table_row()

        # 找到对应工作流的 Execution Log 表
        section_map = {
            "feature-flow": "## 1. feature-flow",
            "analyze-error": "## 2. analyze-error",
            "start": "## 3. start",
        }

        marker = section_map.get(run.workflow)
        if not marker or marker not in text:
            return

        lines = text.split("\n")
        in_section = False
        in_table = False
        insert_pos = None

        for i, line in enumerate(lines):
            if marker in line:
                in_section = True
                continue
            if in_section and line.startswith("## "):
                break
            if in_section and "| Date |" in line:
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                insert_pos = i
            elif in_table and not line.startswith("|"):
                if insert_pos is None:
                    insert_pos = i - 1
                break

        if insert_pos is not None:
            # 替换 "暂无数据" 行
            if "暂无数据" in lines[insert_pos]:
                lines[insert_pos] = row
            else:
                lines.insert(insert_pos + 1, row)
        else:
            return

        # 写回执行日志
        text = "\n".join(lines)
        self.metrics_file.write_text(text, encoding="utf-8")

    def _update_global_stats(self, run: WorkflowRun) -> None:
        """更新全局统计"""
        if not self.metrics_file.exists():
            return

        text = self.metrics_file.read_text(encoding="utf-8")

        # 更新计数器
        for label, delta in [
            ("总执行次数", 1),
            ("总成功次数", 1 if run.success else 0),
            ("总回滚次数", run.rollbacks),
            ("总自动修复次数", run.auto_fix),
        ]:
            pattern = rf"\| {label} \| (\d+) \|"
            m = re.search(pattern, text)
            if m:
                old_val = int(m.group(1))
                new_val = old_val + delta
                text = re.sub(pattern, f"| {label} | {new_val} |", text)

        self.metrics_file.write_text(text, encoding="utf-8")

    def _load_runs(self, workflow: str) -> list[dict]:
        """加载工作流的历史执行记录"""
        if not self.metrics_file.exists():
            return []

        text = self.metrics_file.read_text(encoding="utf-8")
        runs = []

        section_map = {
            "feature-flow": "## 1. feature-flow",
            "analyze-error": "## 2. analyze-error",
            "start": "## 3. start",
        }

        marker = section_map.get(workflow)
        if not marker or marker not in text:
            return []

        in_section = False
        in_table = False
        for line in text.split("\n"):
            if marker in line:
                in_section = True
                continue
            if in_section and line.startswith("## ") and marker not in line:
                break
            if in_section and "| Date |" in line:
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 7 and parts[1] != "-":
                    dur_str = parts[2].replace("min", "").strip()
                    try:
                        dur = int(dur_str)
                    except ValueError:
                        dur = 0
                    runs.append({
                        "date": parts[1],
                        "duration": dur,
                        "success": parts[3] == "✓",
                        "rollbacks": int(parts[4]) if parts[4].isdigit() else 0,
                        "auto_fix": int(parts[5]) if parts[5].isdigit() else 0,
                        "bottleneck": parts[6] if len(parts) > 6 else "",
                    })
            elif in_table and not line.startswith("|"):
                break

        return runs
