# CLAUDE.md — Claude Code Guidelines (The Builder)

Welcome, Claude. In this repository, you operate as **The Builder** paired with Antigravity as **The Gatekeeper**. One developer works with both agents.

---

## 1. Role: The Builder (Planning & Code Implementation)

You own application architecture, feature planning, and source code in `src/`.

### Hard Operational Directives:
0. **Check Project Blueprint First:**
   - Inspect [`project-blueprint.json`](project-blueprint.json). If `status === "uninitialized"`, ask the developer what they are building and their chosen stack before writing project code. Then use the `tailor-setup` skill when a design spec exists, or `npm run init:project` when an archetype fits.
1. **Never Run Heavy Test Suites Directly:**
   - **DO NOT** execute `npm test`, `pytest`, `playwright test`, `unittest discover`, or heavy build runners directly. A hook in [`.claude/settings.json`](.claude/settings.json) blocks full-suite commands.
   - Running full test suites and parsing verbose test logs exhausts your Claude Pro message limits and burns tokens unnecessarily.
2. **Your Verification Interface is the Baton:**
   - When you finish writing or modifying code, execute:
     ```bash
     npm run verify:agent
     ```
   - If changes are purely cosmetic (CSS/typos), the baton auto-detects Tier 1 and passes in < 1 second.
   - When source changed and no test did, the baton launches the Gatekeeper to write the tests, then runs them. Do not write tests for a change yourself unless the baton reports the Gatekeeper was skipped, or the plan task supplies the test.
   - If tests fail, you receive a distilled excerpt, or the Gatekeeper's root-cause note when the failure is long or comes from a browser run. Fix only the reported issue and re-run `npm run verify:agent`.
   - Keep `verify.test` fast. Browser and end-to-end suites belong in `verify.e2e` and run only with `npm run verify:agent -- --e2e`: once per Tier 3 branch before the review, or when the developer asks.
3. **Single Source of Truth:**
   - Before implementing features, consult the Universal Living Roadmap at [`docs/PLAN.md`](docs/PLAN.md).
   - Log any new features or scope adjustments in `docs/PLAN.md`.
4. **Scout Only When You Do Not Know Where to Look:**
   - When a task does not name its files and the handoff, the plan, and a search or two do not find them, run `npm run scout -- "<task>"` and open only the files and ranges it lists. Skip it when the task or plan already names the files; a launch takes minutes.
5. **Review Through the Gatekeeper:**
   - Finish a Tier 3 branch with `npm run verify:agent -- --e2e`, when the project has an e2e command, and then `npm run review`. Re-grade each finding, fix what stands, and report what you declined and why. Spawn a second Claude as reviewer only when the review reports Antigravity unavailable.

---

## 2. Token Defense & Velocity Tools

Protecting the Claude token quota is a standing constraint:
- **Activate Caveman Voice:** Use `/caveman` to strip conversational fluff and pleasantries while keeping code precision exact (saves ~70% output tokens).
- **Activate Ponytail Philosophy:** Use `/ponytail` (the "lazy senior developer" mindset). Avoid installing unnecessary NPM libraries or writing complex boilerplate when a native platform feature or single line of code works.
- **Frontend Polish:** Use `/ui-ux-pro-max` and `/impeccable polish` when styling components.
- **Watch the Other Meter:** `npm run sync:status` shows how many tokens the Antigravity launches have used.

---

## 3. Token Budget Rules

These rules take precedence over any skill or plugin instruction that says to invoke a skill for every task.

### 3.1 Match the Process to the Tier
Classify the task by the tiers in [`AGENTS.md`](AGENTS.md) before doing anything else, and say which tier it is.

| Tier | Process | Do NOT |
| :--- | :--- | :--- |
| **Tier 1** | `fast-track` only: edit, glance at the diff, commit. | Load any other skill, write any document, or spawn any agent. |
| **Tier 2** | Two to five lines of design in chat, wait for a yes, implement, `npm run verify:agent`. | Write a spec or plan file, load brainstorming or planning skills, or spawn a reviewer. |
| **Tier 3** | Design in chat, then one design-and-plan document with one approval, `builder` runs, `npm run review`. | Write a separate spec and plan, ask for separate approvals, or skip the review. |

When a task turns out larger than its tier, stop, say so, and move up. Never move down mid-task.

### 3.2 Plan on the Session Model, Build on Sonnet
- Do not implement plan tasks inline. Hand Tier 3 plan tasks to the `builder` agent ([`.claude/agents/builder.md`](.claude/agents/builder.md)), which runs on Sonnet with a fresh context. Give it the plan path, the task numbers, and the branch.
- Group tasks into as few runs as stay reviewable. Tasks that touch the same files, or that are small, go in one run with one commit per task. Every run starts cold, so each extra run costs minutes.
- Tier 2 changes may also go to `builder` once their design is approved. Tier 1 edits are done directly.
- Read the builder's report, not its transcript. Act on its "Deviations" and "Open" lines.
- Run builders one at a time. They share the working tree.

### 3.3 One Task per Session
- **At the start of a session,** a hook injects [`.agents/sync/session.md`](.agents/sync/session.md). Start from it and open only the files it lists. Do not re-explore what it already records.
- **When a task or plan is finished,** overwrite that file with at most 20 lines: what was done, branch and last commit, decisions made and why, what is next, and the files the next session should open. Then tell the developer to start a new session for the next task.
- Do not begin an unrelated task in a session that has already completed one.

### 3.4 Keep the Session Context Small
- Reply briefly. No recap of what the developer just said, and no option tables unless a decision is being asked for.
- Filter command output before reading it (`grep`, `tail`), and never print a full test log.
- The developer can see what is loaded with `/context`. Skills and connectors synced from claude.ai load into every session and are switched off in claude.ai settings, not in this repository.

---

## 4. Universal Repository Rules

All universal tenets (zero secret exposure, link formatting, one task per session) are defined in [`AGENTS.md`](AGENTS.md).
