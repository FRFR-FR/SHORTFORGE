#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const args = process.argv.slice(2);
function arg(name, fallback = undefined) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
}
const projectPath = path.resolve(arg('--project', 'projects/demo/episode.json'));
const errors = [];
const fail = (message) => errors.push(message);
const isObj = (value) => value && typeof value === 'object' && !Array.isArray(value);

let project;
try {
  project = JSON.parse(fs.readFileSync(projectPath, 'utf8'));
} catch (error) {
  console.error('Cannot read project JSON:', error.message);
  process.exit(1);
}

const required = ['title', 'duration_seconds', 'fps', 'width', 'height', 'episode_module', 'style', 'characters', 'shots'];
for (const key of required) if (!(key in project)) fail('Missing required field: ' + key);

if (typeof project.title !== 'string' || !project.title.trim()) fail('title must be a non-empty string');
if (!Number.isInteger(project.duration_seconds) || project.duration_seconds < 5 || project.duration_seconds > 1800) fail('duration_seconds must be an integer from 5 to 1800');
if (![24, 25, 30].includes(project.fps)) fail('fps must be 24, 25 or 30');
if (!Number.isInteger(project.width) || !Number.isInteger(project.height) || project.width < 640 || project.height < 360) fail('width/height must be integers of at least 640×360');
if (project.width * 9 !== project.height * 16) fail('Anime episodes must be horizontal 16:9');
if (!isObj(project.style)) fail('style must be an object');
else {
  for (const key of ['visual_identity', 'palette', 'lighting', 'linework', 'camera', 'motion']) {
    if (!project.style[key]) fail('style.' + key + ' is required');
  }
  if (!Array.isArray(project.style.palette) || project.style.palette.length < 4) fail('style.palette needs at least four authored colours');
}
if (!Array.isArray(project.characters) || project.characters.length < 1) fail('At least one original character is required');
else {
  const ids = new Set();
  for (const [index, character] of project.characters.entries()) {
    if (!isObj(character) || !character.id || !character.name || !character.design_notes) fail('characters[' + index + '] needs id, name and design_notes');
    else if (ids.has(character.id)) fail('Duplicate character id: ' + character.id);
    else ids.add(character.id);
  }
}
if (!Array.isArray(project.shots) || project.shots.length < 1) fail('At least one shot is required');
else {
  let cursor = 0;
  for (const [index, shot] of project.shots.entries()) {
    if (!isObj(shot)) { fail('shots[' + index + '] must be an object'); continue; }
    if (typeof shot.start !== 'number' || typeof shot.duration !== 'number' || shot.duration <= 0) {
      fail('shots[' + index + '] needs numeric start and positive duration');
      continue;
    }
    if (Math.abs(shot.start - cursor) > 0.001) fail('shots[' + index + '] starts at ' + shot.start + 's; expected ' + cursor + 's');
    if (!shot.action || !shot.camera || !shot.emotional_beat) fail('shots[' + index + '] needs action, camera and emotional_beat');
    if (shot.duration > 12) fail('shots[' + index + '] is longer than 12 seconds; add a motivated visual or camera change');
    cursor = shot.start + shot.duration;
  }
  if (Math.abs(cursor - project.duration_seconds) > 0.001) fail('Shot timeline ends at ' + cursor + 's; episode duration is ' + project.duration_seconds + 's');
  if (project.shots.length < Math.ceil(project.duration_seconds / 12)) fail('Shot count is too low for the requested episode length');
}
const moduleRel = project.episode_module || 'episode.js';
if (path.isAbsolute(moduleRel) || moduleRel.split(/[\\/]/).includes('..')) fail('episode_module must be a project-local relative path');
const modulePath = path.resolve(projectDir, moduleRel);
if (!modulePath.startsWith(projectDir + path.sep) || !fs.existsSync(modulePath)) fail('episode_module does not exist inside the project directory');
else {
  const check = spawnSync(process.execPath, ['--check', modulePath], { encoding: 'utf8' });
  if (check.status !== 0) fail('episode module syntax error: ' + (check.stderr || check.stdout).trim());
  const source = fs.readFileSync(modulePath, 'utf8');
  if (!source.includes('createEpisode')) fail('episode module must export createEpisode()');
  if (source.length < 1800) fail('episode module is too small; add purpose-built scene staging and timed animation');
}

const projectDir = path.dirname(projectPath);
if (project.assets_complete === true) {
  if (!Array.isArray(project.assets) || project.assets.length < 2) {
    fail('assets_complete=true requires a manifest with original character and environment assets.');
  } else {
    for (const [index, asset] of project.assets.entries()) {
      if (!isObj(asset) || typeof asset.path !== 'string' || !asset.path || !asset.license || !asset.kind) {
        fail('assets[' + index + '] must include local path, kind and license/provenance.');
        continue;
      }
      if (path.isAbsolute(asset.path) || asset.path.split(/[\\/]/).includes('..')) {
        fail('assets[' + index + '].path must remain inside the project directory.');
        continue;
      }
      const resolved = path.resolve(projectDir, asset.path);
      if (!resolved.startsWith(projectDir + path.sep) || !fs.existsSync(resolved) || !fs.statSync(resolved).isFile()) {
        fail('assets[' + index + '] does not point to an existing project-local file.');
      }
    }
  }
}
if (project.quality === 'master' && project.assets_complete !== true) {
  fail('Master blocked: supply and verify original final character and environment artwork / rigs before marking assets_complete=true.');
}
if (errors.length) {
  console.error('ANIMEFORGE VALIDATION FAILED');
  for (const error of errors) console.error(' - ' + error);
  process.exit(1);
}
console.log('ANIMEFORGE project valid');
console.log(project.title + ' | ' + project.duration_seconds + 's | ' + project.fps + 'fps | ' + project.width + 'x' + project.height);
console.log(project.shots.length + ' shots | ' + project.characters.length + ' characters');
