"""
Pattern Detector — 模式检测器 MVP (T-206)

代码提交后扫描 Git diff，识别可复用模式：
  - 与 pattern_library.md 中已知模式匹配
  - 出现 ≥ 3 次的结构自动提升为 ACTIVE 模式
  - 新的重复结构入队 pending

Usage:
    from evolution.pattern_detector import PatternDetector
    detector = PatternDetector(base_dir=".agent/memory")
    results = detector.detect_from_diff(diff_text)
    detector.add_pattern(name, category, template, files)
"""

from __future__ import annotations

import re
import subprocess
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PatternMatch:
    """模式匹配结果"""
    pattern_id: str
    pattern_name: str
    matched_file: str
    confidence: float = 0.7


@dataclass
class PatternEntry:
    """模式库条目"""
    id: str
    name: str
    category: str
    occurrences: int = 1
    confidence: float = 0.7
    files: list[str] = field(default_factory=list)
    description: str = ""
    template: str = ""
    status: str = "pending"  # pending | active | deprecated
    first_seen: str = ""

    def __post_init__(self):
        if not self.first_seen:
            self.first_seen = datetime.date.today().isoformat()
        if self.occurrences >= 3 and self.confidence >= 0.7:
            self.status = "active"


# ─── Built-in Pattern Signatures ────────────────────────────

BUILTIN_PATTERNS = [
    {
        "name": "Repository + Cache Pattern",
        "category": "data-layer",
        "keywords": ["_cache", "getWithCache", "Repository"],
        "structure_regex": r"class\s+\w+Repository.*_cache",
    },
    {
        "name": "ViewModel + Service Pattern",
        "category": "business-logic",
        "keywords": ["BaseViewModel", "locator<", "setBusy"],
        "structure_regex": r"class\s+\w+ViewModel\s+extends\s+BaseViewModel",
    },
    {
        "name": "Singleton Service Pattern",
        "category": "common",
        "keywords": ["_instance", "factory", "._internal"],
        "structure_regex": r"static\s+final\s+\w+\s+_instance|factory\s+\w+\.\w+",
    },
    {
        "name": "Builder Pattern",
        "category": "common",
        "keywords": ["Builder", ".build()", ".."],
        "structure_regex": r"class\s+\w+Builder.*build\(\)",
    },
    {
        "name": "Result/Either Pattern",
        "category": "common",
        "keywords": ["Result<", "Either<", "Failure", "Success"],
        "structure_regex": r"(Result|Either)<\w+,\s*\w+>",
    },
    {
        "name": "Dispose Pattern",
        "category": "ui-layer",
        "keywords": ["dispose", "cancel", "close", "StreamSubscription"],
        "structure_regex": r"void\s+dispose\(\)\s*\{[^}]*\.cancel\(\)|\.close\(\)",
    },
    {
        "name": "Loading State Pattern",
        "category": "ui-layer",
        "keywords": ["isLoading", "setBusy", "isBusy"],
        "structure_regex": r"(isLoading|isBusy|setBusy)\s*[=(]",
    },
]


class PatternDetector:
    """
    代码模式检测器。

    职责：
    1. 扫描 Git diff，检测匹配的已知模式
    2. 识别重复出现的新结构
    3. 出现 ≥ 3 次自动提升为 ACTIVE
    """

    PROMOTE_THRESHOLD = 3  # 最小出现次数提升为 ACTIVE

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.pattern_file = self.base_dir / "evolution" / "pattern_library.md"

    # ── Public API ──

    def get_git_diff(self, n_commits: int = 1) -> str:
        """获取最近 N 个 commit 的 diff"""
        try:
            result = subprocess.run(
                ["git", "diff", f"HEAD~{n_commits}", "HEAD"],
                capture_output=True, timeout=30,
            )
            return result.stdout.decode("utf-8", errors="replace")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return ""

    def detect_from_diff(self, diff_text: str) -> list[PatternMatch]:
        """
        从 diff 文本中检测已知模式。

        Parameters
        ----------
        diff_text : str
            Git diff 输出

        Returns
        -------
        list[PatternMatch]
            匹配到的模式列表
        """
        if not diff_text:
            return []

        matches = []

        for pattern in BUILTIN_PATTERNS:
            # 关键词匹配
            keyword_hits = sum(1 for kw in pattern["keywords"] if kw in diff_text)
            # 结构匹配
            struct_match = bool(re.search(pattern["structure_regex"], diff_text))

            if keyword_hits >= 2 or struct_match:
                # 提取涉及的文件
                files = re.findall(r"\+\+\+ b/(.+)", diff_text)
                for f in files:
                    matches.append(PatternMatch(
                        pattern_id="",  # 待分配
                        pattern_name=pattern["name"],
                        matched_file=f,
                        confidence=0.7 + (0.1 if struct_match else 0),
                    ))

        return matches

    def detect_and_update(self, diff_text: str = "") -> dict:
        """
        检测模式并更新 pattern_library.md

        Returns
        -------
        dict
            {"new_patterns": [...], "promoted": [...], "matches": [...]}
        """
        if not diff_text:
            diff_text = self.get_git_diff()

        matches = self.detect_from_diff(diff_text)
        current_patterns = self.load_patterns()

        result = {
            "new_patterns": [],
            "promoted": [],
            "matches": [m.pattern_name for m in matches],
        }

        # 统计每个模式名出现的文件
        pattern_files: dict[str, set] = {}
        for m in matches:
            if m.pattern_name not in pattern_files:
                pattern_files[m.pattern_name] = set()
            pattern_files[m.pattern_name].add(m.matched_file)

        for pname, files in pattern_files.items():
            existing = next((p for p in current_patterns if p["name"] == pname), None)

            if existing:
                # 更新出现次数
                old_count = int(existing.get("occurrences", 0))
                new_count = old_count + len(files)
                existing["occurrences"] = str(new_count)
                # 检查是否可以提升
                new_status = existing.get("status", "pending")
                if new_count >= self.PROMOTE_THRESHOLD and new_status == "pending":
                    new_status = "active"
                    existing["status"] = "active"
                    result["promoted"].append(pname)
                self._update_pattern_in_library(
                    pattern_id=existing.get("id", ""),
                    occurrences=new_count,
                    status=new_status,
                )
            else:
                # 新模式
                result["new_patterns"].append(pname)
                self.add_pattern(
                    name=pname,
                    category="common",
                    description="Auto-detected from recent git diff.",
                    files=sorted(files),
                    occurrences=len(files),
                )

        return result

    def add_pattern(
        self,
        name: str,
        category: str,
        description: str = "",
        template: str = "",
        files: list[str] | None = None,
        occurrences: int = 1,
    ) -> str:
        """手动添加一条模式"""
        patterns = self.load_patterns()
        max_id = 0
        for p in patterns:
            pid = p.get("id", "P-000")
            m = re.match(r"P-(\d+)", pid)
            if m:
                max_id = max(max_id, int(m.group(1)))

        new_id = f"P-{max_id + 1:03d}"
        status = "active" if occurrences >= self.PROMOTE_THRESHOLD else "pending"

        entry = PatternEntry(
            id=new_id,
            name=name,
            category=category,
            occurrences=occurrences,
            description=description,
            template=template,
            files=files or [],
            status=status,
        )

        self._append_pattern_to_library(entry)
        return new_id

    def load_patterns(self) -> list[dict]:
        """加载 pattern_library.md 中的模式索引"""
        if not self.pattern_file.exists():
            return []

        text = self.pattern_file.read_text(encoding="utf-8")
        patterns = []

        # 解析 Pattern Index 表
        in_table = False
        for line in text.split("\n"):
            if "| ID | Name |" in line:
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 7:
                    patterns.append({
                        "id": parts[1],
                        "name": parts[2],
                        "category": parts[3],
                        "occurrences": parts[4],
                        "confidence": parts[5],
                        "status": parts[6] if len(parts) > 6 else "active",
                    })
            elif in_table and not line.startswith("|"):
                break

        return patterns

    def suggest_reuse(self, feature_description: str) -> list[dict]:
        """
        根据功能描述，建议可复用的模式。

        Parameters
        ----------
        feature_description : str
            新功能描述

        Returns
        -------
        list[dict]
            匹配的模式列表
        """
        patterns = self.load_patterns()
        suggestions = []
        desc_lower = feature_description.lower()

        for p in patterns:
            if p.get("status") != "active":
                continue
            name_lower = p.get("name", "").lower()
            category = p.get("category", "").lower()
            # 简单关键词匹配
            if any(word in desc_lower for word in name_lower.split()):
                suggestions.append(p)
            elif category in desc_lower:
                suggestions.append(p)

        return suggestions

    # ── Private Methods ──

    def _append_pattern_to_library(self, entry: PatternEntry) -> None:
        """追加模式到 pattern_library.md"""
        if not self.pattern_file.exists():
            return

        text = self.pattern_file.read_text(encoding="utf-8")

        # 在索引表中插入新行
        new_row = (
            f"| {entry.id} | {entry.name} | {entry.category} "
            f"| {entry.occurrences} | {entry.confidence} | {entry.status} |"
        )

        # 找到索引表末尾
        lines = text.split("\n")
        insert_pos = None
        in_index = False
        for i, line in enumerate(lines):
            if "| ID | Name |" in line:
                in_index = True
                continue
            if in_index and line.startswith("|"):
                insert_pos = i
            elif in_index and not line.startswith("|"):
                break

        if insert_pos is not None:
            lines.insert(insert_pos + 1, new_row)

        # 在 Pattern Details 末尾追加详情
        detail_section = f"""
### {entry.id}: {entry.name}

**Category**: {entry.category}
**Occurrences**: {entry.occurrences}
**Confidence**: {entry.confidence}
**First Seen**: {entry.first_seen}
**Status**: {entry.status}
**Files**: {', '.join(entry.files) if entry.files else 'N/A'}

**Description**:
> {entry.description}

**Template**:
```
{entry.template}
```
"""
        # 在 "## 4." 之前插入
        detail_text = "\n".join(lines)
        marker = "## 4. 模式匹配规则"
        if marker in detail_text:
            idx = detail_text.index(marker)
            detail_text = detail_text[:idx] + detail_section + "\n---\n\n" + detail_text[idx:]
        else:
            detail_text += detail_section

        self.pattern_file.write_text(detail_text, encoding="utf-8")

    def _update_pattern_in_library(self, pattern_id: str, occurrences: int, status: str) -> None:
        """更新模式库中的出现次数和状态。"""
        if not pattern_id or not self.pattern_file.exists():
            return

        text = self.pattern_file.read_text(encoding="utf-8")
        lines = text.split("\n")

        for i, line in enumerate(lines):
            if line.startswith(f"| {pattern_id} |"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 7:
                    parts[4] = str(occurrences)
                    parts[6] = status
                    lines[i] = "| " + " | ".join(parts[1:-1]) + " |"
                break

        text = "\n".join(lines)
        text = re.sub(
            rf"(###\s+{re.escape(pattern_id)}:.*?\n\*\*Occurrences\*\*:\s*)([^\n]*)",
            rf"\g<1>{occurrences}",
            text,
            count=1,
            flags=re.DOTALL,
        )
        text = re.sub(
            rf"(###\s+{re.escape(pattern_id)}:.*?\n\*\*Status\*\*:\s*)([^\n]*)",
            rf"\g<1>{status}",
            text,
            count=1,
            flags=re.DOTALL,
        )

        self.pattern_file.write_text(text, encoding="utf-8")
