import unittest
import re
from pathlib import Path

class TestRulesIntegrity(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.rules_dir = self.root / "docs" / "rules"
        self.expected_files = ["README.md", "requirements.md", "frontend.md", "backend.md"]

    def test_all_rule_files_exist(self):
        self.assertTrue(self.rules_dir.exists(), "docs/rules/ directory must exist")
        for filename in self.expected_files:
            rule_file = self.rules_dir / filename
            self.assertTrue(rule_file.exists(), f"Rule file {filename} must exist in docs/rules/")
            content = rule_file.read_text(encoding="utf-8")
            self.assertGreater(len(content.strip()), 100, f"Rule file {filename} must not be empty")

    def test_rule_files_structure(self):
        readme = self.rules_dir / "README.md"
        if readme.exists():
            content = readme.read_text(encoding="utf-8")
            self.assertIn("When to Read What", content, "README.md must contain a 'When to Read What' routing table")

        domain_files = ["requirements.md", "frontend.md", "backend.md"]
        for filename in domain_files:
            rule_file = self.rules_dir / filename
            if rule_file.exists():
                content = rule_file.read_text(encoding="utf-8")
                self.assertIn("## Core Standards", content, f"{filename} must contain '## Core Standards'")
                self.assertIn("## Dos and Don'ts", content, f"{filename} must contain '## Dos and Don'ts'")

    def test_rules_markdown_links_are_valid(self):
        if not self.rules_dir.exists():
            self.fail("docs/rules/ directory does not exist")
        for f in self.rules_dir.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
            for text, url in links:
                if url.startswith("file:///"):
                    path_str = url.replace("file:///", "").replace("/", "\\")
                    p = Path(path_str)
                    self.assertTrue(p.exists(), f"Broken file link in {f.name}: {url}")
                elif not url.startswith(("http://", "https://", "#", "mailto:")):
                    target = (f.parent / url).resolve()
                    self.assertTrue(target.exists(), f"Broken relative link in {f.name}: {url}")

    def test_harness_integration_links(self):
        agents_md = self.root / "AGENTS.md"
        self.assertTrue(agents_md.exists(), "AGENTS.md must exist")
        agents_content = agents_md.read_text(encoding="utf-8")
        self.assertIn("docs/rules", agents_content, "AGENTS.md must reference docs/rules")

        handbook = self.root / "docs" / "ai" / "agent-handbook.md"
        self.assertTrue(handbook.exists(), "agent-handbook.md must exist")
        handbook_content = handbook.read_text(encoding="utf-8")
        self.assertIn("docs/rules", handbook_content, "agent-handbook.md must reference docs/rules")

if __name__ == "__main__":
    unittest.main()
