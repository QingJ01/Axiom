"""
main.py — Dispatcher 入口 (Phase 1 集成)

提供 `dispatch(prd_path)` 入口函数：
    1. 解析 PRD → 提取 TaskSpec 列表
    2. 按依赖顺序调度执行
    3. 每个任务: Worker 执行 → 重启注入 → Git 提交 → PRD 回写
    4. 输出最终报告

用法:
    python -m dispatcher.main --prd docs/prd/axiom-v4-dev.md
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .core import TaskSpec, TaskStatus, WorkerResult
from .decision_engine import DecisionEngine
from .git_ops import GitOps
from .jsonl_parser import JSONLParser
from .prd_updater import PRDUpdater
from .restart_injector import RestartInjector
from .worker import Worker, WorkerConfig

logger = logging.getLogger(__name__)


@dataclass
class DispatchReport:
    """调度执行的最终报告。"""
    total_tasks: int = 0
    done: int = 0
    failed: int = 0
    blocked: int = 0
    skipped: int = 0
    results: list[WorkerResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.done / self.total_tasks

    def summary(self) -> str:
        return (
            f"\n{'=' * 50}\n"
            f"📊 Dispatch Report\n"
            f"{'=' * 50}\n"
            f"  Total:   {self.total_tasks}\n"
            f"  ✅ Done:  {self.done}\n"
            f"  ❌ Failed: {self.failed}\n"
            f"  🚫 Blocked: {self.blocked}\n"
            f"  ⏭️ Skipped: {self.skipped}\n"
            f"  Success Rate: {self.success_rate:.0%}\n"
            f"{'=' * 50}\n"
        )


class Dispatcher:
    """Dispatcher — PRD 驱动的自动化任务调度器。

    使用方式:
        dispatcher = Dispatcher(prd_path="docs/prd/my-prd.md")
        report = dispatcher.run()
    """

    def __init__(
        self,
        prd_path: str | Path,
        worker_config: WorkerConfig | None = None,
        repo_path: str | Path | None = None,
        dry_run: bool = False,
    ) -> None:
        self.prd_path = Path(prd_path)
        self.dry_run = dry_run

        # 初始化各组件
        self.worker = Worker(worker_config or WorkerConfig())
        self.parser = JSONLParser()
        self.injector = RestartInjector(self.worker, self.parser)
        self.decision_engine = DecisionEngine()
        self.git = GitOps(repo_path)
        self.prd_updater = PRDUpdater(self.prd_path)

    def run(self) -> DispatchReport:
        """执行完整的调度流程。"""
        report = DispatchReport()

        # 1. 解析 PRD
        tasks = self.parse_prd()
        report.total_tasks = len(tasks)

        if not tasks:
            logger.warning("No PENDING tasks found in PRD")
            return report

        logger.info("Found %d PENDING tasks to execute", len(tasks))

        # 2. 按依赖顺序执行
        completed: set[str] = set()

        for task in tasks:
            # 依赖检查
            unmet = [d for d in task.dependencies if d not in completed]
            if unmet:
                logger.info(
                    "Skipping %s: unmet dependencies %s", task.id, unmet
                )
                report.skipped += 1
                continue

            if self.dry_run:
                logger.info("[DRY RUN] Would execute: %s", task.id)
                report.skipped += 1
                continue

            # 执行任务
            logger.info("▶ Executing %s: %s", task.id, task.name)
            result = self.injector.execute_with_injection(
                task,
                answer_func=self.decision_engine.as_answer_callback(),
            )
            report.results.append(result)

            if result.success:
                # 成功 → Git 提交 → PRD 回写
                report.done += 1
                completed.add(task.id)

                git_result = self.git.auto_commit(task.id, task.name)
                if git_result.success:
                    logger.info("  Git: %s", git_result.message)

                prd_result = self.prd_updater.update_task_status(
                    task.id, TaskStatus.DONE
                )
                if prd_result.success:
                    logger.info("  PRD: %s", prd_result.message)

            elif result.error_message and "BLOCKED" in result.error_message:
                report.blocked += 1
                self.prd_updater.update_task_status(task.id, TaskStatus.BLOCKED)
                logger.warning("  ⚠ Task %s BLOCKED: %s", task.id, result.error_message)
            else:
                report.failed += 1
                self.prd_updater.update_task_status(task.id, TaskStatus.FAILED)
                logger.error("  ✗ Task %s FAILED: %s", task.id, result.error_message)

        # 3. 输出报告
        print(report.summary())
        return report

    def parse_prd(self) -> list[TaskSpec]:
        """从 PRD Markdown 文件中解析 PENDING 状态的任务。

        PRD 表格格式:
            | T-101 | **Worker 封装器** | ⏳ PENDING | 描述 | 3h | - | 验收标准 |
        """
        if not self.prd_path.exists():
            logger.error("PRD file not found: %s", self.prd_path)
            return []

        content = self.prd_path.read_text(encoding="utf-8")
        tasks: list[TaskSpec] = []

        # 匹配表格行: | ID | Name | Status | Desc | Est | Deps | Criteria |
        table_pattern = re.compile(
            r"\|\s*(T-\d+)\s*\|"  # Task ID
            r"\s*\*{0,2}(.*?)\*{0,2}\s*\|"  # Name (可能有 ** 加粗)
            r"\s*(⏳\s*PENDING|🔄\s*IN_PROGRESS|✅\s*DONE|🚫\s*BLOCKED|❌\s*FAILED)\s*\|"  # Status
            r"\s*(.*?)\s*\|"  # Description
            r"\s*(.*?)\s*\|"  # Estimate
            r"\s*(.*?)\s*\|"  # Dependencies
            r"\s*(.*?)\s*\|",  # Criteria
        )

        for match in table_pattern.finditer(content):
            task_id = match.group(1).strip()
            name = match.group(2).strip()
            status_text = match.group(3).strip()
            desc = match.group(4).strip()
            deps_text = match.group(6).strip()

            # 只取 PENDING 任务
            if "PENDING" not in status_text:
                continue

            # 解析依赖
            dependencies = []
            if deps_text and deps_text != "-":
                dep_matches = re.findall(r"T-\d+", deps_text)
                dependencies = dep_matches

            # 估算超时（从预估时间推算）
            timeout = self._estimate_timeout(match.group(5).strip())

            tasks.append(TaskSpec(
                id=task_id,
                name=name,
                description=desc,
                dependencies=dependencies,
                status=TaskStatus.PENDING,
                timeout_seconds=timeout,
            ))

        return tasks

    def _estimate_timeout(self, estimate: str) -> int:
        """从预估时间推算超时秒数。

        规则: 预估时间 × 3 (留余量) + 基础 10 分钟
        """
        match = re.search(r"(\d+\.?\d*)\s*h", estimate, re.IGNORECASE)
        if match:
            hours = float(match.group(1))
            return int(hours * 3 * 3600 + 600)

        match = re.search(r"(\d+)\s*min", estimate, re.IGNORECASE)
        if match:
            minutes = int(match.group(1))
            return minutes * 3 * 60 + 600

        return 600  # 默认 10 分钟


def main() -> None:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="Codex Dispatcher — PRD 驱动的自动化任务执行")
    parser.add_argument("--prd", required=True, help="PRD 文件路径")
    parser.add_argument("--repo", default=".", help="Git 仓库路径")
    parser.add_argument("--dry-run", action="store_true", help="仅解析不执行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    dispatcher = Dispatcher(
        prd_path=args.prd,
        repo_path=args.repo,
        dry_run=args.dry_run,
    )
    report = dispatcher.run()

    sys.exit(0 if report.failed == 0 else 1)


if __name__ == "__main__":
    main()
