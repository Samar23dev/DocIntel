#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "manifest.json"
SUMMARY = ROOT / "results" / "summary.json"
RESPONSES = ROOT / "results" / "responses.jsonl"
OUTPUT = ROOT / "REPORT.md"


def main() -> int:
    documents = json.loads(CORPUS.read_text(encoding="utf-8")) if CORPUS.exists() else []
    summary = json.loads(SUMMARY.read_text(encoding="utf-8")) if SUMMARY.exists() else []
    response_records = (
        [json.loads(line) for line in RESPONSES.read_text(encoding="utf-8").splitlines() if line.strip()]
        if RESPONSES.exists()
        else []
    )
    response_count = len(response_records)
    failed_responses = sum(row.get("exit_code") != 0 for row in response_records)
    auth_failures = sum("provider.auth" in str(row.get("answer", "")) for row in response_records)
    lines = [
        "# DocIntel Local Model Comparison Report",
        "",
        "## Scope",
        "",
        "This report compares OpenCode-configured language models against the same extracted-document context.",
        "Direct answers are not yet comparable with DocIntel RAG results because the retrieval pipeline must be added as a separate experiment.",
        "",
        "## Corpus",
        "",
        f"- Source documents: **{len(documents)}**",
        f"- Total extracted characters: **{sum(d['characters'] for d in documents):,}**",
        f"- Total extracted words: **{sum(d['words'] for d in documents):,}**",
        "",
        "| Document | Type | Characters | Words | Source SHA-256 |",
        "|---|---:|---:|---:|---|",
    ]
    for item in documents:
        suffix = Path(item["source"]).suffix.lower().lstrip(".").upper()
        lines.append(
            f"| {item['document_id']} | {suffix} | {item['characters']} | "
            f"{item['words']} | `{item['source_sha256'][:16]}...` |"
        )

    lines += ["", "## Experimental results", "",
              f"- Recorded responses: **{response_count}**",
              f"- Provider/model failures: **{failed_responses}**",
              f"- Authentication failures recorded: **{auth_failures}**", ""]
    if summary:
        lines += [
            "| Model | Responses | Reference contained | Human correct | Partial | Incorrect | Ungraded | Mean latency (s) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for item in summary:
            lines.append(
                f"| {item['model']} | {item['responses']} | "
                f"{item['reference_answer_contained']} | {item['correct']} | {item['partial']} | "
                f"{item['incorrect']} | {item['ungraded']} | {item['mean_latency_seconds']} |"
            )
    else:
        lines += [
            "No results have been evaluated yet. Run corpus extraction, provide verified questions, "
            "execute the models, then run result evaluation."
        ]

    lines += [
        "",
        "## Metrics used",
        "",
        "- Exact or normalized answer match for fixed questions.",
        "- Human correctness, partial correctness, and unsupported-answer assessment.",
        "- First-response/end-to-end latency.",
        "- Successful-response rate.",
        "- Source faithfulness and citation support after retrieval is added.",
        "",
        "## Fair comparison controls",
        "",
        "- Fixed extracted text and source checksum.",
        "- Identical question set and prompt.",
        "- Fixed prompt version.",
        "- Same temperature and maximum output settings.",
        "- Exact OpenCode model IDs.",
        "- Repeated runs to identify provider/model variability.",
        "",
        "## Limitations",
        "",
        "- Automated string matching does not establish semantic correctness.",
        "- The current direct-text baseline can receive context that does not fit a model window.",
        "- Vision/chart quality requires rendered-page testing and separately annotated ground truth.",
        "- This report must not present provider availability, latency, or quality as stable without repeated trials.",
        "- DocIntel's application-level comparison is pending because the local application container was unhealthy during the test run.",
        "",
    ]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
