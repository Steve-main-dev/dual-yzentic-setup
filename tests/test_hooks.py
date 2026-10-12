import os
import subprocess
import tempfile
import unittest

from tests import repo_fixture


class TestGitHooks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.fixture = repo_fixture.git_init(repo_fixture.make_template_repo(self.tmp.name))
        self.pre_commit_hook = self.fixture / ".githooks" / "pre-commit"
        self.install_script = repo_fixture.SCRIPTS / "install-hooks.mjs"

    def test_install_hooks_configures_git_and_creates_hook(self):
        cmd = ["node", str(self.install_script), "--root", str(self.fixture)]
        res = subprocess.run(cmd, cwd=self.fixture, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"install-hooks failed: {res.stderr}")

        # Hook exists and contains baton verify
        self.assertTrue(self.pre_commit_hook.exists(), ".githooks/pre-commit must exist")
        content = self.pre_commit_hook.read_text(encoding="utf-8")
        self.assertIn("scripts/baton.mjs verify", content)

        # Git core.hooksPath is configured in the fixture repo
        git_res = subprocess.run(["git", "config", "core.hooksPath"], cwd=self.fixture, capture_output=True, text=True)
        self.assertEqual(git_res.returncode, 0)
        self.assertEqual(git_res.stdout.strip(), ".githooks")

    def install(self):
        cmd = ["node", str(self.install_script), "--root", str(self.fixture)]
        res = subprocess.run(cmd, cwd=self.fixture, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"install-hooks failed: {res.stderr}")

    def run_hook(self, **env):
        base_env = {k: v for k, v in os.environ.items() if k != "SKIP_VERIFY"}
        return subprocess.run(
            ["sh", ".githooks/pre-commit"], cwd=self.fixture, capture_output=True, text=True, env={**base_env, **env}
        )

    def write_baton_stub(self, source):
        stub = self.fixture / "scripts" / "baton.mjs"
        stub.parent.mkdir(exist_ok=True)
        stub.write_text(source, encoding="utf-8")

    def test_generated_hook_is_lf_only_and_never_stages_sync_state(self):
        self.install()
        raw = self.pre_commit_hook.read_bytes()
        self.assertNotIn(b"\r", raw, "hook must not contain CR bytes")
        content = raw.decode("utf-8")
        self.assertIn("BATON_GATEKEEPER=0", content)
        self.assertIn("BATON_HOOK=1", content)
        self.assertNotIn("git add", content)

    def test_hook_blocks_the_commit_when_baton_fails(self):
        self.install()
        self.write_baton_stub("process.exit(1);\n")
        res = self.run_hook()
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("Commit blocked", res.stdout)

    def test_hook_passes_when_baton_passes_and_skip_verify_bypasses(self):
        self.install()
        self.write_baton_stub("process.exit(0);\n")
        self.assertEqual(self.run_hook().returncode, 0)
        self.write_baton_stub("process.exit(1);\n")
        self.assertEqual(self.run_hook(SKIP_VERIFY="1").returncode, 0)

    def test_hook_still_blocks_when_it_is_rewritten_while_running(self):
        # sh reads a script incrementally; a rewrite with different bytes mid-run used to misalign it
        self.install()
        self.write_baton_stub(
            "import fs from 'node:fs';\n"
            "const hook = '.githooks/pre-commit';\n"
            "const text = fs.readFileSync(hook, 'utf-8');\n"
            "fs.writeFileSync(hook, '# rewritten while running\\r\\n' + text.replace(/\\n/g, '\\r\\n'));\n"
            "process.exit(1);\n"
        )
        res = self.run_hook()
        self.assertEqual(res.returncode, 1, f"hook let a failing commit through: {res.stdout} {res.stderr}")
        self.assertIn(b"\r", self.pre_commit_hook.read_bytes(), "stub did not rewrite the hook")

    def test_root_flag_without_value_fails(self):
        res = subprocess.run(["node", str(self.install_script), "--root"], cwd=self.fixture, capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("--root", res.stderr)


if __name__ == "__main__":
    unittest.main()
