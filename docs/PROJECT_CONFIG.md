# Project configuration

The project is a JSON file. `config/smoke.json` is the exact ten-second test; `config/template.json` is the starting point for a new short.

| Field | Meaning | Rule |
|---|---|---|
| `title` | Short title | Non-empty string |
| `duration_seconds` | Duration | Integer, 1–180 |
| `fps` | Frames per second | Must be 30 |
| `width`, `height` | Output dimensions | Even integers, exact 9:16 ratio |
| `quality` | Profile label | `smoke`, `preview`, `master` or custom |
| `style_bible` | Style guidance path | Use a source-controlled JSON style bible |
| `narration_text` | Optional narration copy | Blank means no voice |
| `captions_file` | Optional SRT subtitles | Blank means no burned-in captions; supplied SRT is burned in by FFmpeg |
| `kokoro_voice` | Kokoro voice ID | Configurable; default `am_michael` |
| `render.crf` | H.264 quality | Integer 14–28; lower is higher quality/larger |
| `render.preset` | FFmpeg speed/size balance | `veryfast`, `fast`, `medium`, etc. |
| `story.hook` | Opening hook | Short, visual and understandable immediately |
| `story.beats` | Story beats | Array of concise beats |
| `character` | Original protagonist design | Name and optional RGBA colors |

The optional `shots` array divides the complete timeline into contiguous segments. Each segment has `start_seconds`, `duration_seconds`, `camera` (`wide`, `push_in`, `close`, `side`, or `low`) and a human-readable `purpose`. Segments must cover the entire project duration without gaps or overlaps. Camera profiles animate between framing distances.

A 30 fps, ten-second job contains exactly 300 frames. Frame numbering in Blender starts at 1, while the final encoded video plays those 300 frames over ten seconds.

## Profiles

| Profile | Duration | Resolution | FPS | Purpose |
|---|---:|---:|---:|---|
| Smoke | 10 s | 540×960 | 30 | Renderer/QA smoke test |
| Preview | 30 s | 720×1280 | 30 | Lightweight review master |
| Master | 30 s | 1080×1920 | 30 | High-resolution starting profile |

Change the duration and content for a real production. The master preset is a resolution profile, not a promise that every scene can render within a particular runner's time limit.
