import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class TestScriptsEntry(unittest.TestCase):
    def test_start_reviews_script_exists(self):
        path = PROJECT_ROOT / ".agent" / "scripts" / "start-reviews.ps1"
        self.assertTrue(path.exists(), "start-reviews.ps1 should exist")

    def test_start_reviews_uses_agent_runner(self):
        path = PROJECT_ROOT / ".agent" / "scripts" / "start-reviews.ps1"
        content = path.read_text(encoding="utf-8")
        self.assertIn("agent-runner.ps1", content)
        self.assertIn("codex exec", content)


if __name__ == "__main__":
    unittest.main()
