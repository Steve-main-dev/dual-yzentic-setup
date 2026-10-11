import json
import unittest

from tests.repo_fixture import run_node

TASKS = [
    {"id": "1.1", "title": "Canvas shell", "priority": "P0", "owner": "Steve", "description": "Drag and drop nodes."},
    {"id": "2.1", "title": "Seed flows", "priority": "P1", "owner": "Bob", "description": "Three demo flows."},
]

P0 = "## P0: Must-Have for Demo"
P1 = "## P1: High Impact Polish"
P2 = "## P2: Post-Hackathon Stretch"


class TestRoadmap(unittest.TestCase):
    def render(self, tasks=TASKS):
        options = {
            "name": "Demo",
            "desc": "A demo project",
            "dev1": "Steve",
            "dev2": "Bob",
            "preset": "custom",
            "tasks": tasks,
        }
        code = f"""
        import {{ generateRoadmap }} from './scripts/roadmap.mjs';
        process.stdout.write(generateRoadmap({json.dumps(options)}));
        """
        res = run_node(code)
        self.assertEqual(res.returncode, 0, res.stderr)
        return res.stdout

    def test_groups_tasks_under_priority_headings(self):
        text = self.render()
        first = text.index("- [ ] **Task 1.1: Canvas shell**")
        second = text.index("- [ ] **Task 2.1: Seed flows**")
        self.assertLess(text.index(P0), first)
        self.assertLess(first, text.index(P1))
        self.assertLess(text.index(P1), second)
        self.assertLess(second, text.index(P2))
        self.assertIn("  - **Owner:** Steve", text)
        self.assertIn("  - **Priority:** P0", text)
        self.assertIn("  - **Status:** Backlog", text)

    def test_empty_priority_keeps_heading(self):
        text = self.render()
        self.assertIn("None yet.", text[text.index(P2):])

    def test_contains_all_required_sections(self):
        text = self.render()
        for section in [
            "Mission & Hackathon Objective",
            "Current Sprint Focus",
            "P0: Must-Have for Demo",
            "P1: High Impact Polish",
            "P2: Post-Hackathon Stretch",
            "Rules for Adding Features",
        ]:
            self.assertIn(section, text)

    def test_multiline_text_collapses_to_one_line(self):
        tasks = [dict(TASKS[0], title="Canvas\nshell", description="  Drag\n\nand drop.  ")]
        text = self.render(tasks)
        self.assertIn("**Task 1.1: Canvas shell**", text)
        self.assertIn("  - **Description:** Drag and drop.\n", text)


if __name__ == "__main__":
    unittest.main()
