# Independent DocIntel Model Evaluation

This folder contains a separate, reproducible model-comparison harness. It does not modify or depend on the DocIntel runtime.

## Corpus

The corpus is read from `../files`. Supported formats are PDF, DOCX, and XLSX. Extraction output and source hashes are written to `corpus/`.

The current repository contains nine test documents: three PDFs, three DOCX files, and three XLSX files. Add documents to `../files` and rerun extraction before producing a larger study.

## Configured models

The initial comparison uses the OpenCode OpenRouter IDs configured in `config/models.json`:

- Nemotron 3 Super 120B
- GLM Flash

OpenCode must be authenticated and the exact IDs must be confirmed before publishing results:

```bash
~/.opencode/bin/opencode models | grep -E 'nemotron|glm'
```

## Run

```bash
cd /path/to/DocIntel
python3 research_eval/scripts/extract_corpus.py
cp research_eval/ground_truth/questions.jsonl.example research_eval/ground_truth/questions.jsonl
# Edit the JSONL to contain verified answers from the source documents.
python3 research_eval/scripts/run_opencode_comparison.py \
  --questions research_eval/ground_truth/questions.jsonl
python3 research_eval/scripts/evaluate_results.py \
  --responses research_eval/results/responses.jsonl
python3 research_eval/scripts/generate_report.py
```

## Human grading

Add a `human_grade` field to relevant records in `results/responses.jsonl` using one of:

- `correct`
- `partial`
- `incorrect`
- `unanswered`

Also add `evidence_citation`, `citation_supported`, `unsupported_claim`, and `source_conflict` fields where available. String-match percentages are only screening metrics and must not be the sole publication result.

## Metrics

The direct-document baseline should report:

- exact and normalized answer match;
- human correctness and partial correctness;
- source-supported answer rate;
- hallucination and unsupported-claim rate;
- unanswered-question accuracy;
- model success and error rate;
- mean and percentile latency; and
- provider cost/token usage when OpenCode exposes it.

For controlled RAG comparisons, add `top-K`, retrieved passage IDs, Recall@K, MRR, NDCG, and citation precision/recall.
