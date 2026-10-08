# Web Development Rules Directory

This directory defines the modular domain standards for modern full-stack web application development within `Yzentic-setup`. It standardizes patterns across **Next.js (React 19)**, **Tailwind CSS**, **Node/Bun**, **Prisma/Drizzle**, and **Zod**.

---

## When to Read What (On-Demand Agent Routing)

To preserve context window tokens, agents MUST NOT load all rules upfront. Consult only the specific rule file matching your active task:

| Developer / Agent Task | Rule File | Purpose & Focus |
| :--- | :--- | :--- |
| **Scoping a feature, writing PRD, or defining user stories** | [`requirements.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/rules/requirements.md) | Given/When/Then acceptance criteria, mandatory 4 UI states, and Definition of Done |
| **Building UI components, forms, state, styling, or layouts** | [`frontend.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/rules/frontend.md) | Server-first RSC, state boundaries, Tailwind tokens, WCAG 2.1 AA A11y, Core Web Vitals |
| **Creating API endpoints, database mutations, schemas, or auth** | [`backend.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/rules/backend.md) | Zod validation, RFC error envelopes, Prisma/Drizzle transactions, HttpOnly cookies, CSRF, CSP |
| **Testing strategy, TDD cycles, branching, or PR reviews** | [`docs/ai/workflows.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/ai/workflows.md) | TDD Red-Green-Refactor, Vitest/RTL/Playwright pyramid, and PR submission checklist |

---

## Architectural Principles
1. **Single Source of Truth:** Domain rules reside here; procedural rules reside in [`AGENTS.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/AGENTS.md) and [`docs/ai/workflows.md`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/docs/ai/workflows.md).
2. **Glanceable & Token-Lean:** Rules are structured around concise principles, checklists, and Dos/Don'ts tables rather than heavy inline code blocks.
3. **Automated Verification:** All rule documents are verified by [`tests/test_rules_integrity.py`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/tests/test_rules_integrity.py).
