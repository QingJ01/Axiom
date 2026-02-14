"""
git_ops.py — Git 自动提交集成 (T-105)

每个任务 DONE 后自动 `git add -A && git commit -m "feat(T-{ID}): {name}"`。
失败时记录日志但不阻塞。

支持特性:
    - 自动提交（ADD + COMMIT）
    - Checkpoint Tag 创建
    - Git 状态检查
    - 操作失败不阻塞（仅日志）
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class GitResult:
    """Git 操作结果。"""
    success: bool
    message: str
    commit_hash: str | None = None


class GitOps:
    """Git 操作封装器。

    使用方式:
        git = GitOps(repo_path="/path/to/repo")
        result = git.auto_commit("T-101", "Worker 封装器")
    """

    def __init__(self, repo_path: str | Path | None = None) -> None:
        """
        Args:
            repo_path: Git 仓库根目录路径。None 则使用当前目录。
        """
        self.repo_path = str(repo_path) if repo_path else "."

    # ── 公开 API ────────────────────────────────────────

    def auto_commit(self, task_id: str, task_name: str) -> GitResult:
        """自动提交任务完成的更改。

        执行: git add -A && git commit -m "feat(T-{ID}): {name}"

        Args:
            task_id: 任务 ID (e.g., "T-101")
            task_name: 任务名称 (e.g., "Worker 封装器")

        Returns:
            GitResult
        """
        try:
            # 检查是否有变更
            if not self.has_changes():
                return GitResult(
                    success=True,
                    message="No changes to commit",
                )

            # git add -A
            self._run_git("add", "-A")

            # git commit
            commit_msg = f"feat({task_id}): {task_name}"
            self._run_git("commit", "-m", commit_msg)

            # 获取 commit hash
            commit_hash = self._get_head_hash()

            logger.info("Auto-committed: %s (%s)", commit_msg, commit_hash)
            return GitResult(
                success=True,
                message=f"Committed: {commit_msg}",
                commit_hash=commit_hash,
            )

        except Exception as exc:
            logger.warning("Auto-commit failed (non-blocking): %s", exc)
            return GitResult(success=False, message=str(exc))

    def create_checkpoint(self, tag_name: str | None = None) -> GitResult:
        """创建检查点 Tag。

        Args:
            tag_name: 自定义 Tag 名称。None 则自动生成。

        Returns:
            GitResult
        """
        try:
            import datetime

            if tag_name is None:
                now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                tag_name = f"checkpoint-{now}"

            self._run_git("tag", tag_name)
            logger.info("Checkpoint created: %s", tag_name)
            return GitResult(success=True, message=f"Tag: {tag_name}")

        except Exception as exc:
            logger.warning("Checkpoint creation failed: %s", exc)
            return GitResult(success=False, message=str(exc))

    def has_changes(self) -> bool:
        """检查是否有未提交的变更。"""
        try:
            result = self._run_git("status", "--porcelain")
            return bool(result.strip())
        except Exception:
            return False

    def get_last_commit_message(self) -> str | None:
        """获取最近一次 commit 的消息。"""
        try:
            return self._run_git("log", "-1", "--format=%s").strip()
        except Exception:
            return None

    def get_diff_stat(self) -> str | None:
        """获取当前变更的 diff 统计。"""
        try:
            return self._run_git("diff", "--stat", "HEAD").strip()
        except Exception:
            return None

    # ── 内部方法 ────────────────────────────────────────

    def _run_git(self, *args: str) -> str:
        """执行 Git 命令并返回 stdout。"""
        cmd = ["git", *args]
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Git command failed: {' '.join(cmd)}\n"
                f"stderr: {result.stderr.strip()}"
            )
        return result.stdout

    def _get_head_hash(self) -> str:
        """获取 HEAD 的短 hash。"""
        return self._run_git("rev-parse", "--short", "HEAD").strip()
