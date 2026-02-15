from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re


@dataclass
class ContextData:
    frontmatter: dict[str, str]
    body: str


class ContextManager:
    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.memory_dir = self.base_dir / ".agent" / "memory"
        self.active_context_path = self.memory_dir / "active_context.md"
        self.state_machine_path = self.memory_dir / "state_machine.md"
        self.project_decisions_path = self.memory_dir / "project_decisions.md"

    def read_context(self) -> ContextData:
        text = self.active_context_path.read_text(encoding="utf-8")
        frontmatter, body = _split_frontmatter(text)
        return ContextData(frontmatter=frontmatter, body=body)

    def update_progress(self, task_id: str, status: str, summary: str) -> None:
        status_text = status.strip().upper()
        marker = {
            "DONE": "[x] **[DONE]**",
            "PENDING": "[ ] **[PENDING]**",
            "BLOCKED": "[ ] **[BLOCKED]**",
        }.get(status_text, "[ ] **[PENDING]**")
        new_line = f"- {marker} {task_id}: {summary}"

        data = self.read_context()
        body = data.body
        section = "## 📝 任务队列 (Active Tasks)"
        idx = body.find(section)
        if idx == -1:
            if body and not body.endswith("\n"):
                body += "\n"
            body += f"\n{section}\n{new_line}\n"
        else:
            insert_at = body.find("\n", idx)
            if insert_at == -1:
                insert_at = len(body)
            body = body[: insert_at + 1] + new_line + "\n" + body[insert_at + 1 :]

        self._write_context(data.frontmatter, body)

    def save_decision(self, decision_type: str, content: str) -> None:
        now = datetime.now().strftime("%Y-%m-%d")
        entry = f"- {now} [{decision_type}] {content}\n"
        text = self.project_decisions_path.read_text(encoding="utf-8")

        section = "## 8. Runtime Decisions"
        if section not in text:
            if not text.endswith("\n"):
                text += "\n"
            text += f"\n{section}\n"
        text += entry
        self.project_decisions_path.write_text(text, encoding="utf-8")

    def update_state(self, new_state: str) -> str:
        new_state = new_state.strip().upper()
        data = self.read_context()
        old_state = data.frontmatter.get("task_status", "IDLE").strip().upper()

        self._validate_state_transition(old_state, new_state)
        data.frontmatter["task_status"] = new_state
        self._write_context(data.frontmatter, data.body)
        return f"State: {old_state} -> {new_state}"

    def record_error(self, error_type: str, root_cause: str, fix_solution: str, scope: str) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        row = f"| {today} | {error_type} | {root_cause} | {fix_solution} | {scope} |\n"
        text = self.project_decisions_path.read_text(encoding="utf-8")

        header = "| 日期 | 错误类型 | 根因分析 | 修复方案 | 影响范围 |"
        divider = "|------|---------|---------|---------|---------|"
        known_issue_section = "## 5. 已知问题 (错误模式学习)"
        if known_issue_section not in text:
            if not text.endswith("\n"):
                text += "\n"
            text += f"\n{known_issue_section}\n{header}\n{divider}\n"
        elif header not in text:
            text = text.replace(known_issue_section, f"{known_issue_section}\n{header}\n{divider}")

        text += row
        self.project_decisions_path.write_text(text, encoding="utf-8")

    def _write_context(self, frontmatter: dict[str, str], body: str) -> None:
        ordered = [f"{k}: {v}" for k, v in frontmatter.items()]
        content = "---\n" + "\n".join(ordered) + "\n---\n"
        if body and not body.startswith("\n"):
            content += "\n"
        content += body
        self.active_context_path.write_text(content, encoding="utf-8")

    def _validate_state_transition(self, old_state: str, new_state: str) -> None:
        states = _extract_states(self.state_machine_path)
        if new_state not in states:
            raise ValueError(f"Unknown state: {new_state}")

        allowed: dict[str, set[str]] = {
            "IDLE": {"DRAFTING"},
            "DRAFTING": {"CONFIRMING"},
            "REVIEWING": {"CONFIRMING"},
            "CONFIRMING": {"REVIEWING", "IDLE", "DECOMPOSING", "IMPLEMENTING"},
            "DECOMPOSING": {"CONFIRMING"},
            "IMPLEMENTING": {"BLOCKED", "IDLE"},
            "BLOCKED": {"IMPLEMENTING"},
        }
        next_states = allowed.get(old_state, set())
        if new_state not in next_states:
            raise ValueError(f"Illegal state transition: {old_state} -> {new_state}")


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text

    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, body


def _extract_states(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r"\|\s*[^|]+\|\s*([A-Z_]+)\s*\|", text))
