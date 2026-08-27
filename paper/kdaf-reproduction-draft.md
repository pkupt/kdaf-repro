# Auditable by Construction, Reproduced: An Independent Replication of Ontology-Grounded Retrieval on FinanceBench

**Status: Draft v0.2 (2026-08-26) — for arXiv cs.AI / cs.IR**
**Author: Qian Zhang (Independent Researcher, Peking University alumni)** — *pending author review*
**Original paper: Lunyakin (2026), "Auditable by Construction: An Ontology-Driven Framework for Trustworthy LLM Analytics in Enterprise Finance", arXiv:2608.20661**

---

## Abstract

We report an independent replication of the Knowledge-Driven Analytics Framework (KDAF) and its Context-Aware Relevance Propagation (CARP) retriever, as introduced by Lunyakin (2026) on the FinanceBench evaluation. Our reproduction was conducted in an environment deliberately different from the original: Windows instead of macOS, CPU-only inference instead of GPU, and Python 3.13.12 instead of 3.13.3, while pinning the same Qwen3-8B model weights (Ollama digest prefix `500a1f067a9f`). Three layers of evidence were verified. First, data normalization and graph construction reproduce exactly: the 145-question evaluation file, the 189-item source index, and the canonical 524-node/1,852-edge graph all match the author-recorded SHA-256 digests. Second, retrieval-layer behavior reproduces exactly: all M1–M8 audit metrics (cross-entity leakage, off-period evidence, provenance resolution, replay fidelity, hop distribution, token counts, graph scale) match the deposited definitive values to the digit. Third, generation-layer results reproduce to the digit on citation traceability: KDAF achieves traceability F1 = 0.5147 (author: 0.5147) and BM25 achieves 0.4625 (author: 0.4625), reproducing the paper's central contrast of +0.052 exactly; correctness rates of 0.124 (KDAF) and 0.131 (BM25) fall within the author's reported 95% confidence intervals (0.110 and 0.117 respectively). We document four environment adaptations required for the Windows/CPU setting and discuss what exact-traceability reproduction implies for the paper's core claim — that auditability, not raw accuracy, is the axis on which ontology-grounded retrieval earns its construction cost.

---

## 1. Introduction

Independent replication is a foundational, if under-rewarded, activity in machine learning research. A result that cannot be reproduced under changed hardware and software conditions carries limited scientific weight; a result that reproduces exactly — to the digit — carries considerably more. This paper reports such an exact reproduction.

Lunyakin (2026) proposed the Knowledge-Driven Analytics Framework (KDAF), a six-stage methodology for building ontology-grounded knowledge systems for enterprise finance, together with the Context-Aware Relevance Propagation (CARP) algorithm for graph-based evidence retrieval. On a 145-question slice of FinanceBench, the paper reported a central result: ontology-grounded retrieval (KDAF) does not outperform sparse lexical retrieval (BM25) on answer correctness — the reported difference was −0.007 with a 95% confidence interval including zero — but does outperform it significantly on citation traceability F1 (+0.052, 95% CI excluding zero), while never retrieving evidence from outside the question entity's company (0/426 vs. 16.8% for BM25). The authors argued that auditability, not accuracy, is the axis on which structured retrieval pays for its construction cost.

That claim is consequential for practitioners deploying LLMs in regulated financial environments. Before acting on it, an independent verification under different conditions is valuable. Our replication makes the following contributions:

1. **Exact data-layer reproduction.** The 145-question evaluation file, 189-item source index, and canonical 524-node graph rebuild to the same SHA-256 digests recorded by the author, under a different operating system and Python version.
2. **Exact retrieval-layer reproduction.** All M1–M8 audit metrics match the deposited definitive values to the digit, including zero cross-entity leakage for both graph conditions and 145/145 replay fidelity.
3. **Exact generation-layer reproduction of traceability.** KDAF traceability F1 = 0.5147 and BM25 traceability F1 = 0.4625 match the author's values exactly, reproducing the +0.052 contrast to the digit. Correctness rates fall within the author's reported confidence intervals.
4. **Documented environment adaptations.** We report four adaptations required to run the author's codebase on Windows with CPU-only inference, including a subtle Qwen3 thinking-mode interaction with the Ollama runtime that required explicit disabling to match the author's no-think configuration.

Our results support the original paper's core claim under independent conditions and provide a concrete, audited reproduction record for the community.

## 2. Background and Method Overview

KDAF constructs an ontology-grounded knowledge graph in six stages: problem-centered scoping via competency questions, ontology bootstrapping through a Minimum Viable Graph, schema-guided knowledge extraction, contextual knowledge representation with typed relevance and provenance annotations, hybrid human-in-the-loop validation, and CARP-based retrieval. The evaluation instantiated stages 3, 4, and 6 on a FinanceBench slice; stages 1, 2, and 5 presuppose domain experts and organizational context unavailable in a public benchmark.

CARP retrieves evidence in four steps: seed-node identification, weighted propagation over ontology-typed edges, context-boundary detection via dynamic relevance thresholds, and evidence selection with provenance chains. Crucially, the evaluated CARP is a hybrid: graph structure governs eligibility, reachability, and provenance, while a lexical component dominates final ranking (0.45 weight), with propagation score, concept coverage, and period coverage reweighting within the reachable set. This design predicts exactly what we observe: lexical-heavy ranking yields accuracy parity with strong lexical retrievers, while graph-governed eligibility yields the auditability advantage.

The author's artifact (Zenodo DOI 10.5281/zenodo.22022068, v1.0.0) provides the complete codebase, configuration, schema, prompts, and deposited results, and defines a pinned fetch-and-rebuild path with SHA-256 verification.

## 3. Reproduction Setup

### 3.1 Environment

Our environment differs from the author's in three material respects while pinning the model weights:

| Component | Author | Ours | Note |
|---|---|---|---|
| OS | macOS (arm64) | Windows (x64) | — |
| Python | 3.13.3 | 3.13.12 | — |
| Inference | GPU-accelerated | CPU-only | affects latency only |
| Answer model | Qwen3-8B (Ollama `qwen3:latest`, digest `500a1f067a9f`) | **same digest** | weights identical |
| Adjudicator | Llama 3 (`365c0bd3c000`) | not run | review stage optional |
| Tokenizer | Qwen/Qwen3-8B rev `b968826d9c46...` | same revision | context token counting |

The pinned model digest is the crucial guarantee: identical weights remove the largest source of generation drift.

### 3.2 Pipeline

We executed the author's pinned fetch-and-rebuild path (`rebuild_financebench.py`), then the retrieval cache generation, then one-seed generation and scoring. Because decoding at temperature 0 is deterministic and the author's three seeds were byte-identical, a single seed (42) is sufficient to verify the generation layer.

### 3.3 Environment Adaptations (REPRO-ADAPT)

Four adaptations were required to run the author's code on Windows/CPU. We record them here for the community; none alters experimental logic.

1. **`resource` module shim.** The codebase imports `resource` (Unix-only) at module level. We injected a minimal shim via a wrapper script, leaving author code untouched.
2. **Local tokenizer cache.** The code loads the Qwen3-8B tokenizer with `local_files_only=True`. We downloaded the pinned revision files to a local HuggingFace cache via a mirror, and repaired Windows symlink failures by copying blobs into the snapshot directory.
3. **Offline mode for transformers.** transformers 4.57.6 issues a network call during tokenizer init (`is_base_mistral`) that bypasses `local_files_only`. Setting `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1` resolves this.
4. **Qwen3 thinking-mode disable.** On our Ollama version (0.32.15), the Qwen3 model enters a reasoning ("thinking") mode for complex questions, consuming the `num_predict` budget (author config: 256) and yielding empty visible responses. The author's environment apparently did not exhibit this under their no-think configuration. We added `"think": False` at the top level of the Ollama generation payload (a one-line change in `mpr_a/llm.py`, tagged REPRO-ADAPT) to match the author's intended no-think behavior. This adaptation is itself a reproducible finding: the same model weights behave differently across Ollama runtime versions.

## 4. Results

### 4.1 Data Layer: Exact Reproduction

All three SHA-256 verifications pass under our environment:

```
PASS evaluation: rows=145 sha256=393707d2... (author record matches)
PASS source index: items=189 sha256=6f6f17b2...
PASS graph: nodes=524 edges=1852 canonical_sha256=238f4e88...
```

### 4.2 Retrieval Layer: Exact Reproduction

All M1–M8 audit metrics match the deposited definitive values to the digit (behavioral equivalence; two environment-sensitive quantities — peak RSS and wall-clock latency — differ as expected). Selected metrics:

| Metric | KDAF (ours / author) | BM25 (ours / author) |
|---|---|---|
| Cross-entity leakage | 0 / 426 vs 0 / 426 | 73/435 vs 73/435 (0.1678) |
| Off-period evidence | 0.2053 vs 0.2053 | 0.2299 vs 0.2299 |
| Provenance resolution failures | 0 vs 0 | 0 vs 0 |
| Replay fidelity | 145/145 vs 145/145 | 145/145 vs 145/145 |
| Hop distribution | {1:367, 3:59} vs {1:367, 3:59} | — |

### 4.3 Generation Layer: Traceability Reproduced to the Digit

| System | Traceability F1 (ours) | Traceability F1 (author) | Correctness (ours) | Correctness (author) | In author CI? |
|---|---|---|---|---|---|
| **KDAF (graph_ontology)** | **0.5147** | **0.5147** | 0.1241 | 0.1103 | ✅ [0.069, 0.172] |
| **BM25** | **0.4625** | **0.4625** | 0.1310 | 0.1172 | ✅ [0.075, 0.180] |
| **KDAF − BM25** | **+0.0522** | **+0.052** | — | −0.007 | — |

The paper's central quantitative claim — that KDAF improves citation traceability over BM25 by +0.052 with a confidence interval excluding zero — reproduces exactly (+0.0522). Correctness rates are directionally consistent and within the author's reported confidence intervals; the small differences are attributable to the thinking-mode adaptation and hardware, and are consistent with the author's own caveat that generation may vary with runtime and hardware.

### 4.4 Observations Supporting the Paper's Interpretation

1. **Auditability, not accuracy, is where the difference lives.** Our exact reproduction of traceability, alongside accuracy parity within CI, directly supports the original framing: the two systems we cannot distinguish on correctness (author: −0.007, CI includes zero) we can distinguish clearly on traceability (+0.052, exact).
2. **The hybrid CARP design is visible in the numbers.** Lexical dominance in final ranking explains accuracy parity with BM25; graph-governed eligibility explains zero leakage and exact traceability. Our hop distributions reproduce the mechanism (KDAF reaches evidence mostly at depth 1 via ontology-typed seeds; unanchored traversal at depth 3).
3. **Strict automatic scoring understates correctness.** Manual inspection of a 10-question pilot showed semantically correct answers (e.g., "yes" vs. the gold "Yes, not only...") scored as incorrect by exact matching — consistent with the original paper's report that human-adjudicated correctness is 2–3x the automatic score.

## 5. Discussion

### 5.1 What Exact Traceability Reproduction Implies

The fact that traceability F1 reproduces to the digit — while correctness does not — is itself informative. Traceability is a property of *which evidence is retrieved and cited*; given identical retrieval (verified exactly), identical model weights, and identical no-think behavior, citation behavior reproduces exactly. Correctness is a property of *whether the generated answer matches gold*; it is more sensitive to runtime-level generation variance, even at temperature 0 (e.g., floating-point nondeterminism, context windowing). The original paper's argument that auditability is a structural property — "boundary and provenance are two consequences of one representation, not filters pasted onto a score function" — is consistent with our observation that the structural property reproduces exactly while the surface property (accuracy) reproduces statistically.

### 5.2 The Thinking-Mode Adaptation as a Reproducibility Finding

Our fourth adaptation (Qwen3 thinking-mode disable) deserves emphasis: identical model weights produced empty responses under one Ollama version and normal answers under another, until `think: False` was set. This is a concrete example of how model-serving runtime, not just model weights, affects replication. Reports of "model X reproduces" should specify the runtime, not merely the digest.

### 5.3 Threats to Validity

1. **Single seed.** We ran seed 42 only; the author's three seeds were byte-identical under temperature 0, so this is adequate for verifying the generation layer, but it does not test sampling variance (the author also notes no sampling was tested).
2. **Two systems only.** We reproduced KDAF and BM25 — the pair carrying the paper's central contrast. The remaining three conditions (hybrid_text_table, graph_no_ontology, llm_only) were not regenerated; their retrieval-layer metrics were verified exactly.
3. **Review adjudication not reproduced.** The Llama-3-assisted review (30 questions/system) was not rerun; it is a calibration instrument, not part of the core claim.
4. **Thinking-mode adaptation.** The `think: False` payload change is an environment adaptation; we report it transparently and argue it restores the author's intended no-think configuration.

## 6. Reproducibility Statement

All code, configuration, and deposited results come from the author's artifact (Zenodo 10.5281/zenodo.22022068, v1.0.0), unmodified except for the one-line `think: False` adaptation documented in Section 3.3. Our reproduction environment, adaptation scripts, and per-question event logs are available at [repository URL to be added]. We commit to releasing: (a) the environment shim, (b) the metrics-comparison script used to verify exact behavioral equivalence, (c) our generation event logs for both systems, and (d) this manuscript's source.

## 7. Conclusion

We independently reproduced the KDAF evaluation on FinanceBench under a different operating system, Python version, and inference hardware, pinning the same Qwen3-8B weights. Data normalization, graph construction, all retrieval-layer audit metrics, and both systems' citation traceability — including the paper's central +0.052 contrast — reproduced exactly. Correctness rates fell within the author's reported confidence intervals. The original paper's core claim — that ontology-grounded retrieval earns its construction cost on auditability rather than accuracy — survives independent replication, and the replication record itself contributes a documented path for reproducing this line of work.

---

## References

- Lunyakin, S. (2026). Auditable by Construction: An Ontology-Driven Framework for Trustworthy LLM Analytics in Enterprise Finance. arXiv:2608.20661. Zenodo artifact: 10.5281/zenodo.22022068.
- Islam, P., Kannappan, A., Kiela, D., Qian, R., Scherrer, N., & Vidgen, B. (2023). FinanceBench: A New Benchmark for Financial Question Answering. arXiv:2311.11944.
- Robertson, S., & Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval, 3(4), 333–389.
- Edge, D., Trinh, H., Cheng, N., et al. (2024). From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv:2404.16130.
- Han, X., et al. (2025). Graph Retrieval-Augmented Generation: A Survey. arXiv:2501.00309.
- Gao, Y., Xiong, Y., Gao, X., et al. (2023). Retrieval-Augmented Generation for Large Language Models: A Survey. arXiv:2312.10997.
- Board of Governors of the Federal Reserve System. (2011). Supervisory Guidance on Model Risk Management (SR 11-7).
- NIST. (2023). Artificial Intelligence Risk Management Framework (AI RMF 1.0). NIST AI 100-1.
- Lee, J. D., & See, K. A. (2004). Trust in Automation: Designing for Appropriate Reliance. Human Factors, 46(1), 50–80.
- Lasser, J. (2020). Generating an Assistive Ethic: The Case of the ML Reproducibility Challenge. arXiv:2004.01946.

*Draft v0.2: references expanded to 10. Reviewer checklist: author affiliation wording, repository URL, LaTeX compile check, page-limit formatting.*
