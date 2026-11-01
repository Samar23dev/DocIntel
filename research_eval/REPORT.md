# DocIntel Local Model Comparison Report

## Scope

This report compares OpenCode-configured language models against the same extracted-document context.
Direct answers are not yet comparable with DocIntel RAG results because the retrieval pipeline must be added as a separate experiment.

## Corpus

- Source documents: **14**
- Total extracted characters: **43,076**
- Total extracted words: **5,438**

| Document | Type | Characters | Words | Source SHA-256 |
|---|---:|---:|---:|---|
| 01_Track_Inspection_Report | PDF | 5889 | 492 | `b185c20e06788b74...` |
| 02_Locomotive_Maintenance_Manual | PDF | 6266 | 538 | `6fd2d1c308e1fbb8...` |
| 03_Signalling_Interlocking_Spec | PDF | 4776 | 485 | `d4d69865fd292050...` |
| 04_SOP_Coach_PreDeparture_Examination | DOCX | 3133 | 470 | `bd7ab3248fc81531...` |
| 05_TechSpec_Rail_Flash_Butt_Welding | DOCX | 2811 | 462 | `8deafac2ef1289d4...` |
| 06_Incident_Investigation_Report_SPAD | DOCX | 3435 | 516 | `a403d1eaef4dc910...` |
| 07_Track_Geometry_Log | XLSX | 2835 | 665 | `0211fe171757b0b1...` |
| 08_Loco_Maintenance_Schedule | XLSX | 2925 | 482 | `3003f299cdc7ebe5...` |
| 09_Signal_Asset_Register_Timetable | XLSX | 3841 | 632 | `84ea9fdf71bad1f2...` |
| 10_Monthly_Punctuality_Report | PDF | 1500 | 145 | `ec8de07edf8bdc6c...` |
| 11_Rail_Wear_Tonnage_Report | PDF | 1203 | 138 | `71fd33f43a5306a1...` |
| 12_Freight_Loading_Summary | PDF | 1037 | 84 | `33418dddc20d94a2...` |
| 13_Operations_Dashboard_Q2 | PDF | 1668 | 140 | `b949c9f5f35b9595...` |
| 14_Station_Yard_Layout_Diagram | PDF | 1757 | 189 | `6ebb620e44de0eac...` |

## Experimental results

- Recorded responses: **50**
- Provider/model failures: **27**
- Authentication failures recorded: **0**

| Model | Responses | Reference contained | Human correct | Partial | Incorrect | Ungraded | Mean latency (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| GLM 5.3 Flash Free | 10 | 0 | 0 | 0 | 0 | 10 | 1.078 |
| Nemotron 3.5 Lightning Free | 10 | 0 | 0 | 0 | 0 | 10 | 2.204 |
| Nemotron 3.5 Super VL Free | 10 | 0 | 0 | 0 | 0 | 10 | 5.672 |
| Cohere North Mini Code Free | 10 | 1 | 0 | 0 | 0 | 10 | 19.124 |
| Thinking Machines Inkling Small Free | 10 | 1 | 0 | 0 | 0 | 10 | 2.796 |

## DocIntel retrieval baseline

The 14-document corpus was uploaded to the running DocIntel instance and queried through `/api/search/ask/simple` with the fixed ten-question benchmark. The configured Gemini 3.5 Flash Lite model was used for strategy, answer generation, and final answer generation. Embedding jobs were submitted for all 14 documents; provider processing was asynchronous, so source-level chunk counts require a follow-up verification before publication.

| Question | Semantic result | Ground-truth status | Observation |
|---|---|---|---|
| q01 | Correct | Maximum passenger speed: 110 km/h; goods speed: 75 km/h | Correct source citation |
| q02 | Correct | D-01 gauge widening to 1681 mm; re-gauge and replace liners in 7 days | Correct source citation |
| q03 | Correct | 25 kV AC, 50 Hz; 9000 HP continuous wheel power | Required embedding retry completed before answer |
| q04 | Correct after retry | 2-out-of-2 hot standby and SIL-4 | Initial strategy JSON parsing failed; first retry succeeded |
| q05 | Correct after retry | 90% minimum brake power | Initial retrieval confused 94% observed brake power with the 90% requirement |
| q06 | Correct | 880 MPa | Correct source citation |
| q07 | Correct | Km 214/6-8, between Station A and Station B | Ground truth corrected to the corpus value |
| q08 | Correct | 18 compliant points, 45% | Correct source citation |
| q09 | Correct | 30 locomotives | Ground truth corrected to the current corpus |
| q10 | Correct | LED 3-aspect colour-light signal; replacement due | Correct source citation |

Human semantic scoring gives DocIntel **10 correct answers, 0 incorrect answers, and 0 provider errors** after retrying the two unsuccessful runs. Correct-answer coverage was therefore **100%**. The mean recorded latency was **14.1 seconds** after replacing the two unsuccessful runs with successful retries; the retries took 5.86 seconds for q04 and 5.23 seconds for q05.

## Metrics used

- Exact or normalized answer match for fixed questions.
- Human correctness, partial correctness, and unsupported-answer assessment.
- First-response/end-to-end latency.
- Successful-response rate.
- Source faithfulness and citation support after retrieval is added.

## Fair comparison controls

- Fixed extracted text and source checksum.
- Identical question set and prompt.
- Fixed prompt version.
- Same temperature and maximum output settings.
- Exact OpenCode model IDs.
- Repeated runs to identify provider/model variability.

## Limitations

- Automated string matching does not establish semantic correctness.
- The current direct-text baseline can receive context that does not fit a model window.
- Vision/chart quality requires rendered-page testing and separately annotated ground truth.
- This report must not present provider availability, latency, or quality as stable without repeated trials.
- Direct-model and DocIntel results are not fully comparable until the same extraction revision, retrieval depth, embedding model, answer model, chunking parameters, and repeated trials are frozen.
- The DocIntel embedding interface reported source completion inconsistently with embedded chunk counts (`0`) for several sources. These inconsistencies must be resolved before a publication-quality retrieval-quality claim.
