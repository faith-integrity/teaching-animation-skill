"""Read-only dependency discovery; no installs or model downloads."""
import importlib.metadata
import json
import platform
import shutil
import sys


def report():
    packages = {}
    for name in ("manim", "faster-whisper", "numpy", "soundfile"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "platform": platform.platform(),
        "packages": packages,
        "commands": {name: shutil.which(name) for name in
                     ("ffmpeg", "ffprobe", "latex", "xelatex", "dvisvgm")},
        "note": "Discovery only. Render, font, voice and ASR smoke tests are still required. Redact local paths before publishing."
    }


if __name__ == "__main__":
    print(json.dumps(report(), ensure_ascii=False, indent=2))
