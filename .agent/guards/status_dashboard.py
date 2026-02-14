"""
status_dashboard.py — /status 仪表盘生成器 (T-308)

读取 Axiom 各数据源，生成结构化 Markdown 仪表盘。
可被工作流直接调用，也可命令行独立运行。

Usage:
    from guards.status_dashboard import StatusDashboard
    dashboard = StatusDashboard(base_dir=".agent")
    print(dashboard.generate())
    
CLI:
    python .agent/guards/status_dashboard.py
"""

from __future__ import annotations

import os
import re
import sys
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


class StatusDashboard:
    """系统仪表盘生成器。"""

    def __init__(self, base_dir: str | Path = ".agent") -> None:
        self.base_dir = Path(base_dir)
        self.memory_dir = self.base_dir / "memory"
        self.evolution_dir = self.memory_dir / "evolution"
        self.config_dir = self.base_dir / "config"
        self.knowledge_dir = self.memory_dir / "knowledge"

    # ── 主入口 ──────────────────────────────────────────

    def generate(self) -> str:
        """生成完整仪表盘 Markdown。"""
        sections = [
            self._header(),
            self._system_state(),
            self._task_progress(),
            self._evolution_stats(),
            self._recent_reflections(),
            self._workflow_metrics(),
            self._guard_status(),
            self._footer(),
        ]
        return "\n".join(sections)

    # ── 各区块生成 ──────────────────────────────────────

    def _header(self) -> str:
        return "# 📊 Axiom — System Dashboard\n"

    def _system_state(self) -> str:
        """系统状态区块。"""
        ctx = self._read_active_context()
        provider = self._read_active_provider()
        
        # 计算 uptime (距上次 context 更新)
        context_file = self.memory_dir / "active_context.md"
        uptime = "unknown"
        if context_file.exists():
            mtime = os.path.getmtime(context_file)
            age_min = int((datetime.now().timestamp() - mtime) / 60)
            uptime = f"{age_min} min"

        lines = [
            "## 🎯 System State\n",
            "| Key | Value |",
            "|-----|-------|",
            f"| Status | `{ctx.get('task_status', 'UNKNOWN')}` |",
            f"| Session | `{ctx.get('session_id', 'N/A')}` |",
            f"| Provider | **{provider}** |",
            f"| Last Checkpoint | `{ctx.get('last_checkpoint', 'N/A')}` |",
            f"| Context Age | {uptime} since last update |",
            "",
            "---\n",
        ]
        return "\n".join(lines)

    def _task_progress(self) -> str:
        """任务进度区块。"""
        ctx_content = self._read_file(self.memory_dir / "active_context.md")
        
        # 解析各状态任务，兼容两种格式:
        # 1) [✅ DONE] T-123
        # 2) - [x] **[DONE]** T-MW-001: ...
        done_tasks: list[str] = []
        pending_tasks: list[str] = []
        progress_tasks: list[str] = []
        blocked_tasks: list[str] = []
        failed_tasks: list[str] = []

        for line in ctx_content.splitlines():
            if "[DONE]" in line:
                bucket = done_tasks
            elif "[PENDING]" in line:
                bucket = pending_tasks
            elif "[IN_PROGRESS]" in line:
                bucket = progress_tasks
            elif "[BLOCKED]" in line:
                bucket = blocked_tasks
            elif "[FAILED]" in line:
                bucket = failed_tasks
            else:
                continue

            task_match = re.search(r"\b(T-[A-Za-z0-9-]+)\b", line)
            if task_match:
                bucket.append(task_match.group(1))
            else:
                bucket.append("-")
        
        total = len(done_tasks) + len(pending_tasks) + len(progress_tasks) + len(blocked_tasks) + len(failed_tasks)
        done_count = len(done_tasks)
        pct = int(done_count / total * 100) if total > 0 else 0
        
        # 生成进度条
        filled = pct // 5
        empty = 20 - filled
        bar = "█" * filled + "░" * empty

        lines = [
            "## 📋 Task Progress\n",
            "| Status | Count | Tasks |",
            "|--------|-------|-------|",
            f"| ✅ Done | {len(done_tasks)} | {', '.join(done_tasks[:10]) or '-'} |",
            f"| ⏳ Pending | {len(pending_tasks)} | {', '.join(pending_tasks[:10]) or '-'} |",
            f"| 🔄 In Progress | {len(progress_tasks)} | {', '.join(progress_tasks) or '-'} |",
            f"| 🚫 Blocked | {len(blocked_tasks)} | {', '.join(blocked_tasks) or '-'} |",
            f"| ❌ Failed | {len(failed_tasks)} | {', '.join(failed_tasks) or '-'} |",
            "",
            f"**Overall**: {bar} {pct}% ({done_count}/{total} tasks)",
            "",
            "---\n",
        ]
        return "\n".join(lines)

    def _evolution_stats(self) -> str:
        """进化引擎统计区块。"""
        # 知识库统计
        kb_content = self._read_file(self.evolution_dir / "knowledge_base.md")
        knowledge_rows = re.findall(r"\|\s*k-\d+\s*\|", kb_content)
        knowledge_count = len(knowledge_rows)

        # 分类统计
        categories = re.findall(r"\|\s*(architecture|debugging|pattern|workflow|tooling)\s*\|\s*(\d+)\s*\|", kb_content)
        cat_summary = " / ".join(f"{c} {n}" for n, c in categories) if categories else "N/A"

        # 模式库统计
        pl_content = self._read_file(self.evolution_dir / "pattern_library.md")
        active_patterns = len(re.findall(r"Status:\s*ACTIVE", pl_content, re.IGNORECASE))
        candidate_patterns = len(re.findall(r"Status:\s*CANDIDATE", pl_content, re.IGNORECASE))

        # 学习队列
        lq_content = self._read_file(self.evolution_dir / "learning_queue.md")
        pending_items = len(re.findall(r"\|\s*pending\s*\|", lq_content, re.IGNORECASE))
        processed_items = len(re.findall(r"\|\s*processed\s*\|", lq_content, re.IGNORECASE))

        # 反思次数
        rl_content = self._read_reflection_log()
        reflection_count = len(re.findall(r"^##\s+\d{4}-\d{2}-\d{2}\b", rl_content, re.MULTILINE))

        lines = [
            "## 🧬 Evolution Stats\n",
            "| Metric | Count | Details |",
            "|--------|-------|---------|",
            f"| 📚 Knowledge Items | {knowledge_count} | {cat_summary} |",
            f"| 🔄 Active Patterns | {active_patterns + candidate_patterns} | {active_patterns} ACTIVE / {candidate_patterns} CANDIDATE |",
            f"| 📥 Learning Queue | {pending_items + processed_items} | {pending_items} pending / {processed_items} processed |",
            f"| 💭 Reflections | {reflection_count} | Last: {self._get_last_reflection_date(rl_content)} |",
            "",
            "---\n",
        ]
        return "\n".join(lines)

    def _recent_reflections(self) -> str:
        """最近反思摘要区块。"""
        rl_content = self._read_reflection_log()
        
        # 提取反思 Session
        sessions = re.findall(r"##\s+(\d{4}-\d{2}-\d{2})\s+(.+?)(?:\n|$)", rl_content)

        lines = [
            "## 💭 Recent Reflections\n",
            "| Date | Session | Key Learning |",
            "|------|---------|-------------|",
        ]

        if sessions:
            for date, session_name in sessions[-5:]:
                # 尝试提取 Learnings 部分
                learning = self._extract_learning(rl_content, date)
                lines.append(f"| {date} | {session_name.strip()} | {learning} |")
        else:
            lines.append("| - | 暂无反思记录 | - |")

        lines.extend(["", "---\n"])
        return "\n".join(lines)

    def _workflow_metrics(self) -> str:
        """工作流指标趋势区块。"""
        wm_content = self._read_file(self.evolution_dir / "workflow_metrics.md")

        workflows = {
            "feature-flow": {"runs": 0, "avg_dur": "-", "success_rate": "-", "last_run": "-"},
            "analyze-error": {"runs": 0, "avg_dur": "-", "success_rate": "-", "last_run": "-"},
            "start": {"runs": 0, "avg_dur": "-", "success_rate": "-", "last_run": "-"},
        }

        for wf_name in workflows:
            rows = self._parse_workflow_rows(wm_content, wf_name)
            if rows:
                workflows[wf_name]["runs"] = len(rows)
                durations = [int(r[1]) for r in rows]
                successes = [r[2] == "✓" for r in rows]
                workflows[wf_name]["avg_dur"] = f"{sum(durations) // len(durations)}min"
                workflows[wf_name]["success_rate"] = f"{sum(successes) / len(successes) * 100:.0f}%"
                workflows[wf_name]["last_run"] = rows[-1][0]

        # 全局统计
        global_match = re.search(r"总执行次数 \| (\d+)", wm_content)
        total_runs = global_match.group(1) if global_match else "0"

        lines = [
            "## 📈 Workflow Metrics\n",
            "| Workflow | Runs | Avg Duration | Success Rate | Last Run |",
            "|----------|------|-------------|-------------|----------|",
        ]
        for name, data in workflows.items():
            lines.append(
                f"| {name} | {data['runs']} | {data['avg_dur']} "
                f"| {data['success_rate']} | {data['last_run']} |"
            )
        lines.extend([
            "",
            f"**Total Workflow Executions**: {total_runs}",
            "",
            "---\n",
        ])
        return "\n".join(lines)

    def _guard_status(self) -> str:
        """守卫状态区块。"""
        # 检查 Git Hooks
        git_hooks_dir = self._find_git_hooks_dir()
        
        pre_commit = "✅ Installed" if (git_hooks_dir / "pre-commit").exists() else "❌ Not installed"
        post_commit = "✅ Installed" if (git_hooks_dir / "post-commit").exists() else "❌ Not installed"

        # 检查最近 checkpoint
        last_cp = self._get_last_checkpoint()

        # 看门狗状态 (检查进程)
        watchdog_status = "⏸️ Stopped"

        lines = [
            "## 🛡️ Guard Status\n",
            "| Guard | Status | Details |",
            "|-------|--------|---------|",
            f"| Pre-commit | {pre_commit} | Warning-only (不阻断) |",
            f"| Post-commit | {post_commit} | Auto-checkpoint (30min) |",
            f"| Session Watchdog | {watchdog_status} | `python .agent/guards/session_watchdog.py` |",
            f"| Last Checkpoint | {last_cp} | |",
            "",
            "---\n",
        ]
        return "\n".join(lines)

    def _footer(self) -> str:
        """页脚。"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"*Dashboard generated at: {now}*\n"
            f"*Axiom v4.0*"
        )

    # ── 辅助方法 ──────────────────────────────────────

    def _read_file(self, path: Path) -> str:
        """安全读取文件。"""
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            try:
                return path.read_bytes().decode("utf-8", errors="replace")
            except Exception:
                return ""

    def _read_reflection_log(self) -> str:
        """读取反思日志，兼容旧/新路径。"""
        candidates = [
            self.evolution_dir / "reflection_log.md",
            self.memory_dir / "reflection_log.md",
        ]
        for path in candidates:
            content = self._read_file(path)
            if content:
                return content
        return ""

    def _parse_workflow_rows(self, content: str, workflow: str) -> list[tuple[str, int, str]]:
        """解析指定 workflow 的执行记录行。"""
        section_map = {
            "feature-flow": "## 1. feature-flow",
            "analyze-error": "## 2. analyze-error",
            "start": "## 3. start",
        }
        marker = section_map.get(workflow)
        if not marker or marker not in content:
            return []

        rows: list[tuple[str, int, str]] = []
        in_section = False
        for line in content.splitlines():
            if line.strip() == marker:
                in_section = True
                continue
            if in_section and line.startswith("## "):
                break
            if not in_section:
                continue

            match = re.match(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d+)min\s*\|\s*([✓✗])\s*\|", line)
            if match:
                date, duration, mark = match.groups()
                rows.append((date, int(duration), mark))

        return rows

    def _read_active_context(self) -> dict[str, str]:
        """解析 active_context.md 的 YAML frontmatter。"""
        content = self._read_file(self.memory_dir / "active_context.md")
        result: dict[str, str] = {}

        # 提取 frontmatter
        fm_match = re.search(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        if fm_match:
            for line in fm_match.group(1).splitlines():
                kv = line.split(":", 1)
                if len(kv) == 2:
                    key = kv[0].strip()
                    val = kv[1].strip().strip('"')
                    result[key] = val

        return result

    def _read_active_provider(self) -> str:
        """读取当前激活的 Provider。"""
        content = self._read_file(self.config_dir / "agent_config.md")
        match = re.search(r"ACTIVE_PROVIDER:\s*(\w+)", content)
        return match.group(1) if match else "gemini"

    def _get_last_reflection_date(self, content: str) -> str:
        """获取最后一次反思日期。"""
        dates = re.findall(r"^##\s+(\d{4}-\d{2}-\d{2})\b", content, re.MULTILINE)
        return dates[-1] if dates else "N/A"

    def _extract_learning(self, content: str, date: str) -> str:
        """从反思日志中提取某次 Session 的关键 Learning。"""
        # 简单提取该日期后的第一个 Learning 行
        pattern = rf"## {date} Session:.*?### 💡 Learnings.*?\n- (.*?)(?:\n|$)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()[:60]
        return "-"

    def _find_git_hooks_dir(self) -> Path:
        """查找 .git/hooks 目录。"""
        current = Path.cwd()
        while current != current.parent:
            git_hooks = current / ".git" / "hooks"
            if git_hooks.is_dir():
                return git_hooks
            current = current.parent
        return Path(".git/hooks")

    def _get_last_checkpoint(self) -> str:
        """获取最近的 checkpoint tag。"""
        try:
            result = subprocess.run(
                ["git", "tag", "-l", "checkpoint-*", "--sort=-creatordate"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().splitlines()[0]
        except Exception:
            pass
        return "N/A"


# ── CLI 入口 ──────────────────────────────────────────

if __name__ == "__main__":
    # 自动查找 .agent 目录
    base = Path(".agent")
    if not base.exists():
        current = Path.cwd()
        while current != current.parent:
            candidate = current / ".agent"
            if candidate.is_dir():
                base = candidate
                break
            current = current.parent

    dashboard = StatusDashboard(base_dir=base)
    output = dashboard.generate()
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    stdout_buffer = getattr(sys.stdout, "buffer", None)
    if stdout_buffer is not None:
        stdout_buffer.write(output.encode(encoding, errors="backslashreplace") + b"\n")
    else:
        print(output.encode(encoding, errors="backslashreplace").decode(encoding, errors="ignore"))
