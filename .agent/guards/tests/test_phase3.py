"""
test_phase3.py — Phase 3 全系统回归测试 (T-309)

验证 Phase 3 所有组件:
  - T-301: Pre-commit 守卫
  - T-302: Post-commit 守卫
  - T-303: Session 看门狗
  - T-304: 配置抽象层
  - T-305/306/307: 适配器
  - T-308: /status 仪表盘

运行:
    cd <project_root>
    python -m pytest .agent/guards/tests/test_phase3.py -v
    或
    python .agent/guards/tests/test_phase3.py
"""

from __future__ import annotations

import os
import sys
import time
import textwrap
from pathlib import Path
from datetime import datetime

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # .agent/guards/tests → project root
AGENT_DIR = PROJECT_ROOT / ".agent"
sys.path.insert(0, str(AGENT_DIR))

_stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
_stderr_reconfigure = getattr(sys.stderr, "reconfigure", None)
if callable(_stdout_reconfigure):
    _stdout_reconfigure(errors="backslashreplace")
if callable(_stderr_reconfigure):
    _stderr_reconfigure(errors="backslashreplace")


# ════════════════════════════════════════════════════
# Test Suite 1: 文件完整性检查
# ════════════════════════════════════════════════════

class TestFileIntegrity:
    """验证 Phase 3 所有交付物文件存在且非空。"""

    REQUIRED_FILES = [
        # Guards (T-301, T-302, T-303)
        ".agent/guards/pre-commit",
        ".agent/guards/pre-commit.ps1",
        ".agent/guards/post-commit",
        ".agent/guards/post-commit.ps1",
        ".agent/guards/session_watchdog.py",
        ".agent/guards/install_hooks.py",
        ".agent/guards/status_dashboard.py",
        # Config (T-304)
        ".agent/config/agent_config.md",
        ".agent/config/config_loader.py",
        ".agent/config/__init__.py",
        # Adapters (T-305, T-306, T-307)
        ".agent/adapters/gemini/GEMINI.md",
        ".agent/adapters/claude/CLAUDE.md",
        ".agent/adapters/copilot/copilot-instructions.md",
        # Workflow update (T-308)
        ".agent/workflows/status.md",
    ]

    def test_all_files_exist(self) -> list[str]:
        """检查所有必需文件存在。"""
        errors = []
        for rel_path in self.REQUIRED_FILES:
            full_path = PROJECT_ROOT / rel_path
            if not full_path.exists():
                errors.append(f"MISSING: {rel_path}")
            elif full_path.stat().st_size == 0:
                errors.append(f"EMPTY: {rel_path}")
        return errors

    def test_directory_structure(self) -> list[str]:
        """检查目录结构完整。"""
        errors = []
        required_dirs = [
            ".agent/guards",
            ".agent/config",
            ".agent/adapters/gemini",
            ".agent/adapters/claude",
            ".agent/adapters/copilot",
        ]
        for d in required_dirs:
            if not (PROJECT_ROOT / d).is_dir():
                errors.append(f"DIR MISSING: {d}")
        return errors


# ════════════════════════════════════════════════════
# Test Suite 2: 配置抽象层 (T-304)
# ════════════════════════════════════════════════════

class TestConfigLoader:
    """验证配置加载器功能。"""

    def test_load_config(self) -> list[str]:
        """测试配置加载。"""
        errors = []
        try:
            from config.config_loader import AgentConfig
            config = AgentConfig(config_path=AGENT_DIR / "config" / "agent_config.md")
            
            # 验证 Provider 名称
            if config.active_provider not in ["gemini", "claude", "copilot"]:
                errors.append(f"Unexpected provider: {config.active_provider}")
            
            # 验证所有 Provider 可获取
            for p in ["gemini", "claude", "copilot"]:
                provider = config.get_provider(p)
                if not provider.display_name:
                    errors.append(f"Provider {p}: missing display_name")
                if not provider.capabilities:
                    errors.append(f"Provider {p}: missing capabilities")
                if not provider.commands:
                    errors.append(f"Provider {p}: missing commands")
        except Exception as e:
            errors.append(f"Config load error: {e}")
        return errors

    def test_capability_mapping(self) -> list[str]:
        """测试能力映射。"""
        errors = []
        try:
            from config.config_loader import AgentConfig
            config = AgentConfig(config_path=AGENT_DIR / "config" / "agent_config.md")
            
            # Gemini 映射
            if config.get_capability("file_read", "gemini") != "view_file":
                errors.append("Gemini file_read should be 'view_file'")
            
            # Claude 映射
            if config.get_capability("file_read", "claude") != "read_file":
                errors.append("Claude file_read should be 'read_file'")
            
            # Copilot 映射
            if config.get_capability("run_command", "copilot") != "run_in_terminal":
                errors.append("Copilot run_command should be 'run_in_terminal'")
        except Exception as e:
            errors.append(f"Capability mapping error: {e}")
        return errors

    def test_shared_config(self) -> list[str]:
        """测试共享配置。"""
        errors = []
        try:
            from config.config_loader import AgentConfig
            config = AgentConfig(config_path=AGENT_DIR / "config" / "agent_config.md")
            
            shared = config.shared
            if shared.project.get("type") != "flutter":
                errors.append("Project type should be 'flutter'")
            if shared.dispatcher.get("max_restarts") != 3:
                errors.append("Max restarts should be 3")
            if shared.evolution.get("min_confidence") != 0.5:
                errors.append("Min confidence should be 0.5")
        except Exception as e:
            errors.append(f"Shared config error: {e}")
        return errors

    def test_provider_switching(self) -> list[str]:
        """测试 Provider 切换。"""
        errors = []
        try:
            from config.config_loader import AgentConfig
            config = AgentConfig(config_path=AGENT_DIR / "config" / "agent_config.md")
            
            for p in ["gemini", "claude", "copilot"]:
                config.active_provider = p
                if config.active_provider != p:
                    errors.append(f"Failed to switch to {p}")
            
            # 测试无效 Provider
            try:
                config.active_provider = "invalid"
                errors.append("Should raise ValueError for invalid provider")
            except ValueError:
                pass  # 期望的行为
        except Exception as e:
            errors.append(f"Provider switch error: {e}")
        return errors


# ════════════════════════════════════════════════════
# Test Suite 3: Session 看门狗 (T-303)
# ════════════════════════════════════════════════════

class TestSessionWatchdog:
    """验证看门狗功能。"""

    def test_check_once(self) -> list[str]:
        """测试单次检查模式。"""
        errors = []
        try:
            sys.path.insert(0, str(AGENT_DIR / "guards"))
            from session_watchdog import SessionWatchdog
            
            watchdog = SessionWatchdog(
                timeout_minutes=30,
                context_path=AGENT_DIR / "memory" / "active_context.md",
            )
            result = watchdog.check_once()
            
            if not isinstance(result, dict):
                errors.append("check_once should return dict")
            if "exists" not in result:
                errors.append("Result missing 'exists' key")
            if "stale" not in result:
                errors.append("Result missing 'stale' key")
            if "message" not in result:
                errors.append("Result missing 'message' key")
            
            # 文件应该存在
            if not result["exists"]:
                errors.append("active_context.md should exist")
        except Exception as e:
            errors.append(f"Watchdog error: {e}")
        return errors

    def test_stale_detection(self) -> list[str]:
        """测试过期检测 (用极短超时)。"""
        errors = []
        try:
            sys.path.insert(0, str(AGENT_DIR / "guards"))
            from session_watchdog import SessionWatchdog
            
            # 使用 0 分钟超时，应立即标记为 stale
            watchdog = SessionWatchdog(
                timeout_minutes=0,
                context_path=AGENT_DIR / "memory" / "active_context.md",
            )
            result = watchdog.check_once()
            
            if result["exists"] and not result["stale"]:
                errors.append("Should be stale with 0-minute timeout")
        except Exception as e:
            errors.append(f"Stale detection error: {e}")
        return errors


# ════════════════════════════════════════════════════
# Test Suite 4: 仪表盘 (T-308)
# ════════════════════════════════════════════════════

class TestStatusDashboard:
    """验证仪表盘生成。"""

    def test_generate_dashboard(self) -> list[str]:
        """测试完整仪表盘生成。"""
        errors = []
        try:
            sys.path.insert(0, str(AGENT_DIR / "guards"))
            from status_dashboard import StatusDashboard
            
            dashboard = StatusDashboard(base_dir=AGENT_DIR)
            output = dashboard.generate()
            
            if not output:
                errors.append("Dashboard output is empty")
            
            # 检查所有区块存在
            required_sections = [
                "System State",
                "Task Progress",
                "Evolution Stats",
                "Recent Reflections",
                "Workflow Metrics",
                "Guard Status",
                "Axiom v4.0",
            ]
            for section in required_sections:
                if section not in output:
                    errors.append(f"Missing section: {section}")
        except Exception as e:
            errors.append(f"Dashboard error: {e}")
        return errors


# ════════════════════════════════════════════════════
# Test Suite 5: 适配器内容验证 (T-305/306/307)
# ════════════════════════════════════════════════════

class TestAdapters:
    """验证适配器内容正确性。"""

    def test_gemini_adapter(self) -> list[str]:
        """验证 Gemini 适配器。"""
        return self._check_adapter(
            AGENT_DIR / "adapters" / "gemini" / "GEMINI.md",
            "Gemini",
            ["view_file", "replace_file_content", "run_command"],
        )

    def test_claude_adapter(self) -> list[str]:
        """验证 Claude 适配器。"""
        return self._check_adapter(
            AGENT_DIR / "adapters" / "claude" / "CLAUDE.md",
            "Claude",
            ["read_file", "replace_string_in_file", "run_in_terminal"],
        )

    def test_copilot_adapter(self) -> list[str]:
        """验证 Copilot 适配器。"""
        return self._check_adapter(
            AGENT_DIR / "adapters" / "copilot" / "copilot-instructions.md",
            "Copilot",
            ["read_file", "replace_string_in_file", "run_in_terminal"],
        )

    def _check_adapter(self, path: Path, name: str, expected_apis: list[str]) -> list[str]:
        errors = []
        try:
            content = path.read_text(encoding="utf-8")
            
            # 检查基本结构
            required = ["启动协议", "工作流触发器", "能力映射", "门禁规则", "进化引擎"]
            for section in required:
                if section not in content:
                    errors.append(f"{name}: Missing section '{section}'")
            
            # 检查 API 映射
            for api in expected_apis:
                if api not in content:
                    errors.append(f"{name}: Missing API '{api}'")
        except Exception as e:
            errors.append(f"{name} adapter error: {e}")
        return errors


# ════════════════════════════════════════════════════
# Test Suite 6: Git 守卫脚本语法 (T-301/302)
# ════════════════════════════════════════════════════

class TestGuardScripts:
    """验证守卫脚本内容。"""

    def test_pre_commit_content(self) -> list[str]:
        """验证 pre-commit 脚本内容。"""
        errors = []
        path = AGENT_DIR / "guards" / "pre-commit"
        content = path.read_text(encoding="utf-8")
        
        if "#!/bin/sh" not in content:
            errors.append("pre-commit: Missing shebang")
        if "active_context.md" not in content:
            errors.append("pre-commit: Missing context check")
        if "exit 0" not in content:
            errors.append("pre-commit: Should exit 0 (non-blocking)")
        if "Axiom Guard" not in content:
            errors.append("pre-commit: Missing guard name")
        return errors

    def test_post_commit_content(self) -> list[str]:
        """验证 post-commit 脚本内容。"""
        errors = []
        path = AGENT_DIR / "guards" / "post-commit"
        content = path.read_text(encoding="utf-8")
        
        if "#!/bin/sh" not in content:
            errors.append("post-commit: Missing shebang")
        if "checkpoint-" not in content:
            errors.append("post-commit: Missing checkpoint logic")
        if "1800" not in content:
            errors.append("post-commit: Missing 30-minute interval")
        if "exit 0" not in content:
            errors.append("post-commit: Should exit 0 (non-blocking)")
        return errors

    def test_install_hooks_script(self) -> list[str]:
        """验证安装脚本。"""
        errors = []
        path = AGENT_DIR / "guards" / "install_hooks.py"
        content = path.read_text(encoding="utf-8")
        
        if "pre-commit" not in content:
            errors.append("install: Missing pre-commit")
        if "post-commit" not in content:
            errors.append("install: Missing post-commit")
        if "--uninstall" not in content:
            errors.append("install: Missing uninstall option")
        return errors


# ════════════════════════════════════════════════════
# Test Suite 7: 命令覆盖率 (回归检查)
# ════════════════════════════════════════════════════

class TestCommandCoverage:
    """验证所有 13 个快捷命令对应的工作流文件存在。"""

    COMMANDS = [
        "start", "suspend1", "feature-flow", "analyze-error",
        "rollback", "status", "evolve", "reflect",
        "knowledge", "patterns", "meta", "export",
        "codex-dispatch",
    ]

    def test_workflow_files(self) -> list[str]:
        """检查所有工作流文件存在。"""
        errors = []
        workflows_dir = AGENT_DIR / "workflows"
        for cmd in self.COMMANDS:
            path = workflows_dir / f"{cmd}.md"
            if not path.exists():
                errors.append(f"MISSING workflow: {cmd}.md")
        return errors


# ════════════════════════════════════════════════════
# 测试运行器
# ════════════════════════════════════════════════════

def run_all_tests() -> bool:
    """运行所有测试并输出报告。"""
    test_suites = [
        ("File Integrity", TestFileIntegrity()),
        ("Config Loader", TestConfigLoader()),
        ("Session Watchdog", TestSessionWatchdog()),
        ("Status Dashboard", TestStatusDashboard()),
        ("Adapters", TestAdapters()),
        ("Guard Scripts", TestGuardScripts()),
        ("Command Coverage", TestCommandCoverage()),
    ]

    total_passed = 0
    total_failed = 0
    all_errors: list[str] = []

    print("\n" + "=" * 60)
    print("  Phase 3 Regression Test Suite")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

    for suite_name, suite in test_suites:
        print(f"\n── {suite_name} ──")
        
        # 获取所有 test_ 方法
        test_methods = [m for m in dir(suite) if m.startswith("test_")]
        
        for method_name in sorted(test_methods):
            method = getattr(suite, method_name)
            try:
                errors = method()
                if errors:
                    total_failed += 1
                    status = "❌ FAIL"
                    for err in errors:
                        all_errors.append(f"  [{suite_name}] {method_name}: {err}")
                else:
                    total_passed += 1
                    status = "✅ PASS"
                print(f"  {status}  {method_name}")
                if errors:
                    for err in errors:
                        print(f"         → {err}")
            except Exception as e:
                total_failed += 1
                print(f"  💥 ERROR  {method_name}: {e}")
                all_errors.append(f"  [{suite_name}] {method_name}: EXCEPTION: {e}")

    # 汇总
    total = total_passed + total_failed
    print("\n" + "=" * 60)
    print(f"  Results: {total_passed}/{total} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("  🎉 All tests passed!")
    else:
        print("\n  Failures:")
        for err in all_errors:
            print(err)
    
    print("=" * 60 + "\n")
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


def test_phase3_suite() -> None:
    """Pytest 入口：确保失败会真实标红。"""
    assert run_all_tests(), "Phase 3 regression suite failed"
