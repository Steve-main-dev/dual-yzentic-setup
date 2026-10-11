/**
 * roadmap.mjs
 * Renders the living roadmap (docs/PLAN.md) from project info and a task list.
 */

const PRIORITY_SECTIONS = [
  { priority: 'P0', heading: 'P0: Must-Have for Demo' },
  { priority: 'P1', heading: 'P1: High Impact Polish' },
  { priority: 'P2', heading: 'P2: Post-Hackathon Stretch' }
];

const oneLine = (text) => String(text ?? '').replace(/\s+/g, ' ').trim();

function renderTask(task) {
  return `- [ ] **Task ${oneLine(task.id)}: ${oneLine(task.title)}**
  - **Priority:** ${task.priority}
  - **Owner:** ${oneLine(task.owner)}
  - **Status:** Backlog
  - **Description:** ${oneLine(task.description)}
`;
}

function renderSection({ priority, heading }, tasks) {
  const matching = tasks.filter(task => task.priority === priority);
  const body = matching.length > 0 ? matching.map(renderTask).join('\n') : 'None yet.\n';
  return `## ${heading}\n\n${body}`;
}

/**
 * Generate fresh living roadmap.
 * tasks: [{ id, title, priority: 'P0'|'P1'|'P2', owner (display name), description }]
 */
export function generateRoadmap({ name, desc, dev1, dev2, preset, tasks = [] }) {
  const dateStr = new Date().toISOString().split('T')[0];
  const sections = PRIORITY_SECTIONS.map(section => renderSection(section, tasks)).join('\n---\n\n');

  return `# Universal Living Roadmap & Feature Plan: ${name}

> **For ${dev1}, ${dev2}, and AI Agents:** This document is the single source of truth for the project. No feature is implemented without an entry here. Keep it updated after every completed task.

- **Project:** ${name}
- **Objective:** ${desc}
- **Archetype:** ${preset}
- **Last Synchronized:** ${dateStr}
- **Sync Protocol:** [\`scripts/baton.mjs\`](../scripts/baton.mjs) via \`npm run verify:agent\`

---

## Mission & Hackathon Objective

${desc}

---

## Rules for Adding Features

1. **No Rogue Work:** When either developer (or their AI agent) wants to add an idea, log it below with Priority, Owner, and initial status \`[ ] Backlog\`.
2. **Prioritization Tiers:**
   - **\`P0\` (Must-Have for Demo):** The core loop required for judges to understand and experience the product.
   - **\`P1\` (High Impact Polish):** Visual enhancers, seed data, and animations that elevate demo day.
   - **\`P2\` (Post-Hackathon Stretch):** Features that can wait until after judging.
3. **Owner Assignment:** Always declare \`Owner: ${dev1}\` or \`Owner: ${dev2}\` to prevent git collisions.
4. **Git Sync Cadence:** Pull before starting a task; commit and push immediately upon completing a task (\`git commit -m "feat: [feature name]"\`).

---

## Current Sprint Focus

Active milestone: **MVP Core Scaffolding & Initial Feature Loop**

---

${sections}`;
}
