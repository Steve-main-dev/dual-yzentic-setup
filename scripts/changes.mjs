/**
 * Change-set discovery (scripts/changes.mjs)
 * Answers "which files did the Builder just change?" for the baton, from git alone.
 */

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const COSMETIC_EXTENSIONS = ['.md', '.css', '.scss', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.ico'];

/**
 * Tier 1 rule: docs, styles and static assets need no test run.
 */
export function isCosmeticFile(path) {
  const lower = path.toLowerCase();
  return COSMETIC_EXTENSIONS.some(ext => lower.endsWith(ext)) || lower.startsWith('docs/');
}

const TEST_DIRS = ['tests', 'test', '__tests__', 'e2e'];
const TEST_NAME = /^test_.*\.py$|_test\..+$|\.test\..+$|\.spec\..+$/;

/**
 * A test file lives under tests/, test/, __tests__/ or e2e/, or is named like one.
 */
export function isTestFile(path) {
  const parts = path.split('/');
  return parts.slice(0, -1).some(dir => TEST_DIRS.includes(dir)) || TEST_NAME.test(parts[parts.length - 1]);
}

const CONFIG_NAMES = [
  'package.json', 'project-blueprint.json',
  'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'bun.lockb', 'uv.lock', 'poetry.lock', 'Cargo.lock', 'go.sum'
];

/**
 * Configuration is any dotfile or dot-directory (.agents, .claude, .github, .gitignore, ...), the package and
 * blueprint manifests, and the lockfiles.
 */
function isConfigFile(path) {
  const parts = path.split('/');
  return parts.some(part => part.startsWith('.')) || CONFIG_NAMES.includes(parts[parts.length - 1]);
}

/**
 * A source file is anything that is not a test, not cosmetic, and not configuration or agent state.
 */
export function isSourceFile(path) {
  return !isTestFile(path) && !isCosmeticFile(path) && !isConfigFile(path);
}

function git(root, args) {
  return execFileSync('git', args, { cwd: root, encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] });
}

// The scripts' own local state (handoff, briefs, logs). Never a change, whether or not it is git-ignored.
const LOCAL_STATE = /^\.agents\/sync\/(?!session\.md$)/;
const isTrackedWork = (file) => !LOCAL_STATE.test(file);

/**
 * Files with uncommitted changes, one entry per file (untracked directories are expanded).
 * Uses -z output so paths are never quoted; a rename lists only its new path.
 */
export function getUncommittedFiles(root = REPO_ROOT) {
  try {
    const entries = git(root, ['status', '--porcelain', '-z', '--untracked-files=all']).split('\0');
    const files = [];
    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i];
      if (entry.length < 4) continue;
      files.push(entry.slice(3));
      if (/[RC]/.test(entry.slice(0, 2))) i++; // -z lists the rename source as a separate entry
    }
    return files.filter(isTrackedWork);
  } catch {
    return [];
  }
}

/**
 * Files touched by the last commit; empty when there is no commit.
 */
export function getLastCommitFiles(root = REPO_ROOT) {
  try {
    return git(root, ['show', '--name-only', '--format=', '-z', 'HEAD']).split('\0').filter(Boolean).filter(isTrackedWork);
  } catch {
    return [];
  }
}

/**
 * The files the baton should classify: the working tree if dirty, otherwise the last commit.
 */
export function resolveChangeSet(root = REPO_ROOT) {
  const uncommitted = getUncommittedFiles(root);
  if (uncommitted.length > 0) return { files: uncommitted, source: 'working-tree' };
  const committed = getLastCommitFiles(root);
  if (committed.length > 0) return { files: committed, source: 'last-commit' };
  return { files: [], source: 'none' };
}

function hashFile(root, path) {
  try {
    return createHash('sha1').update(readFileSync(resolve(root, path))).digest('hex');
  } catch {
    return null; // listed by git but gone from disk: a deletion
  }
}

/**
 * Every uncommitted file mapped to a hash of its contents (null for a deletion).
 */
export function snapshotChanges(root = REPO_ROOT) {
  return new Map(getUncommittedFiles(root).map(path => [path, hashFile(root, path)]));
}

/**
 * Compare two snapshots. A path changed if it is new in `after` or its hash differs.
 * A path missing from `after` was deleted, or restored to its committed content: always out of scope.
 * Read-only runs may change nothing; with allowEdits only test files may change.
 */
export function checkScope(before, after, { allowEdits = false } = {}) {
  const testsWritten = [];
  const outOfScope = [];
  for (const [path, hash] of after) {
    if (before.has(path) && before.get(path) === hash) continue;
    (allowEdits && isTestFile(path) ? testsWritten : outOfScope).push(path);
  }
  for (const path of before.keys()) {
    if (!after.has(path)) outOfScope.push(path);
  }
  return { testsWritten, outOfScope };
}

/**
 * A hash of the current HEAD commit id (empty when there is no commit) and every uncommitted file with its content hash.
 * On a clean tree the change set is empty, so the commit id is what tells two commits apart.
 */
export function fingerprintChanges(root = REPO_ROOT) {
  let head = '';
  try {
    head = git(root, ['rev-parse', 'HEAD']).trim();
  } catch {
    // no commit yet
  }
  const pairs = [...snapshotChanges(root)].sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
  return createHash('sha1').update(JSON.stringify([head, pairs])).digest('hex');
}
