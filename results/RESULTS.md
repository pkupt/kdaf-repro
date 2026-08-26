# Reproduction results (numeric summaries only; no benchmark text)

## Generation layer — 145 questions, seed 42, Qwen3-8B (digest 500a1f067a9f)

| System | Traceability F1 (ours) | Traceability F1 (author) | Correctness (ours) | Correctness (author) | In author CI? |
|---|---|---|---|---|---|
| graph_ontology (KDAF) | 0.5147 | 0.5147 | 0.1241 | 0.1103 | yes [0.069, 0.172] |
| **graph_no_ontology** | **0.4876** | **0.4876** | **0.1172** | **0.1034** | yes [0.062, 0.159] |
| bm25_text | 0.4625 | 0.4625 | 0.1310 | 0.1172 | yes [0.075, 0.180] |

## Retrieval layer — M1–M8 (ours / author, all exact)

| Metric | KDAF | BM25 |
|---|---|---|
| Cross-entity leakage | 0/426 (0.0%) | 73/435 (16.78%) |
| Off-period evidence | 0.2053 | 0.2299 |
| Provenance resolution failures | 0 | 0 |
| Replay fidelity | 145/145 | 145/145 |
| Hop distribution | {1:367, 3:59} | — |
| Graph scale | 524 nodes / 1,852 edges | — |

## Data layer — SHA-256 (all PASS, matching author records)

- evaluation (145 rows): `393707d2ff14dedd8f485d32d0e0390984b3a9254ac68ea844b4758fe9f261ac`
- source index (189 items): `6f6f17b218db414fdbd2e832b5c3793c122059b70818b70563ce60f8e54614c0`
- canonical graph (524/1852): `238f4e88078885a1ba69dc034aba732f1740a65a093b83126b414613aa0dd47b`
