import subprocess
import tempfile
import unittest
from pathlib import Path

from tests import repo_fixture


class TestScaffolder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.fixture = Path(self.tmp.name)
        self.out_dir = self.fixture / "src"
        self.script = repo_fixture.SCRIPTS / "scaffolder.mjs"

    def scaffold(self, *args):
        cmd = ["node", str(self.script), *args, "--root", str(self.fixture)]
        return subprocess.run(cmd, cwd=self.fixture, capture_output=True, text=True)

    def test_scaffold_fullstack_web(self):
        res = self.scaffold("--preset", "fullstack-web", "--name", "MyTestApp", "--desc", "My App", "--dev", "Steve")
        self.assertEqual(res.returncode, 0, f"scaffold failed: {res.stderr}")

        self.assertTrue((self.out_dir / "App.tsx").exists())
        self.assertTrue((self.out_dir / "index.css").exists())
        self.assertTrue((self.out_dir / "components" / "Header.tsx").exists())

        app_content = (self.out_dir / "App.tsx").read_text(encoding="utf-8")
        self.assertIn("MyTestApp", app_content)
        self.assertIn('developer="Steve"', app_content)
        self.assertIn("Agent Roles", app_content)
        self.assertIn("Developer:</strong> Steve", app_content)
        header = (self.out_dir / "components" / "Header.tsx").read_text(encoding="utf-8")
        self.assertIn("developer: string;", header)

    def test_scaffold_ai_agent_app(self):
        res = self.scaffold("--preset", "ai-agent-app", "--name", "AgentFlow", "--desc", "AI Pipeline", "--dev", "Alice")
        self.assertEqual(res.returncode, 0, f"scaffold failed: {res.stderr}")

        self.assertTrue((self.out_dir / "pipeline.py").exists())
        self.assertTrue((self.out_dir / "config.py").exists())
        self.assertTrue((self.out_dir / "api.py").exists())
        config = (self.out_dir / "config.py").read_text(encoding="utf-8")
        self.assertIn('DEVELOPER = "Alice"', config)
        self.assertNotIn("DEV1", config)

    def test_scaffold_minimal(self):
        res = self.scaffold("--preset", "minimal", "--name", "LeanApp", "--desc", "Ultra Lean", "--dev", "Alice")
        self.assertEqual(res.returncode, 0, f"scaffold failed: {res.stderr}")

        self.assertTrue((self.out_dir / "app.js").exists())
        html = (self.out_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn("LeanApp", html)
        self.assertIn("Developer:", html)
        self.assertIn("Alice", html)
        self.assertIn("Starter", html)
        self.assertIn("Trigger Action", html)

    def test_no_scaffold_mentions_two_developers_or_hackathon(self):
        for preset in ["fullstack-web", "frontend-dashboard", "ai-agent-app", "minimal"]:
            with self.subTest(preset=preset):
                res = self.scaffold("--preset", preset, "--dev", "Alice")
                self.assertEqual(res.returncode, 0, res.stderr)
                for path in self.out_dir.rglob("*"):
                    if path.is_file():
                        text = path.read_text(encoding="utf-8")
                        for banned in ["Dev 1", "Dev 2", "dev1", "dev2", "DEV1", "DEV2", "Hackathon", "Pair-Programming"]:
                            self.assertNotIn(banned, text, f"{banned} in {path.name}")

    def test_root_flag_without_value_fails(self):
        res = subprocess.run(["node", str(self.script), "--root"], cwd=self.fixture, capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("--root", res.stderr)


if __name__ == "__main__":
    unittest.main()
