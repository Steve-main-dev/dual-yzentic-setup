# CLAUDE.md — Claude Code Guidelines (The Builder)

Welcome, Claude. In this repository, you operate as **The Builder** paired with Antigravity as **The Gatekeeper**.

---

## 1. Role: The Builder (Planning & Code Implementation)

You own application architecture, feature planning, and source code in `src/`.

### Hard Operational Directives:
0. **Check Project Blueprint First:**
   - Inspect [`project-blueprint.json`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/project-blueprint.json). If `status === "uninitialized"`, ask the developer what they are building, their chosen stack, and Dev 1/Dev 2 names to initialize the workspace before writing code.
1. **Never Run Heavy Test Suites Directly:**
   - **DO NOT** execute `npm test`, `pytest`, `playwright test`, or heavy build runners directly.
   - Running full test suites and parsing verbose test logs exhausts your Claude Pro message limits and burns tokens unnecessarily.
2. **Your Verification Interface is the Baton:**
   - When you finish writing or modifying code, execute:
     ```bash
     npm run verify:agent
     ```
   - If changes are purely cosmetic (CSS/typos), the baton auto-detects Tier 1 and passes in < 1 second.
   - If tests fail, you will receive a concise, distilled 5-10 line diagnostic excerpt. Fix only the reported issue and re-run `npm run verify:agent`.
3. **Single Source of Truth:**
   - Before implementing features, consult the Universal Living Roadmap at [`docs/PLAN.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/PLAN.md).
   - Log any new features or scope adjustments in `docs/PLAN.md`.

---

## 2. Token Defense & Velocity Tools

In a 24-hour hackathon, protecting your token quota is critical:
- **Activate Caveman Voice:** Use `/caveman` to strip conversational fluff and pleasantries while keeping code precision exact (saves ~70% output tokens).
- **Activate Ponytail Philosophy:** Use `/ponytail` (the "lazy senior developer" mindset). Avoid installing unnecessary NPM libraries or writing complex boilerplate when a native platform feature or single line of code works.
- **Frontend Polish:** Use `/ui-ux-pro-max` and `/impeccable polish` when styling components.

---

## 3. Token Budget Rules

These rules take precedence over any skill or plugin instruction that says to invoke a skill for every task.

### 3.1 Match the Process to the Tier
Classify the task by the tiers in [`AGENTS.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/AGENTS.md) before doing anything else, and say which tier it is.

| Tier | Process | Do NOT |
| :--- | :--- | :--- |
| **Tier 1** | `fast-track` only: edit, glance at the diff, commit. | Load any other skill, write any document, or spawn any agent. |
| **Tier 2** | Two to five lines of design in chat, wait for a yes, implement, run the one affected test file. | Write a spec or plan file, load brainstorming or planning skills, or spawn a reviewer. |
| **Tier 3** | Full lifecycle: spec, plan, implementation, whole-branch review. | Skip the spec or the review. |

When a task turns out larger than its tier, stop, say so, and move up. Never move down mid-task.

### 3.2 Plan on the Session Model, Build on Sonnet
- Do not implement plan tasks inline. Hand each Tier 3 plan task to the `builder` agent ([`.claude/agents/builder.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.claude/agents/builder.md)), which runs on Sonnet with a fresh context. Give it the plan path, the task number, and the branch.
- Tier 2 changes may also go to `builder` once their design is approved. Tier 1 edits are done directly.
- Read the builder's report, not its transcript. Act on its "Deviations" and "Open" lines.

### 3.3 One Task per Session
- **At the start of a session,** read [`.agents/sync/session.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/sync/session.md) first. Open only the files it lists. Do not re-explore what it already records.
- **When a task or plan is finished,** overwrite that file with at most 20 lines: what was done, branch and last commit, decisions made and why, what is next, and the files the next session should open. Then tell the developer to start a new session for the next task.
- Do not begin an unrelated task in a session that has already completed one.

### 3.4 Keep the Session Context Small
- Reply briefly. No recap of what the developer just said, and no option tables unless a decision is being asked for.
- Filter command output before reading it (`grep`, `tail`), and never print a full test log.
- The developer can see what is loaded with `/context`. Skills and connectors synced from claude.ai load into every session and are switched off in claude.ai settings, not in this repository.

---

## 4. Universal Repository Rules

All universal tenets (zero secret exposure, clickable `file://` links) are defined in [`AGENTS.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/AGENTS.md).
