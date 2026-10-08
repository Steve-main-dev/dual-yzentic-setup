# Yzentic-setup

**Universal AI-Driven Development Foundation**

A standardized, multi-agent development environment designed for autonomous coding agents—including **Google Antigravity**, **Anthropic Claude Code**, **Cursor AI**, and **Stably Orca**—built on the **Superpowers** engineering operating system and progressive domain skills.

---

## 🌟 Key Architecture & Highlights

* **Single Source of Truth ([`AGENTS.md`](./AGENTS.md)):** Unified root behavioral rules, non-interactive execution standards, zero secret exposure, and task tracking.
* **Platform Native Pointers:** Lightweight compatibility links for [Claude Code](./CLAUDE.md), [Gemini CLI / Antigravity](./GEMINI.md), and [Cursor](./.cursorrules).
* **Superpowers Engineering Operating System:** Formalized Red-Green-Refactor TDD cycles, systematic root-cause debugging, brainstorming gates, and pre-completion evidence checks.
* **Progressive Skills Architecture ([`.agents/skills/`](./.agents/skills/)):** 21 modular domain skills triggered on-demand (covering webapp testing, OWASP security reviews, secret management with Varlock, MCP server creation, and Orca orchestration).
* **Engineering Handbook & Workflows ([`docs/ai/`](./docs/ai/)):**
  - [`docs/ai/agent-handbook.md`](./docs/ai/agent-handbook.md): Complete "When to Use What" skills selection guide and CLI cheat-sheets.
  - [`docs/ai/workflows.md`](./docs/ai/workflows.md): TDD workflows, branching strategies, and task tracking protocols.
  - [`docs/ai/architecture.md`](./docs/ai/architecture.md): Modular decomposition boundaries and lifecycle specs.
  - [`docs/specs/`](./docs/specs/): Dedicated home for approved feature specifications.

---

## 🚀 Running Verification Tests

This repository features an automated self-verification test suite that validates root rules, skill YAML frontmatter schemas, documentation structure, and markdown link integrity:

```powershell
# Run the automated verification test suite
py -m unittest discover tests -v
```

---

## 📂 Repository Directory Layout

```text
Yzentic-setup/
├── AGENTS.md                  # Universal agent contract and behavioral rules
├── GEMINI.md                  # Antigravity & Gemini CLI pointer
├── CLAUDE.md                  # Claude Code pointer
├── .cursorrules               # Cursor AI pointer
├── .agents/
│   └── skills/                # 21 on-demand domain skills
├── docs/
│   ├── ai/                    # Agent handbook, workflows, and architecture
│   ├── rules/                 # Web development domain rules (requirements, frontend, backend)
│   └── specs/                 # Feature designs and technical specifications
└── tests/                     # Automated link, schema, and rule integrity tests
```
