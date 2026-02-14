"""
restart_injector.py — 重启注入机制 (T-103)

检测 Worker 提问 → 终止进程 → 追加答案到 Prompt → 重启。
同一任务最多 3 次重启。

核心流程:
    1. Worker 通过 JSONL 提出问题
    2. PM (决策引擎) 生成回答
    3. RestartInjector 构建新 Prompt (原始 + 所有 QA 对)
    4. 终止旧 Worker → 启动新 Worker
    5. 超过 MAX_RESTARTS 次则标记 BLOCKED

支持特性:
    - 增量 Prompt 压缩（避免 Token 爆炸）
    - QA 历史追踪
    - 风险操作检测（拒绝注入）
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .core import JSONLEvent, TaskSpec, TaskStatus, WorkerResult
from .jsonl_parser import JSONLParser
from .worker import Worker, WorkerConfig

logger = logging.getLogger(__name__)

# 最大 Prompt 字符数（约 4000 token ≈ 16000 字符，中文 ≈ 1 token/字）
MAX_PROMPT_CHARS = 16000
# 压缩后保留的字符数
COMPRESSED_PROMPT_CHARS = 8000
# 风险操作关键词
RISK_KEYWORDS = [
    "删除数据库", "drop database", "rm -rf", "format",
    "生产环境", "production", "密钥", "secret", "password",
    "支付", "payment", "transfer",
]


@dataclass
class QAPair:
    """一组问答对。"""
    question: str
    answer: str
    restart_index: int  # 第几次重启时产生的


@dataclass
class InjectionContext:
    """单个任务的注入上下文。"""
    task_id: str
    original_prompt: str
    qa_pairs: list[QAPair] = field(default_factory=list)
    restart_count: int = 0

    @property
    def total_restarts(self) -> int:
        return self.restart_count


class RestartInjector:
    """重启注入器 — 管理 Worker 的"重启 → 注入 → 继续"循环。

    使用方式:
        injector = RestartInjector(worker, parser)
        result = injector.execute_with_injection(task, answer_func)
    """

    MAX_RESTARTS = 3

    def __init__(
        self,
        worker: Worker,
        parser: JSONLParser | None = None,
    ) -> None:
        self.worker = worker
        self.parser = parser or JSONLParser()
        self._contexts: dict[str, InjectionContext] = {}

    # ── 公开 API ────────────────────────────────────────

    def execute_with_injection(
        self,
        task: TaskSpec,
        answer_func: AnswerCallback | None = None,
        initial_prompt: str | None = None,
    ) -> WorkerResult:
        """带重启注入的任务执行。

        Args:
            task: 任务规格
            answer_func: 当 Worker 提问时，此回调负责生成答案。
                         签名: (task_id, question) -> answer | None
                         返回 None 表示无法回答，应标记 BLOCKED。
            initial_prompt: 初始 Prompt，若 None 则自动生成。

        Returns:
            WorkerResult — 最终结果（可能经过多次重启）
        """
        prompt = initial_prompt or self.worker._build_prompt(task)
        ctx = InjectionContext(task_id=task.id, original_prompt=prompt)
        self._contexts[task.id] = ctx

        while True:
            effective_prompt = self.build_injected_prompt(
                ctx.original_prompt, ctx.qa_pairs
            )

            logger.info(
                "Executing task %s (restart #%d)", task.id, ctx.restart_count
            )
            result = self.worker.execute(task, prompt=effective_prompt)
            result.restart_count = ctx.restart_count

            # 没有问题或任务已完成 → 直接返回
            if not result.has_questions:
                return result

            # 检查重启次数
            if not self.should_restart(task.id, result.questions[0]):
                logger.warning(
                    "Task %s exceeded max restarts (%d) or hit risk keyword",
                    task.id, self.MAX_RESTARTS,
                )
                result.error_message = (
                    f"Exceeded max restarts ({self.MAX_RESTARTS}) "
                    f"or risk keyword detected"
                )
                return result

            # 获取答案
            question = result.questions[0]
            answer: str | None = None

            if answer_func:
                answer = answer_func(task.id, question)

            if answer is None:
                logger.info("Task %s: no answer for question, marking BLOCKED", task.id)
                result.success = False
                result.error_message = f"BLOCKED: Unanswered question: {question[:100]}"
                return result

            # 记录 QA 对并重启
            ctx.qa_pairs.append(
                QAPair(
                    question=question,
                    answer=answer,
                    restart_index=ctx.restart_count,
                )
            )
            ctx.restart_count += 1

            logger.info(
                "Task %s: injecting answer for restart #%d",
                task.id, ctx.restart_count,
            )

    def should_restart(self, task_id: str, question: str) -> bool:
        """判断是否应该重启。

        条件:
            1. 未超过重启次数上限 (MAX_RESTARTS)
            2. 问题不涉及风险操作

        Args:
            task_id: 任务 ID
            question: Worker 提出的问题

        Returns:
            True 如果可以重启
        """
        ctx = self._contexts.get(task_id)
        if not ctx:
            return True  # 首次，允许

        if ctx.restart_count >= self.MAX_RESTARTS:
            return False

        if self._is_risk_question(question):
            logger.warning("Risk keyword detected in question: %s", question[:80])
            return False

        return True

    def build_injected_prompt(
        self,
        original_prompt: str,
        qa_pairs: list[QAPair],
    ) -> str:
        """在原始 Prompt 尾部追加所有 Q&A 对。

        格式:
            ---
            [补充信息 1] 关于 "Q1"，答案是: A1
            [补充信息 2] 关于 "Q2"，答案是: A2

        Args:
            original_prompt: 原始 Prompt
            qa_pairs: 历史 QA 对列表

        Returns:
            注入答案后的新 Prompt
        """
        if not qa_pairs:
            return original_prompt

        injections = ["\n\n---\n## 补充信息（由 PM 自动注入）\n"]
        for i, qa in enumerate(qa_pairs, 1):
            injections.append(
                f"[补充信息 {i}] 关于 \"{qa.question[:200]}\"，答案是:\n"
                f"{qa.answer}\n"
            )

        combined = original_prompt + "\n".join(injections)

        # 压缩检查
        if len(combined) > MAX_PROMPT_CHARS:
            combined = self.compress_context(combined)

        return combined

    def compress_context(self, prompt: str) -> str:
        """增量压缩: 如果 Prompt 超过阈值，保留头部指令 + 尾部 QA。

        策略:
            - 保留前 2000 字符（任务描述）
            - 保留后 COMPRESSED_PROMPT_CHARS 字符（最新 QA）
            - 中间用 "[... 上下文已压缩 ...]" 标记

        Args:
            prompt: 待压缩的 Prompt

        Returns:
            压缩后的 Prompt
        """
        if len(prompt) <= MAX_PROMPT_CHARS:
            return prompt

        head_size = 2000
        tail_size = COMPRESSED_PROMPT_CHARS
        head = prompt[:head_size]
        tail = prompt[-tail_size:]

        compressed = (
            f"{head}\n\n"
            f"[... 上下文已压缩，保留最新 {tail_size} 字符 ...]\n\n"
            f"{tail}"
        )
        logger.info(
            "Prompt compressed: %d → %d chars", len(prompt), len(compressed)
        )
        return compressed

    def get_context(self, task_id: str) -> InjectionContext | None:
        """获取任务的注入上下文。"""
        return self._contexts.get(task_id)

    # ── 内部方法 ────────────────────────────────────────

    def _is_risk_question(self, question: str) -> bool:
        """检测问题是否涉及风险操作。"""
        lower = question.lower()
        return any(kw.lower() in lower for kw in RISK_KEYWORDS)


# 类型别名
AnswerCallback = callable  # (task_id: str, question: str) -> str | None
