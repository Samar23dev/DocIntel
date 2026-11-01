# DocIntel, OpenCode, and OpenRouter Model Comparison Report

## 1. Executive summary

This experiment compares DocIntel retrieval-based question answering with direct full-document prompting of five OpenCode/OpenRouter models. The evaluation uses 14 railway documents and 10 fixed, source-verified questions covering facts, tables, thresholds, and operational records.

| System/model | Correct semantic answers | Textual answers / 10 | Answer success rate | Mean latency of textual answers |
|---|---:|---:|---:|---:|
| DocIntel + Gemini 3.5 Flash Lite | 10 | 10 | 100% | 14.11 s (recorded runs) |
| Thinking Machines Inkling Small Free | 10 | 10 | 100% | 2.80 s |
| Cohere North Mini Code Free | 8 | 8 | 80% | 2.99 s |
| GLM 5.3 Flash Free | 2 | 2 | 20% | 3.12 s |
| Nemotron 3.5 Lightning Free | 2 | 2 | 20% | 8.92 s |
| Nemotron 3.5 Super VL Free | 2 | 2 | 20% | 26.15 s* |

\*The first Super VL run succeeded and the second produced a correct textual answer despite a non-zero process exit. Its latency mean covers both textual responses.

DocIntel achieved the strongest observed semantic coverage (10/10) because it restricts the answer workflow to retrieved workspace evidence. The two OpenCode OpenRouter models with reliable provider responses also performed strongly.

## 2. Experimental setup

### 2.1 Corpus

The corpus contains 14 documents:

- 3 PDF railway inspection or manual documents;
- 3 PDF operational reports;
- 3 DOCX procedural, technical, and incident documents;
- 3 XLSX operational or asset registers; and
- 2 additional PDF documents covering freight and dashboard information.

All source texts and source SHA-256 hashes are recorded in `corpus/manifest.json`.

### 2.2 Direct-model experiment

Each OpenCode model received extracted document text plus the question. This is a **full-text direct prompting** baseline, not a visual-page or DocIntel-RAG baseline.

- Model routes: the three `opencode/*` routes and two direct OpenRouter routes;
- Prompt version: `v1`;
- Mode: `direct-document-text`;
- Maximum output timeout: 180 seconds;
- Evaluation basis: source-grounded human semantic correctness.

### 2.3 DocIntel experiment

DocIntel received the same 10 questions through `/api/search/ask/simple`. It used the configured Gemini 3.5 Flash Lite model for strategy, answer, and final-answer stages, with corpus retrieval and source citations.

DocIntel is not directly equivalent to the model-only experiments because it adds:

- document ingestion and extraction;
- text chunking and embedding;
- semantic retrieval;
- source-constrained answer generation;
- final answer synthesis.

## 3. Per-model results

### 3.1 Direct OpenCode/OpenRouter models

#### Thinking Machines Inkling Small Free

Inkling provided a semantic answer for all 10 questions and all 10 answers were human-correct.

- Valid textual responses: 10/10;
- Human correctness: 10/10;
- Provider or process failures: 0;
- Mean latency: 2.796 seconds.

#### Cohere North Mini Code Free

Cohere answered the first 8 questions correctly. Questions q09 and q10 did not return usable answer text and are recorded as provider/session failures.

- Valid textual responses: 8/10;
- Human correctness among valid responses: 8/8;
- Provider or process failures: 2;
- Mean latency for valid responses: approximately 2.99 seconds.

#### GLM 5.3 Flash Free

GLM returned only two usable textual answers (q01 and q02), and both were correct. The remaining runs returned OpenCode JSON event records rather than a final answer and had exit status 0, indicating incomplete CLI result extraction rather than valid model answers.

- Valid textual responses: 2/10;
- Correct among valid responses: 2/2;
- Mean latency for valid responses: 3.121 seconds.

#### Nemotron 3.5 Lightning Free

Lightning returned two usable textual answers (q01 and q02), and both were correct.

- Valid textual responses: 2/10;
- Correct among valid responses: 2/2;
- Mean latency for valid responses: 8.922 seconds.

#### Nemotron 3.5 Super VL Free

Super VL produced usable text for q01 and q02. Both answers were correct. The q02 invocation had a non-zero process exit despite returning a complete answer.

- Valid textual responses: 2/10;
- Correct among valid responses: 2/2;
- Process exit anomaly: 1 response;
- Mean latency for textual responses: approximately 26.15 seconds.

### 3.2 DocIntel

DocIntel answered all 10 questions correctly in the final verified run.

- Strategy/answer/final-answer model: Gemini 3.5 Flash Lite;
- Correct answers: 10/10;
- Incorrect answers: 0;
- Provider/parsing failures in final dataset: 0;
- Mean recorded latency: 14.106 seconds.

## 4. Question-level semantic comparison

| ID | Question category | DocIntel | GLM | Lightning | Super VL | Cohere | Inkling |
|---|---|---:|---:|---:|---:|---:|---:|
| q01 | Maximum speed | Correct | Correct | Correct | Correct | Correct | Correct |
| q02 | Table defect/action | Correct | Correct | Correct | Correct | Correct | Correct |
| q03 | Technical specifications | Correct | No final answer | No final answer | No final answer | Correct | Correct |
| q04 | Safety architecture | Correct | No final answer | No final answer | No final answer | Correct | Correct |
| q05 | Threshold lookup | Correct | No final answer | No final answer | No final answer | Correct | Correct |
| q06 | Material strength | Correct | No final answer | No final answer | No final answer | Correct | Correct |
| q07 | Incident location | Correct | No final answer | No final answer | No final answer | Correct | Correct |
| q08 | Spreadsheet summary | Correct | No final answer | No final answer | No final answer | Correct | Correct |
| q09 | Fleet count | Correct | No final answer | No final answer | No final answer | Provider failure | Correct |
| q10 | Asset register | Correct | No final answer | No final answer | No final answer | Provider failure | Correct |

A provider failure is different from a wrong answer: it means the comparison invocation did not yield a usable answer. These events are still reported in denominator metrics rather than silently ignored.

## 5. Accuracy interpretation

Two denominator conventions are necessary:

1. **Coverage accuracy:** correct answers divided by all 10 questions.
2. **Conditional correctness:** correct answers divided by usable textual answers.

| System/model | Coverage accuracy | Conditional correctness |
|---|---:|---:|
| DocIntel | 10/10 = 100% | 10/10 = 100% |
| Inkling Small | 10/10 = 100% | 10/10 = 100% |
| Cohere North Mini | 8/10 = 80% | 8/8 = 100% |
| GLM 5.3 Flash | 2/10 = 20% | 2/2 = 100% |
| Lightning Free | 2/10 = 20% | 2/2 = 100% |
| Super VL Free | 2/10 = 20% | 2/2 = 100% |

The conditional-correctness column demonstrates answer quality when each model did respond. It does not replace coverage accuracy, because service reliability is part of real-world system performance.

## 6. Reliability and latency

- **DocIntel:** complete reliability in the final rerun; highest latency, but includes retrieval, synthesis, and citation generation.
- **Inkling Small:** best direct-model balance in this run: 100% coverage and the lowest completed-response mean latency of the complete models.
- **Cohere:** strong conditional correctness, with two late provider failures.
- **GLM and Lightning:** usable answers only for the two initial questions; the observed validity issue prevents broad performance conclusions.
- **Super VL:** correct usable answers but slower latency and one non-zero process exit; this is not evidence of superior vision capability because the experiment supplied extracted text, not page images.

## 7. Fairness and validity constraints

- Direct models received extracted text, whereas DocIntel performed document ingestion, retrieval, and synthesis.
- DocIntel retrieval settings, embedding model, chunk size, overlap, and top-K must be frozen for a publication-quality RAG study.
- The OpenCode records include provider-session and CLI-result-extraction failures. They must not be treated as incorrect document answers.
- Free-provider availability can change, and free-route models may be rate-limited.
- Nemotron Super VL's vision capability was not exercised by this text-only run.
- Automated string containment is useful only as screening, not as the final correctness metric.
- One measured run is insufficient for statistical confidence. Repeat the full benchmark at least three times.

## 8. Conclusions

For this limited 10-question study:

1. **DocIntel achieved 100% coverage** and source-grounded answers for every question after provider-sensitive reruns.
2. **Inkling Small achieved the same 100% coverage among direct OpenCode/OpenRouter models**, with substantially lower mean direct-answer latency.
3. **Cohere achieved 100% conditional correctness among eight usable responses**, but two invocations failed.
4. The partial results for GLM, Lightning, and Super VL cannot support a broad quality ranking. Additional reruns are required to separate provider/harness failures from model capability.
5. Vision-based chart and diagram accuracy is not established by this experiment and requires rendered-page evaluation.

## 9. Recommended reporting language

Use coverage and reliability separately:

- “DocIntel answered 10/10 questions correctly in a source-grounded final run.”
- “Inkling answered 10/10 questions correctly; its mean textual-response latency was 2.80 seconds.”
- “Cohere answered 8/8 usable questions correctly, but 2 of 10 invocations failed.”
- “GLM, Lightning, and Super VL were usable for 2 questions each, so their 20% coverage must not be interpreted as a definitive model-quality score.”
