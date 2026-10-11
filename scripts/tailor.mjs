#!/usr/bin/env node

/**
 * tailor.mjs
 * Spec-driven setup tailoring: validates and applies the manifest in project-blueprint.json.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

export const ALWAYS_KEPT_SKILLS = ['tailor-setup', 'fast-track', 'caveman', 'ponytail'];

const PRIORITIES = ['P0', 'P1', 'P2'];
const OWNERS = ['dev1', 'dev2'];
const SKILL_NAME_PATTERN = /^[a-z0-9][a-z0-9-]*$/;

const isText = (value) => typeof value === 'string' && value.trim().length > 0;
const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);

/**
 * Read installed skill names without creating directories
 */
function readSkillDirs(root) {
  const read = (folder) => {
    const dir = path.resolve(root, '.agents', folder);
    if (!fs.existsSync(dir)) return [];
    return fs.readdirSync(dir, { withFileTypes: true })
      .filter(entry => entry.isDirectory() && !entry.name.startsWith('_'))
      .map(entry => entry.name)
      .sort();
  };
  return { active: read('skills'), archived: read('skills-archive') };
}

function sourceSpecProblem(sourceSpec, root) {
  if (!isText(sourceSpec)) return 'must be a repo-relative path to the project spec';
  if (path.isAbsolute(sourceSpec)) return 'must be relative to the repo root';
  const resolved = path.resolve(root, sourceSpec);
  const relative = path.relative(root, resolved);
  if (relative.startsWith('..') || path.isAbsolute(relative)) return 'must be inside the repo';
  if (!fs.existsSync(resolved) || !fs.statSync(resolved).isFile()) return `file not found: ${sourceSpec}`;
  return null;
}

/**
 * Validate the tailoring manifest. Returns a list of problems, each prefixed with its field path.
 */
export function validateManifest(blueprint, { root = REPO_ROOT } = {}) {
  const project = blueprint?.project;
  if (!isObject(project)) {
    return ['project: missing or not an object'];
  }

  const problems = [];
  const add = (field, message) => problems.push(`${field}: ${message}`);

  if (!isText(project.name)) add('project.name', 'must be a non-empty string');
  if (!isText(project.description)) add('project.description', 'must be a non-empty string');
  if (project.archetype !== 'custom') add('project.archetype', 'must be "custom"');

  const specProblem = sourceSpecProblem(project.source_spec, root);
  if (specProblem) add('project.source_spec', specProblem);

  if (!isObject(project.stack)) add('project.stack', 'must be an object');

  for (const dev of OWNERS) {
    if (!isText(project.team?.[dev]?.name)) add(`project.team.${dev}.name`, 'must be a non-empty string');
  }

  if (!Array.isArray(project.skills)) {
    add('project.skills', 'must be an array of skill names');
  } else {
    const installed = readSkillDirs(root);
    const known = new Set([...installed.active, ...installed.archived]);
    const unknown = [...new Set(project.skills)].filter(
      name => typeof name !== 'string' || !SKILL_NAME_PATTERN.test(name) || !known.has(name)
    );
    if (unknown.length > 0) {
      add('project.skills', `unknown skills: ${unknown.map(name => name || '(empty)').join(', ')}`);
    }
  }

  if (!isText(project.verify?.test)) add('project.verify.test', 'must be a non-empty command');
  const scoped = project.verify?.test_scoped;
  if (scoped !== undefined && (!isText(scoped) || !scoped.includes('{scope}'))) {
    add('project.verify.test_scoped', 'must be a command containing {scope}');
  }

  if (!Array.isArray(project.roadmap) || project.roadmap.length === 0) {
    add('project.roadmap', 'must contain at least one task');
  } else {
    const seenIds = new Set();
    project.roadmap.forEach((task, index) => {
      const field = (name) => `project.roadmap[${index}].${name}`;
      if (!isObject(task)) {
        add(`project.roadmap[${index}]`, 'must be an object');
        return;
      }
      if (!isText(task.id)) add(field('id'), 'must be a non-empty string');
      else if (seenIds.has(task.id)) add(field('id'), `duplicate id "${task.id}"`);
      else seenIds.add(task.id);
      if (!isText(task.title)) add(field('title'), 'must be a non-empty string');
      if (!PRIORITIES.includes(task.priority)) add(field('priority'), `must be one of ${PRIORITIES.join(', ')}`);
      if (!OWNERS.includes(task.owner)) add(field('owner'), `must be one of ${OWNERS.join(', ')}`);
      if (!isText(task.description)) add(field('description'), 'must be a non-empty string');
    });
  }

  return problems;
}
