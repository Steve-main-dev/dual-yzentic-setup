import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / "run_parallel.py"

PASSING = "import unittest\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        print('PASSING-MODULE-OUTPUT')\n"
FAILING = "import unittest\n\nclass T(unittest.TestCase):\n    def test_bad(self):\n        self.fail('FAILING-MODULE-OUTPUT')\n"


class TestRunParallel(unittest.TestCase):
    def make_tests_dir(self, modules):
        """A temp parent holding a `tests` package; the runner never sees the real tests directory."""
        tmp = tempfile.TemporaryDirectory(prefix="run parallel ")
        self.addCleanup(tmp.cleanup)
        tests_dir = Path(tmp.name) / "tests"
        tests_dir.mkdir()
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        for name, body in modules.items():
            (tests_dir / name).write_text(body, encoding="utf-8")
        return tests_dir

    def run_runner(self, tests_dir):
        # Run from an unrelated directory: the runner must not depend on the current directory.
        return subprocess.run([sys.executable, str(RUNNER), str(tests_dir)], cwd=tests_dir.parent.parent,
                              capture_output=True, text=True)

    def test_a_failing_module_fails_the_run_and_shows_only_its_own_output(self):
        res = self.run_runner(self.make_tests_dir({"test_good.py": PASSING, "test_bad.py": FAILING}))
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertIn("FAILING-MODULE-OUTPUT", res.stdout)
        self.assertNotIn("PASSING-MODULE-OUTPUT", res.stdout)
        last = res.stdout.strip().splitlines()[-1]
        self.assertRegex(last, r"^Ran 2 test modules in [\d.]+s: 1 passed, 1 failed$")

    def test_all_passing_modules_exit_zero(self):
        res = self.run_runner(self.make_tests_dir({"test_a.py": PASSING, "test_b.py": PASSING}))
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        last = res.stdout.strip().splitlines()[-1]
        self.assertRegex(last, r"^Ran 2 test modules in [\d.]+s: 2 passed, 0 failed$")


if __name__ == "__main__":
    unittest.main()
