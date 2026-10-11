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
        path.write_text(text, encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
