# AGENTS.md — Universal Agent Instructions

Welcome to the `Yzentic-setup` repository. This repository follows an AI-driven development standard where all autonomous agents (Google Antigravity, Claude Code, Cursor AI, and Stably Orca) adhere to uniform behavioral tenets, the **Superpowers** engineering framework, and progressive domain skills.

<CRITICAL-DIRECTIVES>
These rules are MANDATORY and NON-NEGOTIABLE. Violating the letter of the rules is violating the spirit of the rules. You CANNOT rationalize bypassing these gates.
</CRITICAL-DIRECTIVES>

---

## 1. Task Tiering & Execution Lanes

To prevent token waste and excessive latency on minor adjustments, all tasks are classified into three operational tiers:

| Tier | Scope | Required Process & Verification |
| :--- | :--- | :--- |
| **Tier 1: Express Lane** *(Micro / Cosmetic)* | Pure CSS/Tailwind tweaks, copy/text edits, icon swaps, single-file non-structural adjustments. | Use [`fast-track`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/fast-track/SKILL.md). Direct edit → scoped sanity check (diff or single test file if one exists). **Exempt from Red-Green TDD, full regression runs, and production build.** |
| **Tier 2: Standard Bounded Lane** *(Component / Fix)* | Localized component logic, single API route, or isolated bug fix. | Scoped TDD on the affected test file (`superpowers:test-driven-development`). Verify touched test suite before completion. |
| **Tier 3: Architectural Deep Lane** *(Full Features)* | Multi-file features, database schema/migrations, authentication, breaking architectural changes. | Full Superpowers lifecycle: Spec (`superpowers:brainstorming`) → Plan (`superpowers:writing-plans`) → Full TDD → Full regression suite → Production build (`npm run build`). |

---

## 2. Hard Operational Gates

1. **Gate 1: Mandatory Skills Discovery & Invocation**
   - You MUST read and consult [`docs/ai/agent-handbook.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/ai/agent-handbook.md) to discover and invoke required domain skills before beginning any non-trivial user task.
   - For Tier 1 micro-tasks, invoke [`fast-track`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/fast-track/SKILL.md).
   - Invoke relevant Superpowers process skills BEFORE taking any action or answering.
2. **Gate 2: Spec & Plan First (Tier 2 & Tier 3)**
   - For any multi-step task, complete requirements discovery (`superpowers:brainstorming`) and write an implementation plan (`superpowers:writing-plans`) in [`docs/specs/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/specs/) before editing code. Tier 1 micro-tasks are exempt from plan files.
3. **Gate 3: The Iron Law of TDD (Tier 2 & Tier 3)**
   - NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST for logic, mutations, or endpoints (`superpowers:test-driven-development`). Tier 1 pure visual styling and copy edits are exempt from upfront test authoring. If you write logic code before the test, delete it and start over.
4. **Gate 4: Systematic Root-Cause Debugging**
   - Never guess or blindly patch bugs. Investigate root causes with evidence before touching implementation (`superpowers:systematic-debugging`).
5. **Gate 5: Evidence Before Assertions**
   - Never claim code works, bugs are fixed, or tasks are complete without verifying output (`superpowers:verification-before-completion`).
   - For Tier 1: Evidence is a clean `git diff` and passing scoped single-component test (if a test file already exists).
   - For Tier 3: Evidence requires full test suites and clean `npm run build` exit code 0.

---

## 3. Red Flags: Thoughts that Mean STOP

If you catch yourself thinking any of these, STOP immediately — you are rationalizing:

| Rationalization Thought | Reality & Mandatory Action |
| :--- | :--- |
| *"I don't need to check the handbook, I know what to do."* | **STOP.** Read [`docs/ai/agent-handbook.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/ai/agent-handbook.md) to select the right skill. |
| *"I should run the entire test suite and full build for a 1-line CSS change."* | **STOP.** Tier 1 tasks use [`fast-track`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/fast-track/SKILL.md) to prevent token waste and latency. |
| *"This is just a small bug, no need to debug systematically."* | **STOP.** Bugs are symptoms. Invoke `superpowers:systematic-debugging`. |
| *"I'll write the tests after the feature code is working."* | **STOP.** For Tier 2/3 logic, that violates TDD. Write failing tests first. *(Tier 1 cosmetic edits use [`fast-track`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/fast-track/SKILL.md) and are exempt).* |
| *"The prompt is clear, I can jump straight to code."* | **STOP.** Invoke `superpowers:writing-plans` and write a spec first. |
| *"I know it works without running the test command."* | **STOP.** Evidence before assertions. Run the command and inspect output. |
| *"This file is too simple to need clickable links."* | **STOP.** All paths and symbols MUST use clickable `file://` Markdown links. |
| *"I'll just write a quick custom button/modal here instead of searching components."* | **STOP.** You must inspect and reuse existing components per [`docs/rules/frontend.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/rules/frontend.md). |

---

## 4. Core Behavioral Tenets

1. **Evidence before assertions:**
   - Always verify exit codes and output before declaring completion.
2. **Navigable file and symbol references:**
   - You MUST format all file paths and code symbols as clickable Markdown links using the `file://` scheme (e.g. [`README.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/README.md) or [`AGENTS.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/AGENTS.md)).
   - On Windows, always normalize URI paths to use forward slashes (`/`).
3. **Continuous task tracking:**
   - For any multi-step task, maintain a markdown checklist (`- [ ]` / `- [x]`) tracking every phase of execution. Update it after every step.
4. **Non-destructive & non-interactive execution:**
   - Always run commands non-interactively (e.g., passing `-y`, `--yes`, or non-blocking flags).
   - Ensure proper console encoding on Windows: `$env:PYTHONIOENCODING="utf-8"`.
5. **Zero secret exposure:**
   - Never print, echo, or log raw `.env` contents, API keys, credentials, or tokens in chat or terminal traces.
   - Use [`varlock`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/varlock/SKILL.md) for secrets management and review security-sensitive changes against [`owasp-security`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/owasp-security/SKILL.md).

---

## 5. Skills & Documentation Routing

To preserve context window efficiency, domain skills and detailed runbooks are discovered progressively:

- [`docs/ai/agent-handbook.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/ai/agent-handbook.md): **Mandatory skills catalog & routing index**. Read this to select from the 21 domain skills, Superpowers matrix, CLI cheatsheets, and operational SOPs.
- [`.agents/skills/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/): Directory housing the 21 on-demand domain skills.
- [`docs/ai/workflows.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/ai/workflows.md): Superpowers process loops, TDD cycles, and branching standards.
- [`docs/ai/architecture.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/ai/architecture.md): Modular separation and system boundaries.
- [`docs/specs/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/specs/): Location for feature specifications and implementation plans.
- [`docs/rules/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/rules/README.md): Modular full-stack web development standards (requirements, frontend, backend API & security).
