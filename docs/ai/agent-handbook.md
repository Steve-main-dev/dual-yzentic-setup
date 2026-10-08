# AI Agent Handbook

This handbook serves as the operational onboarding manual and skills selection guide for all AI coding agents working within `dual-yzentic-setup`.

---

## 1. Initial Session Orientation

Whenever starting a new session or receiving a task in this repository:
1. **Inspect Git Status:** Run `git status` to verify current branch and uncommitted modifications.
2. **Review Recent Changes:** Check `git log -n 5 --oneline` to understand recent commits.
3. **Check the Universal Living Roadmap:** Consult [`docs/PLAN.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/PLAN.md) to understand current sprint priorities (`P0`, `P1`, `P2`) and assignees.
4. **Inspect Sync Bus:** Check [`.agents/sync/handoff.json`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/sync/handoff.json) using `npm run sync:status`.
5. **Locate Skills:** Review available procedural skills in [`.agents/skills/`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/).
6. **Check Domain Rules:** If implementing web components or APIs, check [`docs/rules/README.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/rules/README.md).

---

## 2. CLI Execution & Platform Conventions

### Execution Guidelines
- Run non-interactively (`PAGER=cat`, non-blocking flags).
- All file paths and code symbols MUST be formatted as clickable markdown links using the `file://` scheme.
- Verification is performed via the Baton Coordinator:
  ```bash
  npm run verify:agent
  ```

---

## 3. Communication & Safety Guardrails
- **Destructive Actions:** Stop and request explicit user confirmation before deleting files, dropping tables, or force-pushing.
- **Zero Secret Exposure:** Never display, print, or leak contents of `.env` files or API credentials into logs or chat. Use [`varlock`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/varlock/SKILL.md).
- **Conciseness:** Keep responses concise, evidence-driven, and focused on working deliverables.

---

## 4. Skills Quick-Selection Guide ("When to Use What")

### Core Process Skills (Superpowers Framework)

| Scenario / Task | Process Skill | Purpose |
| :--- | :--- | :--- |
| **Starting any turn / prompt** | `superpowers:using-superpowers` | Check and invoke applicable skills BEFORE any response or action |
| **New feature, idea, or creative work** | `superpowers:brainstorming` | Mandatory discovery of intent, requirements, and design before implementation |
| **Multi-step implementation planning** | `superpowers:writing-plans` | Mandatory implementation plan generation for multi-step tasks |
| **Executing implementation plans** | `superpowers:executing-plans` | Deterministic inline task execution with strict per-task verification |
| **Writing or modifying any code** | `superpowers:test-driven-development` | Mandatory Red-Green-Refactor test cycle (Tier 2/3 tasks) |
| **Bug fixing or troubleshooting** | `superpowers:systematic-debugging` | Root-cause investigation before proposing fixes (no guessing) |
| **Pre-completion claim** | `superpowers:verification-before-completion` | Pre-completion evidence gate (verify tests before claiming complete) |

---

### Hackathon & Domain Skills ([`.agents/skills/`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/))

| Scenario / Task | Recommended Skill | Purpose |
| :--- | :--- | :--- |
| **Token defense on Claude Pro** | [`caveman`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/caveman/SKILL.md) | Strips conversational filler, saves ~70% output tokens |
| **Minimalist coding & anti-over-engineering** | [`ponytail`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/ponytail/SKILL.md) | "Lazy senior developer" mode: smallest workable diff, no bloated libraries |
| **Design intelligence (React, Tailwind, Shadcn)** | [`ui-ux-pro-max`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/ui-ux-pro-max/SKILL.md) | Searchable design tokens, color palettes, typography, and UX patterns |
| **Award-winning UI polish & accessibility** | [`impeccable`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/impeccable/SKILL.md) | Precision commands: `/impeccable polish`, `bolder`, `quieter`, `audit` |
| **System architecture & sequence diagrams** | [`archify`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/archify/SKILL.md) | Generates interactive, visual architecture diagrams for judge slide decks |
| **3-minute hackathon pitch & demo flow** | [`pitch-architect`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/pitch-architect/SKILL.md) | Structured pitch formulas, live demo script, and judge Q&A preparation |
| **Realistic mock & seed data for demos** | [`demo-seed-data`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/demo-seed-data/SKILL.md) | Populates dashboards with avatars, realistic names, dynamic metrics |
| **Micro-tasks, cosmetic CSS & quick fixes** | [`fast-track`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/fast-track/SKILL.md) | Express-lane protocol for token-efficient edits without test ceremony |
| **Web application browser testing** | [`webapp-testing`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/webapp-testing/SKILL.md) | Headless Playwright automation and DOM verification |
| **Managing API keys & secrets safely** | [`varlock`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/varlock/SKILL.md) | Zero-leak secret management |
| **Security audit, auth, crypto** | [`owasp-security`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/owasp-security/SKILL.md) | Audit against OWASP Top 10 |

---

## 5. Web Development Domain Rules ([`docs/rules/`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/rules/README.md))

| Task / Scope | Rule File | Focus & Standards |
| :--- | :--- | :--- |
| **Feature Scoping & Acceptance Criteria** | [`requirements.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/rules/requirements.md) | Given/When/Then criteria, 4 UI states (loading, empty, error, success) |
| **Frontend Components & UX** | [`frontend.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/rules/frontend.md) | Server-first RSC, state boundaries, Tailwind tokens, WCAG 2.1 AA |
| **Backend APIs, DB & Security** | [`backend.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/rules/backend.md) | Zod schema validation, RFC error envelopes, transaction safety |
