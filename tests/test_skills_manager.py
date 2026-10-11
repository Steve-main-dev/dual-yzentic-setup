import json
import subprocess
import tempfile
import unittest

from tests import repo_fixture


class TestSkillsManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.fixture = repo_fixture.make_template_repo(self.tmp.name)
        self.skills_dir = self.fixture / ".agents" / "skills"
        self.archive_dir = self.fixture / ".agents" / "skills-archive"
        self.script = repo_fixture.SCRIPTS / "skills-manager.mjs"

    def manage(self, *args):
        cmd = ["node", str(self.script), *args, "--root", str(self.fixture)]
        return subprocess.run(cmd, cwd=self.fixture, capture_output=True, text=True)

    def test_skills_manager_list_command(self):
        res = self.manage("list", "--json")
        self.assertEqual(res.returncode, 0, f"skills-manager list failed: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertIn("active", data)
        self.assertIn("archived", data)
        self.assertIsInstance(data["active"], list)
        self.assertIsInstance(data["archived"], list)

    def test_disable_and_enable_skill_roundtrip(self):
        test_skill = self.skills_dir / "_test_dummy_skill"
        test_skill.mkdir(parents=True)
        (test_skill / "SKILL.md").write_text("---\nname: _test_dummy_skill\ndescription: dummy test\n---\n", encoding="utf-8")

        # Disable
        res = self.manage("disable", "_test_dummy_skill")
        self.assertEqual(res.returncode, 0, f"disable failed: {res.stderr}")
        self.assertFalse((self.skills_dir / "_test_dummy_skill").exists())
        self.assertTrue((self.archive_dir / "_test_dummy_skill").exists())

        # Enable
        res = self.manage("enable", "_test_dummy_skill")
        self.assertEqual(res.returncode, 0, f"enable failed: {res.stderr}")
        self.assertTrue((self.skills_dir / "_test_dummy_skill").exists())
        self.assertFalse((self.archive_dir / "_test_dummy_skill").exists())

    def test_root_flag_without_value_fails(self):
        res = subprocess.run(["node", str(self.script), "list", "--root"], cwd=self.fixture, capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("--root", res.stderr)


if __name__ == "__main__":
    unittest.main()
