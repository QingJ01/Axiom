"""
config_loader.py — 配置抽象层加载器 (T-304)

从 agent_config.md 读取配置，提供统一的 Python API 访问。
支持按 provider 获取能力映射、路径配置和共享设置。

Usage:
    from config.config_loader import AgentConfig
    config = AgentConfig()
    
    # 获取当前 provider
    provider = config.active_provider  # "gemini"
    
    # 获取能力映射
    read_cmd = config.get_capability("file_read")  # "view_file"
    
    # 获取所有 provider 信息
    info = config.get_provider_info()
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ProviderConfig:
    """单个模型 Provider 的配置。"""
    name: str
    display_name: str = ""
    global_config_path: str = ""
    adapter_path: str = ""
    capabilities: dict[str, str] = field(default_factory=dict)
    commands: dict[str, str] = field(default_factory=dict)
    features: dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedConfig:
    """跨模型共享配置。"""
    project: dict[str, str] = field(default_factory=dict)
    paths: dict[str, str] = field(default_factory=dict)
    guards: dict[str, Any] = field(default_factory=dict)
    evolution: dict[str, Any] = field(default_factory=dict)
    dispatcher: dict[str, Any] = field(default_factory=dict)


class AgentConfig:
    """
    Axiom 配置管理器。

    从 .agent/config/agent_config.md 读取配置，
    提供统一的 API 供各模块使用。
    """

    # 预定义 Provider 配置 (与 agent_config.md 保持同步)
    _PROVIDERS: dict[str, ProviderConfig] = {
        "gemini": ProviderConfig(
            name="gemini",
            display_name="Gemini (Google AI)",
            global_config_path="~/.gemini/GEMINI.md",
            adapter_path=".agent/adapters/gemini/GEMINI.md",
            capabilities={
                "file_read": "view_file",
                "file_write": "replace_file_content",
                "file_create": "create_file",
                "run_command": "run_command",
                "search": "search_files",
            },
            commands={
                "run": "flutter run",
                "test": "flutter test",
                "analyze": "flutter analyze",
                "build": "flutter build",
            },
            features={
                "json_output": True,
                "streaming": True,
                "function_calling": True,
                "context_window": 1_000_000,
                "supports_exec_mode": True,
            },
        ),
        "claude": ProviderConfig(
            name="claude",
            display_name="Claude (Anthropic)",
            global_config_path="~/.claude/CLAUDE.md",
            adapter_path=".agent/adapters/claude/CLAUDE.md",
            capabilities={
                "file_read": "read_file",
                "file_write": "replace_string_in_file",
                "file_create": "create_file",
                "run_command": "run_in_terminal",
                "search": "grep_search",
            },
            commands={
                "run": "flutter run",
                "test": "flutter test",
                "analyze": "flutter analyze",
                "build": "flutter build",
            },
            features={
                "json_output": False,
                "streaming": True,
                "function_calling": True,
                "context_window": 200_000,
                "supports_exec_mode": False,
            },
        ),
        "copilot": ProviderConfig(
            name="copilot",
            display_name="Copilot / GPT (OpenAI)",
            global_config_path="~/.copilot/copilot-instructions.md",
            adapter_path=".agent/adapters/copilot/copilot-instructions.md",
            capabilities={
                "file_read": "read_file",
                "file_write": "replace_string_in_file",
                "file_create": "create_file",
                "run_command": "run_in_terminal",
                "search": "semantic_search",
            },
            commands={
                "run": "flutter run",
                "test": "flutter test",
                "analyze": "flutter analyze",
                "build": "flutter build",
            },
            features={
                "json_output": False,
                "streaming": True,
                "function_calling": True,
                "context_window": 128_000,
                "supports_exec_mode": False,
            },
        ),
    }

    _SHARED: SharedConfig = SharedConfig(
        project={"name": "Axiom", "type": "flutter", "language": "dart"},
        paths={
            "memory": ".agent/memory",
            "rules": ".agent/rules",
            "skills": ".agent/skills",
            "workflows": ".agent/workflows",
            "guards": ".agent/guards",
            "evolution": ".agent/evolution",
            "dispatcher": ".agent/dispatcher",
            "config": ".agent/config",
            "adapters": ".agent/adapters",
        },
        guards={
            "pre_commit_warning": True,
            "post_commit_checkpoint": True,
            "checkpoint_interval_min": 30,
            "watchdog_timeout_min": 30,
            "watchdog_interval_min": 5,
        },
        evolution={
            "min_confidence": 0.5,
            "seed_confidence": 0.85,
            "decay_days": 30,
            "decay_amount": 0.1,
            "max_learning_queue": 50,
            "pattern_min_occurrences": 3,
        },
        dispatcher={
            "max_restarts": 3,
            "default_timeout_sec": 600,
            "timeout_tiers": {"simple": 600, "medium": 900, "complex": 1200},
            "prompt_max_tokens": 4000,
            "compress_threshold": 4000,
        },
    )

    def __init__(self, config_path: str | Path | None = None) -> None:
        """
        Args:
            config_path: agent_config.md 路径。None 则自动查找。
        """
        self._active_provider = "gemini"

        if config_path:
            self._config_file = Path(config_path)
        else:
            self._config_file = self._find_config_file()

        self._load_active_provider()

    def _find_config_file(self) -> Path:
        """查找 agent_config.md。"""
        current = Path.cwd()
        while current != current.parent:
            candidate = current / ".agent" / "config" / "agent_config.md"
            if candidate.exists():
                return candidate
            current = current.parent
        return Path(".agent/config/agent_config.md")

    def _load_active_provider(self) -> None:
        """从 agent_config.md 读取 ACTIVE_PROVIDER。"""
        try:
            if not self._config_file.exists():
                return

            content = self._config_file.read_text(encoding="utf-8")
            match = re.search(r"ACTIVE_PROVIDER:\s*(\w+)", content)
            if match:
                provider = match.group(1).strip()
                if provider in self._PROVIDERS:
                    self._active_provider = provider
        except Exception:
            pass  # 使用默认值

    # ── Public API ──────────────────────────────────────

    @property
    def active_provider(self) -> str:
        """当前激活的 Provider 名称。"""
        return self._active_provider

    @active_provider.setter
    def active_provider(self, value: str) -> None:
        """设置当前 Provider (不持久化)。"""
        if value not in self._PROVIDERS:
            raise ValueError(
                f"Unknown provider: {value}. "
                f"Available: {list(self._PROVIDERS.keys())}"
            )
        self._active_provider = value

    def get_provider(self, name: str | None = None) -> ProviderConfig:
        """获取 Provider 配置。"""
        name = name or self._active_provider
        if name not in self._PROVIDERS:
            raise ValueError(f"Unknown provider: {name}")
        return self._PROVIDERS[name]

    def get_capability(self, capability: str, provider: str | None = None) -> str:
        """获取某个能力的 API 名称。

        Args:
            capability: 能力名称 (file_read, file_write, etc.)
            provider: Provider 名称。None 则使用当前激活的。

        Returns:
            对应的 API 名称
        """
        p = self.get_provider(provider)
        return p.capabilities.get(capability, capability)

    def get_command(self, command: str, provider: str | None = None) -> str:
        """获取项目命令。"""
        p = self.get_provider(provider)
        return p.commands.get(command, command)

    def get_feature(self, feature: str, provider: str | None = None) -> Any:
        """获取 Provider 特性。"""
        p = self.get_provider(provider)
        return p.features.get(feature)

    @property
    def shared(self) -> SharedConfig:
        """共享配置。"""
        return self._SHARED

    def get_path(self, key: str) -> str:
        """获取 Axiom 路径配置。"""
        return self._SHARED.paths.get(key, "")

    def get_all_providers(self) -> list[str]:
        """获取所有可用 Provider 名称。"""
        return list(self._PROVIDERS.keys())

    def get_provider_info(self, provider: str | None = None) -> dict:
        """获取 Provider 摘要信息 (适合展示)。"""
        p = self.get_provider(provider)
        return {
            "name": p.name,
            "display_name": p.display_name,
            "global_config": p.global_config_path,
            "context_window": p.features.get("context_window", "unknown"),
            "exec_mode": p.features.get("supports_exec_mode", False),
            "capabilities": list(p.capabilities.keys()),
        }

    def supports(self, feature: str, provider: str | None = None) -> bool:
        """检查 Provider 是否支持某特性。"""
        val = self.get_feature(feature, provider)
        return bool(val)

    def __repr__(self) -> str:
        return (
            f"AgentConfig(provider={self._active_provider!r}, "
            f"config={self._config_file})"
        )
