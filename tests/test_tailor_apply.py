import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.tailor_fixture import SCRIPTS, VALID_PROJECT, make_repo, skill_dirs


def tailor(root, *flags):
    cmd = ["node", str(SCRIPTS / "tailor.mjs"), "--root", str(root), *flags]
    return subprocess.run(cmd, capture_output=True, text=True)


def snapshot(root):
    root = Path(root)
    files = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    dirs = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_dir()}
    return files, dirs


class TestTailorApply(unittest.TestCase):
    def repo(self, project=None, status="uninitialized"):
        tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(tmp.cleanup)
        return make_repo(tmp.name, project=project, status=status)

    def read_json(self, root, relative):
        return json.loads((root / relative).read_text(encoding="utf-8"))

    def test_applies_manifest(self):
        root = self.repo()
        res = tailor(root)
        self.assertEqual(res.returncode, 0, res.stderr)

        self.assertEqual(
            skill_dirs(root) - {"_staging"},
            {"alpha", "gamma", "tailor-setup", "fast-track", "caveman", "ponytail"},
        )
        self.assertEqual(skill_dirs(root, "skills-archive"), {"beta"})

        plan = (root / "docs" / "PLAN.md").read_text(encoding="utf-8")
        self.assertIn("Task 1.1: Canvas shell", plan)
        self.assertIn("**Owner:** Steve", plan)
        self.assertIn("**Owner:** Bob", plan)
        self.assertNotIn("ORIGINAL PLAN", plan)

        package = self.read_json(root, "package.json")
        self.assertEqual(package["name"], "ai-flow-canvas")
        self.assertEqual(package["description"], VALID_PROJECT["description"])
        self.assertEqual(package["scripts"], {"tailor": "node scripts/tailor.mjs"})

        handoff = self.read_json(root, ".agents/sync/handoff.json")
        self.assertEqual(handoff["task_id"], "INIT-01")
        self.assertEqual(handoff["status"], "idle")
        self.assertEqual(handoff["turn_count"], 0)

        blueprint = self.read_json(root, "project-blueprint.json")
        self.assertEqual(blueprint["status"], "initialized")
        self.assertEqual(blueprint["project"], VALID_PROJECT)
        self.assertIn("archetypes", blueprint)

    def test_dry_run_writes_nothing(self):
        root = self.repo()
        before = snapshot(root)

        res = tailor(root, "--dry-run")

        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(snapshot(root), before)
        self.assertIn("[Tailor] archive: beta", res.stdout)
        self.assertIn("[Tailor] restore: gamma", res.stdout)
        self.assertIn("Dry run", res.stdout)

    def test_invalid_manifest_changes_nothing(self):
        project = copy.deepcopy(VALID_PROJECT)
        project["skills"] = ["nope"]
        project["roadmap"][0]["priority"] = "P3"
        root = self.repo(project=project)
        before = snapshot(root)

        res = tailor(root)

        self.assertEqual(res.returncode, 1)
        self.assertIn("project.skills", res.stderr)
        self.assertIn("project.roadmap[0].priority", res.stderr)
        self.assertEqual(snapshot(root), before)

    def test_refuses_initialized_without_force(self):
        root = self.repo(status="initialized")
        before = snapshot(root)

        res = tailor(root)
        self.assertEqual(res.returncode, 1)
        self.assertIn("--force", res.stderr)
        self.assertEqual(snapshot(root), before)

        res = tailor(root, "--force")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Task 1.1: Canvas shell", (root / "docs" / "PLAN.md").read_text(encoding="utf-8"))

    def test_unparseable_blueprint(self):
        root = self.repo()
        (root / "project-blueprint.json").write_text("{not json", encoding="utf-8")

        res = tailor(root)

        self.assertEqual(res.returncode, 1)
        self.assertIn("project-blueprint.json", res.stderr)
        self.assertNotIn("    at ", res.stderr)

    def test_duplicate_skills_apply_once(self):
        project = copy.deepcopy(VALID_PROJECT)
        project["skills"] = ["alpha", "alpha", "caveman"]
        root = self.repo(project=project)

        res = tailor(root)

        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("alpha", skill_dirs(root))
        self.assertIn("gamma", skill_dirs(root, "skills-archive"))

    def test_no_git_dir_skips_hook(self):
        root = self.repo()
        res = tailor(root)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertFalse((root / ".githooks").exists())


if __name__ == "__main__":
    unittest.main()
