import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectValidationTests(unittest.TestCase):
    def test_smoke_config_passes(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_project.py"), str(ROOT / "config/smoke.json")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("300 frames", result.stdout)

    def test_wrong_frame_rate_fails(self):
        config = json.loads((ROOT / "config/smoke.json").read_text())
        config["fps"] = 24
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(config, handle)
            path = handle.name
        try:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_project.py"), path], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exactly 30", result.stdout)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_wrong_aspect_ratio_fails(self):
        config = json.loads((ROOT / "config/smoke.json").read_text())
        config["width"] = 640
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(config, handle)
            path = handle.name
        try:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_project.py"), path], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("9:16", result.stdout)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_shot_segments_must_cover_the_full_timeline(self):
        config = json.loads((ROOT / "config/smoke.json").read_text())
        config["shots"][-1]["duration_seconds"] = 2
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(config, handle)
            path = handle.name
        try:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_project.py"), path], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete project duration", result.stdout)
        finally:
            Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
