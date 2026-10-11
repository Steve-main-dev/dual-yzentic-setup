import copy
import json
import tempfile
import unittest

from tests.tailor_fixture import VALID_PROJECT, make_repo, run_node


class TestTailorValidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = make_repo(self.tmp.name)

    def validate(self, blueprint):
        code = f"""
        import {{ validateManifest }} from './scripts/tailor.mjs';
        console.log(JSON.stringify(validateManifest({json.dumps(blueprint)}, {{ root: {json.dumps(str(self.root))} }})));
        """
        res = run_node(code)
        self.assertEqual(res.returncode, 0, res.stderr)
        return json.loads(res.stdout)

    def problems(self, project):
        return self.validate({"project": project})

    def test_valid_manifest_has_no_problems(self):
        self.assertEqual(self.problems(VALID_PROJECT), [])

    def test_each_rule_reports_its_field(self):
        cases = [
            (lambda p: p.update(name=""), "project.name"),
            (lambda p: p.update(description="  "), "project.description"),
            (lambda p: p.update(archetype="fullstack-web"), "project.archetype"),
            (lambda p: p.update(source_spec="docs/specs/no.md"), "project.source_spec"),
            (lambda p: p.update(source_spec="../outside.md"), "project.source_spec"),
            (lambda p: p.update(stack=[]), "project.stack"),
            (lambda p: p["team"]["dev2"].update(name=""), "project.team.dev2.name"),
            (lambda p: p.update(skills="alpha"), "project.skills"),
            (lambda p: p.update(skills=["alpha", "nope"]), "project.skills"),
            (lambda p: p["verify"].pop("test"), "project.verify.test"),
            (lambda p: p["verify"].update(test_scoped="npm test"), "project.verify.test_scoped"),
            (lambda p: p.update(roadmap=[]), "project.roadmap"),
            (lambda p: p["roadmap"][0].update(priority="P3"), "project.roadmap[0].priority"),
            (lambda p: p["roadmap"][1].update(owner="Bob"), "project.roadmap[1].owner"),
            (lambda p: p["roadmap"][1].update(id="1.1"), "project.roadmap[1].id"),
            (lambda p: p["roadmap"][0].update(title=""), "project.roadmap[0].title"),
        ]
        for mutate, expected in cases:
            with self.subTest(field=expected):
                project = copy.deepcopy(VALID_PROJECT)
                mutate(project)
                found = self.problems(project)
                self.assertEqual(len(found), 1, found)
                self.assertTrue(found[0].startswith(expected), found[0])

    def test_all_problems_reported_together(self):
        project = copy.deepcopy(VALID_PROJECT)
        project["name"] = ""
        project["roadmap"][0]["priority"] = "P3"
        project["skills"] = ["nope"]
        self.assertEqual(len(self.problems(project)), 3)

    def test_missing_project_block(self):
        found = self.validate({})
        self.assertEqual(len(found), 1)
        self.assertTrue(found[0].startswith("project"), found[0])

    def test_optional_fields_may_be_absent(self):
        project = copy.deepcopy(VALID_PROJECT)
        del project["verify"]["test_scoped"]
        del project["verify"]["build"]
        del project["team"]["dev1"]["role"]
        self.assertEqual(self.problems(project), [])

    def test_duplicate_and_always_kept_skills_are_valid(self):
        project = copy.deepcopy(VALID_PROJECT)
        project["skills"] = ["alpha", "alpha", "caveman"]
        self.assertEqual(self.problems(project), [])


if __name__ == "__main__":
    unittest.main()
