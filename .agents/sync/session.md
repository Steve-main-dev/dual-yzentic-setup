# Session Handoff

- **Done:** The 2026-10-11 audit is fixed, the setup is single-developer with no hackathon framing, and Antigravity delegation is built and proven with real launches. Everything is merged to local `main`. Plan with every ruling: `docs/specs/2026-10-11-workflow-remediation-plan.md`.
- **How it works now:** `npm run scout -- "<task>"`, `npm run verify:agent` (Gatekeeper writes missing tests and diagnoses failures), `npm run review`. The pre-commit hook blocks failing commits. Hooks in `.claude/settings.json` inject this file at session start and block direct full-suite runs.
- **Decisions:**
  - Sync state (`handoff.json`, `handoff.md`, briefs, logs) is local and untracked; only this file is committed.
  - `--scope` on verify means "tests exist": no test-writing launch.
  - Every Antigravity launch uses `gemini-3.8-flash-high`, timeout 600 s. Measured: scout 240 s / 121k tokens, test writing 128 s / 150k, diagnosis 22 s / 61k, branch review 374 s / 246k.
- **Open, needs the developer:**
  - No project has been started. Say what you are building; then brainstorm a spec and run the `tailor-setup` skill.
  - `main` is not pushed to `origin`.
  - Whether to move scout and diagnosis to a lighter model (`BATON_AGY_MODEL`).
  - Deferred review minors from `tailor-setup` (dry-run omits the hook; skill present in both folders; backslash `source_spec`).
- **Not enforced, only written:** tier sizing and handing plan tasks to the `builder` agent.
- **Next:** start a project, or pick an open item above.
- **Open these first:** `README.md`, `CLAUDE.md` section 3, the plan named above.
