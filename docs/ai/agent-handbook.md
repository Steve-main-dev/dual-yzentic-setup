# AI Agent Handbook

This handbook serves as the operational onboarding manual and skills selection guide for all AI coding agents working within `Yzentic-setup`.

---

## 1. Initial Session Orientation

Whenever starting a new session or receiving a task in this repository:
1. **Inspect Git Status:** Run `git status` to verify current branch and uncommitted modifications.
2. **Review Recent Changes:** Check `git log -n 5 --oneline` to understand recent commits.
3. **Check Relevant Specs:** If working on an existing feature, review specifications in [`docs/specs/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/specs/).
4. **Locate Skills:** Review available procedural skills in [`.agents/skills/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/).
5. **Check Domain Rules:** If implementing web components, APIs, or requirements, check [`docs/rules/README.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/rules/README.md) to locate applicable domain standards.

---

## 2. CLI Execution & Platform Conventions

### Operating System & Shell Guidelines
- **Windows / PowerShell Rules:**
  - Execute commands non-interactively.
  - Set UTF-8 encoding for Python outputs: `$env:PYTHONIOENCODING="utf-8"`.
  - Use double quotes around paths containing spaces or special characters.
  - Do NOT issue bare interactive commands that prompt for user input (e.g. interactive git rebase, vim, nano).
- **POSIX / Linux Rules:**
  - Run with `PAGER=cat` to avoid paging traps.
  - Standard flags: `-y` or `--non-interactive`.

### Hyperlinks in Responses and Documents
- All file paths and code symbols MUST be formatted as clickable markdown links using the `file://` scheme.
- Examples:
  - File: [`AGENTS.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/AGENTS.md)
  - Subdirectory: [`docs/ai/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/ai/)
  - Always normalize Windows backslashes (`\`) to forward slashes (`/`) in URIs.

---

## 3. Communication & Safety Guardrails
- **Destructive Actions:** Stop and request explicit user confirmation before:
  - Deleting files or branches.
  - Running database drop/reset commands.
  - Force-pushing to remote branches.
- **Secret Zero-Exposure:** Never display, print, or leak contents of `.env` files or API credentials into logs or chat. Use [`varlock`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/varlock/SKILL.md) for secret operations.
- **Conciseness:** Keep responses concise, evidence-driven, and focused on working deliverables.

---

## 4. Skills Quick-Selection Guide ("When to Use What")

### Core Process Skills (Superpowers Framework)

Process skills dictate *how* agents think, plan, and verify code. They are provided globally via the installed `superpowers` plugin. Agents MUST invoke these before touching implementation code:

| Scenario / Task | Process Skill | Purpose |
| :--- | :--- | :--- |
| **Starting any turn / prompt** | `superpowers:using-superpowers` | Check and invoke applicable skills BEFORE any response or action |
| **New feature, idea, or creative work** | `superpowers:brainstorming` | Mandatory discovery of intent, requirements, and design before implementation |
| **Multi-step implementation planning** | `superpowers:writing-plans` | Mandatory implementation plan generation for multi-step tasks |
| **Executing implementation plans** | `superpowers:executing-plans` / `superpowers:subagent-driven-development` | Deterministic task execution (inline or subagent-driven) |
| **Writing or modifying any code** | `superpowers:test-driven-development` | Mandatory Red-Green-Refactor test cycle (no production code without a failing test first) |
| **Bug fixing or troubleshooting** | `superpowers:systematic-debugging` | Root-cause investigation before proposing fixes (no guessing) |
| **Isolated feature workspace** | `superpowers:using-git-worktrees` | Create parallel git worktrees to keep main workspace unpolluted |
| **Reviewing completed changes** | `superpowers:requesting-code-review` & `superpowers:receiving-code-review` | Verification and review rigor before merging |
| **Pre-completion claim** | `superpowers:verification-before-completion` | Pre-completion evidence gate (verify tests before claiming complete) |
| **Concluding a feature branch** | `superpowers:finishing-a-development-branch` | Guided menu to verify tests, merge locally, PR, and clean worktree |

---

### Domain & Tooling Skills ([`.agents/skills/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/))

Before performing specialized engineering tasks, activate the corresponding on-demand skill from [`.agents/skills/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/):

| Scenario / Task | Recommended Skill | Purpose |
| :--- | :--- | :--- |
| **Planning interview & requirement Q&A** | [`blueprint`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/blueprint/SKILL.md) | Structured interview exploring intent, constraints, and architecture |
| **Finalizing blueprint into an implementation plan** | [`blueprint-generate`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/blueprint-generate/SKILL.md) | Convert collected blueprint interview context into an actionable plan |
| **Self-critique & iterative LLM refinement** | [`agentic-eval`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/agentic-eval/SKILL.md) | Evaluator-optimizer loops, rubric-based grading, and output scoring |
| **Security audit, auth, crypto, untrusted inputs** | [`owasp-security`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/owasp-security/SKILL.md) | Audit against OWASP Top 10, ASVS 5.0, and agentic vulnerabilities |
| **Web application browser testing** | [`webapp-testing`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/webapp-testing/SKILL.md) | Playwright headless automation, DOM inspection, and screenshots |
| **Managing API keys & secrets safely** | [`varlock`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/varlock/SKILL.md) | Zero-leak secret management; prevents exposing `.env` in context |
| **Orca worktree, terminal, & browser control** | [`orca-cli`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/orca-cli/SKILL.md) | Headless control of isolated worktrees, PTYs, and Orca browser |
| **Supervising multi-agent workers & DAGs** | [`orchestration`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/orchestration/SKILL.md) | Coordinate subordinate agents with threaded messages and DAGs |
| **Handoff between subagents or orchestrators** | [`multi-agent-handoff`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/multi-agent-handoff/SKILL.md) | Standardized markdown artifact for state, progress, and next steps |
| **Designing AI tools & function schemas** | [`tool-design`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/tool-design/SKILL.md) | Design defensible, agent-friendly tools that models invoke reliably |
| **Building Model Context Protocol (MCP) servers** | [`mcp-builder`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/mcp-builder/SKILL.md) | Build production-ready MCP servers in Python (FastMCP) or TypeScript |
| **Creating, benchmarking, & evaluating skills** | [`skill-creator`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/skill-creator/SKILL.md) | Anthropic toolchain to author, run evals, and optimize skill triggers |
| **Advanced prompt engineering & system prompts** | [`prompt-engineer`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/prompt-engineer/SKILL.md) | Structure system prompts, few-shot examples, and chain-of-thought |
| **Discovering & installing new agent skills** | [`find-skills`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/find-skills/SKILL.md) | Search open registries to discover and install community skills |
| **OpenAI API & Codex reference** | [`openai-docs`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/openai-docs/SKILL.md) | Official OpenAI documentation, model selection, and Codex manuals |
| **UI/UX design specs & interface reviews** | [`oiloil-ui-ux-guide`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/oiloil-ui-ux-guide/SKILL.md) | Generate design specifications, select style families, and review UI |
| **Complex React/Tailwind web artifacts** | [`web-artifacts-builder`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/web-artifacts-builder/SKILL.md) | Multi-component artifacts with React, Tailwind CSS, and shadcn/ui |
| **Responsive HTML emails** | [`email-html-mjml`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/email-html-mjml/SKILL.md) | Build, compile, and troubleshoot responsive HTML email templates |
| **UI/UX design auditing & accessibility reviews** | [`design-auditor`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/design-auditor/SKILL.md) | Comprehensive audit against 19 rules across Figma, code, a11y, and dark patterns |
| **Micro-tasks, cosmetic CSS & quick fixes** | [`fast-track`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/fast-track/SKILL.md) | Express-lane protocol for token-efficient small edits without heavy test ceremony |
| **On-demand documentation ingestion & skill synthesis** | [`skill-seeker`](file:///C:/Users/Admin/Yzen/Yzentic-setup/.agents/skills/skill-seeker/SKILL.md) | Convert documentation sites, GitHub repos, and PDFs into staged, validated agent skills |

---

### Web Development Domain Rules ([`docs/rules/`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/rules/README.md))

For full-stack web application development, load domain rules on-demand matching your active task:

| Task / Scope | Rule File | Focus & Standards |
| :--- | :--- | :--- |
| **Feature Scoping & Acceptance Criteria** | [`requirements.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/rules/requirements.md) | Given/When/Then criteria, mandatory 4 UI states (loading, empty, error, success), DoD |
| **Frontend Components & UX** | [`frontend.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/rules/frontend.md) | Server-first RSC, state boundaries, Tailwind tokens, WCAG 2.1 AA A11y, Core Web Vitals |
| **Backend APIs, DB & Security** | [`backend.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/rules/backend.md) | Zod schema validation, RFC error envelopes, Prisma/Drizzle transactions, HttpOnly cookies, CSRF |
| **Rule Directory Index & Routing** | [`docs/rules/README.md`](file:///C:/Users/Admin/Yzen/Yzentic-setup/docs/rules/README.md) | Master overview and glanceable "When to Read What" routing table |
