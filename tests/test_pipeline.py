from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_project import validate


class ShortForgeProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "config/one-minute.json").read_text(encoding="utf-8"))

    def test_one_minute_project_is_valid(self):
        self.assertEqual(validate(self.config), [])

    def test_exact_one_minute_frame_count(self):
        self.assertEqual(self.config["duration_seconds"] * self.config["fps"], 1800)

    def test_all_seven_emotions_and_eight_poses_are_used(self):
        emotions = {shot["emotion"] for shot in self.config["shots"]}
        poses = {shot["pose"] for shot in self.config["shots"]}
        self.assertEqual(emotions, {"neutral", "happy", "sad", "angry", "surprised", "scared", "determined"})
        self.assertEqual(poses, {"neutral", "wave", "point", "confident", "thinking", "celebrating", "running", "crouching"})

    def test_external_environment_is_a_registered_scene(self):
        self.assertEqual(self.config["environment"]["id"], "house_of_chores")

    def test_invalid_emotion_is_rejected(self):
        broken = json.loads(json.dumps(self.config))
        broken["shots"][2]["emotion"] = "sleepy"
        self.assertTrue(any("emotion" in error for error in validate(broken)))

    def test_shots_cover_whole_story_without_gaps(self):
        self.assertEqual(sum(shot["duration_seconds"] for shot in self.config["shots"]), 60)
        self.assertEqual(validate(self.config), [])


if __name__ == "__main__":
    unittest.main()
