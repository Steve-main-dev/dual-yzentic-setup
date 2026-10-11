import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent

# Literal patterns that mean a test is writing to the real repo.
ALWAYS_BAD = ['rmtree(self.src_dir', 'self.root / "src"']
# A restore-style write back to an attribute is only suspect in a file that builds real paths from Path(__file__).
BAD_WITH_REAL_PATHS = ["write_text(self."]


class TestRepoIsolation(unittest.TestCase):
    def test_no_test_writes_to_the_real_repo(self):
        offenders = []
        for path in sorted(TESTS_DIR.glob("test_*.py")):
            if path.name == Path(__file__).name:
                continue
            text = path.read_text(encoding="utf-8")
            patterns = list(ALWAYS_BAD)
            if "Path(__file__)" in text:
                patterns += BAD_WITH_REAL_PATHS
            offenders += [f"{path.name}: {pattern}" for pattern in patterns if pattern in text]
        self.assertEqual(offenders, [], "tests must run scripts against a fixture repo, not the real one")


if __name__ == "__main__":
    unittest.main()
