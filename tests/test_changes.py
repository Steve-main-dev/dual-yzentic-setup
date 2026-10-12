import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests import repo_fixture


class TestChanges(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, text=True)

    def write(self, rel, text="x\n"):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def commit_all(self, message="change"):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def fixture(self):
        self.write("README.md", "# fixture\n")
        repo_fixture.git_init(self.root)

    def call(self, expression):
        code = f"""
        import * as changes from './scripts/changes.mjs';
        const root = {json.dumps(str(self.root))};
        console.log(JSON.stringify({expression}));
        """
        res = repo_fixture.run_node(code)
        self.assertEqual(res.returncode, 0, res.stderr)
        return json.loads(res.stdout.strip())

    def test_cosmetic_classification(self):
        code = """
        import { isCosmeticFile } from './scripts/changes.mjs';
        console.log(JSON.stringify(['README.md', 'src/App.CSS', 'logo.png', 'docs/notes.txt', 'src/app.js', 'package.json'].map(isCosmeticFile)));
        """
        res = repo_fixture.run_node(code)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout.strip()), [True, True, True, True, False, False])

    def test_untracked_files_in_new_directory_are_listed_individually(self):
        self.fixture()
        self.write("src/ui/a.js")
        self.write("src/ui/b.js")
        files = self.call("changes.getUncommittedFiles(root)")
        self.assertEqual(sorted(files), ["src/ui/a.js", "src/ui/b.js"])

    def test_path_with_space_is_returned_unquoted(self):
        self.fixture()
        self.write("src/my file.js")
        self.assertEqual(self.call("changes.getUncommittedFiles(root)"), ["src/my file.js"])

    def test_rename_reports_the_new_path(self):
        self.write("src/old.js")
        repo_fixture.git_init(self.root)
        self.git("mv", "src/old.js", "src/new.js")
        self.assertEqual(self.call("changes.getUncommittedFiles(root)"), ["src/new.js"])

    def test_clean_tree_after_code_commit_resolves_to_last_commit(self):
        self.fixture()
        self.write("src/app.js")
        self.commit_all("add app")
        self.assertEqual(self.call("changes.getUncommittedFiles(root)"), [])
        self.assertEqual(self.call("changes.getLastCommitFiles(root)"), ["src/app.js"])
        self.assertEqual(self.call("changes.resolveChangeSet(root)"), {"files": ["src/app.js"], "source": "last-commit"})

    def test_dirty_tree_resolves_to_working_tree(self):
        self.fixture()
        self.write("src/app.js")
        self.assertEqual(self.call("changes.resolveChangeSet(root)"), {"files": ["src/app.js"], "source": "working-tree"})

    def test_repo_without_commits_resolves_to_none(self):
        self.git("init", "-q")
        self.assertEqual(self.call("changes.getLastCommitFiles(root)"), [])
        self.assertEqual(self.call("changes.resolveChangeSet(root)"), {"files": [], "source": "none"})

    def test_test_file_patterns(self):
        paths = {
            "tests/helper.js": True,
            "test/helper.js": True,
            "src/__tests__/a.js": True,
            "test_add.py": True,
            "src/test_add.py": True,
            "src/add_test.go": True,
            "src/app.test.js": True,
            "src/app.spec.ts": True,
            "src/app.js": False,
            "src/latest.js": False,
            "src/testing/app.js": False,
            "src/contest.py": False,
            "tests": False,
            "e2e/login.spec.ts": True,
            "e2e/helpers/auth.js": True,
        }
        flags = self.call(f"{json.dumps(list(paths))}.map(changes.isTestFile)")
        self.assertEqual(flags, list(paths.values()))

    def test_source_file_classification(self):
        paths = {
            "src/app.js": True,
            "config/settings.py": True,  # the directory name does not start with a dot
            "lib/package.json.js": True,
            "tests/app.test.js": False,
            "README.md": False,
            "docs/notes.txt": False,
            "styles/site.css": False,
            ".agents/skills/x/SKILL.md": False,
            ".agents/sync/handoff.json": False,
        }
        flags = self.call(f"{json.dumps(list(paths))}.map(changes.isSourceFile)")
        self.assertEqual(flags, list(paths.values()))

    def test_configuration_is_not_source(self):
        paths = [
            ".claude/settings.json",
            ".githooks/pre-commit",
            ".github/workflows/ci.yml",
            ".gitignore",
            ".env.example",
            "src/.eslintrc.js",
            "package.json",
            "web/package.json",
            "project-blueprint.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "bun.lockb",
            "uv.lock",
            "poetry.lock",
            "Cargo.lock",
            "go.sum",
            "app/yarn.lock",
        ]
        self.assertEqual(self.call(f"{json.dumps(paths)}.map(changes.isSourceFile)"), [False] * len(paths))

    def test_snapshot_hashes_changed_files_and_maps_a_deletion_to_null(self):
        self.write("src/app.js")
        self.write("src/gone.js")
        repo_fixture.git_init(self.root)
        self.write("src/app.js", "changed\n")
        self.write("src/new.js")
        self.root.joinpath("src", "gone.js").unlink()
        snapshot = self.call("Object.fromEntries(changes.snapshotChanges(root))")
        self.assertEqual(sorted(snapshot), ["src/app.js", "src/gone.js", "src/new.js"])
        self.assertIsNone(snapshot["src/gone.js"])
        self.assertRegex(snapshot["src/app.js"], r"^[0-9a-f]{40}$")
        self.assertNotEqual(snapshot["src/app.js"], snapshot["src/new.js"])

    def test_fingerprint_is_stable_and_follows_content_new_files_and_head(self):
        self.fixture()
        self.write("src/app.js", "one\n")
        first = self.call("changes.fingerprintChanges(root)")
        self.assertRegex(first, r"^[0-9a-f]{40}$")
        self.assertEqual(self.call("changes.fingerprintChanges(root)"), first)
        self.write("src/app.js", "two\n")
        edited = self.call("changes.fingerprintChanges(root)")
        self.assertNotEqual(edited, first)
        self.write("src/other.js", "x\n")
        added = self.call("changes.fingerprintChanges(root)")
        self.assertNotEqual(added, edited)
        self.commit_all("add")
        clean_one = self.call("changes.fingerprintChanges(root)")
        self.git("commit", "-q", "--allow-empty", "-m", "empty")
        self.assertNotEqual(self.call("changes.fingerprintChanges(root)"), clean_one)

    def scope(self, before, after, allow_edits):
        return self.call(
            f"changes.checkScope(new Map(Object.entries({json.dumps(before)})), "
            f"new Map(Object.entries({json.dumps(after)})), {{ allowEdits: {json.dumps(allow_edits)} }})"
        )

    def test_read_only_scope_rejects_any_change(self):
        result = self.scope({"src/app.js": "h1"}, {"src/app.js": "h1", "tests/new.test.js": "h2"}, False)
        self.assertEqual(result, {"testsWritten": [], "outOfScope": ["tests/new.test.js"]})

    def test_edit_scope_splits_tests_from_source(self):
        after = {"tests/new.test.js": "h1", "src/rogue.js": "h2", "tests/old.test.js": "h4"}
        result = self.scope({"tests/old.test.js": "h3"}, after, True)
        self.assertEqual(result, {"testsWritten": ["tests/new.test.js", "tests/old.test.js"], "outOfScope": ["src/rogue.js"]})

    def test_unchanged_paths_are_in_scope(self):
        state = {"src/app.js": "h1", "tests/a.test.js": "h2", "src/gone.js": None}
        self.assertEqual(self.scope(state, state, True), {"testsWritten": [], "outOfScope": []})

    def test_a_path_missing_from_after_is_out_of_scope_in_both_modes(self):
        before = {"src/new.js": "h1", "tests/old.test.js": "h2"}
        for allow_edits in (False, True):
            with self.subTest(allow_edits=allow_edits):
                result = self.scope(before, {}, allow_edits)
                self.assertEqual(result, {"testsWritten": [], "outOfScope": ["src/new.js", "tests/old.test.js"]})

    def disappearance(self, vanish):
        """checkScope over a real repo: `vanish` runs in the fixture between the two snapshots."""
        code = f"""
        import * as changes from './scripts/changes.mjs';
        import {{ rmSync, writeFileSync }} from 'node:fs';
        const root = {json.dumps(str(self.root))};
        const before = changes.snapshotChanges(root);
        {vanish}
        console.log(JSON.stringify(changes.checkScope(before, changes.snapshotChanges(root), {{ allowEdits: true }})));
        """
        res = repo_fixture.run_node(code)
        self.assertEqual(res.returncode, 0, res.stderr)
        return json.loads(res.stdout.strip())

    def test_an_untracked_file_deleted_during_a_launch_is_out_of_scope(self):
        self.fixture()
        self.write("src/new.js")
        result = self.disappearance("rmSync(root + '/src/new.js');")
        self.assertEqual(result, {"testsWritten": [], "outOfScope": ["src/new.js"]})

    def test_a_tracked_file_restored_to_its_committed_content_is_out_of_scope(self):
        self.write("src/app.js", "committed\n")
        repo_fixture.git_init(self.root)
        self.write("src/app.js", "builder edit\n")
        result = self.disappearance("writeFileSync(root + '/src/app.js', 'committed\\n');")
        self.assertEqual(result, {"testsWritten": [], "outOfScope": ["src/app.js"]})

    def test_a_tracked_file_deleted_during_a_launch_is_still_out_of_scope(self):
        self.write("src/app.js", "committed\n")
        repo_fixture.git_init(self.root)
        result = self.disappearance("rmSync(root + '/src/app.js');")
        self.assertEqual(result, {"testsWritten": [], "outOfScope": ["src/app.js"]})

    def test_file_already_changed_and_modified_again_is_caught_by_its_hash(self):
        self.write("src/app.js")
        repo_fixture.git_init(self.root)
        self.write("src/app.js", "builder edit\n")
        code = f"""
        import * as changes from './scripts/changes.mjs';
        import {{ writeFileSync }} from 'node:fs';
        const root = {json.dumps(str(self.root))};
        const before = changes.snapshotChanges(root);
        writeFileSync(root + '/src/app.js', 'agent edit\\n');
        console.log(JSON.stringify(changes.checkScope(before, changes.snapshotChanges(root), {{ allowEdits: true }})));
        """
        res = repo_fixture.run_node(code)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout.strip()), {"testsWritten": [], "outOfScope": ["src/app.js"]})


if __name__ == "__main__":
    unittest.main()
