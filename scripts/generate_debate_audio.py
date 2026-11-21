#!/usr/bin/env python3
"""Generate Liam/George/Eponine dialogue, speaker stems, timings and SRT.

Liam: Kokoro am_liam. George/Eponine: Kyutai Pocket TTS built-in catalogue voices.
No substitute voice is silently selected. The script fails when a requested
engine/voice is unavailable so the final mix can never mislabel a speaker.
"""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path
from typing import Any
import numpy as np
import soundfile as sf

SAMPLE_RATE = 24000
SPEAKERS = ("Liam", "George", "Eponine")
POCKET_VOICES = {
    "George": "george",
    "Eponine": "eponine",
}


def audio_array(value: Any) -> np.ndarray:
    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    arr = np.asarray(value, dtype=np.float32).reshape(-1)
    if arr.size == 0 or not np.isfinite(arr).all():
        raise RuntimeError("TTS returned an empty or invalid waveform")
    peak = float(np.max(np.abs(arr)))
    if peak > 0.999:
        arr = arr * (0.92 / peak)
    rms = float(np.sqrt(np.mean(arr * arr)))
    if rms > 1e-5:
        arr *= min(2.3, max(0.55, 0.115 / rms))
    peak = float(np.max(np.abs(arr)))
    if peak > 0.96:
        arr *= 0.96 / peak
    fade = min(int(SAMPLE_RATE * 0.008), arr.size // 4)
    if fade:
        arr[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
        arr[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
    return arr


def build_engines():
    try:
        from kokoro import KPipeline
    except ImportError as exc:
        raise RuntimeError("Kokoro is required for Liam (install requirements-debate-audio.txt)") from exc
    try:
        from pocket_tts import TTSModel
    except ImportError as exc:
        raise RuntimeError("Pocket TTS is required for George and Eponine") from exc
    kokoro = KPipeline(lang_code="a", device="cpu")
    pocket = TTSModel.load_model()
    pocket.to("cpu")
    # Use native catalogue voices; custom audio prompts require gated voice-cloning weights.
    states = {speaker: pocket.get_state_for_audio_prompt(voice_id)
              for speaker, voice_id in POCKET_VOICES.items()}
    return kokoro, pocket, states


def render_line(line: dict, kokoro, pocket, pocket_states) -> np.ndarray:
    speaker, text = line["speaker"], line["text"].strip()
    if speaker == "Liam":
        chunks = []
        for _, _, audio in kokoro(text, voice="am_liam", speed=1.0):
            if audio is not None:
                chunks.append(audio_array(audio))
        if not chunks:
            raise RuntimeError("Kokoro produced no audio for Liam")
        return np.concatenate(chunks)
    if speaker in ("George", "Eponine"):
        audio = pocket.generate_audio(pocket_states[speaker], text, copy_state=True)
        return audio_array(audio)
    raise ValueError(f"Unknown speaker: {speaker}")


def run_ffmpeg(input_path: Path, output_path: Path, tempo: float, duration: float) -> None:
    if not (0.85 <= tempo <= 1.15):
        raise RuntimeError(f"Required speech tempo {tempo:.3f}x exceeds safe 0.85–1.15 range; edit the script")
    filters = []
    if abs(tempo - 1.0) > 0.0001:
        filters.append(f"atempo={tempo:.6f}")
    filters.append("apad")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(input_path),
        "-filter:a", ",".join(filters), "-t", f"{duration:.3f}",
        "-ar", str(SAMPLE_RATE), "-ac", "1", "-c:a", "pcm_s16le", str(output_path)
    ], check=True)
    info = sf.info(output_path)
    if abs(info.duration - duration) > 0.03 or info.samplerate != SAMPLE_RATE or info.channels != 1:
        raise RuntimeError(f"Audio output validation failed: {info}")


def srt_time(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dialogue", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--duration", type=float, default=300.0)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--outro-reserve", type=float, default=8.0)
    args = parser.parse_args()
    dialogue_path = Path(args.dialogue).resolve()
    out = Path(args.output_dir).resolve()
    clips_dir = out / "clips"
    out.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)
    project = json.loads(dialogue_path.read_text(encoding="utf-8"))
    lines = project.get("lines", [])
    if not lines or any(line.get("speaker") not in SPEAKERS for line in lines):
        raise SystemExit("Dialogue must contain non-empty turns from Liam, George and Eponine only")
    if set(line["speaker"] for line in lines) != set(SPEAKERS):
        raise SystemExit("All three voices must appear in the debate")

    kokoro, pocket, pocket_states = build_engines()
    raw_cursor = 0
    raw_timings: list[dict] = []
    for index, line in enumerate(lines):
        audio = render_line(line, kokoro, pocket, pocket_states)
        clip_path = clips_dir / f"line-{index + 1:02d}-{line['speaker'].lower()}.wav"
        sf.write(clip_path, audio, SAMPLE_RATE, subtype="PCM_16")
        pause_seconds = max(0.15, min(1.5, float(line.get("pause_after", 0.35))))
        pause_samples = int(round(pause_seconds * SAMPLE_RATE))
        start = raw_cursor
        raw_cursor += len(audio)
        end = raw_cursor
        raw_timings.append({
            "index": index + 1, "speaker": line["speaker"], "scene": line["scene"],
            "focus": line.get("focus", "none"), "camera": line.get("camera", "wide"),
            "emotion": line.get("emotion", "neutral"), "gesture": line.get("gesture", "neutral"),
            "keyword": line.get("keyword", ""), "keyword_type": line.get("keyword_type", "term"),
            "text": line["text"], "raw_start_samples": start, "raw_end_samples": end,
            "raw_pause_samples": pause_samples, "raw_clip_seconds": round(len(audio) / SAMPLE_RATE, 4),
        })
        raw_cursor += pause_samples
        print(f"AUDIO_LINE {index + 1}/{len(lines)} {line['speaker']} {len(audio)/SAMPLE_RATE:.2f}s", flush=True)

    raw_duration = raw_cursor / SAMPLE_RATE
    speech_budget = args.duration - args.outro_reserve
    tempo = raw_duration / speech_budget
    if not 0.85 <= tempo <= 1.15:
        raise SystemExit(
            f"Speech needs {raw_duration:.1f}s for a {speech_budget:.1f}s dialogue window "
            f"(required tempo {tempo:.2f}x). Edit the script rather than stretching it beyond 0.85–1.15x."
        )

    mix = np.zeros(raw_cursor, dtype=np.float32)
    stems = {speaker: np.zeros(raw_cursor, dtype=np.float32) for speaker in SPEAKERS}
    cursor = 0
    final_timing = []
    for info in raw_timings:
        clip = sf.read(clips_dir / f"line-{info['index']:02d}-{info['speaker'].lower()}.wav", dtype="float32")[0]
        clip_start = cursor
        clip_end = cursor + len(clip)
        mix[clip_start:clip_end] += clip
        stems[info["speaker"]][clip_start:clip_end] += clip
        final_timing.append({**{k: info[k] for k in (
            "index","speaker","scene","focus","camera","emotion","gesture","keyword","keyword_type","text")},
            "raw_start_seconds": clip_start / SAMPLE_RATE,
            "raw_end_seconds": clip_end / SAMPLE_RATE})
        cursor = clip_end + info["raw_pause_samples"]

    peak = float(np.max(np.abs(mix))) if mix.size else 0.0
    if peak > 0:
        gain = min(0.90 / peak, 1.0)
        mix *= gain
        for stem in stems.values():
            stem *= gain

    raw_mix_path = out / "dialogue-raw.wav"
    sf.write(raw_mix_path, mix, SAMPLE_RATE, subtype="PCM_16")
    run_ffmpeg(raw_mix_path, out / "dialogue.wav", tempo, args.duration)
    for speaker, stem in stems.items():
        raw_stem = out / f"{speaker}-raw.wav"
        sf.write(raw_stem, stem, SAMPLE_RATE, subtype="PCM_16")
        run_ffmpeg(raw_stem, out / f"{speaker}.wav", tempo, args.duration)
        raw_stem.unlink(missing_ok=True)
    raw_mix_path.unlink(missing_ok=True)

    srt = []
    timed_lines = []
    for info in final_timing:
        start = info["raw_start_seconds"] / tempo
        end = info["raw_end_seconds"] / tempo
        start_frame = int(round(start * args.fps))
        end_frame = int(round(end * args.fps))
        timed_lines.append({**info, "start_seconds": round(start, 4), "end_seconds": round(end, 4),
                            "start_frame": start_frame, "end_frame": end_frame})
        srt.append(f"{info['index']}\n{srt_time(start)} --> {srt_time(end)}\n{info['speaker'].upper()}: {info['text']}\n")
    (out / "dialogue.srt").write_text("\n".join(srt), encoding="utf-8")
    timings = {
        "episode_id": project.get("episode_id"), "duration_seconds": args.duration,
        "fps": args.fps, "sample_rate": SAMPLE_RATE, "raw_dialogue_seconds": round(raw_duration, 4),
        "tempo_factor": round(tempo, 5), "outro_reserve_seconds": args.outro_reserve,
        "voice_mapping": {
            "Liam": "Kokoro-82M / am_liam",
            "George": "Kyutai Pocket TTS / george (built-in catalogue voice)",
            "Eponine": "Kyutai Pocket TTS / eponine (built-in catalogue voice)"
        },
        "lines": timed_lines
    }
    (out / "timings.json").write_text(json.dumps(timings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for path in [out / "dialogue.wav", *(out / f"{s}.wav" for s in SPEAKERS)]:
        info = sf.info(path)
        if abs(info.duration - args.duration) > 0.03 or info.samplerate != SAMPLE_RATE:
            raise RuntimeError(f"Final voice file invalid: {path} {info}")
    report = {"status": "passed", "duration_seconds": args.duration, "raw_dialogue_seconds": round(raw_duration, 3),
              "tempo_factor": round(tempo, 4), "speakers": list(SPEAKERS), "line_count": len(lines),
              "voice_tracks": [f"{s}.wav" for s in SPEAKERS], "captions_burned_in": False,
              "background_music": False, "sample_rate": SAMPLE_RATE}
    (out / "audio-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
