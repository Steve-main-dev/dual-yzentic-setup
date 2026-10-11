#!/usr/bin/env node

/**
 * guard-commands.mjs
 * Claude Code PreToolUse hook: blocks full test-suite runs issued through the shell tools.
 * Full suites go through the baton (npm run verify:agent), which distills their output.
 */

import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);

const SHELL_TOOLS = ['Bash', 'PowerShell'];
const PACKAGE_MANAGERS = ['npm', 'pnpm', 'yarn', 'bun'];
const RUNNER_PREFIXES = ['npx', 'bunx', 'pnpx'];
const PYTHON = ['python', 'python3', 'py'];
const FILTER_FLAGS = ['-k', '-g', '--grep', '-t', '--testNamePattern', '--test-name-pattern'];

const REASON = 'Blocked by project rule (CLAUDE.md): full test suites run through the baton, which distills their output. '
  + 'Use `npm run verify:agent -- --tier 2 --scope <test file>` for one file, or `npm run verify:agent -- --tier 3` for the whole suite.';

const isFlag = (token) => token.startsWith('-');
const looksLikeTarget = (token) => !isFlag(token) && /[\/\\.:]/.test(token);

/**
 * A run is scoped when it names a file or module, or carries a test-name filter.
 */
function isScoped(args) {
  return args.some(looksLikeTarget) || args.some(token => FILTER_FLAGS.includes(token));
}

/**
 * Strip leading environment assignments and package-runner prefixes from one command segment.
 */
function commandTokens(segment) {
  const tokens = segment.trim().split(/\s+/).filter(Boolean);
  while (tokens.length > 0 && /^[A-Za-z_][A-Za-z0-9_]*=/.test(tokens[0])) tokens.shift();
  if (RUNNER_PREFIXES.includes(tokens[0])) tokens.shift();
  if (PACKAGE_MANAGERS.includes(tokens[0]) && ['exec', 'dlx'].includes(tokens[1])) tokens.splice(0, 2);
  return tokens;
}

function isFullSuiteRun(tokens) {
  const [head, second, third] = tokens;
  if (!head) return false;

  // npm test, npm run test, yarn test, ...
  if (PACKAGE_MANAGERS.includes(head)) {
    const rest = second === 'run' ? tokens.slice(2) : tokens.slice(1);
    if (!['test', 't'].includes(rest[0])) return false;
    return !isScoped(rest.slice(1).filter(token => token !== '--'));
  }

  // python -m pytest, python -m unittest
  if (PYTHON.includes(head) && second === '-m') {
    const args = tokens.slice(3);
    if (third === 'pytest') return !isScoped(args);
    if (third === 'unittest') return args.length === 0 || args.includes('discover');
    return false;
  }

  if (['pytest', 'py.test', 'jest'].includes(head)) return !isScoped(tokens.slice(1));
  if (head === 'vitest') return !isScoped(tokens.slice(1).filter(token => token !== 'run'));
  if (head === 'playwright' && second === 'test') return !isScoped(tokens.slice(2));

  return false;
}

/**
 * Returns the offending segment when a shell command runs a full test suite, otherwise null.
 */
export function findBlockedCommand(command) {
  if (typeof command !== 'string') return null;
  const segments = command.split(/&&|\|\||[;|\n]/);
  for (const segment of segments) {
    if (isFullSuiteRun(commandTokens(segment))) return segment.trim();
  }
  return null;
}

async function readStdin() {
  let data = '';
  for await (const chunk of process.stdin) data += chunk;
  return data;
}

export async function main() {
  let input;
  try {
    input = JSON.parse(await readStdin());
  } catch {
    return; // Not a hook payload: never block on our own parsing failure
  }

  if (!SHELL_TOOLS.includes(input?.tool_name)) return;
  const blocked = findBlockedCommand(input.tool_input?.command);
  if (!blocked) return;

  console.log(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: `${REASON} Offending command: ${blocked}`
    }
  }));
}

// Execute if run directly
if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  main();
}
