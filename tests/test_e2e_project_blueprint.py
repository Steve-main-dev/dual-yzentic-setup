import json
import subprocess
import tempfile
import unittest

from tests import repo_fixture


class TestE2EProjectBlueprint(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.fixture = repo_fixture.make_template_repo(self.tmp.name)
        self.skills_dir = self.fixture / ".agents" / "skills"
        self.archive_dir = self.fixture / ".agents" / "skills-archive"

    def node(self, script, *args):
        cmd = ["node", str(repo_fixture.SCRIPTS / script), *args, "--root", str(self.fixture)]
        return subprocess.run(cmd, cwd=self.fixture, capture_output=True, text=True)

    def test_full_project_init_and_skill_toggle_lifecycle(self):
        # 1. Execute project init
        res = self.node(
            "init-project.mjs",
            "--preset", "fullstack-web",
            "--name", "e2e-demo-system",
            "--desc", "Fullstack AI Web App",
            "--dev1", "Alice",
            "--dev2", "Bob",
            "--non-interactive",
        )
        self.assertEqual(res.returncode, 0, f"init failed: {res.stderr}")

        # 2. Check blueprint status
        bp = json.loads((self.fixture / "project-blueprint.json").read_text(encoding="utf-8"))
        self.assertEqual(bp["status"], "initialized")
        self.assertEqual(bp["project"]["archetype"], "fullstack-web")
        self.assertEqual(bp["project"]["name"], "e2e-demo-system")

        # 3. Check active skills count
        res_list = self.node("skills-manager.mjs", "list", "--json")
        self.assertEqual(res_list.returncode, 0, res_list.stderr)
        skills_data = json.loads(res_list.stdout)
        self.assertEqual(len(skills_data["active"]), 11)
        self.assertIn("ui-ux-pro-max", skills_data["active"])
        self.assertIn("caveman", skills_data["active"])
        self.assertIn("ponytail", skills_data["active"])

        # 4. Check archived skill can be restored on demand
        self.assertIn("slides", skills_data["archived"])
        res_enable = self.node("skills-manager.mjs", "enable", "slides")
        self.assertEqual(res_enable.returncode, 0, res_enable.stderr)
        self.assertTrue((self.skills_dir / "slides").exists())
        self.assertFalse((self.archive_dir / "slides").exists())

        # 5. Check baton status works cleanly in initialized state
        res_baton = self.node("baton.mjs", "status")
        self.assertEqual(res_baton.returncode, 0, res_baton.stderr)


if __name__ == "__main__":
    unittest.main()
