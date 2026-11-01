#!/usr/bin/env python3
import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESEARCH_DIR = ROOT / "research_eval"
CORPUS_DIR = RESEARCH_DIR / "corpus"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_opencode_text(output: str) -> str:
    texts = []
    for line in output.splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") == "text":
            texts.append(record.get("part", {}).get("text", ""))
    return "".join(texts).strip() or output.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--models", type=Path, default=RESEARCH_DIR / "config/models.json")
    parser.add_argument("--output", type=Path, default=RESEARCH_DIR / "results/responses.jsonl")
    args = parser.parse_args()

    manifest = json.loads((CORPUS_DIR / "manifest.json").read_text(encoding="utf-8"))
    questions = [
        json.loads(line)
        for line in args.questions.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    models = json.loads(args.models.read_text(encoding="utf-8"))["models"]
    args.output.parent.mkdir(parents=True, exist_ok=True)

    texts = {
        item["document_id"]: Path(item["extracted_text"]).read_text(encoding="utf-8")
        for item in manifest
    }
    with args.output.open("w", encoding="utf-8") as output:
        for question in questions:
            document_id = question["document_id"]
            document_text = texts[document_id]
            prompt = (
                "Answer only from the supplied document. If the document does not "
                "contain enough evidence, say that the answer is not stated.\n\n"
                f"DOCUMENT ({document_id}):\n{document_text}\n\n"
                f"QUESTION:\n{question['question']}\n"
            )
            for model in models:
                started = time.perf_counter()
                result = subprocess.run(
                    [
                        "opencode",
                        "run",
                        "--format",
                        "json",
                        "--model",
                        model["id"],
                        "--auto",
                        prompt,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                elapsed = time.perf_counter() - started
                record = {
                    "timestamp": utc_now(),
                    "document_id": document_id,
                    "question_id": question["id"],
                    "question_type": question.get("type", "unknown"),
                    "reference_answer": question.get("reference_answer"),
                    "model_id": model["id"],
                    "model_name": model["name"],
                    "mode": "direct-document-text",
                    "prompt_version": "v1",
                    "answer": extract_opencode_text(result.stdout),
                    "stderr": result.stderr.strip(),
                    "exit_code": result.returncode,
                    "latency_seconds": round(elapsed, 4),
                    "document_sha256": next(
                        item["source_sha256"] for item in manifest if item["document_id"] == document_id
                    ),
                }
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                output.flush()
                print(f"{model['name']} :: {document_id}/{question['id']}: exit {result.returncode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
