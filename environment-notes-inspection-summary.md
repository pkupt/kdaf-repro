# KDAF Reproduction — Environment Notes & Inspection Summary

> Prepared for the author's review, August 2026. This accompanies the
> reproduction of **Lunyakin (2026), "Auditable by Construction: An Ontology-Driven
> Framework for Trustworthy LLM Analytics in Enterprise Finance"** (arXiv:2608.20661).
> All hashes and metrics below are the values recorded in our independent, CPU-only
> run; nothing here is benchmark text.

---

## 1. Environment

| Component | Author (recorded) | Ours (reproduction) |
|---|---|---|
| OS | macOS (arm64) | Windows 11 (x64) |
| Python | CPython 3.13.3 | CPython 3.13.12 (venv) |
| NumPy / pandas | numpy 2.4.3, pandas 2.3.3 | same (from `environment/requirements.txt`) |
| transformers | 4.57.6 | 4.57.6 |
| Inference hardware | GPU | CPU-only |
| Answer model | Qwen3-8B, digest prefix `500a1f067a9f` | same digest |
| Adjudicator | llama3:latest (`365c0bd3c000`) | same digest |
| Tokenizer | Qwen/Qwen3-8B rev `b968826d9c46...` | same pinned revision, local cache |

Everything is run inside a Python 3.13 venv created from
`environment/requirements.txt`, with `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`
set throughout.

---

## 2. Environment adaptations required (Windows / CPU-only)

Four changes were needed, none of which modify the author's source behavior:

1. **`resource` module shim.** Windows has no Unix `resource` module. A shim
   (`win_wrapper.py`) injects stub `getrlimit`/`setrlimit` without touching the
   author's code.
2. **Local tokenizer cache.** The codebase loads the Qwen3-8B tokenizer with
   `local_files_only=True`; we cached the pinned revision locally via the HF CLI.
3. **Offline transformers.** `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` — on
   transformers 4.57.6 a network call fires during tokenizer init and bypasses
   `local_files_only`.
4. **Windows symlink repair.** HF CLI snapshot files were 0 bytes after extraction
   (Windows symlink failure); fixed by copying the underlying blobs into the
   snapshot layout.

---

## 3. Data-layer verification (SHA-256, all PASS)

| Artifact | SHA-256 | Status |
|---|---|---|
| Evaluation (145 rows) | `393707d2ff14dedd8f485d32d0e0390984b3a9254ac68ea844b4758fe9f261ac` | PASS |
| Source index (189 items) | `6f6f17b218db414fdbd2e832b5c3793c122059b70818b70563ce60f8e54614c0` | PASS |
| Canonical graph (524/1852) | `238f4e88078885a1ba69dc034aba732f1740a65a093b83126b414613aa0dd47b` | PASS |

---

## 4. Retrieval-layer inspection (M1–M8, all exact)

| Metric | Ours | Author (definitive) | Match |
|---|---|---|---|
| Cross-entity leakage — graph_ontology | 0.0000 | 0.0000 | ✅ exact |
| Cross-entity leakage — graph_no_ontology | 0.0000 | 0.0000 | ✅ exact |
| Cross-entity leakage — bm25_text | 0.1678 | 0.1678 | ✅ exact |
| Cross-entity leakage — hybrid | 0.2023 | 0.2023 | ✅ exact |
| Off-period evidence — graph_ontology | 0.2053 | 0.2053 | ✅ exact |
| Off-period evidence — graph_no_ontology | 0.2815 | 0.2815 | ✅ exact |
| Off-period evidence — bm25 / hybrid | 0.2299 / 0.2529 | 0.2299 / 0.2529 | ✅ exact |
| Provenance resolution failures (all systems) | 0 | 0 | ✅ |
| Replay fidelity (all systems) | 145/145 | 145/145 | ✅ |
| Hop distribution — graph_ontology | {1:367, 3:59} | {1:367, 3:59} | ✅ exact |
| Hop distribution — graph_no_ontology | {3:424} | {3:424} | ✅ exact |
| Graph scale | 524 nodes / 1,852 edges | same | ✅ |
| Context tokens — graph_ontology | mean 1581.4 / p50 1551 | same | ✅ |
| Context tokens — bm25_text | mean 1510.8 / p50 1423 | same | ✅ |

---

## 5. Generation-layer results (seed 42, 145 questions, Qwen3-8B)

| System | Traceability F1 (ours / author) | Correctness (ours / author) | In author CI? |
|---|---|---|---|
| graph_ontology (KDAF) | 0.5147 / 0.5147 | 0.1241 / 0.1103 | yes [0.069, 0.172] |
| graph_no_ontology | 0.4876 / 0.4876 | 0.1172 / 0.1034 | yes [0.062, 0.159] |
| bm25_text | 0.4625 / 0.4625 | 0.1310 / 0.1172 | yes [0.075, 0.180] |

Core comparison reproduces to the digit: **KDAF − BM25 = +0.0522** traceability
against the author's **+0.052**; the correctness difference (−0.007) is within
the reported confidence intervals.

---

## 6. Noted gap in documentation: Qwen3 thinking-mode

On our stack the one-line generation payload did **not** include an explicit
`"think": False`. Under Ollama, Qwen3 enters a reasoning mode on complex
questions, consuming the `num_predict` budget (256) and returning empty
responses. Adding `"think": False` to the top level of the generation payload (a
one-line change in `mpr_a/llm.py`) reproduces the author's no-think behavior and
the recorded metrics. The no-think configuration was implicit in the author's
environment, so it is absent from the artifact README; we flag it here as a
reproducibility fix and recommend documenting it for future reproductions.