# Engineering Workflows & The Superpowers Lifecycle

This document defines the core development lifecycle for `Yzentic-setup`. It unites the **Superpowers** process engineering system with repository-specific domain skills.

---

## 1. Tiered Execution Lifecycle

To balance engineering rigor with token efficiency and speed, tasks follow one of three lifecycle paths based on scope:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 1: EXPRESS LANE (Micro-Tasks & Styling)                           │
│ Trigger: /fast-track, CSS tweaks, copy updates, icon swaps             │
│ Flow: Locate & Edit -> Scoped Check (diff/single test) -> Fast Commit  │
│ Exemption: Bypasses Red-Green TDD, full test suites, & npm run build   │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ TIER 2: BOUNDED LANE (Component Features & Bugfixes)                   │
│ Trigger: Single component logic, localized API route, targeted bug     │
│ Flow: Short in-chat design -> Build -> npm run verify:agent -> Commit  │
│ Rule: The Gatekeeper writes the missing tests; only those are run      │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ TIER 3: ARCHITECTURAL DEEP LANE (Major Features & Refactors)           │
│ Trigger: Schema changes, auth, multi-file features, breaking changes   │
│ Flow: Full 5-phase lifecycle (see below)                               │
└────────────────────────────────────────────────────────────────────────┘
```

### The End-to-End Lifecycle (Tier 3)

Major architectural and multi-step tasks progress through this complete pipeline:

```text
1. BRAINSTORMING (superpowers:brainstorming)
   ├── Requirements discovery & edge-case mapping
   ├── Design spec: docs/specs/YYYY-MM-DD-<name>-design.md
   └── Developer approval gate before implementation

2. PLANNING (superpowers:writing-plans)
   ├── Implementation plan: docs/specs/YYYY-MM-DD-<name>-plan.md
   └── Bite-sized, independently testable tasks

3. EXECUTION (builder agent, one plan task per launch)
   ├── npm run scout -- "<task>" where the plan does not already name the files
   ├── Sonnet builder implements the task on a feature branch
   └── npm run verify:agent after each task; commit per task

4. VERIFICATION & QUALITY GATE (the baton)
   ├── Gatekeeper writes tests for changes that have none
   ├── Baton runs the suite: npm run verify:agent -- --tier 3
   ├── On failure, Gatekeeper writes a root-cause note for the Builder
   └── The project's build command, when project.verify.build is set

5. REVIEW & BRANCH FINISH
   ├── npm run review (Gatekeeper reviews the diff against spec and plan)
   ├── Builder re-grades findings and fixes what stands
   └── Merge, then rewrite .agents/sync/session.md
```

---

## 2. Test Authorship & TDD Rules

**Every logic change ships with tests. The Gatekeeper writes them.**

- When `npm run verify:agent` sees changed source files and no changed test file, it launches the Gatekeeper to write the tests, then runs them. A failing Gatekeeper-written test is an ordinary failure: fix the code, or say the test is wrong and fix the test.
- The Builder writes a test only when the baton reports the Gatekeeper was skipped, or when a plan task supplies the test. In those cases `superpowers:test-driven-development` applies:
  - **RED:** Write a minimal failing test expressing the desired behavior.
  - **VERIFY RED:** Run the test to confirm it fails for the expected reason.
  - **GREEN:** Write the minimal implementation code to pass the test.
  - **VERIFY GREEN:** Run tests to confirm clean passing output.
  - **REFACTOR:** Clean up code while keeping tests green.
- Tests are run by the baton, never directly: `npm run verify:agent -- --tier 2 --scope <test file>` for one file, `-- --tier 3` for the suite.

### Web Testing Pyramid
Web applications in this repository adhere to a three-tier testing pyramid:
- **Unit & Custom Hook Tests (Vitest):** Millisecond-fast execution of pure business logic, calculations, and custom React hooks.
- **Component & Interaction Tests (React Testing Library):** User-centric verification of UI rendering, form events, and accessibility attributes without mocking internal state.
- **End-to-End User Journeys (Playwright via [`webapp-testing`](../../.agents/skills/webapp-testing/SKILL.md)):** Headless browser automation verifying critical user paths (auth, multi-step checkout, forms, and all 4 UI states).

---

## 3. Systematic Debugging Rules

Enforced via `superpowers:systematic-debugging`:
- **Never guess or patch symptoms.**
- Investigate root causes using minimal reproduction scripts, inspection logs, and stack trace analysis.
- Formulate a testable hypothesis before writing any fix.

---

## 4. Git Hygiene & Branching Strategy

- **Feature Branches:** Create dedicated topic branches from `main`:
  ```bash
  git checkout -b feature/<descriptive-name>
  ```
- **Isolated Worktrees:** For parallel agent work or large refactors, use `superpowers:using-git-worktrees` or [`orca-cli`](../../.agents/skills/orca-cli/SKILL.md).
- **Conventional Commits:** Format commit messages with clear semantic types (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).

### Pull Request & Pre-Merge Checklist
Before completing a task, opening a PR, or merging into `main`:
- [ ] **Automated Tests Green:** `npm run verify:agent -- --tier 3` passes. Do not run the suite directly.
- [ ] **Reviewed:** `npm run review` findings are fixed or answered.
- [ ] **Acceptance Criteria Met:** Feature satisfies Given/When/Then scenarios defined in [`docs/rules/requirements.md`](../rules/requirements.md).
- [ ] **The 4 UI States Handled:** Loading (skeletons), Empty, Error, and Success states verified.
- [ ] **Accessibility & Web Vitals:** Keyboard operable (WCAG 2.1 AA) with zero layout shift regressions (CLS < 0.1).
- [ ] **Zero Secret Leaks:** Zero credentials, tokens, or `.env` traces in commits or logs.

