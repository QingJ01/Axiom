"""
test_decision_engine.py — PM 自主决策引擎测试 (T-104)

测试覆盖:
  - 自动决策规则匹配 (10 类)
  - BLOCKED 规则匹配 (7 类)
  - 兜底决策
  - 决策日志
  - as_answer_callback 集成
  - 样本问题分类正确率 ≥ 80%
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_dispatcher_parent = str(Path(__file__).resolve().parent.parent.parent)
if _dispatcher_parent not in sys.path:
    sys.path.insert(0, _dispatcher_parent)

from dispatcher.decision_engine import DecisionEngine, DecisionType


class TestAutoDecision:
    """自动决策: 技术细节应返回 AUTO_DECIDE。"""

    def setup_method(self) -> None:
        self.engine = DecisionEngine()

    def test_naming(self) -> None:
        d = self.engine.decide("T-001", "这个变量名用什么好？")
        assert d.type == DecisionType.AUTO_DECIDE
        assert d.answer is not None

    def test_directory(self) -> None:
        d = self.engine.decide("T-001", "工具类放在哪个目录？")
        assert d.type == DecisionType.AUTO_DECIDE

    def test_code_style(self) -> None:
        d = self.engine.decide("T-001", "代码风格用什么规范？")
        assert d.type == DecisionType.AUTO_DECIDE

    def test_testing(self) -> None:
        d = self.engine.decide("T-001", "需要写单元测试吗？")
        assert d.type == DecisionType.AUTO_DECIDE

    def test_error_handling(self) -> None:
        d = self.engine.decide("T-001", "异常处理策略是什么？")
        assert d.type == DecisionType.AUTO_DECIDE

    def test_logging(self) -> None:
        d = self.engine.decide("T-001", "日志应该用什么级别？")
        assert d.type == DecisionType.AUTO_DECIDE

    def test_default_value(self) -> None:
        d = self.engine.decide("T-001", "超时默认值设多少？")
        assert d.type == DecisionType.AUTO_DECIDE

    def test_implementation(self) -> None:
        d = self.engine.decide("T-001", "这个方法怎么实现比较好？")
        assert d.type == DecisionType.AUTO_DECIDE


class TestBlockedDecision:
    """BLOCKED 决策: 需用户介入的问题。"""

    def setup_method(self) -> None:
        self.engine = DecisionEngine()

    def test_requirement(self) -> None:
        d = self.engine.decide("T-001", "这个需求的具体含义是什么？")
        assert d.type == DecisionType.BLOCKED

    def test_security(self) -> None:
        d = self.engine.decide("T-001", "API key 应该如何管理？")
        assert d.type == DecisionType.BLOCKED

    def test_cost(self) -> None:
        d = self.engine.decide("T-001", "这个功能的成本预算是多少？")
        assert d.type == DecisionType.BLOCKED

    def test_user_data(self) -> None:
        d = self.engine.decide("T-001", "用户数据如何处理？")
        assert d.type == DecisionType.BLOCKED

    def test_scope_change(self) -> None:
        d = self.engine.decide("T-001", "需要新增额外功能吗？")
        assert d.type == DecisionType.BLOCKED

    def test_architecture(self) -> None:
        d = self.engine.decide("T-001", "系统架构是用微服务还是单体？")
        assert d.type == DecisionType.BLOCKED


class TestFallbackDecision:
    """兜底决策测试。"""

    def setup_method(self) -> None:
        self.engine = DecisionEngine()

    def test_tech_fallback(self) -> None:
        d = self.engine.decide("T-001", "这个函数的返回值类型用什么？")
        assert d.type == DecisionType.AUTO_DECIDE

    def test_non_tech_fallback(self) -> None:
        d = self.engine.decide("T-001", "商业策略选哪个方向？")
        assert d.type == DecisionType.BLOCKED


class TestDecisionLog:
    def test_log_accumulates(self) -> None:
        engine = DecisionEngine()
        engine.decide("T-001", "变量名用什么？")
        engine.decide("T-002", "需求是什么？")
        assert len(engine.decision_log) == 2

    def test_empty_question(self) -> None:
        engine = DecisionEngine()
        d = engine.decide("T-001", "")
        assert d.type == DecisionType.AUTO_DECIDE
        assert d.confidence == 0.5


class TestAsAnswerCallback:
    def test_callback_returns_answer(self) -> None:
        engine = DecisionEngine()
        callback = engine.as_answer_callback()

        answer = callback("T-001", "文件名用什么规范？")
        assert answer is not None

    def test_callback_returns_none_for_blocked(self) -> None:
        engine = DecisionEngine()
        callback = engine.as_answer_callback()

        answer = callback("T-001", "这个需求到底是什么意思？")
        assert answer is None


class TestSampleClassification:
    """用 10 个样本问题验证正确分类率 ≥ 80%。"""

    SAMPLES = [
        # (问题, 期望类型)
        ("这个类名应该叫什么？", DecisionType.AUTO_DECIDE),
        ("日志打哪个级别？", DecisionType.AUTO_DECIDE),
        ("测试用 pytest 还是 unittest？", DecisionType.AUTO_DECIDE),
        ("默认超时设多少秒？", DecisionType.AUTO_DECIDE),
        ("文件放到 src 还是 lib 目录？", DecisionType.AUTO_DECIDE),
        ("这个需求要不要支持多语言？", DecisionType.BLOCKED),
        ("API token 放在哪里？", DecisionType.BLOCKED),
        ("用户数据要做脱敏吗？", DecisionType.BLOCKED),
        ("项目预算还够吗？", DecisionType.BLOCKED),
        ("要不要扩展到移动端？", DecisionType.BLOCKED),
    ]

    def test_classification_accuracy(self) -> None:
        engine = DecisionEngine()
        correct = 0

        for question, expected_type in self.SAMPLES:
            decision = engine.decide("T-TEST", question)
            if decision.type == expected_type:
                correct += 1

        accuracy = correct / len(self.SAMPLES)
        assert accuracy >= 0.8, f"分类正确率 {accuracy:.0%} < 80%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
