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
        res = self.scaffold("--preset", "fullstack-web", "--name", "MyTestApp", "--desc", "My App Pitch", "--dev1", "Steve", "--dev2", "Bob")
        self.assertEqual(res.returncode, 0, f"scaffold failed: {res.stderr}")

        self.assertTrue((self.out_dir / "App.tsx").exists())
        self.assertTrue((self.out_dir / "index.css").exists())
        self.assertTrue((self.out_dir / "components" / "Header.tsx").exists())

        app_content = (self.out_dir / "App.tsx").read_text(encoding="utf-8")
        self.assertIn("MyTestApp", app_content)
        self.assertIn("Steve", app_content)

    def test_scaffold_ai_agent_app(self):
        res = self.scaffold("--preset", "ai-agent-app", "--name", "AgentFlow", "--desc", "AI Pipeline", "--dev1", "Alice", "--dev2", "Bob")
        self.assertEqual(res.returncode, 0, f"scaffold failed: {res.stderr}")

        self.assertTrue((self.out_dir / "pipeline.py").exists())
        self.assertTrue((self.out_dir / "config.py").exists())
        self.assertTrue((self.out_dir / "api.py").exists())

    def test_scaffold_minimal_hackathon(self):
        res = self.scaffold("--preset", "minimal-hackathon", "--name", "SpeedDemo", "--desc", "Ultra Lean", "--dev1", "Alice", "--dev2", "Bob")
        self.assertEqual(res.returncode, 0, f"scaffold failed: {res.stderr}")

        self.assertTrue((self.out_dir / "index.html").exists())
        self.assertTrue((self.out_dir / "app.js").exists())

    def test_root_flag_without_value_fails(self):
        res = subprocess.run(["node", str(self.script), "--root"], cwd=self.fixture, capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("--root", res.stderr)


if __name__ == "__main__":
    unittest.main()
