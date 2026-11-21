#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import { fileURLToPath } from 'node:url';
import { spawn, spawnSync } from 'node:child_process';
import { chromium } from 'playwright';
import { auditRender } from './qa.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
function option(name, fallback) {
  const i = argv.indexOf(name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback;
}
function run(command, args, label) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: 'inherit' });
    child.once('error', reject);
    child.once('exit', (code) => code === 0 ? resolve() : reject(new Error(label + ' failed with exit code ' + code)));
  });
}
function safeInside(root, candidate) {
  const resolved = path.resolve(root, candidate);
  return resolved === root || resolved.startsWith(root + path.sep);
}
function mime(file) {
  const ext = path.extname(file).toLowerCase();
  return ({
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.mjs': 'text/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
    '.glb': 'model/gltf-binary',
    '.gltf': 'model/gltf+json',
    '.bin': 'application/octet-stream',
    '.wav': 'audio/wav',
    '.mp3': 'audio/mpeg',
    '.ogg': 'audio/ogg'
  })[ext] || 'application/octet-stream';
}
function startStaticServer() {
  const server = http.createServer((request, response) => {
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      response.writeHead(405).end('Method not allowed');
      return;
    }
    let pathname;
    try { pathname = decodeURIComponent(new URL(request.url, 'http://127.0.0.1').pathname); }
    catch { response.writeHead(400).end('Bad path'); return; }
    const target = path.resolve(ROOT, '.' + pathname);
    if (!safeInside(ROOT, target)) { response.writeHead(403).end('Forbidden'); return; }
    fs.stat(target, (statError, stat) => {
      if (statError || !stat.isFile()) { response.writeHead(404).end('Not found'); return; }
      response.writeHead(200, {
        'Content-Type': mime(target),
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff',
        'Content-Security-Policy': "default-src 'self' data: blob:; script-src 'self' 'unsafe-eval' blob:; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self' data:"
      });
      if (request.method === 'HEAD') { response.end(); return; }
      fs.createReadStream(target).pipe(response);
    });
  });
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      resolve({ server, url: 'http://127.0.0.1:' + address.port });
    });
  });
}

const projectPath = path.resolve(option('--project', 'projects/demo/episode.json'));
if (!safeInside(ROOT, projectPath)) throw new Error('Project must be inside anime-studio/projects.');
const projectDir = path.dirname(projectPath);
const project = JSON.parse(fs.readFileSync(projectPath, 'utf8'));
const quality = option('--quality', project.quality || 'preview');
const profiles = {
  smoke: [640, 360],
  preview: [1280, 720],
  master: [1920, 1080]
};
if (!profiles[quality]) throw new Error('Unknown quality profile: ' + quality);
if (quality === 'master' && project.assets_complete !== true) {
  throw new Error('Master render blocked: final original character/environment assets have not been marked complete.');
}
const [width, height] = profiles[quality];
const fps = Number(project.fps || 30);
const duration = Number(project.duration_seconds);
const totalFrames = Math.round(duration * fps);
if (!Number.isInteger(totalFrames) || totalFrames < 1) throw new Error('Invalid frame count.');

const modulePath = path.resolve(projectDir, project.episode_module || 'episode.js');
if (!safeInside(projectDir, modulePath) || !fs.existsSync(modulePath)) throw new Error('Episode module must exist inside its project folder.');
const relativeModule = '/' + path.relative(ROOT, modulePath).split(path.sep).join('/');
const outputPath = path.resolve(option('--output', 'out/' + path.basename(projectDir) + '.mp4'));
if (!safeInside(ROOT, outputPath)) throw new Error('Output path must be inside anime-studio.');
fs.mkdirSync(path.dirname(outputPath), { recursive: true });

const validate = spawnSync(process.execPath, [path.join(ROOT, 'src/validate.mjs'), '--project', projectPath, '--quality', quality], { cwd: ROOT, encoding: 'utf8' });
if (validate.stdout) process.stdout.write(validate.stdout);
if (validate.stderr) process.stderr.write(validate.stderr);
if (validate.status !== 0) throw new Error('Episode validation failed before rendering.');

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'animeforge-frames-'));
const framePattern = path.join(tempDir, 'frame-%06d.png');
const audioFile = project.audio?.file ? path.resolve(projectDir, project.audio.file) : null;
if (audioFile && (!safeInside(projectDir, audioFile) || !fs.existsSync(audioFile))) {
  throw new Error('Audio file must exist inside the project folder.');
}

let browser;
let staticServer;
const pageErrors = [];
try {
  const host = await startStaticServer();
  staticServer = host.server;
  browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--use-gl=angle',
      '--use-angle=swiftshader',
      '--enable-webgl',
      '--ignore-gpu-blocklist'
    ]
  });
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  page.on('pageerror', (error) => pageErrors.push(error.message));
  const url = host.url + '/runtime/index.html?episode=' + encodeURIComponent(relativeModule) +
    '&width=' + width + '&height=' + height + '&fps=' + fps;
  console.log('ANIMEFORGE browser stage: ' + width + 'x' + height + ' @ ' + fps + ' fps');
  await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForFunction(() => window.__ANIME_READY__ === true || Boolean(window.__ANIME_ERROR__), null, { timeout: 90000 });
  const initError = await page.evaluate(() => window.__ANIME_ERROR__ || null);
  if (initError) throw new Error('Three.js episode initialization failed:\n' + initError);
  const canvas = page.locator('canvas');
  if (await canvas.count() !== 1) throw new Error('Expected exactly one render canvas.');
  console.log('Capturing ' + totalFrames + ' deterministic frames...');
  for (let frame = 0; frame < totalFrames; frame++) {
    await page.evaluate((index) => window.setFrame(index), frame);
    const framePath = path.join(tempDir, 'frame-' + String(frame).padStart(6, '0') + '.png');
    await canvas.screenshot({ path: framePath, animations: 'disabled' });
    if ((frame + 1) % Math.max(1, Math.floor(fps * 5)) === 0 || frame + 1 === totalFrames) {
      const percent = Math.round(((frame + 1) / totalFrames) * 100);
      console.log('Frames: ' + (frame + 1) + '/' + totalFrames + ' (' + percent + '%)');
    }
  }
  await page.close();
  await browser.close();
  browser = null;
  staticServer.close();
  staticServer = null;

  if (pageErrors.length) throw new Error('Browser runtime reported errors: ' + pageErrors.join(' | '));
  const ffmpegArgs = [
    '-hide_banner', '-loglevel', 'error', '-y',
    '-framerate', String(fps),
    '-start_number', '0',
    '-i', framePattern
  ];
  if (audioFile) ffmpegArgs.push('-i', audioFile, '-map', '0:v:0', '-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k', '-shortest');
  else ffmpegArgs.push('-an');
  ffmpegArgs.push(
    '-c:v', 'libx264',
    '-preset', quality === 'master' ? 'slow' : 'medium',
    '-crf', quality === 'master' ? '16' : '18',
    '-pix_fmt', 'yuv420p',
    '-r', String(fps),
    '-movflags', '+faststart',
    outputPath
  );
  console.log('Encoding H.264 MP4...');
  await run('ffmpeg', ffmpegArgs, 'FFmpeg');
  const report = await auditRender({
    framesDir: tempDir,
    videoPath: outputPath,
    outputDir: path.dirname(outputPath),
    project,
    width,
    height,
    fps,
    totalFrames
  });
  const reportPath = outputPath.replace(/\.mp4$/i, '.qa.json');
  const contactPath = outputPath.replace(/\.mp4$/i, '.contact-sheet.png');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
  console.log('QA: ' + report.status);
  console.log('Video: ' + outputPath);
  console.log('Report: ' + reportPath);
  console.log('Contact sheet: ' + contactPath);
  if (report.status !== 'passed') throw new Error('ANIMEFORGE render failed QA. See ' + reportPath);
} finally {
  if (browser) await browser.close().catch(() => {});
  if (staticServer) staticServer.close();
  fs.rmSync(tempDir, { recursive: true, force: true });
}
