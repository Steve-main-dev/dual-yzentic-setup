import json
import tempfile
import unittest
from pathlib import Path

from tests.tailor_fixture import VALID_PROJECT, make_repo, run_node

V = {"test": "pnpm test", "test_scoped": "pnpm vitest run {scope}"}


class TestBatonVerifyConfig(unittest.TestCase):
    def node_json(self, expression):
        code = f"""
        import {{ resolveTestExecution, readVerifyConfig }} from './scripts/baton.mjs';
        console.log(JSON.stringify({expression}));
        """
        res = run_node(code)
        self.assertEqual(res.returncode, 0, res.stderr)
        return json.loads(res.stdout)

    def resolve(self, tier, scope, verify=None):
        args = [json.dumps(tier), json.dumps(scope)]
        if verify is not None:
            args.append(json.dumps(verify))
        return self.node_json(f"resolveTestExecution({', '.join(args)})")

    def test_resolve_uses_verify_commands(self):
        self.assertEqual(self.resolve(3, None, V)["command"], "pnpm test")
        self.assertEqual(self.resolve(2, "src/a.test.ts", V)["command"], "pnpm vitest run src/a.test.ts")
        self.assertEqual(self.resolve(1, None, V), {"command": "git diff --stat", "isExpress": True})

    def test_resolve_falls_back_without_verify(self):
        self.assertEqual(self.resolve(3, None)["command"], "python3 -m unittest discover tests")
        self.assertEqual(self.resolve(2, "tests/x.py")["command"], "python3 -m unittest tests/x.py")
        self.assertEqual(self.resolve(2, "src/a.test.ts")["command"], "npm test -- src/a.test.ts")

    def test_scope_without_scoped_command_falls_back(self):
        self.assertEqual(self.resolve(2, "src/a.test.ts", {"test": "pnpm test"})["command"], "npm test -- src/a.test.ts")

    def read(self, blueprint_path):
        return self.node_json(f"readVerifyConfig({json.dumps(str(blueprint_path))})")

    def test_read_verify_config(self):
        tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)

        initialized = make_repo(base / "a", status="initialized") / "project-blueprint.json"
        self.assertEqual(self.read(initialized), VALID_PROJECT["verify"])

        uninitialized = make_repo(base / "b") / "project-blueprint.json"
        self.assertIsNone(self.read(uninitialized))

        self.assertIsNone(self.read(base / "missing.json"))

        broken = base / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        self.assertIsNone(self.read(broken))

        project = dict(VALID_PROJECT, verify={"test": ""})
        empty = make_repo(base / "c", project=project, status="initialized") / "project-blueprint.json"
        self.assertIsNone(self.read(empty))


if __name__ == "__main__":
    unittest.main()
