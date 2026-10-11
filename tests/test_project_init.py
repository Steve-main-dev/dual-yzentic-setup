import json
import subprocess
import tempfile
import unittest

from tests import repo_fixture


class TestProjectInit(unittest.TestCase):
    def setUp(self):
        self.script = repo_fixture.SCRIPTS / "init-project.mjs"
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.fixture = repo_fixture.make_template_repo(self.tmp.name)

    def run_init(self, *args):
        cmd = ["node", str(self.script), *args, "--non-interactive", "--root", str(self.fixture)]
        return subprocess.run(cmd, cwd=self.fixture, capture_output=True, text=True)

    def test_invalid_preset_fails_gracefully(self):
        res = self.run_init("--preset", "nonexistent-preset")
        self.assertEqual(res.returncode, 1)
        self.assertIn("not found", res.stderr.lower())

    def test_non_interactive_init_execution(self):
        res = self.run_init(
            "--preset", "minimal-hackathon",
            "--name", "demo-ai-hack",
            "--desc", "AI Hackathon Demo Project",
            "--dev1", "Steve",
            "--dev2", "Bob",
        )
        self.assertEqual(res.returncode, 0, f"init-project failed: {res.stderr}")

        # 1. Blueprint status updated
        blueprint = json.loads((self.fixture / "project-blueprint.json").read_text(encoding="utf-8"))
        self.assertEqual(blueprint["status"], "initialized")
        self.assertEqual(blueprint["project"]["name"], "demo-ai-hack")
        self.assertEqual(blueprint["project"]["team"]["dev1"]["name"], "Steve")

        # 2. Package.json updated
        pkg = json.loads((self.fixture / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg["name"], "demo-ai-hack")
        self.assertEqual(pkg["description"], "AI Hackathon Demo Project")

        # 3. PLAN.md updated
        plan_content = (self.fixture / "docs" / "PLAN.md").read_text(encoding="utf-8")
        self.assertIn("demo-ai-hack", plan_content)
        self.assertIn("Steve", plan_content)
        self.assertIn("Bob", plan_content)

        # 4. Handoff reset
        handoff = json.loads((self.fixture / ".agents" / "sync" / "handoff.json").read_text(encoding="utf-8"))
        self.assertEqual(handoff["status"], "idle")
        self.assertEqual(handoff["turn_count"], 0)

        # 5. No git repo in the fixture, so no hook was installed
        self.assertFalse((self.fixture / ".githooks").exists())

    def test_root_flag_without_value_fails(self):
        cmd = ["node", str(self.script), "--preset", "minimal-hackathon", "--non-interactive", "--root"]
        res = subprocess.run(cmd, cwd=self.fixture, capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("--root", res.stderr)


if __name__ == "__main__":
    unittest.main()
