#!/usr/bin/env node

/**
 * session-context.mjs
 * Claude Code SessionStart hook: injects the session handoff, the blueprint status, and the
 * tier rules, so a new session starts from them without having to be told to read anything.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

const MAX_HANDOFF_LINES = 40;

function readText(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf-8');
  } catch {
    return null;
  }
}

function blueprintLine(root) {
  const raw = readText(path.resolve(root, 'project-blueprint.json'));
  if (raw === null) return 'Blueprint: project-blueprint.json not found.';
  try {
    const status = JSON.parse(raw).status;
    if (status === 'initialized') return 'Blueprint: initialized.';
    return `Blueprint: ${status ?? 'unknown'}. Before writing project code, ask what the developer is building, `
      + 'then use the tailor-setup skill (a spec exists) or `npm run init:project` (an archetype fits).';
  } catch {
    return 'Blueprint: project-blueprint.json is not valid JSON.';
  }
}

function handoffBlock(root) {
  const raw = readText(path.resolve(root, '.agents', 'sync', 'session.md'));
  if (raw === null || raw.trim().length === 0) {
    return 'No session handoff recorded (.agents/sync/session.md is missing or empty).';
  }
  const lines = raw.trimEnd().split(/\r?\n/);
  if (lines.length <= MAX_HANDOFF_LINES) return lines.join('\n');
  return [
    ...lines.slice(0, MAX_HANDOFF_LINES),
    `... [truncated ${lines.length - MAX_HANDOFF_LINES} lines; the handoff should stay under 20]`
  ].join('\n');
}

export function buildContext(root = REPO_ROOT) {
  return [
    'Project session context (injected by .claude/settings.json):',
    blueprintLine(root),
    'Process by tier: Tier 1 = fast-track only, no documents or agents. Tier 2 = a few lines of design in chat, '
      + 'wait for a yes, no spec or plan file. Tier 3 = spec, plan, builder agent per task, `npm run review`.',
    'Tests: never run a full suite directly; use `npm run verify:agent`. '
      + 'Start from the handoff below and open only the files it lists.',
    '',
    '--- .agents/sync/session.md ---',
    handoffBlock(root)
  ].join('\n');
}

export function main() {
  const args = process.argv.slice(2);
  const rootIndex = args.indexOf('--root');
  const root = rootIndex !== -1 && args[rootIndex + 1] ? path.resolve(args[rootIndex + 1]) : REPO_ROOT;

  let additionalContext;
  try {
    additionalContext = buildContext(root);
  } catch (err) {
    additionalContext = `Project session context unavailable: ${err.message}`;
  }

  console.log(JSON.stringify({ hookSpecificOutput: { hookEventName: 'SessionStart', additionalContext } }));
}

// Execute if run directly
if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  main();
}
