import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "teaching-animation"
spec = importlib.util.spec_from_file_location("timeline", SKILL / "scripts" / "check_timeline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL / "assets" / "timeline.example.json").read_text(encoding="utf-8"))

    def errors(self, data=None):
        return module.validate(data or self.data, Path("."))

    def test_silent_example(self):
        self.assertEqual(self.errors(), [])

    def test_cover_offset(self):
        self.data.update(cover_duration=2, duration=6)
        self.assertEqual(self.errors(), [])
        self.data["duration"] = 4
        self.assertTrue(self.errors())

    def test_overlapping_cue(self):
        self.data["shots"][0]["cues"][1]["start"] = 1.5
        self.assertTrue(self.errors())

    def test_duplicate_id(self):
        self.data["shots"][0]["cues"][1]["id"] = "C01"
        self.assertTrue(self.errors())

    def test_out_of_shot(self):
        self.data["shots"][0]["cues"][1]["end"] = 5
        self.assertTrue(self.errors())

    def test_event_outside_cue(self):
        self.data["shots"][0]["cues"][0]["events"][0]["end"] = 3
        self.assertTrue(self.errors())

    def test_nonfinite_time(self):
        self.data["duration"] = float("nan")
        self.assertTrue(self.errors())

    def test_narration_requires_audio(self):
        self.data["shots"][0]["cues"][0]["speech_text"] = "test"
        self.assertTrue(self.errors())

    def test_voice_truncation(self):
        cue = self.data["shots"][0]["cues"][0]
        cue.update(speech_text="test", audio_path="cue.wav", audio_start=0.2, audio_duration=2)
        self.assertTrue(self.errors())

    def test_shot_overlap(self):
        shot = copy.deepcopy(self.data["shots"][0])
        shot.update(id="S02", start=3)
        self.data["shots"].append(shot)
        self.data["duration"] = 7
        self.assertTrue(self.errors())

    def test_real_wav_duration_and_missing_file(self):
        cue = self.data["shots"][0]["cues"][0]
        cue.update(speech_text="test", audio_path="cue.wav", audio_start=0.1, audio_duration=1)
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            self.assertTrue(module.validate(self.data, base, True))
            with wave.open(str(base / "cue.wav"), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                wav.writeframes(b"\0\0" * 16000)
            self.assertEqual(module.validate(self.data, base, True), [])
            cue["audio_duration"] = 1.4
            self.assertTrue(module.validate(self.data, base, True))


if __name__ == "__main__":
    unittest.main()
