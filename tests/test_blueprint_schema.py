import unittest
import json
from pathlib import Path

class TestBlueprintSchema(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.blueprint_file = self.root / "project-blueprint.json"

    def test_blueprint_file_exists_and_valid(self):
        self.assertTrue(self.blueprint_file.exists(), "project-blueprint.json must exist")
        data = json.loads(self.blueprint_file.read_text(encoding="utf-8"))
        self.assertIn("status", data)
        self.assertIn(data["status"], ["uninitialized", "initialized"])
        self.assertIn("project", data)
        self.assertIn("archetypes", data)
        for expected in ["fullstack-web", "ai-agent-app", "frontend-dashboard", "minimal"]:
            self.assertIn(expected, data["archetypes"])
            self.assertIn("keep_skills", data["archetypes"][expected])
            self.assertIn("rules_preset", data["archetypes"][expected])

    def test_single_developer_and_no_hackathon_leftovers(self):
        data = json.loads(self.blueprint_file.read_text(encoding="utf-8"))
        self.assertNotIn("team", data["project"])
        self.assertIsInstance(data["project"]["developer"], str)
        self.assertNotIn("minimal-hackathon", data["archetypes"])
        for name, archetype in data["archetypes"].items():
            self.assertNotIn("pitch-architect", archetype["keep_skills"], name)

if __name__ == "__main__":
    unittest.main()
