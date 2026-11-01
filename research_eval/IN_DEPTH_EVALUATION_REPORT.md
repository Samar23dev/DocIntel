# In-Depth DocIntel Evaluation and Model Comparison Report

## Abstract

This report documents an end-to-end comparative evaluation of DocIntel and five direct OpenCode/OpenRouter language-model configurations. The study used 14 railway documents, 10 fixed source-grounded questions, automated document extraction, checksum recording, provider response collection, latency measurement, and human semantic grading. DocIntel's final verified result was 10 correct answers out of 10. The direct-model results were mixed because several OpenCode provider runs produced incomplete JSON event output or provider-session failures rather than usable final answers. Consequently, reliability must be reported together with semantic accuracy.

## 1. Research objective

The evaluation was designed to answer:

1. Can DocIntel retrieve and synthesize correct answers from a small document corpus?
2. How do selected free OpenCode/OpenRouter models perform when the complete extracted source text is supplied directly?
3. What differences arise between direct full-context prompting and application-level retrieval plus synthesis?
4. How reliable are provider/model executions, and which measured failures are operational rather than semantic?
5. Which evidence, controls, and repeat experiments are required before publishing the result as a statistically supported paper claim?

## 2. Scope of the completed work

### 2.1 What has been implemented

The following components were created and used:

| Area | Implementation |
|---|---|
| Corpus extraction | PDF extraction with `pdftotext`, DOCX paragraph extraction, and XLSX sheet/cell extraction |
| Source identity | SHA-256 checksums recorded for every source document |
| Benchmark questions | 10 fixed JSONL questions with reference answers |
| Direct-model runner | OpenCode CLI runner using JSON output and 180-second command timeouts |
| Model configuration | Five named model routes stored in JSON |
| Response logging | Timestamp, question, model, provider exit code, answer, stderr, latency, and source hash |
| Automated screening | Normalized-text reference containment |
| Human scoring | Semantic grading of usable answers against source-grounded references |
| DocIntel baseline | Upload, extraction, embedding, retrieval, generation, and source citation checks |
| Comparative reporting | Detailed Markdown and machine-readable result summaries |

### 2.2 What has been measured

| Measurement | Status |
|---|---:|
| Corpus extraction success | 14/14 documents |
| DocIntel final semantic accuracy | 10/10 |
| Direct-model semantic answers with human review | 22 usable answers |
| OpenCode/OpenRouter provider execution failures | Recorded in raw responses |
| End-to-end model or application latency | Recorded |
| Source citation presence | Recorded for DocIntel |
| OCR/image vision accuracy | Not measured |
| Retrieval Recall@K | Not measured |
| MRR/NDCG | Not measured |
| Citation precision/recall | Not measured |
| Repeated statistical runs | Not yet complete |

## 3. Corpus and data preparation

### 3.1 Source corpus

The corpus is located in `../sampledocs` and consists of 14 documents:

- PDF: 8
- DOCX: 3
- XLSX: 3

| Document | Format | Extracted words |
|---|---|---:|
| 01 Track Inspection Report | PDF | 492 |
| 02 Locomotive Maintenance Manual | PDF | 538 |
| 03 Signalling Interlocking Specification | PDF | 485 |
| 04 Coach Pre-Departure Examination SOP | DOCX | 470 |
| 05 Rail Flash Butt Welding Technical Specification | DOCX | 462 |
| 06 SPAD Incident Investigation Report | DOCX | 516 |
| 07 Track Geometry Log | XLSX | 665 |
| 08 Locomotive Maintenance Schedule | XLSX | 482 |
| 09 Signal Asset Register Timetable | XLSX | 632 |
| 10 Monthly Punctuality Report | PDF | 145 |
| 11 Rail Wear Tonnage Report | PDF | 138 |
| 12 Freight Loading Summary | PDF | 84 |
| 13 Operations Dashboard Q2 | PDF | 140 |
| 14 Station Yard Layout Diagram | PDF | 189 |

The extracted corpus contains approximately 5,438 words.

### 3.2 Extraction strategy

PDFs were converted to layout-oriented text with `pdftotext`. DOCX paragraphs were read from `word/document.xml`. XLSX worksheets were read from workbook XML and relationship metadata, with shared-string lookup and row-preserving tab-separated output.

This preserves textual values and tables but does not necessarily preserve every visual layout, merged cell, rendered page, chart, label, or image.

### 3.3 Integrity controls

Each source is identified by:

- original file path;
- document ID derived from its filename;
- extracted-text path;
- extracted character and word counts;
- SHA-256 source hash.

The hashes permit any later run to verify that source documents have not changed.

## 4. Question set design

Ten fixed questions were used:

| ID | Type | Information tested |
|---|---|---|
| q01 | Direct fact | Train speed |
| q02 | Table lookup | Defect and corrective action |
| q03 | Technical fact | Voltage and traction power |
| q04 | Technical fact | Safety architecture |
| q05 | Threshold lookup | Brake-power acceptance criterion |
| q06 | Technical fact | Rail tensile strength |
| q07 | Incident lookup | Location and kilometre |
| q08 | Spreadsheet summary | Compliant count and percentage |
| q09 | Spreadsheet aggregation | Fleet count |
| q10 | Asset-register lookup | Asset type and replacement status |

The references cover numeric, categorical, procedural, and multi-part facts. Five additional documents were not represented by the original ten-question set and should receive additional questions for balanced coverage.

## 5. Direct-model experimental protocol

### 5.1 Models tested

| Display name | Model route |
|---|---|
| GLM 5.3 Flash Free | `opencode/glm-5.3-flash-free` |
| Nemotron 3.5 Lightning Free | `opencode/nemotron-3.5-lightning-free` |
| Nemotron 3.5 Super VL Free | `opencode/nemotron-3.5-super-vl-free` |
| Cohere North Mini Code Free | `openrouter/cohere/north-mini-code:free` |
| Thinking Machines Inkling Small Free | `openrouter/thinkingmachines/inkling-small:free` |

The experiment did not use text, image, and model configuration in separate controlled branches. All direct-model requests used extracted document text.

### 5.2 Prompt

The fixed prompt instructed the model to answer only from the supplied document and explicitly permitted a non-answer if the document did not contain evidence. It supplied:

1. document ID;
2. full extracted text associated with that ID;
3. fixed question.

The prompt version was `v1`.

### 5.3 Execution

The runner recorded wall-clock latency around the complete OpenCode CLI process, with a 180-second timeout. It requested JSON output, extracted `text` event records, and preserved raw CLI output if parsing yielded no final text.

## 6. DocIntel experimental protocol

DocIntel was used through the `/api/search/ask/simple` API. A notebook or corpus-wide scope restriction was not used in the stored baseline.

The three-stage request used Gemini 3.5 Flash Lite for:

- query strategy;
- answer synthesis;
- final answer synthesis.

The workflow was:

1. Upload the source document.
2. Extract text and metadata.
3. Submit embedding work.
4. Retrieve relevant corpus passages.
5. Generate source-grounded partial answers.
6. Produce and return a final answer with source IDs.

## 7. Result classification

Four categories are used for the direct-model outputs:

- **Usable text:** a non-empty answer extracted from the final response.
- **Correct:** the answer is semantically equivalent to the verified reference.
- **Provider/session failure:** CLI output contains only JSON event records, provider errors, incomplete output, or an invocation anomaly.
- **Exit anomaly:** a textual answer exists but the OpenCode process returns a non-zero status.

Automated normalized-reference containment was not used as proof of semantic correctness. Human semantic review was applied to usable answers.

## 8. Detailed results

### 8.1 DocIntel

| Result | Count |
|---|---:|
| Correct | 10 |
| Incorrect | 0 |
| Provider/process failures | 0 |
| Coverage | 100% |

The previously observed DocIntel failures on q04 and q05 were corrected by independent retries:

- q04 initially suffered strategy-response parsing, then produced a correct SIL-4 architecture answer.
- q05 initially confused 94% observed brake power with the 90% required minimum, then produced the correct threshold.

The final verified latency after replacing unsuccessful observations with successful retries was 14.106 seconds mean across 10 stored runs.

### 8.2 Thinking Machines Inkling Small

| Metric | Value |
|---|---:|
| Usable responses | 10/10 |
| Correct | 10/10 |
| Coverage accuracy | 100% |
| Conditional correctness | 100% |
| Provider failures | 0 |
| Mean textual-answer latency | 2.796 seconds |

Inkling was the strongest complete direct-model result in the measured run. Its answers covered all 10 documents represented in the fixed question set and included q09 and q10, which two direct models did not successfully complete.

### 8.3 Cohere North Mini Code

| Metric | Value |
|---|---:|
| Usable responses | 8/10 |
| Correct among usable responses | 8/8 |
| Coverage accuracy | 80% |
| Conditional correctness | 100% |
| Provider/process failures | 2 |
| Mean usable-response latency | Approximately 3.0 seconds |

The failures were q09 and q10. They should be treated as incomplete provider executions rather than evidence that Cohere answered those questions incorrectly.

### 8.4 GLM 5.3 Flash

GLM produced usable final answers for q01 and q02, and both were semantically correct.

The later rows contained OpenCode JSON event records where the runner was not able to extract a final answer. Despite exit status 0, they cannot be counted as usable model responses.

| Metric | Value |
|---|---:|
| Usable responses | 2/10 |
| Correct among usable responses | 2/2 |
| Coverage accuracy | 20% |

### 8.5 Nemotron 3.5 Lightning

Lightning produced usable final answers for q01 and q02, and both were correct. Other rows contained incomplete CLI output rather than a final textual answer.

| Metric | Value |
|---|---:|
| Usable responses | 2/10 |
| Correct among usable responses | 2/2 |
| Coverage accuracy | 20% |
| Mean usable-response latency | 8.922 seconds |

### 8.6 Nemotron 3.5 Super VL

Super VL returned correct textual answers for q01 and q02. q02 additionally demonstrated a process exit anomaly:

- complete text was present;
- process exit status was non-zero.

| Metric | Value |
|---|---:|
| Usable responses | 2/10 |
| Correct among usable responses | 2/2 |
| Coverage accuracy | 20% |
| Exit anomalies | 1 |

This is not a vision evaluation. The text-only prompt did not send rendered page images, charts, diagram regions, or OCR pixels to the vision-language model.

## 9. Comparative interpretation

| System/model | Coverage | Usable responses | Reliability |
|---|---:|---:|---:|
| DocIntel | 100% | 10/10 | Complete final rerun |
| Inkling Small | 100% | 10/10 | Complete |
| Cohere | 80% | 8/10 | Two provider/process failures |
| GLM Flash | 20% | 2/10 | Eight incomplete output records |
| Lightning | 20% | 2/10 | Eight incomplete output records |
| Super VL | 20% | 2/10 | Eight incomplete output records; one exit anomaly |

Coverage accuracy should not be used alone:

- A model with 2 correct answers out of 2 usable responses can still have only 20% corpus coverage.
- A provider failure is not the same thing as an incorrect answer.
- Conditional correctness and coverage should be published together.

## 10. Latency

Direct latency measures the OpenCode CLI process. DocIntel latency includes retrieval and generation stages, while direct-model latency includes sending extracted text through the OpenCode/provider route.

These values are therefore not equivalent service-level latency measurements.

The reported direct model ranges are:

- Inkling: approximately 2.80 seconds per textual response;
- Cohere: approximately 3.0 seconds per usable response;
- GLM: approximately 3.12 seconds per usable response;
- Lightning: approximately 8.92 seconds per usable response;
- Super VL: approximately 26.15 seconds across the two textual responses.

Provider queueing, authentication, route instability, geographic location, and concurrent use may materially change these values.

## 11. Threats to validity

### 11.1 Corpus imbalance

The question set covers only the first nine documents with the original numbering, plus the first question from document 01. Fourteen documents were extracted, but five additional documents lack matching evaluation questions. The benchmark therefore cannot claim balanced coverage of the full corpus.

### 11.2 Extraction mismatch

The direct models consumed extracted text. PDF layout, DOCX formatting, spreadsheet formula results, merged cells, images, and diagrams may not be represented accurately. DocIntel itself may run a different extraction pipeline.

### 11.3 Provider instability

Free OpenCode/OpenRouter routes can rate-limit, change routing, become unavailable, or return partial CLI output. One provider run recording exit status 0 can still contain JSON event data instead of a final answer.

### 11.4 No repeated trials

A single 50-call result cannot measure variability. Confidence intervals and median/p95 latency require repeated runs on the same fixed corpus and prompt.

### 11.5 Human scoring consistency

The publication should retain the question references and independent human-review records. Grading from answer text alone is susceptible to scorer interpretation, especially for multi-part answers.

## 12. Remaining work before publication

1. Add balanced questions for documents 10-14.
2. Include chart, table, numerical, summary, cross-document, and unanswerable questions.
3. Fix or broaden final-text extraction for OpenCode JSON.
4. Retry failed calls until provider status can be classified reproducibly.
5. Add human grades directly to every raw response.
6. Run three or more complete trials.
7. Report success rate, accuracy, macro-average latency, median latency, p95 latency, and confidence intervals.
8. Freeze chunk size, overlap, embedding model, top-K, retrieval temperature, generation model, and output settings.
9. Measure retrieval Recall@K, MRR, and NDCG against human-labelled supporting passages.
10. Measure citation precision, citation recall, unsupported claims, hallucination, and source conflicts.
11. Compare full-document direct prompting with matching retrieved context.
12. Add rendered-page and vision-model testing for images, charts, diagrams, and tables.

## 13. Recommended publication metrics

| Category | Primary metric |
|---|---|
| Answer quality | Human correctness coverage |
| Reliability | Answer-return success rate |
| Robustness | Repeated-run correctness variance |
| Evidence | Citation precision and recall |
| Hallucination | Unsupported-claim rate |
| Retrieval | Recall@K, MRR, NDCG |
| Source localization | Correct-source citation rate |
| Latency | Median and p95 latency |
| Cost | Provider cost or token usage when available |
| Vision | OCR accuracy, table accuracy, chart numeric accuracy |

## 14. Recommended conclusions

The defensible conclusions from the completed run are:

1. DocIntel produced correct source-grounded answers for all 10 questions in the final rerun.
2. Inkling Small produced complete, correct answers for all 10 direct-model questions in one complete run.
3. Cohere produced correct answers for every usable response, with 2 provider/session failures.
4. Partial GLM, Lightning, and Super VL coverage cannot establish their relative document-question quality and must be rerun.
5. The current evidence supports reliability and small-corpus correctness reporting, but not a statistically significant claim of general superiority.
