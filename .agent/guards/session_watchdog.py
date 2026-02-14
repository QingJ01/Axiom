"""
session_watchdog.py — Session 看门狗 (T-303)

轻量 Python 脚本: 监控 .agent/memory/active_context.md 的最后修改时间，
超过指定时间未更新则在终端提醒。

支持特性:
    - 可配置超时阈值 (默认 30 分钟)
    - 可配置检查间隔 (默认 5 分钟)
    - Windows / Unix 跨平台
    - 后台运行模式
    - 优雅退出 (Ctrl+C)

Usage:
    python .agent/guards/session_watchdog.py
    python .agent/guards/session_watchdog.py --timeout 20 --interval 3
    python .agent/guards/session_watchdog.py --once  # 单次检查模式
"""

from __future__ import annotations

import argparse
import os
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path


# ── 配置 ──────────────────────────────────────────────

DEFAULT_TIMEOUT_MINUTES = 30
DEFAULT_CHECK_INTERVAL_MINUTES = 5
CONTEXT_RELATIVE_PATH = ".agent/memory/active_context.md"


# ── ANSI 颜色 (支持 Windows Terminal) ─────────────────

class Colors:
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# ── 核心逻辑 ──────────────────────────────────────────

class SessionWatchdog:
    """会话看门狗: 监控 active_context.md 的更新状态。"""

    def __init__(
        self,
        timeout_minutes: int = DEFAULT_TIMEOUT_MINUTES,
        check_interval_minutes: int = DEFAULT_CHECK_INTERVAL_MINUTES,
        context_path: str | Path | None = None,
    ) -> None:
        self.timeout_seconds = timeout_minutes * 60
        self.check_interval_seconds = check_interval_minutes * 60
        self._running = True
        self._alert_count = 0

        # 查找 context 文件
        if context_path:
            self.context_file = Path(context_path)
        else:
            self.context_file = self._find_context_file()

    def _find_context_file(self) -> Path:
        """从当前目录向上查找 .agent/memory/active_context.md"""
        current = Path.cwd()
        while current != current.parent:
            candidate = current / CONTEXT_RELATIVE_PATH
            if candidate.exists():
                return candidate
            current = current.parent

        # 回退到相对路径
        return Path(CONTEXT_RELATIVE_PATH)

    def check_once(self) -> dict:
        """
        单次检查 active_context.md 的状态。
        
        Returns:
            dict with keys: exists, stale, last_modified, age_minutes, message
        """
        result = {
            "exists": False,
            "stale": False,
            "last_modified": None,
            "age_minutes": 0,
            "message": "",
        }

        if not self.context_file.exists():
            result["message"] = f"❌ 文件不存在: {self.context_file}"
            return result

        result["exists"] = True

        # 获取最后修改时间
        mtime = os.path.getmtime(self.context_file)
        last_modified = datetime.fromtimestamp(mtime)
        age_seconds = time.time() - mtime
        age_minutes = int(age_seconds / 60)

        result["last_modified"] = last_modified.isoformat()
        result["age_minutes"] = age_minutes

        if age_seconds > self.timeout_seconds:
            result["stale"] = True
            result["message"] = (
                f"⚠️  active_context.md 已 {age_minutes} 分钟未更新！"
                f" (阈值: {self.timeout_seconds // 60} 分钟)"
            )
        else:
            remaining = int((self.timeout_seconds - age_seconds) / 60)
            result["message"] = (
                f"✅ active_context.md 状态正常"
                f" (上次更新: {age_minutes} 分钟前, 剩余: {remaining} 分钟)"
            )

        return result

    def _print_alert(self, check_result: dict) -> None:
        """打印告警信息。"""
        now = datetime.now().strftime("%H:%M:%S")

        if check_result["stale"]:
            self._alert_count += 1
            severity = "🔴" if self._alert_count >= 3 else "🟡"

            print(f"\n{'=' * 60}")
            print(f"{Colors.YELLOW}{Colors.BOLD}")
            print(f"  {severity} [{now}] SESSION WATCHDOG ALERT #{self._alert_count}")
            print(f"  {check_result['message']}")
            print(f"")
            print(f"  💡 建议操作:")
            print(f"     1. 执行 /suspend 保存当前状态")
            print(f"     2. 更新 active_context.md 中的任务进度")
            print(f"     3. 如果任务已完成，执行 /status 检查")
            print(f"{Colors.RESET}")
            print(f"{'=' * 60}\n")
        else:
            print(
                f"  {Colors.GREEN}[{now}]{Colors.RESET} "
                f"{check_result['message']}"
            )

    def run(self) -> None:
        """启动持续监控循环。"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}")
        print(f"  🐕 Axiom Session Watchdog 已启动")
        print(f"     监控文件: {self.context_file}")
        print(f"     超时阈值: {self.timeout_seconds // 60} 分钟")
        print(f"     检查间隔: {self.check_interval_seconds // 60} 分钟")
        print(f"     按 Ctrl+C 停止")
        print(f"{Colors.RESET}\n")

        # 注册信号处理
        signal.signal(signal.SIGINT, self._handle_signal)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._handle_signal)

        while self._running:
            try:
                result = self.check_once()
                self._print_alert(result)
                time.sleep(self.check_interval_seconds)
            except KeyboardInterrupt:
                break

        print(f"\n{Colors.CYAN}  🐕 Watchdog 已停止。共发出 {self._alert_count} 次告警。{Colors.RESET}")

    def _handle_signal(self, signum: int, frame) -> None:
        """优雅退出。"""
        self._running = False


# ── CLI 入口 ──────────────────────────────────────────

def main() -> None:
    """CLI 入口函数。"""
    stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
    stderr_reconfigure = getattr(sys.stderr, "reconfigure", None)
    if callable(stdout_reconfigure):
        stdout_reconfigure(errors="backslashreplace")
    if callable(stderr_reconfigure):
        stderr_reconfigure(errors="backslashreplace")

    # 启用 Windows ANSI 支持
    if sys.platform == "win32":
        os.system("")  # 激活 Windows Terminal ANSI

    parser = argparse.ArgumentParser(
        description="Axiom Session Watchdog — 监控 active_context.md 更新状态",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_MINUTES,
        help=f"超时阈值 (分钟, 默认 {DEFAULT_TIMEOUT_MINUTES})",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_CHECK_INTERVAL_MINUTES,
        help=f"检查间隔 (分钟, 默认 {DEFAULT_CHECK_INTERVAL_MINUTES})",
    )
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="active_context.md 文件路径 (默认自动查找)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="单次检查模式 (不循环)",
    )

    args = parser.parse_args()

    watchdog = SessionWatchdog(
        timeout_minutes=args.timeout,
        check_interval_minutes=args.interval,
        context_path=args.context,
    )

    if args.once:
        result = watchdog.check_once()
        print(result["message"])
        sys.exit(1 if result["stale"] else 0)
    else:
        watchdog.run()


if __name__ == "__main__":
    main()
