"""
Evolution Orchestrator — 进化协调器

整合所有进化引擎模块，提供统一入口：
  - /evolve: 完整进化周期
  - /reflect: 反思工作流
  - /knowledge: 知识查询
  - /patterns: 模式查询

Usage:
    from evolution.orchestrator import EvolutionOrchestrator
    evo = EvolutionOrchestrator(base_dir=".agent/memory")
    report = evo.evolve()         # 完整进化
    evo.reflect(session_name=...) # 反思
"""

from __future__ import annotations

import datetime
from pathlib import Path

from evolution.harvester import KnowledgeHarvester
from evolution.index_manager import KnowledgeIndexManager
from evolution.confidence import ConfidenceEngine
from evolution.reflection import ReflectionEngine
from evolution.pattern_detector import PatternDetector
from evolution.learning_queue import LearningQueue
from evolution.metrics import WorkflowMetrics


class EvolutionOrchestrator:
    """
    进化引擎总控制器。

    整合五大模块:
    1. Knowledge Harvester (知识收割)
    2. Knowledge Index (索引管理)
    3. Confidence Engine (置信度管理)
    4. Reflection Engine (反思引擎)
    5. Pattern Detector (模式检测)
    6. Learning Queue (学习队列)
    7. Workflow Metrics (工作流指标)
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.harvester = KnowledgeHarvester(base_dir)
        self.index_mgr = KnowledgeIndexManager(base_dir)
        self.confidence = ConfidenceEngine(base_dir)
        self.reflection = ReflectionEngine(base_dir)
        self.pattern_detector = PatternDetector(base_dir)
        self.learning_queue = LearningQueue(base_dir)
        self.metrics = WorkflowMetrics(base_dir)

    # ── /evolve ──

    def evolve(self) -> str:
        """
        执行完整进化周期。

        Steps:
        1. 处理学习队列
        2. 重建知识索引
        3. 运行 Confidence 衰减
        4. 检测代码模式
        5. 分析工作流效能
        6. 生成进化报告

        Returns
        -------
        str
            进化报告 (Markdown)
        """
        today = datetime.date.today().isoformat()

        # Step 1: 处理学习队列
        queue_stats = self.learning_queue.get_stats()
        processed = self.learning_queue.process_queue()

        # Step 2: 重建知识索引
        self.index_mgr.rebuild_index()
        entries = self.harvester.list_entries()

        # Step 3: Confidence 衰减
        decayed = self.confidence.decay_unused(days=30)
        deprecated = self.confidence.get_deprecated()

        # Step 4: 模式检测
        pattern_result = self.pattern_detector.detect_and_update()

        # Step 5: 工作流洞察
        insights = self.metrics.get_all_insights()

        # Step 6: 反思摘要
        reflection_summary = self.reflection.get_reflection_summary(5)
        pending_actions = self.reflection.get_pending_action_items()

        # Step 7: 清理
        cleaned = self.learning_queue.cleanup(days=7)

        # 生成报告
        report = self._generate_report(
            today=today,
            total_knowledge=len(entries),
            queue_processed=len(processed),
            queue_pending=queue_stats.get("pending", 0),
            decayed=decayed,
            deprecated=deprecated,
            pattern_result=pattern_result,
            insights=insights,
            reflection_summary=reflection_summary,
            pending_actions=pending_actions,
            cleaned=cleaned,
        )

        return report

    # ── /reflect ──

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
    ) -> str:
        """执行反思并返回报告"""
        report = self.reflection.reflect(
            session_name=session_name,
            duration=duration,
            went_well=went_well,
            could_improve=could_improve,
            learnings=learnings,
            action_items=action_items,
            auto_fix_count=auto_fix_count,
            rollback_count=rollback_count,
        )

        # 将学习成果入队
        for learning in (learnings or []):
            self.learning_queue.add_item(
                source_type="conversation",
                source_id=f"reflect-{session_name}",
                priority="P2",
                description=learning,
            )

        return report.to_markdown()

    # ── /knowledge ──

    def search_knowledge(self, query: str) -> list[dict]:
        """搜索知识库"""
        return self.harvester.search(query)

    # ── /patterns ──

    def search_patterns(self, query: str) -> list[dict]:
        """搜索模式库"""
        return self.pattern_detector.suggest_reuse(query)

    # ── Task Lifecycle Hooks ──

    def on_task_completed(self, task_id: str, description: str = "") -> None:
        """任务完成钩子: 入队学习素材"""
        self.learning_queue.add_item(
            source_type="code_change",
            source_id=task_id,
            priority="P2",
            description=description,
        )

    def on_error_fixed(
        self, error_type: str, root_cause: str, solution: str
    ) -> None:
        """错误修复钩子: 入队学习素材 + 直接生成知识条目"""
        self.learning_queue.add_item(
            source_type="error_fix",
            source_id=f"fix-{error_type[:20]}",
            priority="P1",
            description=f"{error_type}: {root_cause}",
        )
        # 直接收割为知识
        entry = self.harvester.harvest_from_error_fix(
            error_type=error_type,
            root_cause=root_cause,
            solution=solution,
        )
        # 更新索引
        self.index_mgr.add_to_index(
            kid=entry.id,
            title=entry.title,
            category=entry.category,
            confidence=entry.confidence,
            created=entry.created,
        )

    def on_workflow_completed(
        self,
        workflow: str,
        duration_min: int,
        success: bool = True,
        notes: str = "",
    ) -> None:
        """工作流完成钩子: 记录指标"""
        self.metrics.record_run(
            workflow=workflow,
            duration_min=duration_min,
            success=success,
            notes=notes,
        )

    # ── Report Generation ──

    def _generate_report(
        self,
        today: str,
        total_knowledge: int,
        queue_processed: int,
        queue_pending: int,
        decayed: list,
        deprecated: list,
        pattern_result: dict,
        insights: dict,
        reflection_summary: str,
        pending_actions: list,
        cleaned: int,
    ) -> str:
        """生成进化报告"""
        lines = [
            f"# 🧬 Evolution Report — {today}",
            "",
            "## 📚 Knowledge Updates",
            f"- **Total**: {total_knowledge} items",
            f"- **Decayed** (30d unused): {len(decayed)} items",
            f"- **Deprecated** (confidence < 0.5): {len(deprecated)} items",
        ]
        if deprecated:
            for d in deprecated:
                lines.append(f"  - {d['id']}: {d['title']} (conf: {d['confidence']})")

        lines += [
            "",
            "## 📥 Learning Queue",
            f"- **Processed**: {queue_processed} items",
            f"- **Remaining**: {queue_pending} items",
            f"- **Cleaned** (7d old): {cleaned} items",
        ]

        lines += [
            "",
            "## 🔄 Pattern Detection",
            f"- **Matches**: {len(pattern_result.get('matches', []))}",
            f"- **New Patterns**: {len(pattern_result.get('new_patterns', []))}",
            f"- **Promoted**: {len(pattern_result.get('promoted', []))}",
        ]
        for p in pattern_result.get("new_patterns", []):
            lines.append(f"  - NEW: {p}")
        for p in pattern_result.get("promoted", []):
            lines.append(f"  - PROMOTED: {p}")

        lines += [
            "",
            "## 📊 Workflow Insights",
            "| Workflow | Avg Duration | Success Rate | Runs | Bottleneck |",
            "|----------|--------------|--------------|------|------------|",
        ]
        for wf, insight in insights.items():
            if insight.total_runs > 0:
                lines.append(
                    f"| {wf} | {insight.avg_duration} min "
                    f"| {insight.success_rate:.0%} | {insight.total_runs} "
                    f"| {insight.common_bottleneck or 'N/A'} |"
                )
        if all(i.total_runs == 0 for i in insights.values()):
            lines.append("| - | - | - | - | 暂无数据 |")

        # Suggestions
        suggestions = [i.suggestion for i in insights.values() if i.suggestion]
        if suggestions:
            lines += ["", "### Optimization Suggestions"]
            for i, s in enumerate(suggestions, 1):
                lines.append(f"{i}. {s}")

        lines += [
            "",
            "## 💭 Reflection Summary",
            reflection_summary,
            f"- **Pending Action Items**: {len(pending_actions)}",
        ]

        lines += [
            "",
            "## 🎯 Recommended Next Steps",
        ]
        if pending_actions:
            for act in pending_actions[:5]:
                lines.append(f"1. {act}")
        else:
            lines.append("1. 继续积累知识条目")
            lines.append("2. 执行 `/reflect` 反思最近的工作")

        lines += [
            "",
            "---",
            f"*Evolution Engine v1.0 | Total Knowledge: {total_knowledge} items "
            f"| Patterns: {len(pattern_result.get('matches', []))}*",
            "",
        ]

        return "\n".join(lines)
