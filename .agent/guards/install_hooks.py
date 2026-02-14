"""
install_hooks.py — Git Hooks 安装器

自动将 .agent/guards/ 中的 Hook 脚本安装到 .git/hooks/ 目录。
支持 Windows 和 Unix 系统。

Usage:
    python .agent/guards/install_hooks.py
    python .agent/guards/install_hooks.py --uninstall
"""

from __future__ import annotations

import os
import platform
import shutil
import stat
import sys
from pathlib import Path


HOOKS = ["pre-commit", "post-commit"]
GUARDS_DIR = Path(__file__).parent
BACKUP_SUFFIX = ".bak.antigravity"


def find_git_hooks_dir() -> Path:
    """查找 .git/hooks 目录。"""
    current = Path.cwd()
    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.is_dir():
            hooks_dir = git_dir / "hooks"
            hooks_dir.mkdir(exist_ok=True)
            return hooks_dir
        current = current.parent
    raise FileNotFoundError("未找到 .git 目录，请在 Git 仓库根目录运行此脚本")


def install_hooks() -> None:
    """安装所有 Hook 到 .git/hooks/。"""
    hooks_dir = find_git_hooks_dir()
    is_windows = platform.system() == "Windows"

    for hook_name in HOOKS:
        source = GUARDS_DIR / hook_name
        if not source.exists():
            print(f"  ⏭️  {hook_name}: 源文件不存在，跳过")
            continue

        target = hooks_dir / hook_name

        # 备份已有 Hook
        if target.exists():
            backup = target.with_suffix(BACKUP_SUFFIX)
            shutil.copy2(target, backup)
            print(f"  📦 {hook_name}: 已备份原 Hook → {backup.name}")

        # 复制 Hook
        shutil.copy2(source, target)

        # Unix: 添加可执行权限
        if not is_windows:
            st = os.stat(target)
            os.chmod(target, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        print(f"  ✅ {hook_name}: 已安装到 {target}")

    print("\n🎉 Git Hooks 安装完成！")


def uninstall_hooks() -> None:
    """卸载所有 Hook，恢复备份。"""
    hooks_dir = find_git_hooks_dir()

    for hook_name in HOOKS:
        target = hooks_dir / hook_name
        backup = target.with_suffix(BACKUP_SUFFIX)

        if target.exists():
            target.unlink()
            print(f"  🗑️  {hook_name}: 已移除")

        if backup.exists():
            shutil.move(str(backup), str(target))
            print(f"  ♻️  {hook_name}: 已恢复原 Hook")

    print("\n🎉 Git Hooks 已卸载")


if __name__ == "__main__":
    print("=" * 50)
    print("  Axiom — Hook Installer")
    print("=" * 50)

    if "--uninstall" in sys.argv:
        uninstall_hooks()
    else:
        install_hooks()
