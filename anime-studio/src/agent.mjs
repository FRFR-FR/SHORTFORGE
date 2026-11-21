#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { query } from '@anthropic-ai/claude-agent-sdk';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const prompt = args.filter((x, i) => !x.startsWith('--') && (i === 0 || !args[i - 1].startsWith('--'))).join(' ').trim();
function option(name, fallback) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
}
function slugify(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 48) || 'untitled-episode';
}
function runNode(script, scriptArgs) {
  const result = spawnSync(process.execPath, [script, ...scriptArgs], { cwd: ROOT, stdio: 'inherit' });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error('Command failed: ' + path.basename(script));
}

if (!prompt) {
  console.error('Usage: npm run agent -- "episode concept" --slug episode-name --duration 60 --quality preview [--render]');
  process.exit(2);
}
if (!process.env.ANTHROPIC_API_KEY && !process.env.CLAUDE_CODE_OAUTH_TOKEN) {
  console.error('Set ANTHROPIC_API_KEY (or an authorized Claude Code token) before running the agent.');
  process.exit(2);
}

const slug = slugify(option('--slug', prompt.slice(0, 60)));
const duration = Number(option('--duration', '30'));
const quality = option('--quality', 'preview');
if (!Number.isInteger(duration) || duration < 5 || duration > 1800) throw new Error('--duration must be 5–1800 seconds');
if (!['smoke', 'preview', 'master'].includes(quality)) throw new Error('--quality must be smoke, preview or master');

const projectDir = path.join(ROOT, 'projects', slug);
fs.mkdirSync(projectDir, { recursive: true });
for (const name of ['episode.json', 'episode.js']) {
  const source = path.join(ROOT, 'projects', 'demo', name);
  const target = path.join(projectDir, name);
  if (!fs.existsSync(target)) fs.copyFileSync(source, target);
}
const dimensions = quality === 'master' ? [1920, 1080] : quality === 'smoke' ? [640, 360] : [1280, 720];
const projectManifestPath = path.join(projectDir, 'episode.json');
const projectManifest = JSON.parse(fs.readFileSync(projectManifestPath, 'utf8'));
projectManifest.duration_seconds = duration;
projectManifest.fps = 30;
projectManifest.width = dimensions[0];
projectManifest.height = dimensions[1];
projectManifest.quality = quality;
projectManifest.assets_complete = false;
projectManifest.assets = [];
fs.writeFileSync(projectManifestPath, JSON.stringify(projectManifest, null, 2) + '\n', 'utf8');

const task = [
  '# ANIMEFORGE episode brief',
  '',
  'Concept: ' + prompt,
  'Target duration: ' + duration + ' seconds',
  'Render profile: ' + quality + ' (' + dimensions[0] + 'x' + dimensions[1] + ')',
  'Frame rate: 30 fps',
  '',
  'Create an original horizontal 16:9 anime episode. Deliver a coherent script, cast, scene staging, shot-by-shot camera plan and expressive timed action. The visual direction should be a premium, high-energy cyberpunk action anime with saturated neon, bold ink contours, painted cel-shading, detailed layered city environments, motivated camera motion, dynamic perspective and atmospheric effects. It must be an original work; do not reproduce any existing show's characters, exact costume designs, scenes, frames, logos, scripts or signature compositions.',
  '',
  'Production expectation: use Three.js 2.5D depth layering, not a static slideshow. Create foreground occlusion, midground character action, distant parallax architecture, camera dolly/orbit, lighting changes, secondary animation and purposeful cuts. Use the shared runtime kit. Do not use primitive low-poly cubes as the main characters or final environment art.',
  '',
  'Edit only episode.json and episode.js in this project directory. Do not edit repository engine files. Do not run shell commands. Keep module imports local to three and ../../runtime/kit.js, or project-local assets. If original final art assets are not present, explicitly leave assets_complete=false and describe the missing asset pack in the JSON.'
].join('\n');
fs.writeFileSync(path.join(projectDir, 'TASK.md'), task, 'utf8');

const systemPrompt = [
  'You are ANIMEFORGE, an autonomous senior anime episode production coding agent powered by Claude Code.',
  'You are not a generic video summarizer. You author actual timed Three.js 2.5D scene code, an episode manifest, camera choreography, character acting and cinematic staging.',
  'The project folder is your only workspace. Edit only episode.json and episode.js. Use Read, Write, Edit, Glob and Grep; never request or attempt shell execution.',
  'The output is horizontal 16:9, 30 fps, with complete continuous shot coverage. Every shot is 2–12 seconds, has a specific visual action, a motivated camera move and an emotional purpose.',
  'Read TASK.md, episode.json and episode.js before editing. Keep the project manifest and module consistent.',
  'Use the shared kit functions from ../../runtime/kit.js. Do not use remote URLs, external fetches, eval, dynamic code loading or arbitrary npm dependencies.',
  'Give the protagonist a distinctive original silhouette, readable facial expression, clear goal and physical acting. Every action needs anticipation, contact or reaction, follow-through and a readable held pose.',
  'Design complex environments with foreground, middle distance and skyline depth. Avoid empty stages, single-object scenes, flat text slides, low-poly placeholders and repeated camera angles.',
  'The reference direction is broad cyberpunk anime craft only: saturated neon, painterly cel shading, controlled black linework, expressive character acting, fast cinematic editing and atmospheric city depth. Never copy a named show's distinctive designs, character likenesses, props, logos, frames or exact scene choreography.',
  'A production-quality master must not claim assets_complete=true unless actual original layered artwork / rigged models and detailed environment assets are linked in the project assets directory. Procedural kit puppets are smoke-test fallbacks only.',
  'Use the storyboard-director, anime-art-director, animation-engineer and continuity-supervisor subagents for independent passes, then reconcile their feedback into the final files.',
  'Do not state that a render passed; the repository validator and renderer will run after your work.'
].join('\n');

const agents = {
  'storyboard-director': {
    description: 'Plans episode structure, visual storytelling, shot rhythm and dramatic escalation.',
    prompt: 'Act as an anime storyboard director. Review the supplied brief and project files. Improve the shot order, staging, visual causality, emotional beats and cuts. Keep all ideas original. Write actionable notes into director-review.md.',
    tools: ['Read', 'Write', 'Edit', 'Glob', 'Grep']
  },
  'anime-art-director': {
    description: 'Defines original character silhouettes, palette, lighting, linework and environment art direction.',
    prompt: 'Act as an anime art director. Establish a coherent original style bible, distinctive cast silhouettes, palette, lighting and dense environment design. Do not imitate a specific show's designs. Write your feedback to art-review.md.',
    tools: ['Read', 'Write', 'Edit', 'Glob', 'Grep']
  },
  'animation-engineer': {
    description: 'Authors high-quality Three.js animation, 2.5D staging, camera rigs and timing.',
    prompt: 'Act as a senior Three.js animation TD. Inspect the starter module and kit API, then review animation curves, pose readability, depth layers, camera motion, collision staging and deterministic time seeking. Write precise fixes to animation-review.md.',
    tools: ['Read', 'Write', 'Edit', 'Glob', 'Grep']
  },
  'continuity-supervisor': {
    description: 'Checks scene geography, character continuity, asset references and timeline correctness.',
    prompt: 'Act as a continuity supervisor. Verify character identities, props, geography, timeline coverage, shot continuity, screen direction, asset references and original-work requirements. Write fixes to continuity-review.md.',
    tools: ['Read', 'Glob', 'Grep']
  }
};

const sdkOptions = {
  cwd: projectDir,
  model: process.env.CLAUDE_MODEL || 'claude-opus-5-5',
  systemPrompt,
  tools: ['Read', 'Write', 'Edit', 'Glob', 'Grep', 'Agent'],
  allowedTools: ['Read', 'Write', 'Edit', 'Glob', 'Grep', 'Agent'],
  disallowedTools: ['Bash', 'WebFetch', 'WebSearch', 'NotebookEdit'],
  permissionMode: 'dontAsk',
  settingSources: [],
  maxTurns: 45,
  maxBudgetUsd: Number(process.env.CLAUDE_MAX_BUDGET_USD || 12),
  agents
};

async function runAgent(instruction) {
  let finalText = '';
  for await (const message of query({ prompt: instruction, options: sdkOptions })) {
    if (message.type === 'assistant') {
      const blocks = message.message?.content || [];
      for (const block of blocks) if (block.type === 'text') process.stdout.write(block.text);
    }
    if (message.type === 'result') {
      finalText = message.result || '';
      if (message.subtype && message.subtype !== 'success') throw new Error('Claude agent ended with status: ' + message.subtype);
    }
  }
  return finalText;
}

console.log('ANIMEFORGE: generating project ' + slug);
await runAgent([
  'Read TASK.md, episode.json and episode.js. Create the complete original episode inside these two files.',
  'The exact duration is ' + duration + ' seconds, at 30 fps, resolution ' + dimensions[0] + 'x' + dimensions[1] + '.',
  'Make enough tightly authored shots to cover every frame with no gaps. Aim for 3–7 seconds per shot, never over 12 seconds.',
  'Make the scene visually dense, cinematic, layered and animated. The runtime will call createEpisode({ scene, camera, kit, config, THREE }); return an object with update(time, frame) and use only helpers exposed by ../../runtime/kit.js.',
  'The demo is allowed to use procedural fallback puppets, but never mark them as final artwork. Include all subagent review findings and fix them before finishing.'
].join('\n'));

let validation = spawnSync(process.execPath, [path.join(ROOT, 'src/validate.mjs'), '--project', path.join(projectDir, 'episode.json')], { cwd: ROOT, encoding: 'utf8' });
if (validation.stdout) process.stdout.write(validation.stdout);
if (validation.stderr) process.stderr.write(validation.stderr);
if (validation.status !== 0) {
  console.log('ANIMEFORGE: running one repair pass from validator feedback.');
  await runAgent('The trusted validator rejected this episode. Fix every issue below by editing only episode.json and episode.js, then re-check your own timeline and exported function.\n\n' + (validation.stderr || validation.stdout));
  validation = spawnSync(process.execPath, [path.join(ROOT, 'src/validate.mjs'), '--project', path.join(projectDir, 'episode.json')], { cwd: ROOT, encoding: 'utf8' });
  if (validation.stdout) process.stdout.write(validation.stdout);
  if (validation.stderr) process.stderr.write(validation.stderr);
  if (validation.status !== 0) throw new Error('Episode still fails validation; inspect projects/' + slug);
}

console.log('ANIMEFORGE project authored: projects/' + slug);
if (args.includes('--render')) {
  const output = option('--output', 'out/' + slug + '.mp4');
  runNode(path.join(ROOT, 'src/render.mjs'), ['--project', path.join(projectDir, 'episode.json'), '--output', output, '--quality', quality]);
}
