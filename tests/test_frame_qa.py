import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


class FrameQATests(unittest.TestCase):
    def test_contact_sheet_and_report_are_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frames = root / "frames"
            frames.mkdir()
            for index in range(1, 7):
                image = Image.new("RGB", (54, 96), (20 + index * 15, 70, 120))
                draw = ImageDraw.Draw(image)
                draw.rectangle((index * 2, 20, index * 2 + 8, 80), fill=(240, 200, 80))
                image.save(frames / f"frame_{index:06d}.png")
            report = root / "qa.json"
            contact = root / "contact.jpg"
            result = subprocess.run([
                sys.executable, str(ROOT / "src/qa/analyze_frames.py"),
                "--frames-dir", str(frames), "--expected-frames", "6",
                "--width", "54", "--height", "96",
                "--report", str(report), "--contact-sheet", str(contact)
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(report.exists())
            self.assertTrue(contact.exists())
            self.assertIn('"status": "passed"', report.read_text())


if __name__ == "__main__":
    unittest.main()
