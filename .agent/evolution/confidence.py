"""
Confidence Decay Engine — 置信度衰减引擎 (T-204)

管理知识条目的置信度分数：
  - 验证成功: +0.1
  - 被引用使用: +0.05
  - 导致错误/误导: -0.2
  - 30 天未使用: -0.1
  - Confidence < 0.5: 标记 deprecated

Usage:
    from evolution.confidence import ConfidenceEngine
    engine = ConfidenceEngine(base_dir=".agent/memory")
    engine.on_verified("k-001")
    engine.on_referenced("k-003")
    engine.on_misleading("k-010")
    engine.decay_unused(days=30)
"""

from __future__ import annotations

import re
import datetime
from pathlib import Path
from typing import Optional


class ConfidenceEngine:
    """
    管理知识条目的 Confidence 分数生命周期。
    
    规则:
      - on_verified():   +0.1 (上限 1.0)
      - on_referenced(): +0.05 (上限 1.0)
      - on_misleading(): -0.2 (下限 0.0)
      - decay_unused():  30 天未更新 -0.1 (下限 0.0)
      - Confidence < 0.5 → status = deprecated
    """

    VERIFY_BOOST = 0.1
    REFERENCE_BOOST = 0.05
    MISLEADING_PENALTY = -0.2
    UNUSED_DECAY = -0.1
    UNUSED_THRESHOLD_DAYS = 30
    DEPRECATION_THRESHOLD = 0.5

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.knowledge_dir = self.base_dir / "knowledge"

    # ── Public API ──

    def on_verified(self, kid: str) -> Optional[float]:
        """知识被再次验证 → Confidence +0.1"""
        return self._adjust(kid, self.VERIFY_BOOST, "verified")

    def on_referenced(self, kid: str) -> Optional[float]:
        """知识被引用使用 → Confidence +0.05"""
        return self._adjust(kid, self.REFERENCE_BOOST, "referenced")

    def on_misleading(self, kid: str) -> Optional[float]:
        """知识导致错误/误导 → Confidence -0.2"""
        return self._adjust(kid, self.MISLEADING_PENALTY, "misleading")

    def decay_unused(self, days: int = 30) -> list[dict]:
        """
        扫描所有知识条目，超过 {days} 天未更新的 → Confidence -0.1

        Returns
        -------
        list[dict]
            被衰减的条目列表 [{id, old_confidence, new_confidence, deprecated}]
        """
        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        decayed = []

        for f in self.knowledge_dir.glob("k-*.md"):
            meta = self._parse_frontmatter(f)
            if not meta:
                continue

            # 获取创建日期（作为最后活跃日期的代理）
            created_str = meta.get("created", "")
            try:
                created_date = datetime.date.fromisoformat(created_str)
            except (ValueError, TypeError):
                continue

            if created_date <= cutoff:
                old_conf = self._get_confidence(meta)
                new_conf = max(0.0, round(old_conf + self.UNUSED_DECAY, 2))
                self._set_confidence(f, new_conf)

                deprecated = new_conf < self.DEPRECATION_THRESHOLD
                decayed.append({
                    "id": meta.get("id", f.stem),
                    "old_confidence": old_conf,
                    "new_confidence": new_conf,
                    "deprecated": deprecated,
                })

        return decayed

    def get_deprecated(self) -> list[dict]:
        """获取所有 deprecated 的知识条目 (Confidence < 0.5)"""
        deprecated = []
        for f in self.knowledge_dir.glob("k-*.md"):
            meta = self._parse_frontmatter(f)
            if not meta:
                continue
            conf = self._get_confidence(meta)
            if conf < self.DEPRECATION_THRESHOLD:
                deprecated.append({
                    "id": meta.get("id", f.stem),
                    "title": meta.get("title", "?"),
                    "confidence": conf,
                    "file": str(f),
                })
        return deprecated

    def get_confidence(self, kid: str) -> Optional[float]:
        """获取指定知识条目的当前 Confidence"""
        f = self._find_file(kid)
        if not f:
            return None
        meta = self._parse_frontmatter(f)
        if not meta:
            return None
        return self._get_confidence(meta)

    # ── Private Methods ──

    def _adjust(self, kid: str, delta: float, event: str) -> Optional[float]:
        """调整 Confidence 分数"""
        f = self._find_file(kid)
        if not f:
            return None

        meta = self._parse_frontmatter(f)
        if not meta:
            return None

        old_conf = self._get_confidence(meta)
        new_conf = max(0.0, min(1.0, round(old_conf + delta, 2)))
        self._set_confidence(f, new_conf)

        return new_conf

    def _find_file(self, kid: str) -> Optional[Path]:
        """按 ID 查找知识文件"""
        files = list(self.knowledge_dir.glob(f"{kid}-*.md"))
        return files[0] if files else None

    def _get_confidence(self, meta: dict) -> float:
        """从 frontmatter 中提取 confidence"""
        conf = meta.get("confidence", "0.7")
        try:
            return float(conf)
        except (ValueError, TypeError):
            return 0.7

    def _set_confidence(self, filepath: Path, new_confidence: float) -> None:
        """更新文件中的 confidence 值"""
        text = filepath.read_text(encoding="utf-8")
        # 替换 confidence 行
        text = re.sub(
            r"(confidence:\s*)\S+",
            f"\\g<1>{new_confidence}",
            text,
            count=1,
        )
        filepath.write_text(text, encoding="utf-8")

    @staticmethod
    def _parse_frontmatter(filepath: Path) -> Optional[dict]:
        """解析 YAML Frontmatter"""
        try:
            text = filepath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return None
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            return None
        meta = {}
        for line in m.group(1).strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        return meta
