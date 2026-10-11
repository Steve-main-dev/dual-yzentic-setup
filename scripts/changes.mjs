/**
 * Change-set discovery (scripts/changes.mjs)
 * Answers "which files did the Builder just change?" for the baton, from git alone.
 */

import { execFileSync } from 'node:child_process';
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

function git(root, args) {
  return execFileSync('git', args, { cwd: root, encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] });
}

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
    return files;
  } catch {
    return [];
  }
}

/**
 * Files touched by the last commit; empty when there is no commit.
 */
export function getLastCommitFiles(root = REPO_ROOT) {
  try {
    return git(root, ['show', '--name-only', '--format=', '-z', 'HEAD']).split('\0').filter(Boolean);
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
