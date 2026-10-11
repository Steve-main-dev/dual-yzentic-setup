#!/usr/bin/env node

/**
 * install-hooks.mjs
 * Installs git hooks into .githooks and configures git core.hooksPath.
 */

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

export function installHooks({ root = REPO_ROOT } = {}) {
  const HOOKS_DIR = path.resolve(root, '.githooks');
  const PRE_COMMIT = path.resolve(HOOKS_DIR, 'pre-commit');

  if (!fs.existsSync(HOOKS_DIR)) {
    fs.mkdirSync(HOOKS_DIR, { recursive: true });
  }

  const hookContent = `#!/bin/sh
# Git pre-commit hook enforcing Baton verification

if [ "$SKIP_VERIFY" = "1" ]; then
  exit 0
fi

echo "[Git Hook] Running Baton pre-commit verification..."
node scripts/baton.mjs verify

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
  echo ""
  echo "[Git Hook Error] Commit blocked: Baton verification failed."
  echo "Fix the reported issue or run 'npm run verify:agent' to inspect diagnostics."
  echo "To bypass (not recommended): git commit --no-verify"
  echo ""
  exit $EXIT_CODE
fi

git add .agents/sync/handoff.json 2>/dev/null
exit 0
`;

  fs.writeFileSync(PRE_COMMIT, hookContent, { mode: 0o755 });
  try {
    fs.chmodSync(PRE_COMMIT, 0o755);
  } catch {}

  try {
    execSync('git config core.hooksPath .githooks', { cwd: root });
  } catch (err) {
    console.warn(`[Hooks Warning] Could not configure git core.hooksPath: ${err.message}`);
  }

  return { success: true, hooksDir: HOOKS_DIR };
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const args = process.argv.slice(2);
  const options = {};
  const rootIndex = args.indexOf('--root');
  if (rootIndex !== -1) {
    if (!args[rootIndex + 1] || args[rootIndex + 1].startsWith('--')) {
      console.error('[Hooks Error] --root requires a path');
      process.exit(1);
    }
    options.root = path.resolve(args[rootIndex + 1]);
  }
  installHooks(options);
  console.log('[Git Hooks] Pre-commit hook installed to .githooks and configured in git.');
}
