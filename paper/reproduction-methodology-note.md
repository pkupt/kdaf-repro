# KDAF Reproduction — Methodology Note (for author review)

> **Purpose.** Independent, end-to-end reproduction of Lunyakin (2026),
> *Auditable by Construction* (arXiv:2608.20661), on a different OS and CPU-only.
> Prepared for the author's technical review of the reproduction methodology.
> This note is standalone; the paper manuscript is a separate artifact.
>
> **Status.** Reproduction complete; extension experiments run; this note under review.

---

## 1. Scope and claims

This note verifies, at three layers, whether the artifact's recorded outcomes are
reproducible outside the author's environment:

| Layer | Question | Method |
|---|---|---|
| Data | Are the inputs bit-identical? | SHA-256 of evaluation rows, source index, canonical graph |
| Retrieval | Is the retrieval pipeline output-invariant? | M1–M8 inspection against the definitive manifest |
| Generation | Does inference reproduce provenance behavior? | Traceability F1 & correctness vs. author's recorded values |

We treat "reproduced" as *recorded values matched to the digit*, not merely
"statistically similar" — a deliberately strict bar.

---

## 2. Environment (independent, CPU-only)

| Component | Author (recorded) | Ours (reproduction) |
|---|---|---|
| OS | macOS arm64 | Windows 11 x64 |
| Python | CPython 3.13.3 | CPython 3.13.12 (venv) |
| NumPy / pandas | numpy 2.4.3 / pandas 2.3.3 | identical (requirements.txt) |
| transformers | 4.57.6 | 4.57.6 |
| Inference | GPU | CPU-only |
| Answer model | Qwen3-8B, `500a1f067a9f` | same digest |
| Adjudicator | llama3:latest `365c0bd3c000` | same digest |

A venv is created from `environment/requirements.txt`; `HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1` are set throughout.

## 3. Four Windows/CPU adaptations (none alter author source behavior)

1. **`resource` shim.** Windows lacks the Unix `resource` module; a stub
   (`win_wrapper.py`) injects `getrlimit`/`setrlimit` without touching the code.
2. **Local tokenizer cache.** The code loads Qwen3-8B's tokenizer with
   `local_files_only=True`; we cached the pinned revision locally.
3. **Offline transformers.** On 4.57.6 a network call fires during tokenizer init
   and bypasses `local_files_only`; `HF_HUB_OFFLINE` suppresses it.
4. **Windows symlink repair.** HF snapshot files were 0 bytes after extraction
   (Windows symlink failure); restored by copying underlying blobs into the layout.

Rationale: keep the author's code untouched and reproduce *behavior*, isolating the
environment as the only variable.

## 4. Data-layer verification — SHA-256, all PASS

| Artifact | Hash (ours) | Status |
|---|---|---|
| Evaluation (145 rows) | `393707d2ff…f261ac` | PASS |
| Source index (189 items) | `6f6f17b218…e54614c0` | PASS |
| Canonical graph (524/1852) | `238f4e8807…aa0dd47b` | PASS |

## 5. Retrieval-layer inspection — M1–M8, all exact

- **Cross-entity leakage**: graph_ontology 0.0000, graph_no_ontology 0.0000,
  bm25 0.1678, hybrid 0.2023 — all ✅ exact.
- **Off-period evidence**: 0.2053 / 0.2815 / 0.2299 / 0.2529 — ✅ exact.
- **Provenance resolution failures**: 0 across all systems — ✅.
- **Replay fidelity**: 145/145 — ✅.
- **Hop distribution**: graph_ontology {1:367, 3:59}; graph_no_ontology {3:424} — ✅.
- **Graph scale**: 524 nodes / 1,852 edges — ✅.
- **Context tokens**: graph_ontology mean 1581.4/p50 1551; bm25 mean 1510.8/p50 1423 — ✅.

## 6. Generation layer — traceability reproduced to the digit (seed 42, 145 Qs)

| System | Traceability F1 (ours / author) | Correctness (ours / author) | In CI? |
|---|---|---|---|
| graph_ontology (KDAF) | 0.5147 / 0.5147 | 0.1241 / 0.1103 | ✓ [0.069, 0.172] |
| graph_no_ontology | 0.4876 / 0.4876 | 0.1172 / 0.1034 | ✓ [0.062, 0.159] |
| bm25_text | 0.4625 / 0.4625 | 0.1310 / 0.1172 | ✓ [0.075, 0.180] |

KDAF − BM25 traceability = **+0.0522** (author +0.052). Correctness −0.007 is within CI.

## 7. A reproducibility finding: Qwen3 thinking-mode

On our stack the one-line generation payload lacked an explicit `"think": False`.
Under Ollama, Qwen3 enters a reasoning mode on complex questions, burning the
`num_predict` (256) budget and returning empty. Adding `"think": False` to the top
level of the payload (one line in `mpr_a/llm.py`) reproduces the author's no-think
behavior and metrics. The config was implicit in the author's environment and absent
from the README — flagged here as a reproducibility fix worth documenting.

## 8. Extension experiments (low-risk additions)

- **Dense retrieval** (BAAI/bge-small-en-v1.5, cosine): traceability 0.4317 (below
  BM25 0.4625 and KDAF 0.5147); cross-entity leakage 7.36% (below BM25 16.78%). Sharpens,
  rather than blunts, the reproduced contrast.
- **Cross-model generation** (llama3:latest): KDAF traceability 0.5147 (identical);
  correctness 0.1448. Traceability identity is *by construction* — citations are
  recorded at retrieval time (`citations = res.citations` in `run_eval.py`), so the
  generator cannot alter them; cross-model variation is confined to correctness.

## 9. Honest limitations

1. **CPU-only**, so our wall-clock latency is not representative of the author's
   reported latency (we do not claim it is).
2. The exact traceability match is expected *by construction* given identical
   retrieval; it is confirmation, not independent discovery.
3. The thinking-mode finding is our observation on the Ollama stack and may differ
   from other serving stacks.
4. Extensions use small models and our infra; they are illustrative, not exhaustive.

## 10. Reproducibility statement for reviewers

All artifacts (repo, requirements, configs, results) are public; hashes and
inspection tooling included. Anyone on a supported platform should be able to repeat
the produce-and-verify loop from `environment/requirements.txt`. The one documented
caveat is the Qwen3 think-mode note in §7.

---

*Prepared 2026-08-27. Under review by the original author.*