"""
decision_engine.py — PM 自主决策引擎 (T-104)

语义分析 Worker 提问，按规则判断:
- 技术细节 → 自行决定（返回答案）
- 需求歧义 → 标记 BLOCKED（返回 None）

决策规则:
    1. 命名/格式/代码风格 → 自行决定
    2. 技术实现细节（框架选择、API 设计、目录结构）→ 按项目约定决定
    3. 需求含义不明确 → BLOCKED
    4. 涉及成本/安全/用户数据 → BLOCKED
    5. 涉及项目范围变更 → BLOCKED
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """决策类型。"""
    AUTO_DECIDE = "auto"  # PM 自行决定
    BLOCKED = "blocked"  # 需要用户介入
    DEFER = "defer"  # 延后处理


@dataclass
class Decision:
    """决策结果。"""
    type: DecisionType
    answer: str | None  # AUTO_DECIDE 时有值
    reason: str  # 决策理由
    confidence: float  # 置信度 0.0 ~ 1.0
    category: str  # 问题分类


# ── 自动决策规则 ──────────────────────────────────────

# 可自动决定的问题模式 → (分类, 默认答案模板)
AUTO_RULES: list[tuple[re.Pattern[str], str, str]] = [
    # 命名/格式
    (re.compile(r"(命名|起名|取名|变量名|文件名|类名|函数名|方法名)", re.IGNORECASE),
     "命名规范",
     "请遵循项目现有命名规范: Python 使用 snake_case，类名使用 PascalCase，常量使用 UPPER_SNAKE_CASE。"),

    # 目录结构
    (re.compile(r"(放在哪|目录|文件夹|路径|位置|放到哪|放哪)", re.IGNORECASE),
     "目录结构",
     "请按照 PRD 中定义的目录结构放置文件。如果是新模块，放在最相关的现有目录下。"),

    # 代码风格
    (re.compile(r"(代码风格|格式化|缩进|空格|引号|分号|lint)", re.IGNORECASE),
     "代码风格",
     "遵循 PEP 8 规范，使用 type hints，所有公共函数需要 docstring。"),

    # 测试相关
    (re.compile(r"(测试|test|unittest|pytest|覆盖率|coverage)", re.IGNORECASE),
     "测试策略",
     "为核心逻辑编写单元测试，使用 pytest 框架，目标覆盖率 ≥ 80%。"),

    # 错误处理
    (re.compile(r"(错误处理|异常|exception|error handling|try.*catch|except)", re.IGNORECASE),
     "错误处理",
     "使用具体异常类型捕获，不使用裸 except。关键操作记录日志，非关键操作静默处理。"),

    # 日志
    (re.compile(r"(日志|log|logging|打印|print)", re.IGNORECASE),
     "日志策略",
     "使用 logging 模块，不使用 print。DEBUG 级别用于调试信息，INFO 级别用于关键操作，WARNING/ERROR 用于异常。"),

    # 导入/依赖
    (re.compile(r"(导入|import|依赖|库|package|module)", re.IGNORECASE),
     "依赖管理",
     "优先使用 Python 标准库，避免引入外部依赖。如必须引入，需说明理由。"),

    # 编码/字符集
    (re.compile(r"(编码|encoding|utf|charset|unicode)", re.IGNORECASE),
     "编码规范",
     "统一使用 UTF-8 编码。"),

    # 注释
    (re.compile(r"(注释|comment|文档|docstring|说明)", re.IGNORECASE),
     "文档规范",
     "公共 API 需要 docstring（Google 风格），复杂逻辑需要行内注释。"),

    # 配置/默认值
    (re.compile(r"(默认值|default|配置项|超时|timeout|阈值|threshold)", re.IGNORECASE),
     "配置决策",
     "使用合理的默认值，并确保可通过参数覆盖。参考 PRD 中已定义的默认值。"),

    # 方法/实现选择
    (re.compile(r"(实现方式|做法|方案|approach|implementation|怎么做|怎么实现|如何实现)", re.IGNORECASE),
     "实现决策",
     "选择最简单、最易维护的实现方式。优先考虑可读性，其次是性能。"),
]

# 需要用户介入的问题模式 → (分类, 理由)
BLOCKED_RULES: list[tuple[re.Pattern[str], str, str]] = [
    # 需求歧义
    (re.compile(r"(需求|功能|特性|feature|requirement|用户故事|user story)", re.IGNORECASE),
     "需求歧义",
     "涉及需求定义，需要用户确认"),

    # 安全/隐私
    (re.compile(r"(安全|security|密钥|key|token|认证|auth|加密|encrypt|隐私|privacy)", re.IGNORECASE),
     "安全决策",
     "涉及安全相关决策，需要用户确认"),

    # 成本/资源
    (re.compile(r"(成本|cost|付费|收费|计费|billing|资源|resource|预算)", re.IGNORECASE),
     "成本决策",
     "涉及成本/资源分配，需要用户确认"),

    # 用户数据
    (re.compile(r"(用户数据|user data|个人信息|PII|GDPR|数据迁移|migration)", re.IGNORECASE),
     "数据决策",
     "涉及用户数据处理，需要用户确认"),

    # 范围变更
    (re.compile(r"(范围|scope|额外功能|新增需求|change request|扩展|extend)", re.IGNORECASE),
     "范围变更",
     "涉及项目范围变更，需要用户确认"),

    # 架构决策
    (re.compile(r"(架构|architecture|微服务|monolith|数据库选型|database choice)", re.IGNORECASE),
     "架构决策",
     "涉及架构级别决策，需要用户确认"),

    # 第三方服务
    (re.compile(r"(第三方|third.party|外部服务|external service|API key|SaaS)", re.IGNORECASE),
     "第三方集成",
     "涉及第三方服务集成，需要用户确认"),
]


class DecisionEngine:
    """PM 自主决策引擎 — 分析 Worker 的问题并做出自动决策或标记 BLOCKED。

    使用方式:
        engine = DecisionEngine()
        decision = engine.decide("T-001", "这个文件放哪里？")
        if decision.type == DecisionType.AUTO_DECIDE:
            answer = decision.answer
        else:
            # 标记 BLOCKED，等待用户
    """

    def __init__(
        self,
        project_context: dict[str, Any] | None = None,
    ) -> None:
        """
        Args:
            project_context: 项目上下文（可包含 tech_stack, conventions 等），
                            用于增强决策质量。
        """
        self.project_context = project_context or {}
        self._decision_log: list[Decision] = []

    def decide(self, task_id: str, question: str) -> Decision:
        """分析问题并做出决策。

        Args:
            task_id: 任务 ID
            question: Worker 提出的问题文本

        Returns:
            Decision — 包含决策类型、答案、理由和置信度
        """
        if not question or len(question.strip()) < 3:
            decision = Decision(
                type=DecisionType.AUTO_DECIDE,
                answer="请继续执行。",
                reason="问题过短或为空，默认继续",
                confidence=0.5,
                category="空问题",
            )
            self._decision_log.append(decision)
            return decision

        # 1. 先检查 BLOCKED 规则（高优先级）
        for pattern, category, reason in BLOCKED_RULES:
            if pattern.search(question):
                decision = Decision(
                    type=DecisionType.BLOCKED,
                    answer=None,
                    reason=reason,
                    confidence=0.9,
                    category=category,
                )
                logger.info(
                    "Task %s BLOCKED: [%s] %s", task_id, category, reason
                )
                self._decision_log.append(decision)
                return decision

        # 2. 再检查自动决策规则
        for pattern, category, default_answer in AUTO_RULES:
            if pattern.search(question):
                # 用项目上下文增强答案
                answer = self._enhance_answer(category, default_answer)
                decision = Decision(
                    type=DecisionType.AUTO_DECIDE,
                    answer=answer,
                    reason=f"匹配自动决策规则: {category}",
                    confidence=0.8,
                    category=category,
                )
                logger.info(
                    "Task %s AUTO: [%s] confidence=%.1f",
                    task_id, category, decision.confidence,
                )
                self._decision_log.append(decision)
                return decision

        # 3. 无匹配规则 → 尝试通用决策
        decision = self._fallback_decision(task_id, question)
        self._decision_log.append(decision)
        return decision

    def as_answer_callback(self) -> callable:
        """返回一个可用于 RestartInjector.execute_with_injection 的回调函数。

        Returns:
            (task_id, question) -> str | None
        """
        def callback(task_id: str, question: str) -> str | None:
            decision = self.decide(task_id, question)
            return decision.answer

        return callback

    @property
    def decision_log(self) -> list[Decision]:
        """已做出的决策日志。"""
        return list(self._decision_log)

    # ── 内部方法 ────────────────────────────────────────

    def _enhance_answer(self, category: str, default_answer: str) -> str:
        """根据项目上下文增强默认答案。"""
        # 如果有项目特定约定，追加到答案中
        conventions = self.project_context.get("conventions", {})
        if category in conventions:
            return f"{default_answer}\n\n项目特定约定: {conventions[category]}"
        return default_answer

    def _fallback_decision(self, task_id: str, question: str) -> Decision:
        """无规则匹配时的兜底决策。

        策略: 如果问题看起来是技术实现细节，自动决定；
              否则标记 BLOCKED。
        """
        # 简单启发式: 问题中包含代码相关词汇 → 自动决定
        tech_hints = [
            "代码", "code", "函数", "function", "类", "class",
            "方法", "method", "变量", "variable", "参数", "param",
            "返回值", "return", "类型", "type", "接口", "interface",
        ]

        is_tech = any(hint in question.lower() for hint in tech_hints)

        if is_tech:
            return Decision(
                type=DecisionType.AUTO_DECIDE,
                answer="请按照最佳工程实践自行决定技术实现细节，确保代码可读、可测试、可维护。",
                reason="兜底: 问题包含技术关键词，视为实现细节",
                confidence=0.6,
                category="通用技术",
            )
        else:
            return Decision(
                type=DecisionType.BLOCKED,
                answer=None,
                reason="兜底: 无法自动分类，需用户确认",
                confidence=0.4,
                category="未分类",
            )
