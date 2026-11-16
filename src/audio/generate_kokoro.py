"""Optional Kokoro TTS adapter. Install requirements-tts.txt to enable it."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--voice", default="am_michael")
    args = parser.parse_args()
    config = json.loads(Path(args.project).read_text(encoding="utf-8"))
    text = str(config.get("narration_text", "")).strip()
    if not text:
        raise SystemExit("narration_text is empty; refusing to create a silent narration file")
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
    except ImportError as exc:
        raise SystemExit(f"Kokoro dependencies are missing. Install requirements-tts.txt: {exc}")

    pipeline = KPipeline(lang_code="a")
    chunks = []
    for _, _, audio in pipeline(text, voice=args.voice, speed=1.0, split_pattern=r"\n+"):
        if audio is not None:
            chunks.append(np.asarray(audio, dtype=np.float32))
    if not chunks:
        raise SystemExit("Kokoro returned no audio chunks")
    waveform = np.concatenate(chunks)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output), waveform, 24000)
    print(f"Wrote Kokoro narration: {output} ({len(waveform) / 24000:.2f}s, voice={args.voice})")


if __name__ == "__main__":
    main()
