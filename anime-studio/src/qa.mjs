import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { PNG } from 'pngjs';

function listFrames(directory) {
  return fs.readdirSync(directory)
    .filter((name) => /^frame-\d{6}\.png$/.test(name))
    .sort();
}
function readProbe(videoPath) {
  const result = spawnSync('ffprobe', [
    '-v', 'error',
    '-count_frames',
    '-show_entries', 'stream=codec_name,codec_type,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,pix_fmt',
    '-show_entries', 'format=duration',
    '-of', 'json',
    videoPath
  ], { encoding: 'utf8' });
  if (result.status !== 0) throw new Error('ffprobe failed: ' + (result.stderr || '').trim());
  return JSON.parse(result.stdout);
}
function frameStats(file) {
  const png = PNG.sync.read(fs.readFileSync(file));
  let sum = 0;
  let sumSq = 0;
  let samples = 0;
  const signature = [];
  const stepX = Math.max(1, Math.floor(png.width / 48));
  const stepY = Math.max(1, Math.floor(png.height / 27));
  for (let y = 0; y < png.height; y += stepY) {
    for (let x = 0; x < png.width; x += stepX) {
      const index = (y * png.width + x) * 4;
      const luma = 0.2126 * png.data[index] + 0.7152 * png.data[index + 1] + 0.0722 * png.data[index + 2];
      sum += luma;
      sumSq += luma * luma;
      samples++;
      signature.push(Math.round(luma / 16));
    }
  }
  const mean = sum / samples;
  const variance = Math.max(0, sumSq / samples - mean * mean);
  const hash = crypto.createHash('sha1').update(Buffer.from(signature)).digest('hex');
  return { width: png.width, height: png.height, mean, variance, hash };
}
function makeContactSheet(directory, names, output) {
  const selected = [];
  const count = Math.min(12, names.length);
  for (let i = 0; i < count; i++) {
    const index = count === 1 ? 0 : Math.round((i / (count - 1)) * (names.length - 1));
    selected.push(names[index]);
  }
  const cellW = 320;
  const cellH = 180;
  const cols = 4;
  const rows = Math.ceil(selected.length / cols);
  const sheet = new PNG({ width: cols * cellW, height: rows * cellH });
  for (let tile = 0; tile < selected.length; tile++) {
    const src = PNG.sync.read(fs.readFileSync(path.join(directory, selected[tile])));
    const ox = (tile % cols) * cellW;
    const oy = Math.floor(tile / cols) * cellH;
    for (let y = 0; y < cellH; y++) {
      for (let x = 0; x < cellW; x++) {
        const sx = Math.floor((x / cellW) * src.width);
        const sy = Math.floor((y / cellH) * src.height);
        const si = (sy * src.width + sx) * 4;
        const di = ((oy + y) * sheet.width + ox + x) * 4;
        sheet.data[di] = src.data[si];
        sheet.data[di + 1] = src.data[si + 1];
        sheet.data[di + 2] = src.data[si + 2];
        sheet.data[di + 3] = 255;
      }
    }
  }
  fs.writeFileSync(output, PNG.sync.write(sheet));
  return { path: output, frames: selected };
}

export async function auditRender({ framesDir, videoPath, outputDir, project, width, height, fps, totalFrames }) {
  const errors = [];
  const warnings = [];
  const names = listFrames(framesDir);
  if (names.length !== totalFrames) errors.push('Expected ' + totalFrames + ' PNG frames, found ' + names.length);

  let previousHash = '';
  let frozenRun = 0;
  let maxFrozenRun = 0;
  let veryDarkFrames = 0;
  let minVariance = Number.POSITIVE_INFINITY;
  let maxVariance = 0;

  for (const name of names) {
    const stats = frameStats(path.join(framesDir, name));
    if (stats.width !== width || stats.height !== height) errors.push(name + ' has incorrect dimensions');
    minVariance = Math.min(minVariance, stats.variance);
    maxVariance = Math.max(maxVariance, stats.variance);
    if (stats.mean < 1.2 && stats.variance < 1.5) veryDarkFrames++;
    if (stats.hash === previousHash) frozenRun++;
    else frozenRun = 0;
    maxFrozenRun = Math.max(maxFrozenRun, frozenRun);
    previousHash = stats.hash;
  }
  if (veryDarkFrames > Math.max(2, Math.floor(totalFrames * 0.02))) errors.push('Too many near-black frames: ' + veryDarkFrames);
  if (maxFrozenRun >= 5) errors.push('Detected at least six consecutive visually identical frames');
  if (maxVariance < 1.5) errors.push('All frames are visually flat or blank');

  const probe = readProbe(videoPath);
  const video = probe.streams?.find((stream) => stream.codec_type === 'video');
  if (!video) errors.push('No video stream found by ffprobe');
  else {
    if (video.codec_name !== 'h264') errors.push('Expected H.264 video, got ' + video.codec_name);
    if (video.width !== width || video.height !== height) errors.push('Encoded resolution does not match the selected profile');
    if (video.pix_fmt !== 'yuv420p') errors.push('Expected yuv420p output, got ' + video.pix_fmt);
    const rate = (video.avg_frame_rate || video.r_frame_rate || '').split('/');
    const numericRate = rate.length === 2 ? Number(rate[0]) / Number(rate[1]) : Number(rate[0]);
    if (Math.abs(numericRate - fps) > 0.01) errors.push('Encoded frame rate is ' + numericRate + ', expected ' + fps);
    if (Number(video.nb_read_frames) !== totalFrames) errors.push('Encoded video frame count is ' + video.nb_read_frames + ', expected ' + totalFrames);
  }
  const duration = Number(probe.format?.duration || 0);
  if (Math.abs(duration - project.duration_seconds) > (1 / fps) + 0.05) errors.push('Encoded duration does not match the episode duration');

  const contactPath = videoPath.replace(/\.mp4$/i, '.contact-sheet.png');
  const contactSheet = makeContactSheet(framesDir, names, contactPath);
  const report = {
    status: errors.length ? 'failed' : 'passed',
    title: project.title,
    checked_at: new Date().toISOString(),
    expected_frames: totalFrames,
    rendered_frames: names.length,
    duration_seconds: duration,
    fps,
    resolution: width + 'x' + height,
    codec: video?.codec_name ?? null,
    pixel_format: video?.pix_fmt ?? null,
    frame_variance: { minimum: Number.isFinite(minVariance) ? Number(minVariance.toFixed(2)) : null, maximum: Number(maxVariance.toFixed(2)) : null },
    near_black_frames: veryDarkFrames,
    max_identical_frame_run: maxFrozenRun,
    contact_sheet: contactSheet,
    errors,
    warnings
  };
  return report;
}
