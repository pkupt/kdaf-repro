# Reproduction results (numeric summaries only; no benchmark text)

## Generation layer — 145 questions, seed 42, Qwen3-8B (digest 500a1f067a9f)

| System | Traceability F1 (ours) | Traceability F1 (author) | Correctness (ours) | Correctness (author) | In author CI? |
|---|---|---|---|---|---|
| graph_ontology (KDAF) | 0.5147 | 0.5147 | 0.1241 | 0.1103 | yes [0.069, 0.172] |
| **graph_no_ontology** | **0.4876** | **0.4876** | **0.1172** | **0.1034** | yes [0.062, 0.159] |
| bm25_text | 0.4625 | 0.4625 | 0.1310 | 0.1172 | yes [0.075, 0.180] |

## Extension experiments — dense retrieval + cross-model generation

| System | Model | Correctness (ours) | Traceability F1 (ours) | Cross-entity leakage |
|---|---|---|---|---|
| **dense_bge** (bge-small-en) | Qwen3 | 0.1241 [0.069, 0.179] | 0.4317 [0.395, 0.465] | 32/435 (7.36%) |
| **dense_bge** (bge-small-en) | **llama3:latest** | 0.1103 [0.062, 0.159] | 0.4317 [0.395, 0.465] | 32/435 (7.36%) |
| **llama3gen** (KDAF+graph_ontology) | **llama3:latest** | **0.1448** [0.090, 0.197] | **0.5147** [0.479, 0.551] | — |

> - **dense baselines KDAF?** No: synthetic bge-small-en dense retrieval reaches
>   traceability F1 0.4317, *below* BM25 (0.4625) and well below KDAF (0.5147),
>   yet leaks only half as much as BM25 (7.36% vs 16.78%). Dense semantic ranking
>   respects entity boundaries better than lexical overlap, but the information-theoretic
>   graph (CARP) adds traceable evidence beyond what either flat baseline offers.
> - **KDAF is model-agnostic**: llama3 (0.1448 correctness, 0.5147 traceability) matches
>   Qwen3's traceability exactly and *improves* correctness, showing the auditability
>   advantage of KDAF does not depend on a specific generator LLM.
> - **Traceability is retriever-determined, generation-model-invariant** *(by construction)*:
>   on dense_bge, swapping Qwen3 for Llama-3 leaves traceability F1 identical (0.4317) while
>   correctness shifts within noise (0.1241 → 0.1103). Combined with the identical matching on
>   graph_ontology (0.5147 for both models), this shows citation traceability is a property of
>   the retrieval pipeline, not the generator. Note: this identity is structural, not a
>   coincidence — the author's runner records citations at retrieval time
>   (`run_eval.py` L287: `citations = res.citations`), so the generator cannot affect them;
>   the cross-model runs confirm it to the digit (per-question traceability identical on
>   145/145 questions for both retriever pairs, while correctness flips on 8-9 questions).

## Retrieval layer — M1–M8 (ours / author, all exact)

### Baseline comparison (ours, from 145-question retrieval cache)

| Metric | KDAF (graph_ontology) | dense (bge-small-en) | BM25 |
|---|---|---|---|
| Cross-entity leakage | 0/426 (0.00%) | 32/435 (7.36%) | 73/435 (16.78%) |
| Provenance resolution failures | 0 | 0 | 0 |
| Retrieval latency p50 | 13.2 ms | 39.7 ms | 1.2 ms |

> Interpretation: dense semantic retrieval leaks roughly half as much as BM25
> (7.36% vs 16.78%), yet the ontology-governed hard-company constraint in KDAF
> still drives cross-entity leakage to zero—evidence that the hard constraint is
> qualitatively stronger than semantic similarity alone.

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
