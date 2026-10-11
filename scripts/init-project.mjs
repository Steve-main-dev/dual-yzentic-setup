#!/usr/bin/env node

/**
 * init-project.mjs
 * Project Blueprint & Dynamic Repo Tailoring Wizard.
 */

import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline/promises';
import { fileURLToPath } from 'node:url';
import { syncSkillsToArchetype, listSkills } from './skills-manager.mjs';
import { installHooks } from './install-hooks.mjs';
import { scaffoldProject } from './scaffolder.mjs';
import { generateRoadmap } from './roadmap.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

const BLUEPRINT_PATH = path.resolve(REPO_ROOT, 'project-blueprint.json');
const PLAN_PATH = path.resolve(REPO_ROOT, 'docs', 'PLAN.md');
const PACKAGE_PATH = path.resolve(REPO_ROOT, 'package.json');
const HANDOFF_JSON_PATH = path.resolve(REPO_ROOT, '.agents', 'sync', 'handoff.json');
const HANDOFF_MD_PATH = path.resolve(REPO_ROOT, '.agents', 'sync', 'handoff.md');

/**
 * Placeholder roadmap tasks for a freshly initialized archetype project
 */
function defaultTasks(dev1, dev2) {
  return [
    { id: '1.1', title: 'Core Application Shell & Navigation', priority: 'P0', owner: dev1, description: 'Scaffolds primary app shell, responsive container, and header navigation.' },
    { id: '1.2', title: 'Core Data Models & API Endpoints', priority: 'P0', owner: dev2, description: 'Core data models and backend routes for the primary application flow.' },
    { id: '1.3', title: 'Hero Flow & Interactive Value Loop', priority: 'P0', owner: dev1, description: 'The primary user action that produces the "WOW" moment for judges.' },
    { id: '2.1', title: 'Demo Mock & Realistic Seed Data', priority: 'P1', owner: dev2, description: 'Populate realistic transactions, profiles, and state using demo-seed-data.' },
    { id: '2.2', title: 'UI Contrast, Responsive Refinement & Polish', priority: 'P1', owner: dev1, description: 'Polish typography, animations, and WCAG contrast using ui-ux-pro-max and impeccable.' },
    { id: '3.1', title: 'Secondary Edge-Case Workflows', priority: 'P2', owner: dev2, description: 'Advanced configurations and secondary administrative settings.' }
  ];
}

/**
 * Initialize project with options
 */
export function initProject({ preset, name, desc, dev1, dev2, scaffold = true }) {
  if (!fs.existsSync(BLUEPRINT_PATH)) {
    throw new Error(`project-blueprint.json not found at ${BLUEPRINT_PATH}`);
  }

  const blueprint = JSON.parse(fs.readFileSync(BLUEPRINT_PATH, 'utf-8'));
  const archetype = blueprint.archetypes?.[preset];

  if (!archetype) {
    const available = Object.keys(blueprint.archetypes || {}).join(', ');
    throw new Error(`Archetype '${preset}' not found. Available archetypes: ${available}`);
  }

  // 1. Soft-delete skills to match archetype
  const syncResult = syncSkillsToArchetype(preset);

  // 2. Update project-blueprint.json
  blueprint.status = 'initialized';
  blueprint.project.name = name || blueprint.project.name || 'my-project';
  blueprint.project.description = desc || blueprint.project.description || 'Project';
  blueprint.project.archetype = preset;
  if (!blueprint.project.team) blueprint.project.team = {};
  blueprint.project.team.dev1 = { name: dev1 || 'Dev 1', role: 'Fullstack' };
  blueprint.project.team.dev2 = { name: dev2 || 'Dev 2', role: 'Frontend' };
  fs.writeFileSync(BLUEPRINT_PATH, JSON.stringify(blueprint, null, 2), 'utf-8');

  // 3. Update package.json
  if (fs.existsSync(PACKAGE_PATH)) {
    const pkg = JSON.parse(fs.readFileSync(PACKAGE_PATH, 'utf-8'));
    pkg.name = (name || pkg.name).toLowerCase().replace(/[^a-z0-9_-]/g, '-');
    pkg.description = desc || pkg.description;
    fs.writeFileSync(PACKAGE_PATH, JSON.stringify(pkg, null, 2), 'utf-8');
  }

  // 4. Update docs/PLAN.md
  const roadmapContent = generateRoadmap({
    name: blueprint.project.name,
    desc: blueprint.project.description,
    dev1: dev1 || 'Dev 1',
    dev2: dev2 || 'Dev 2',
    preset,
    tasks: defaultTasks(dev1 || 'Dev 1', dev2 || 'Dev 2')
  });
  fs.writeFileSync(PLAN_PATH, roadmapContent, 'utf-8');

  // 5. Reset Sync Bus
  const handoffData = {
    version: '1.0',
    task_id: 'INIT-01',
    active_agent: 'claude',
    status: 'idle',
    turn_count: 0,
    max_turns: 5,
    last_updated: new Date().toISOString(),
    summary: `Project initialized (${blueprint.project.name} - ${preset})`,
    files_modified: []
  };
  fs.writeFileSync(HANDOFF_JSON_PATH, JSON.stringify(handoffData, null, 2), 'utf-8');

  const handoffMd = `# Agent Handoff Ticket: INIT-01

- **Status:** idle
- **Active Agent:** claude
- **Turn:** 0 / 5
- **Timestamp:** ${new Date().toISOString()}

## Project Initialized
- **Name:** ${blueprint.project.name}
- **Archetype:** ${preset}
- **Active Skills:** ${syncResult.active_count} (Archived: ${syncResult.archived_count})
- **Team:** ${dev1 || 'Dev 1'} & ${dev2 || 'Dev 2'}
`;
  fs.writeFileSync(HANDOFF_MD_PATH, handoffMd, 'utf-8');

  // 6. Scaffold starter code into src/
  let scaffoldResult = null;
  if (scaffold !== false) {
    scaffoldResult = scaffoldProject({
      preset,
      name: blueprint.project.name,
      desc: blueprint.project.description,
      dev1: dev1 || 'Dev 1',
      dev2: dev2 || 'Dev 2',
      root: REPO_ROOT
    });
  }

  // 7. Install git pre-commit hook
  installHooks();

  return {
    success: true,
    project: blueprint.project,
    syncResult,
    scaffoldResult
  };
}

/**
 * Interactive or CLI Entry
 */
export async function main() {
  const args = process.argv.slice(2);
  let preset = null;
  let name = null;
  let desc = null;
  let dev1 = null;
  let dev2 = null;
  let isNonInteractive = false;
  let shouldScaffold = true;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--preset' && args[i + 1]) preset = args[++i];
    if (args[i] === '--name' && args[i + 1]) name = args[++i];
    if (args[i] === '--desc' && args[i + 1]) desc = args[++i];
    if (args[i] === '--dev1' && args[i + 1]) dev1 = args[++i];
    if (args[i] === '--dev2' && args[i + 1]) dev2 = args[++i];
    if (args[i] === '--non-interactive') isNonInteractive = true;
    if (args[i] === '--skip-scaffold') shouldScaffold = false;
  }

  try {
    // If running in terminal interactively
    if (!isNonInteractive && process.stdin.isTTY && !preset) {
      const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
      console.log('\n======================================================');
      console.log('   🚀 Project Blueprint & Repo Tailoring Wizard');
      console.log('======================================================\n');

      name = (await rl.question('1. Project Name (e.g. ai-flow-canvas): ')).trim() || 'my-hackathon-app';
      desc = (await rl.question('2. 1-Sentence Project Mission / Pitch: ')).trim() || 'Rapid MVP Prototyping';
      
      console.log('\n3. Select Project Archetype:');
      console.log('   [1] fullstack-web     (Next.js/Vite + Full Backend + DB)');
      console.log('   [2] ai-agent-app      (FastAPI/Node + Prompt & Agentic Eval)');
      console.log('   [3] frontend-dashboard (Vite + React + Tailwind + Charts)');
      console.log('   [4] minimal-hackathon (Ultra-Lean Core Suite Only)');
      const choice = (await rl.question('   Choice [1-4, default 1]: ')).trim();

      const presetMap = {
        '1': 'fullstack-web',
        '2': 'ai-agent-app',
        '3': 'frontend-dashboard',
        '4': 'minimal-hackathon'
      };
      preset = presetMap[choice] || 'fullstack-web';

      dev1 = (await rl.question('\n4. Developer 1 Name / Handle (e.g. Steve): ')).trim() || 'Dev 1';
      dev2 = (await rl.question('5. Developer 2 Name / Handle (e.g. Partner): ')).trim() || 'Dev 2';
      rl.close();
    } else if (!preset) {
      preset = 'fullstack-web';
    }

    const res = initProject({
      preset,
      name: name || 'my-hackathon-app',
      desc: desc || 'Hackathon Prototype',
      dev1: dev1 || 'Dev 1',
      dev2: dev2 || 'Dev 2'
    });

    console.log('\n[SUCCESS] Project successfully initialized and tailored!');
    console.log(`- Project:       ${res.project.name}`);
    console.log(`- Archetype:     ${res.project.archetype}`);
    console.log(`- Active Skills: ${res.syncResult.active_count} active (Archived ${res.syncResult.archived_count} into .agents/skills-archive/)`);
    console.log(`- Roadmap:       Fresh docs/PLAN.md generated for ${res.project.team.dev1.name} & ${res.project.team.dev2.name}`);
    console.log(`- Sync Bus:      Reset to idle in .agents/sync/handoff.json`);
    console.log('\nYou can now start pair-programming with Claude Code and Antigravity!\n');
    process.exit(0);
  } catch (err) {
    console.error(`\n[Init Project Error] ${err.message}\n`);
    process.exit(1);
  }
}

// Execute if run directly
if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  main();
}
