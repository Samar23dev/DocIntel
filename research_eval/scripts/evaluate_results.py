#!/usr/bin/env python3
import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--responses", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "results")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = [
        json.loads(line)
        for line in args.responses.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["model_name"]].append(row)

    summary = []
    for model, model_rows in grouped.items():
        correct = partial = incorrect = unanswered = 0
        latencies = []
        for row in model_rows:
            latencies.append(row.get("latency_seconds", 0))
            grade = normalize(str(row.get("human_grade", "")))
            if grade.startswith("correct"):
                correct += 1
            elif grade.startswith("partial"):
                partial += 1
            elif grade in ("unanswered", "not_answered", "missing"):
                unanswered += 1
            elif grade:
                incorrect += 1
        total = len(model_rows)
        summary.append({
            "model": model,
            "responses": total,
            "correct": correct,
            "partial": partial,
            "incorrect": incorrect,
            "ungraded": total - correct - partial - incorrect - unanswered,
            "reference_answer_contained": sum(
                normalize(str(row.get("reference_answer", ""))) != ""
                and normalize(str(row.get("reference_answer", ""))) in normalize(str(row.get("answer", "")))
                for row in model_rows
            ),
            "mean_latency_seconds": round(sum(latencies) / total, 3) if total else 0,
        })

    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (args.output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary[0].keys() if summary else [])
        if summary:
            writer.writeheader()
            writer.writerows(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
