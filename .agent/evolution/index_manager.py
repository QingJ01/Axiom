"""
Knowledge Index Manager — 知识索引系统 (T-202)

管理 knowledge_base.md 的 CRUD：
  - 添加/更新/删除索引条目
  - 自动更新分类统计
  - 自动更新标签云

Usage:
    from evolution.index_manager import KnowledgeIndexManager
    mgr = KnowledgeIndexManager(base_dir=".agent/memory")
    mgr.add_to_index(entry)
    mgr.rebuild_index()
"""

from __future__ import annotations

import re
import datetime
from pathlib import Path
from typing import Optional


class KnowledgeIndexManager:
    """
    管理 knowledge_base.md 索引文件。

    核心职责：
    - 维护索引表 (ID / Title / Category / Confidence / Created / Status)
    - 维护分类统计
    - 维护标签云
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.knowledge_dir = self.base_dir / "knowledge"
        self.index_file = self.base_dir / "evolution" / "knowledge_base.md"

    def rebuild_index(self) -> str:
        """
        从 knowledge/ 目录中扫描所有知识条目，
        重建 knowledge_base.md 索引文件。

        Returns
        -------
        str
            重建后的 knowledge_base.md 内容
        """
        entries = self._scan_knowledge_entries()
        content = self._generate_index(entries)
        self.index_file.write_text(content, encoding="utf-8")
        return content

    def add_to_index(self, kid: str, title: str, category: str,
                     confidence: float, created: str, status: str = "active") -> None:
        """增量添加一条索引记录（如果文件存在则追加，不存在则重建）"""
        if not self.index_file.exists():
            self.rebuild_index()
            return

        # 读取当前索引
        text = self.index_file.read_text(encoding="utf-8")

        # 检查是否已存在
        if f"| {kid} |" in text:
            # 更新现有行
            text = self._update_index_row(text, kid, title, category, confidence, created, status)
        else:
            # 在索引表末尾插入新行
            new_row = f"| {kid} | {title} | {category} | {confidence} | {created} | {status} |"
            text = self._insert_index_row(text, new_row)

        # 重新计算统计和标签
        entries = self._scan_knowledge_entries()
        text = self._update_category_stats(text, entries)
        text = self._update_tag_cloud(text, entries)

        self.index_file.write_text(text, encoding="utf-8")

    def remove_from_index(self, kid: str) -> None:
        """从索引中移除一条记录"""
        if not self.index_file.exists():
            return
        text = self.index_file.read_text(encoding="utf-8")
        # 删除包含 kid 的行
        lines = text.split("\n")
        lines = [l for l in lines if f"| {kid} |" not in l]
        text = "\n".join(lines)
        self.index_file.write_text(text, encoding="utf-8")

    def update_confidence(self, kid: str, new_confidence: float) -> None:
        """更新指定知识条目的 Confidence"""
        if not self.index_file.exists():
            return
        text = self.index_file.read_text(encoding="utf-8")
        # 查找并更新该行
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if f"| {kid} |" in line:
                parts = [p.strip() for p in line.split("|")]
                # parts: ['', kid, title, category, confidence, created, status, '']
                if len(parts) >= 7:
                    parts[4] = str(round(new_confidence, 2))
                    lines[i] = "| " + " | ".join(p for p in parts[1:-1]) + " |"
                break
        self.index_file.write_text("\n".join(lines), encoding="utf-8")

    # ── Private Methods ──

    def _scan_knowledge_entries(self) -> list[dict]:
        """扫描 knowledge/ 目录，解析所有知识条目"""
        entries = []
        if not self.knowledge_dir.exists():
            return entries

        for f in sorted(self.knowledge_dir.glob("k-*.md")):
            meta = self._parse_frontmatter(f)
            if meta:
                entries.append(meta)
        return entries

    def _generate_index(self, entries: list[dict]) -> str:
        """生成完整的 knowledge_base.md"""
        today = datetime.date.today().isoformat()

        # Header
        lines = [
            "---",
            "description: 知识图谱索引 - 管理所有知识条目的元信息",
            "version: 1.0",
            f"last_updated: {today}",
            "---",
            "",
            "# Knowledge Base (知识图谱索引)",
            "",
            "本文件是知识系统的中央索引，记录所有知识条目的元信息。",
            "",
            "## 1. 索引表 (Knowledge Index)",
            "",
            "| ID | Title | Category | Confidence | Created | Status |",
            "|----|-------|----------|------------|---------|--------|",
        ]

        for e in entries:
            kid = e.get("id", "?")
            title = e.get("title", "?")
            cat = e.get("category", "?")
            conf = e.get("confidence", "0.7")
            created = e.get("created", "?")
            status = "active"
            # Check deprecation
            if isinstance(conf, str):
                try:
                    conf_val = float(conf)
                except ValueError:
                    conf_val = 0.7
            else:
                conf_val = conf
            if conf_val < 0.5:
                status = "deprecated"
            lines.append(f"| {kid} | {title} | {cat} | {conf} | {created} | {status} |")

        # Category Stats
        lines += [
            "",
            "## 2. 分类统计 (Category Stats)",
            "",
            "| Category | Count | Description |",
            "|----------|-------|-------------|",
        ]
        cat_counts = {}
        cat_desc = {
            "architecture": "架构相关知识",
            "debugging": "调试技巧",
            "pattern": "代码模式",
            "workflow": "工作流相关",
            "tooling": "工具使用",
        }
        for e in entries:
            cat = e.get("category", "other")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        for cat in ["architecture", "debugging", "pattern", "workflow", "tooling"]:
            count = cat_counts.get(cat, 0)
            desc = cat_desc.get(cat, "其他")
            lines.append(f"| {cat} | {count} | {desc} |")

        # Tag Cloud
        lines += [
            "",
            "",
            "## 3. 标签云 (Tag Cloud)",
            "",
            "> 使用频率: (tag: count)",
            "",
        ]
        tag_counts: dict[str, int] = {}
        for e in entries:
            tags = e.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            for t in tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            lines.append(f"- {tag}: {count}")
        if not tag_counts:
            lines.append("- (暂无标签)")

        # Quality Management
        lines += [
            "",
            "## 4. 知识质量管理",
            "",
            "### 4.1 Confidence 分数说明",
            "- `0.9+`: 高置信度，经过多次验证",
            "- `0.7-0.9`: 中等置信度，单次成功经验",
            "- `0.5-0.7`: 低置信度，需要更多验证",
            "- `<0.5`: 待清理，可能已过时",
            "",
            "### 4.2 清理规则",
            "- Confidence < 0.5 且超过 30 天未使用 → 标记为 `deprecated`",
            "",
        ]

        return "\n".join(lines)

    def _insert_index_row(self, text: str, row: str) -> str:
        """在索引表末尾插入一行"""
        lines = text.split("\n")
        # 找到索引表的最后一行 (以 | 开头且包含 k-)
        insert_pos = None
        in_index = False
        for i, line in enumerate(lines):
            if "| ID | Title |" in line:
                in_index = True
                continue
            if in_index and line.startswith("|"):
                insert_pos = i
            elif in_index and not line.startswith("|"):
                break
        if insert_pos is not None:
            lines.insert(insert_pos + 1, row)
        else:
            # 没找到索引表，追加到文件末
            lines.append(row)
        return "\n".join(lines)

    def _update_index_row(self, text: str, kid: str, title: str,
                          category: str, confidence: float, created: str, status: str) -> str:
        """更新已存在的索引行"""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if f"| {kid} |" in line:
                lines[i] = f"| {kid} | {title} | {category} | {confidence} | {created} | {status} |"
                break
        return "\n".join(lines)

    def _update_category_stats(self, text: str, entries: list[dict]) -> str:
        """更新分类统计区段"""
        cat_counts: dict[str, int] = {}
        for e in entries:
            cat = e.get("category", "other")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        cat_desc = {
            "architecture": "架构相关知识",
            "debugging": "调试技巧",
            "pattern": "代码模式",
            "workflow": "工作流相关",
            "tooling": "工具使用",
        }
        new_rows = []
        for cat in ["architecture", "debugging", "pattern", "workflow", "tooling"]:
            count = cat_counts.get(cat, 0)
            desc = cat_desc.get(cat, "其他")
            new_rows.append(f"| {cat} | {count} | {desc} |")

        # Replace old category stats block
        lines = text.split("\n")
        start = None
        end = None
        in_cat = False
        for i, line in enumerate(lines):
            if "| Category | Count |" in line:
                in_cat = True
                start = i + 2  # skip header + separator
                continue
            if in_cat and line.startswith("|"):
                end = i
            elif in_cat and not line.startswith("|"):
                break

        if start is not None and end is not None:
            lines[start:end + 1] = new_rows
        return "\n".join(lines)

    def _update_tag_cloud(self, text: str, entries: list[dict]) -> str:
        """更新标签云区段"""
        tag_counts: dict[str, int] = {}
        for e in entries:
            tags = e.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            for t in tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1

        new_lines = ["> 使用频率: (tag: count)", ""]
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            new_lines.append(f"- {tag}: {count}")
        if not tag_counts:
            new_lines.append("- (暂无标签)")

        # Replace old tag cloud block
        lines = text.split("\n")
        start = None
        end = None
        in_tags = False
        for i, line in enumerate(lines):
            if "## 3. 标签云" in line:
                in_tags = True
                start = i + 2  # skip header + blank line
                continue
            if in_tags and (line.startswith("## ") or line.startswith("# ")):
                end = i - 1
                break
            if in_tags:
                end = i

        if start is not None and end is not None:
            lines[start:end + 1] = new_lines
        return "\n".join(lines)

    @staticmethod
    def _parse_frontmatter(filepath: Path) -> Optional[dict]:
        """解析 YAML Frontmatter"""
        text = filepath.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            return None
        meta = {}
        for line in m.group(1).strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if val.startswith("[") and val.endswith("]"):
                    val = [v.strip() for v in val[1:-1].split(",") if v.strip()]
                meta[key] = val
        meta["_file"] = str(filepath)
        return meta
