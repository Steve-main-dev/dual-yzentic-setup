import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests import repo_fixture

REPO_ROOT = repo_fixture.REPO_ROOT
BATON = repo_fixture.SCRIPTS / "baton.mjs"


class TestE2EBatonFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.sync_json = Path(self.tmp.name) / "handoff.json"

        initial_state = {
            "version": "1.0",
            "task_id": "TEST-01",
            "active_agent": "claude",
            "status": "idle",
            "turn_count": 0,
            "max_turns": 5,
            "last_updated": "2026-10-08T00:00:00.000Z",
            "summary": "E2E testing",
            "files_modified": []
        }
        with open(self.sync_json, "w", encoding="utf-8") as f:
            json.dump(initial_state, f)

    def make_fixture(self):
        """A git-initialised template repo, separate from the sync file used by the snippet tests."""
        fixture_tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(fixture_tmp.cleanup)
        return repo_fixture.git_init(repo_fixture.make_template_repo(fixture_tmp.name))

    def make_verify_fixture(self, test_command):
        """An initialized project whose last commit changed only src/app.js and whose tree is clean."""
        fixture_tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(fixture_tmp.cleanup)
        root = repo_fixture.make_template_repo(fixture_tmp.name)
        blueprint_path = root / "project-blueprint.json"
        blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
        blueprint["status"] = "initialized"
        blueprint["project"] = {"verify": {"test": test_command}}
        blueprint_path.write_text(json.dumps(blueprint, indent=2) + "\n", encoding="utf-8")
        repo_fixture.git_init(root)
        (root / "src").mkdir()
        (root / "src" / "app.js").write_text("module.exports = 1;\n", encoding="utf-8")
        for args in (["add", "-A"], ["commit", "-q", "-m", "add app"]):
            subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
        return root

    def baton(self, fixture, *args, env=None):
        cmd = ["node", str(BATON), *args, "--root", str(fixture)]
        base_env = {k: v for k, v in os.environ.items() if k not in ("npm_config_tier", "npm_config_scope")}
        base_env["BATON_GATEKEEPER"] = "0"  # these runs are about the gate, so they must never launch the real agy
        return subprocess.run(cmd, cwd=fixture, capture_output=True, text=True, env={**base_env, **(env or {})})

    def test_tier_1_express_pass(self):
        code = f"""
        import {{ readSyncState, writeSyncState }} from './scripts/baton.mjs';
        const state = readSyncState({json.dumps(str(self.sync_json))});
        state.status = 'verified';
        writeSyncState(state, {json.dumps(str(self.sync_json))});
        """
        res = repo_fixture.run_node(code)
        self.assertEqual(res.returncode, 0, res.stderr)

        with open(self.sync_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["status"], "verified")

    def test_circuit_breaker_halts_at_max_turns(self):
        state = {
            "version": "1.0",
            "task_id": "TEST-02",
            "active_agent": "claude",
            "status": "verification_failed",
            "turn_count": 5,
            "max_turns": 5,
            "last_updated": "2026-10-08T00:00:00.000Z",
            "summary": "Failing loop",
            "files_modified": ["src/app.ts"]
        }
        with open(self.sync_json, "w", encoding="utf-8") as f:
            json.dump(state, f)

        code = f"""
        import {{ checkCircuitBreaker, readSyncState }} from './scripts/baton.mjs';
        const st = readSyncState({json.dumps(str(self.sync_json))});
        if (!checkCircuitBreaker(st)) {{
            process.exit(42);
        }}
        """
        res = repo_fixture.run_node(code)
        self.assertEqual(res.returncode, 42, "Circuit breaker should have halted execution with exit 42")

    def test_cli_status_command(self):
        res = self.baton(self.make_fixture(), "status")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("=== Baton Sync Status ===", res.stdout)
        self.assertIn("Detected Tier:", res.stdout)

    def test_cli_verify_tier1_express(self):
        res = self.baton(self.make_fixture(), "verify", "--tier", "1")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Tier 1 Express Lane", res.stdout)

    def test_root_flag_isolates_state(self):
        fixture = self.make_fixture()
        real_json = REPO_ROOT / ".agents" / "sync" / "handoff.json"
        real_before = real_json.read_bytes()
        fixture_json = fixture / ".agents" / "sync" / "handoff.json"
        fixture_before = fixture_json.read_bytes()

        res = self.baton(fixture, "verify", "--tier", "1")
        self.assertEqual(res.returncode, 0, res.stderr)

        self.assertNotEqual(fixture_json.read_bytes(), fixture_before)
        self.assertEqual(json.loads(fixture_json.read_text(encoding="utf-8"))["status"], "verified")
        self.assertEqual(real_json.read_bytes(), real_before)

    def test_clean_tree_verifies_the_last_commit(self):
        fixture = self.make_verify_fixture('node -e "process.exit(0)"')
        res = self.baton(fixture, "verify")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Working tree clean: classifying the last commit.", res.stdout)
        self.assertIn('Executing test command: node -e "process.exit(0)"', res.stdout)
        self.assertNotIn("Express Lane", res.stdout)

    def test_clean_tree_with_failing_test_fails_and_counts_a_turn(self):
        fixture = self.make_verify_fixture('node -e "process.exit(1)"')
        res = self.baton(fixture, "verify")
        self.assertEqual(res.returncode, 1, res.stdout)
        state = json.loads((fixture / ".agents" / "sync" / "handoff.json").read_text(encoding="utf-8"))
        self.assertEqual(state["turn_count"], 1)
        self.assertEqual(state["status"], "verification_failed")

    def test_npm_config_tier_selects_the_tier(self):
        fixture = self.make_verify_fixture('node -e "process.exit(1)"')
        res = self.baton(fixture, "verify", env={"npm_config_tier": "1"})
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Tier 1 Express Lane", res.stdout)

    def test_flag_beats_npm_config_tier(self):
        fixture = self.make_verify_fixture('node -e "process.exit(1)"')
        res = self.baton(fixture, "verify", "--tier", "2", env={"npm_config_tier": "1"})
        self.assertEqual(res.returncode, 1)
        self.assertNotIn("Express Lane", res.stdout)

    def test_root_flag_without_value_fails(self):
        res = subprocess.run(["node", str(BATON), "status", "--root"], cwd=self.tmp.name, capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("--root", res.stderr)


if __name__ == "__main__":
    unittest.main()
