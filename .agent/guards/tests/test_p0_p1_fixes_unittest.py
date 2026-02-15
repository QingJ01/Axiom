import os
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENT_DIR = PROJECT_ROOT / ".agent"
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from evolution.metrics import WorkflowMetrics
from evolution.reflection import ReflectionEngine
from evolution.orchestrator import EvolutionOrchestrator


class TestP0P1Fixes(unittest.TestCase):
    def test_reflection_pending_items_only_from_action_section(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            evo_dir = base / "evolution"
            evo_dir.mkdir(parents=True, exist_ok=True)
            (evo_dir / "reflection_log.md").write_text(
                """
## Session History

### 2026-02-14 Session: Demo

#### ⚠️ What Could Improve (待改进)
- [ ] 这不是 action

#### 🎯 Action Items (后续行动)
- [ ] 真正的 action
""".strip()
                + "\n",
                encoding="utf-8",
            )

            engine = ReflectionEngine(base_dir=base)
            pending = engine.get_pending_action_items()
            self.assertEqual(pending, ["真正的 action"])

    def test_metrics_persists_bottleneck_for_insights(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            tracker = WorkflowMetrics(base_dir=base)
            tracker.record_run(
                workflow="feature-flow",
                duration_min=12,
                success=True,
                bottleneck="io",
                notes="demo",
            )

            insight = tracker.get_insights("feature-flow")
            self.assertEqual(insight.common_bottleneck, "io")

    def test_evolve_reports_remaining_after_processing(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            evo = EvolutionOrchestrator(base_dir=base)

            state = {"pending": 1}

            class FakeQueue:
                def get_stats(self):
                    return {"pending": state["pending"], "processing": 0, "done": 0, "total": state["pending"]}

                def process_queue(self, max_items=10):
                    state["pending"] = 0
                    return ["x"]

                def cleanup(self, days=7):
                    return 0

            class FakeIndex:
                def rebuild_index(self):
                    return "ok"

            class FakeHarvester:
                def list_entries(self):
                    return []

            class FakeConfidence:
                def decay_unused(self, days=30):
                    return []

                def get_deprecated(self):
                    return []

            class FakePattern:
                def detect_and_update(self):
                    return {"matches": [], "new_patterns": [], "promoted": []}

            class FakeMetrics:
                def get_all_insights(self):
                    return {}

            class FakeReflection:
                def get_reflection_summary(self, last_n=5):
                    return "ok"

                def get_pending_action_items(self):
                    return []

            evo.learning_queue = FakeQueue()
            evo.index_mgr = FakeIndex()
            evo.harvester = FakeHarvester()
            evo.confidence = FakeConfidence()
            evo.pattern_detector = FakePattern()
            evo.metrics = FakeMetrics()
            evo.reflection = FakeReflection()

            report = evo.evolve()
            self.assertIn("- **Remaining**: 0 items", report)

    def test_setup_templates_include_required_frontmatter_keys(self):
        ps1 = (PROJECT_ROOT / "setup.ps1").read_text(encoding="utf-8")
        sh = (PROJECT_ROOT / "setup.sh").read_text(encoding="utf-8")

        self.assertIn("session_id:", ps1)
        self.assertIn("last_checkpoint:", ps1)
        self.assertIn("auto_fix_attempts:", ps1)

        self.assertIn("session_id:", sh)
        self.assertIn("last_checkpoint:", sh)
        self.assertIn("auto_fix_attempts:", sh)

    def test_analyze_error_requires_confirmation_before_destructive_rollback(self):
        flow = (PROJECT_ROOT / ".agent" / "workflows" / "analyze-error.md").read_text(encoding="utf-8")
        self.assertIn("要求用户确认", flow)

    def test_pre_commit_declares_flutter_ci_gate(self):
        sh = (PROJECT_ROOT / ".agent" / "guards" / "pre-commit").read_text(encoding="utf-8")
        ps1 = (PROJECT_ROOT / ".agent" / "guards" / "pre-commit.ps1").read_text(encoding="utf-8")

        self.assertIn("flutter analyze", sh)
        self.assertIn("flutter test", sh)
        self.assertIn("flutter analyze", ps1)
        self.assertIn("flutter test", ps1)


if __name__ == "__main__":
    unittest.main()
