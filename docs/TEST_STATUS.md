# Validation status for this bootstrap

Checks run while assembling this package:

- [x] Project JSON and style-bible JSON parse.
- [x] Smoke profile validates as 10 seconds, 300 frames, 30 fps, 540×960.
- [x] Invalid frame rate is rejected.
- [x] Invalid 9:16 aspect ratio is rejected.
- [x] Shot segments are validated for continuous timeline coverage and supported camera profiles.
- [x] Frame-QA test creates a report/contact sheet and accepts a changing, correctly sized sequence.
- [x] Python sources compile.
- [x] Three.js preview JavaScript parses.
- [x] GitHub Actions workflow YAML parses.
- [x] FFmpeg/ffprobe pipeline was exercised end-to-end using a synthetic frame generator in place of Blender; it produced a 10-second 540×960 H.264 file, verified at 30 fps and 300 frames.

Not yet verified:

- [ ] A real Blender process has not been run in this build environment because Blender was unavailable and system package installation timed out.
- [ ] The GitHub Actions job has not been run; the repository has not yet been created on GitHub.
- [ ] Kokoro model download, synthesis speed and audio quality have not been tested.
- [ ] The seven specialist reviews are review procedures for ChatGPT/human execution, not seven autonomous hosted AI agents.

Do not treat the synthetic FFmpeg test as a rendered animated short. The real end-to-end Blender smoke test must pass in GitHub Actions before the pipeline is declared production-ready.
