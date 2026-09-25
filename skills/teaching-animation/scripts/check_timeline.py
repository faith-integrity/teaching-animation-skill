"""Validate sequential single-narrator measured timelines and optional PCM WAVs."""
import argparse
import json
import math
from pathlib import Path
import wave


def validate(data, base, check_audio=False, tolerance=0.05):
    errors = []
    formats = set()

    def require(condition, message):
        if not condition:
            errors.append(message)

    def number(obj, key, where, default=None):
        value = obj.get(key, default)
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            errors.append(f"{where}.{key}: expected finite number")
            return 0.0
        return float(value)

    require(data.get("schema_version") == 1, "schema_version must be 1")
    cover = number(data, "cover_duration", "timeline", 0)
    total = number(data, "duration", "timeline")
    require(cover >= 0 and total > 0, "invalid cover/total duration")
    shots = data.get("shots", [])
    require(isinstance(shots, list) and bool(shots), "shots must be a nonempty list")
    if not isinstance(shots, list):
        return errors
    previous_end = 0.0
    shot_ids = set()
    for shot in shots:
        sid = shot.get("id")
        require(isinstance(sid, str) and bool(sid) and sid not in shot_ids, f"duplicate/invalid shot id: {sid}")
        shot_ids.add(sid)
        start = number(shot, "start", str(sid))
        duration = number(shot, "duration", str(sid))
        require(start >= previous_end - 1e-9 and duration > 0, f"{sid}: overlapping shot or invalid duration")
        previous_end = start + duration
        cue_ids = set()
        previous_cue_end = 0.0
        cues = shot.get("cues", [])
        require(isinstance(cues, list), f"{sid}: cues must be a list")
        if not isinstance(cues, list):
            continue
        for cue in cues:
            cid = cue.get("id")
            label = f"{sid}:{cid}"
            require(isinstance(cid, str) and bool(cid) and cid not in cue_ids, f"{label}: duplicate/invalid cue id")
            cue_ids.add(cid)
            a = number(cue, "start", label)
            b = number(cue, "end", label)
            require(a >= previous_cue_end - 1e-9 and b > a and b <= duration + 1e-9,
                    f"{label}: cue overlap, out of shot, or invalid interval")
            previous_cue_end = b
            require(isinstance(cue.get("display_text"), str) and bool(cue.get("display_text", "").strip()),
                    f"{label}: missing display_text")
            require(isinstance(cue.get("speech_text"), str), f"{label}: speech_text must be a string")
            has_audio = any(k in cue for k in ("audio_path", "audio_start", "audio_duration"))
            if cue.get("speech_text") or has_audio:
                path = cue.get("audio_path")
                require(isinstance(path, str) and bool(path), f"{label}: missing audio_path")
                va = number(cue, "audio_start", label)
                vd = number(cue, "audio_duration", label)
                require(vd > 0 and va >= a - 1e-9 and va + vd <= b + tolerance,
                        f"{label}: audio outside cue or invalid duration")
                if check_audio and isinstance(path, str) and path:
                    try:
                        with wave.open(str(base / path), "rb") as wav:
                            frames = wav.getnframes()
                            rate = wav.getframerate()
                            actual = frames / rate
                            formats.add((rate, wav.getnchannels()))
                            require(frames > 0, f"{label}: empty WAV")
                            require(abs(actual - vd) <= tolerance, f"{label}: WAV duration mismatch")
                    except (OSError, EOFError, wave.Error, ZeroDivisionError) as exc:
                        errors.append(f"{label}: cannot read PCM WAV: {exc}")
            event_ids = set()
            for event in cue.get("events", []):
                eid = event.get("id")
                require(isinstance(eid, str) and bool(eid) and eid not in event_ids,
                        f"{label}: duplicate/invalid event id")
                event_ids.add(eid)
                ea = number(event, "start", label)
                eb = number(event, "end", label)
                require(a <= ea <= eb <= b, f"{label}: event outside cue")
    require(abs(total - (cover + previous_end)) <= tolerance, "total duration differs from cover + last shot end")
    require(len(formats) <= 1, "inconsistent audio sample rates/channels")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--check-audio", action="store_true")
    parser.add_argument("--tolerance", type=float, default=0.05)
    args = parser.parse_args()
    if not math.isfinite(args.tolerance) or args.tolerance < 0:
        parser.error("tolerance must be finite and nonnegative")
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
        errors = validate(data, args.manifest.resolve().parent, args.check_audio, args.tolerance)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        errors = [f"Invalid manifest: {exc}"]
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
