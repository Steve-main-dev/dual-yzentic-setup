import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"

ACTIVE_SKILLS = ["tailor-setup", "fast-track", "caveman", "ponytail", "alpha", "beta"]
ARCHIVED_SKILLS = ["gamma"]

VALID_PROJECT = {
    "name": "AI Flow Canvas",
    "description": "Visual canvas for chaining AI steps",
    "archetype": "custom",
    "source_spec": "docs/specs/demo-design.md",
    "stack": {"runtime": "Python 3.12 CLI"},
    "team": {"dev1": {"name": "Steve", "role": "Fullstack"}, "dev2": {"name": "Bob"}},
    "skills": ["alpha", "gamma"],
    "verify": {"test": "npm test", "test_scoped": "npm test -- {scope}", "build": "npm run build"},
    "roadmap": [
        {"id": "1.1", "title": "Canvas shell", "priority": "P0", "owner": "dev1", "description": "Drag and drop nodes."},
        {"id": "2.1", "title": "Seed flows", "priority": "P1", "owner": "dev2", "description": "Three demo flows."},
    ],
}


def _write_skill(base, name):
    skill_dir = base / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(f"---\nname: {name}\ndescription: fixture skill\n---\n", encoding="utf-8")


def make_repo(tmp, project=None, status="uninitialized"):
    """Build a minimal fixture repo under tmp and return its root."""
    root = Path(tmp)
    for name in ACTIVE_SKILLS:
        _write_skill(root / ".agents" / "skills", name)
    (root / ".agents" / "skills" / "_staging").mkdir()
    for name in ARCHIVED_SKILLS:
        _write_skill(root / ".agents" / "skills-archive", name)

    sync_dir = root / ".agents" / "sync"
    sync_dir.mkdir()
    (sync_dir / "handoff.json").write_text("{}", encoding="utf-8")
    (sync_dir / "handoff.md").write_text("# Handoff\n", encoding="utf-8")

    (root / "docs" / "specs").mkdir(parents=True)
    (root / "docs" / "PLAN.md").write_text("ORIGINAL PLAN\n", encoding="utf-8")
    (root / "docs" / "specs" / "demo-design.md").write_text("# Demo design\n", encoding="utf-8")

    package = {"name": "template", "description": "template", "scripts": {"tailor": "node scripts/tailor.mjs"}}
    (root / "package.json").write_text(json.dumps(package, indent=2), encoding="utf-8")

    blueprint = {"status": status, "project": VALID_PROJECT if project is None else project, "archetypes": {}}
    (root / "project-blueprint.json").write_text(json.dumps(blueprint, indent=2), encoding="utf-8")
    return root


def run_node(code):
    """Evaluate an ES module snippet from the real repo root, so imports use ./scripts/..."""
    cmd = ["node", "--input-type=module", "-e", code]
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)


def skill_dirs(root, folder="skills"):
    base = Path(root) / ".agents" / folder
    return {p.name for p in base.iterdir() if p.is_dir()}
