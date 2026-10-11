# Design Spec: Automated Gatekeeper on Verify

- **Date:** 2026-10-11
- **Status:** Draft / Pending Review
- **Repository:** [`dual-yzentic-setup`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup)
- **Builds on:** [`2026-10-11-tailor-setup-design.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/specs/2026-10-11-tailor-setup-design.md) (branch `feat/tailor-setup`)

---

## 1. Objective

### Problem Statement
The repository describes a Builder (Claude Code, source code) and a Gatekeeper (Antigravity, tests), but nothing connects them. [`scripts/baton.mjs`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/scripts/baton.mjs) is a test runner: it never launches the Gatekeeper, and `active_agent` in `handoff.json` is always `claude`. The handoff only happens if a developer opens Antigravity by hand, so in practice the Builder writes the tests too and spends Claude quota doing it.

### Intended Outcome
When the Builder runs `npm run verify:agent` on a code change that has no accompanying tests, the baton launches Antigravity headlessly to write them, then runs the tests and reports the result. The developer stays in one Claude session.

### Success Criteria
1. Test authoring for untested code changes is done by Antigravity and billed to the Antigravity account, with no manual step.
2. Pass or fail is decided by the baton running the tests, never by what a model reports.
3. A developer without Antigravity installed, logged in, or in quota is not blocked.
4. The Gatekeeper cannot silently change source code.
5. Existing baton behaviour is unchanged when the Gatekeeper is not launched.

### Out of Scope
- Test-first ordering (Gatekeeper writes failing tests before the Builder implements).
- A hands-off loop that also launches the Builder headlessly.
- Launching through Orca terminals.
- The Gatekeeper running tests, browsers, or any shell command.

### Cost Note
This moves test authoring from Claude quota to Antigravity quota. Total tokens across both agents rise slightly, because Antigravity re-reads the changed files and the spec. Running the tests costs no tokens on either side.

---

## 2. Approach: Gatekeeper Writes, Baton Runs

The baton launches `agy --print` with a prompt limited to writing tests. When it returns, the baton runs the tests itself, as it does today. Antigravity needs permission to edit files only.

Rejected alternatives: letting the Gatekeeper run tests and write the diagnosis (needs `--dangerously-skip-permissions` and makes the verdict a model's claim); launching through Orca (adds a dependency for the second developer).

---

## 3. Unverified Assumptions (Probe First)

Only `agy --help` (version 1.3.3) has been read. Before any design below is implemented, a probe launches `agy --print` once against a throwaway file in a temp directory and records:

| Question | Why it matters |
| :--- | :--- |
| Does `--mode accept-edits` allow unattended file edits in print mode? | Decides the launch flags. |
| What does it print, and what is the exit code on success, on refusal, and when not logged in? | Decides how the baton detects "unavailable". |
| How long does one small run take? | Decides the default timeout. |
| Which model does it default to, and what does one run cost in quota? | Reported to the developer before building further. |
| Does it honour the working directory it is launched in? | Decides how the repo root is passed. |

**Stop condition.** If unattended edits are only possible with `--dangerously-skip-permissions`, implementation stops and the developer decides. That flag is never enabled by default.

The probe's findings are appended to this spec as Section 11 before the remaining tasks start.

---

## 4. Trigger

In `npm run verify:agent`, after tier detection and the circuit-breaker check:

| Condition | Behaviour |
| :--- | :--- |
| Tier 1 | Unchanged. No launch. |
| `--no-gatekeeper` flag, or `BATON_GATEKEEPER=0` | No launch. Tests run as today. |
| Tier 2 or 3, and the change set has no source files | No launch. |
| Tier 2 or 3, source files changed, and at least one test file changed | No launch. Tests run as today. |
| Tier 2 or 3, source files changed, and no test file changed | **Launch the Gatekeeper**, then run tests. |

**Change set.** The files reported by `git status --porcelain`, as the baton already collects.

**Test file.** A path that is under a `tests/`, `test/`, or `__tests__/` directory, or whose file name matches `test_*.py`, `*_test.*`, `*.test.*`, or `*.spec.*`.

**Source file.** Any changed file that is not a test file and not cosmetic by the baton's existing Tier 1 rule (docs, Markdown, styles, images), and not under `.agents/`.

The pre-commit hook calls the same command. Because a hook must not stall a commit for minutes, the hook runs with `BATON_GATEKEEPER=0`; the Gatekeeper launches only on an explicit `npm run verify:agent`.

---

## 5. Launch

New module `scripts/gatekeeper.mjs`, so `baton.mjs` stays near its current size.

1. Record the change set (`before`).
2. Write `active_agent: "antigravity"` and `status: "gatekeeper_running"` to `handoff.json`.
3. Run `agy --print <prompt>` in the repo root with the flags the probe settles on and a timeout (default 300 seconds, overridable with `BATON_GATEKEEPER_TIMEOUT`). The executable defaults to `agy` and is overridable with `BATON_GATEKEEPER_CMD`, which is also how tests substitute a stub.
4. Write `active_agent: "claude"` back, whatever the outcome.
5. Record the change set again (`after`) and apply the scope guard (Section 7).

### Prompt
Built by the baton and passed as one argument. It contains:
- The role line from [`GEMINI.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/GEMINI.md): you are the Gatekeeper.
- The list of changed source files.
- The path in `project.source_spec`, when the blueprint has one, and `docs/PLAN.md`.
- The test command from `project.verify.test`, when present, so tests are written for the right runner.
- The rules: write or update tests covering the listed changes; create or modify test files only; do not modify source files; do not run commands; if the code appears to contradict the spec, write the test to the spec and say so in one line of output.

The prompt contains file paths, not file contents. Antigravity reads the files itself.

---

## 6. Verdict

After the launch the baton runs the test command exactly as today (`project.verify` when initialized, the existing defaults otherwise).

- Pass: `status: "verified"`, turn count reset.
- Fail: `status: "verification_failed"`, turn count incremented, distilled diagnostic printed for the Builder. A failing Gatekeeper-written test is a normal failure: the Builder fixes the code, or, if the test is wrong, says so and fixes the test.

`handoff.json` gains a `gatekeeper` field recording the last launch: `"ran"`, `"skipped"`, or `"not_needed"`, plus `tests_written` (the test files it added or changed).

---

## 7. Scope Guard

Compare `before` and `after`:

- Files newly changed that are test files: recorded in `tests_written`.
- Files newly changed that are **not** test files: verification fails with `status: "gatekeeper_out_of_scope"` and the list of those files. The baton does **not** revert them, because a revert could destroy the Builder's own uncommitted work in the same file. The developer or Builder decides.

A source file that was already in `before` and was further modified by the Gatekeeper cannot be detected from the change set alone. To cover it, `before` also records a content hash of each changed source file, and any hash difference is treated as out of scope.

---

## 8. Unavailable Gatekeeper

| Condition | Behaviour |
| :--- | :--- |
| Executable not found | Warn once, `gatekeeper: "skipped"`, run existing tests. |
| Non-zero exit, including not logged in or out of quota | Warn with the first lines of its output, `"skipped"`, run existing tests. |
| Timeout | Kill the process, warn, `"skipped"`, run existing tests. The scope guard still runs, since a killed run may have written files. |
| Ran but wrote no test files | Warn that changed source remains untested, `"ran"` with empty `tests_written`, run existing tests. |

A skipped Gatekeeper never fails verification on its own. The warning tells the Builder that tests for the change are still owed.

---

## 9. Documentation Changes

- [`GEMINI.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/GEMINI.md): a short "Headless Mode" section. When launched by the baton, write tests only; do not run suites or write the handoff files. The existing directives remain for interactive sessions. The strings `Gatekeeper`, `handoff`, and `project-blueprint.json` stay, as tests assert them.
- [`CLAUDE.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/CLAUDE.md): one line under "Your Verification Interface is the Baton" saying the baton may launch the Gatekeeper to write tests, and that the Builder does not write tests for a change unless the Gatekeeper was skipped.
- [`AGENTS.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/AGENTS.md) Gate 3 (TDD): note that under the automated Gatekeeper, tests for Tier 2 and 3 changes are authored by the Gatekeeper at verify time, and that test-first by the Builder still applies when the Gatekeeper is skipped.
- [`docs/ai/workflows.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/ai/workflows.md): the verify flow with the launch step.
- `scripts/install-hooks.mjs`: the generated hook sets `BATON_GATEKEEPER=0`.

---

## 10. Testing

Python `unittest` in `tests/`, driving the Node scripts through `subprocess`, against temp fixture repos initialised with `git init`. No test launches the real `agy`. A stub executable, set through `BATON_GATEKEEPER_CMD`, stands in for it and is scripted per case to: write a test file; write a source file; modify an already-changed source file; exit non-zero; sleep past the timeout; write nothing.

- **Trigger:** each row of the Section 4 table; test-file and source-file classification for each listed pattern.
- **Launch:** the prompt contains the changed source paths, the spec path, and the rules, and no file contents; `active_agent` is `claude` again after success, failure, and timeout.
- **Scope guard:** a new non-test file fails verification and is not reverted; a further-modified source file is caught by the hash; test files land in `tests_written`.
- **Unavailable:** each row of the Section 8 table leaves verification governed by the existing tests alone.
- **Regression:** the existing baton tests pass unchanged.

The probe in Section 3 is the only step that launches the real `agy`. It is run by hand once and is not part of the suite.
