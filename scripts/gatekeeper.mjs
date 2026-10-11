/**
 * Gatekeeper steps for the baton (scripts/gatekeeper.mjs)
 * Launches Antigravity to write missing tests and to diagnose a failing test run, and renders the handoff ticket.
 * The baton imports this module, so it never imports the baton: state and a saveState callback come in as arguments.
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { launchAgy, appendDelegation, PLAIN_PATHS_RULE } from './agy.mjs';
import { isSourceFile, isTestFile, snapshotChanges, checkScope } from './changes.mjs';

const FAILURE_LOG = '.agents/sync/last-failure.log';
const FAILURE_FOLDERS = ['test-results', 'playwright-report'];

/**
 * True when the Gatekeeper is switched off: `--no-gatekeeper` on the command line or BATON_GATEKEEPER=0.
 */
export function gatekeeperDisabled(args, env = process.env) {
  return args.includes('--no-gatekeeper') || env.BATON_GATEKEEPER === '0';
}

/**
 * Tier 2 or 3, source files changed, and no test file changed (spec section 5.1).
 */
export function shouldWriteTests({ tier, files, disabled = false }) {
  if (disabled || (tier !== 2 && tier !== 3)) return false;
  return files.some(isSourceFile) && !files.some(isTestFile);
}

/**
 * The blueprint's source spec and test command; either is null when absent or the blueprint is unreadable.
 */
function readProject(root) {
  try {
    const project = JSON.parse(readFileSync(resolve(root, 'project-blueprint.json'), 'utf-8')).project;
    return { spec: project?.source_spec || null, testCommand: project?.verify?.test || null };
  } catch {
    return { spec: null, testCommand: null };
  }
}

function buildWritePrompt(sources, { spec, testCommand }) {
  return [
    'You are the Gatekeeper of this repository (your role is defined in GEMINI.md).',
    'The Builder changed these source files and changed no tests:',
    ...sources.map(path => `- ${path}`),
    `Read ${spec ? `docs/PLAN.md and ${spec}` : 'docs/PLAN.md'} for the intended behaviour.`,
    ...(testCommand ? [`The project runs its tests with: ${testCommand}. Write tests that suit that runner.`] : []),
    'Rules:',
    '- Write or update tests that cover the listed changes.',
    '- Touch test files only.',
    '- Run nothing.',
    '- Where the code contradicts the spec, test to the spec and say so in one line.',
    PLAIN_PATHS_RULE
  ].join('\n');
}

function buildDiagnosePrompt(root) {
  const folders = FAILURE_FOLDERS.filter(name => existsSync(resolve(root, name)));
  return [
    'A test run failed in this repository. The full output is in .agents/sync/last-failure.log.',
    ...(folders.length > 0 ? [`Test artifacts are in ${folders.map(name => `${name}/`).join(' and ')}.`] : []),
    'Find the root cause. Answer in at most 15 lines with no introduction. Give:',
    '- the failing test',
    '- the file and line',
    '- expected against actual',
    '- the most likely cause in the source',
    'Read only. Edit nothing. Run nothing.',
    PLAIN_PATHS_RULE
  ].join('\n');
}

/**
 * Run one launch with active_agent set to antigravity, restore claude whatever happens, and log the delegation.
 */
function launchAsAntigravity(state, saveState, options) {
  state.active_agent = 'antigravity';
  saveState();
  try {
    const result = launchAgy(options);
    appendDelegation(state, result.entry);
    return result;
  } finally {
    state.active_agent = 'claude';
    saveState();
  }
}

/**
 * Ask Antigravity to write tests for the changed source files. The result is 'ran' when the launch was ok, else 'skipped'.
 * The scope guard runs whatever the launch result, since a killed run may have written files.
 */
export function writeTests({ root, state, files, saveState = () => {} }) {
  const before = snapshotChanges(root);
  const launch = launchAsAntigravity(state, saveState, {
    job: 'write_tests',
    prompt: buildWritePrompt(files.filter(isSourceFile), readProject(root)),
    allowEdits: true,
    root
  });
  const { testsWritten, outOfScope } = checkScope(before, snapshotChanges(root), { allowEdits: true });
  return { result: launch.ok ? 'ran' : 'skipped', testsWritten, outOfScope, reason: launch.reason };
}

/**
 * Ask Antigravity, read only, for a root-cause note on a failed test run.
 * Returns the note (null when the launch was not ok) and the files changed during the launch, which are never reverted.
 */
export function diagnoseFailure({ root, state, output, saveState = () => {} }) {
  const logPath = resolve(root, FAILURE_LOG);
  mkdirSync(dirname(logPath), { recursive: true });
  writeFileSync(logPath, output, 'utf-8');

  const before = snapshotChanges(root);
  const launch = launchAsAntigravity(state, saveState, { job: 'diagnose', prompt: buildDiagnosePrompt(root), root });
  const { outOfScope } = checkScope(before, snapshotChanges(root));

  if (!launch.ok) {
    console.error(`[Baton] Gatekeeper diagnosis unavailable (${launch.reason}).`);
    return { note: null, outOfScope };
  }
  return { note: launch.response.trim(), outOfScope };
}

/**
 * The handoff ticket for the last verify, as Markdown.
 */
export function renderHandoff({ state, tier, files, diagnosis = null }) {
  const written = state.gatekeeper?.tests_written ?? [];
  const outOfScope = state.gatekeeper?.out_of_scope ?? [];
  const report = [];
  if (written.length > 0) report.push('Tests written:', ...written.map(path => `- ${path}`));
  if (diagnosis) report.push(...(report.length > 0 ? [''] : []), 'Diagnosis:', diagnosis);
  if (outOfScope.length > 0) {
    report.push(...(report.length > 0 ? [''] : []), 'Out of scope (not reverted):', ...outOfScope.map(path => `- ${path}`));
  }
  if (report.length === 0) report.push('Not launched.');
  if (state.gatekeeper?.result === 'skipped') {
    report.push('', 'Gatekeeper skipped: tests for this change are still owed.');
  }

  return [
    `# Agent Handoff Ticket: ${state.task_id ?? 'TASK-00'}`,
    '',
    `- Status: ${state.status}`,
    `- Tier: ${tier}`,
    '',
    '## Changes Implemented by Claude',
    ...(files.length > 0 ? files.map(path => `- ${path}`) : ['- (none)']),
    '',
    '## Verification Report by Antigravity',
    ...report,
    ''
  ].join('\n');
}

/**
 * Rewrite handoff.md for the last verify.
 */
export function writeHandoff(mdPath, details) {
  mkdirSync(dirname(mdPath), { recursive: true });
  writeFileSync(mdPath, renderHandoff(details), 'utf-8');
}
