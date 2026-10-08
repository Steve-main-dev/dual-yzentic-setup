# Universal Living Roadmap & Feature Plan

> **For Dev 1, Dev 2, and AI Agents:** This document is the single source of truth for the project. No feature is implemented without an entry here. Keep it updated after every completed task.

- **Sprint Deadline:** 24-Hour Hackathon Submission
- **Last Synchronized:** 2026-10-08
- **Sync Protocol:** [`scripts/baton.mjs`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/scripts/baton.mjs) via `npm run verify:agent`

---

## Mission & Hackathon Objective

Build, test, and deliver an MVP for judge demonstration within 24 hours. Focus ruthlessly on the primary user journey, visually stunning aesthetics, and rock-solid demo data.

---

## Rules for Adding Features

1. **No Rogue Work:** When either developer (or their AI agent) wants to add an idea, log it below with Priority, Owner, and initial status `[ ] Backlog`.
2. **Prioritization Tiers:**
   - **`P0` (Must-Have for Demo):** The core loop required for judges to understand and experience the product.
   - **`P1` (High Impact Polish):** Visual enhancers, seed data, and animations that elevate demo day.
   - **`P2` (Post-Hackathon Stretch):** Features that can wait until after judging.
3. **Owner Assignment:** Always declare `Owner: Dev 1` or `Owner: Dev 2` to prevent git collisions.
4. **Git Sync Cadence:** Pull before starting a task; commit and push immediately upon completing a task (`git commit -m "feat: [feature name]"`).

---

## Current Sprint Focus

Active milestone: **MVP Core Scaffolding & Dual-Agent Setup**

---

## P0: Must-Have for Demo

- [x] **Task 0.1: Dual-Agent Synchronization Bus & Baton Setup**
  - **Priority:** P0
  - **Owner:** Dev 1 (Antigravity & Claude)
  - **Status:** In Progress
  - **Description:** Implement `scripts/baton.mjs`, `.agents/sync/`, and persona rules for token defense.

- [ ] **Task 1.1: Core Application Shell & Routing**
  - **Priority:** P0
  - **Owner:** Dev 1
  - **Status:** Backlog
  - **Description:** Scaffolds primary app shell, responsive container, and header navigation.

- [ ] **Task 1.2: Primary Feature API & Data Model**
  - **Priority:** P0
  - **Owner:** Dev 2
  - **Status:** Backlog
  - **Description:** Core data models and backend routes for the primary application flow.

- [ ] **Task 1.3: Hero Flow & Interactive Value Loop**
  - **Priority:** P0
  - **Owner:** Dev 1
  - **Status:** Backlog
  - **Description:** The primary user action that produces the "WOW" moment for judges.

---

## P1: High Impact Polish

- [ ] **Task 2.1: Rich Demo Mock Data & Trends**
  - **Priority:** P1
  - **Owner:** Dev 2
  - **Status:** Backlog
  - **Description:** Populate dashboards with realistic activity feeds, metrics, and avatars using `demo-seed-data`.

- [ ] **Task 2.2: Frontend Visual Polish & Contrast Audit**
  - **Priority:** P1
  - **Owner:** Dev 1
  - **Status:** Backlog
  - **Description:** Run UI polish pass with `ui-ux-pro-max` and `impeccable` on buttons, empty states, and badges.

- [ ] **Task 2.3: Interactive System Architecture Diagram**
  - **Priority:** P1
  - **Owner:** Dev 2
  - **Status:** Backlog
  - **Description:** Generate architecture diagrams for slide decks using `archify`.

---

## P2: Post-Hackathon Stretch

- [ ] **Task 3.1: Multi-Tenant Team Organizations**
  - **Priority:** P2
  - **Owner:** Dev 2
  - **Status:** Backlog
  - **Description:** Extended workspace collaboration for enterprise teams.

- [ ] **Task 3.2: Advanced Export to PDF / External Integrations**
  - **Priority:** P2
  - **Owner:** Dev 1
  - **Status:** Backlog
  - **Description:** Exporting generated assets to external third-party cloud services.
