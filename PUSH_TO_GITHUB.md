# Put SHORTFORGE on GitHub

The code package is ready. The connected GitHub integration in the build session does not expose a **create repository** operation, so the remote repository cannot be created by the agent from this session. The repository contents and a local Git history are included in the supplied bundle.

1. Open [GitHub's new repository page](https://github.com/new?name=SHORTFORGE&description=Blender%20and%20Three.js%20animated%20shorts%20pipeline).
2. Create `FRFR-FR/SHORTFORGE` as an empty repository (do not add a README, license or `.gitignore`, because they are already included).
3. Clone the supplied `SHORTFORGE.bundle` locally, then push its `main` branch:

```bash
git clone SHORTFORGE.bundle SHORTFORGE
cd SHORTFORGE
git remote add origin https://github.com/FRFR-FR/SHORTFORGE.git
git push -u origin main
```

4. In the new repository, confirm Actions are enabled and the workflow can write contents/releases (the workflow declares `contents: write`).
5. Run **Actions → SHORTFORGE render → Run workflow → smoke**. The smoke profile is ten seconds / 300 frames. Enable release publishing to attach the MP4 and QA files to a GitHub Release.

The first Actions run is the required real Blender smoke test. The current local verification is documented in `docs/TEST_STATUS.md` and does not claim that a Blender-rendered MP4 has already been produced.
