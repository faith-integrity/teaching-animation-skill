"""Transcribe with a local faster-whisper model; preserve raw timestamps."""
import argparse
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--language", default="zh")
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda", "auto"))
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--no-vad", action="store_true")
    args = parser.parse_args()
    if not args.input.is_file() or not args.model.is_dir():
        parser.error("Input file and local model directory must exist.")
    outputs = [args.output / "transcript_raw.json", args.output / "transcript_raw.tsv"]
    if any(p.exists() for p in outputs):
        parser.error("Output exists; choose a new output directory to preserve previous transcripts.")
    from faster_whisper import WhisperModel
    model = WhisperModel(str(args.model.resolve()), device=args.device,
                         compute_type=args.compute_type, local_files_only=True)
    segments, info = model.transcribe(
        str(args.input.resolve()), language=args.language, beam_size=5,
        vad_filter=not args.no_vad, word_timestamps=True,
        initial_prompt=args.prompt or None,
    )
    rows = []
    for segment in segments:
        rows.append({"id": segment.id, "start": segment.start, "end": segment.end,
                     "text": segment.text,
                     "words": [{"start": w.start, "end": w.end, "word": w.word,
                                "probability": w.probability} for w in (segment.words or [])]})
    data = {"input_name": args.input.name, "language": info.language,
            "language_probability": info.language_probability, "duration": info.duration,
            "segments": rows, "status": "raw_unreviewed"}
    args.output.mkdir(parents=True, exist_ok=True)
    outputs[0].write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    with outputs[1].open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(("id", "start", "end", "text"))
        writer.writerows((r["id"], r["start"], r["end"], r["text"]) for r in rows)
    print(f"Saved {len(rows)} raw segments; human review is still required.")


if __name__ == "__main__":
    main()
