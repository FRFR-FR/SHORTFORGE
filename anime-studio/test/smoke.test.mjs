import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const project = path.join(root, 'projects/demo/episode.json');

test('demo project passes the production schema validator', () => {
  const result = spawnSync(process.execPath, [path.join(root, 'src/validate.mjs'), '--project', project], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr || result.stdout);
  assert.match(result.stdout, /ANIMEFORGE project valid/);
});

test('demo is horizontal 16:9 at 30 fps', () => {
  const data = JSON.parse(fs.readFileSync(project, 'utf8'));
  assert.equal(data.width * 9, data.height * 16);
  assert.equal(data.fps, 30);
  assert.ok(data.duration_seconds * data.fps > 0);
});

test('demo episode module is valid JavaScript and uses the runtime kit', () => {
  const modulePath = path.join(root, 'projects/demo/episode.js');
  const result = spawnSync(process.execPath, ['--check', modulePath], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  const source = fs.readFileSync(modulePath, 'utf8');
  assert.match(source, /export async function createEpisode/);
  assert.match(source, /createCyberpunkCity/);
});

test('all production JavaScript modules parse successfully', () => {
  const modules = [
    'src/agent.mjs',
    'src/validate.mjs',
    'src/render.mjs',
    'src/qa.mjs',
    'runtime/kit.js',
    'runtime/main.js',
    'projects/demo/episode.js'
  ];
  for (const module of modules) {
    const result = spawnSync(process.execPath, ['--check', path.join(root, module)], { encoding: 'utf8' });
    assert.equal(result.status, 0, module + ': ' + result.stderr);
  }
});
