# KDAF Reproduction

Independent replication of **Lunyakin (2026), "Auditable by Construction: An Ontology-Driven Framework for Trustworthy LLM Analytics in Enterprise Finance"** (arXiv:2608.20661), evaluated on FinanceBench.

**Result: the paper's central claim reproduces to the digit.**

| System | Traceability F1 (ours) | Traceability F1 (author) | Correctness (ours) | Correctness (author) |
|---|---|---|---|---|
| KDAF (graph_ontology) | **0.5147** | **0.5147** | 0.1241 | 0.1103 |
| Graph, no ontology | **0.4876** | **0.4876** | 0.1172 | 0.1034 |
| BM25 | **0.4625** | **0.4625** | 0.1310 | 0.1172 |
| KDAF − BM25 | **+0.0522** | **+0.052** | — | −0.007 |

All data-layer SHA-256 checks and retrieval-layer M1–M8 audit metrics also match the author's deposited values exactly.

### Extension experiments (ours, beyond the original scope)

| System | Model | Correctness | Trace F1 | Cross-entity leak |
|---|---|---|---|---|
| dense_bge (bge-small-en, new) | Qwen3-8B | 0.1241 | 0.4317 | 32/435 (7.36%) |
| dense_bge (new) | Llama-3 | 0.1103 | 0.4317 | 32/435 (7.36%) |
| KDAF graph_ontology (reproduced) | Qwen3-8B | 0.1241 | 0.5147 | 0/426 (0%) |
| llama3gen (new) | Llama-3 | **0.1448** | **0.5147** | — |

Dense semantic retrieval leaks half as much as BM25 but trails it on traceability; swapping the generator leaves traceability identical to the digit (retriever-determined) while correctness moves within noise. See `results/RESULTS.md` and the paper's extension section.

## Environment

| Component | Author | Ours |
|---|---|---|
| OS | macOS (arm64) | Windows (x64) |
| Python | 3.13.3 | 3.13.12 |
| Inference | GPU | CPU-only |
| Answer model | Qwen3-8B (digest `500a1f067a9f`) | same digest |

## How to Reproduce

1. Download the author's artifact: Zenodo 10.5281/zenodo.22022068 (v1.0.0)
2. Create a Python 3.13 venv and install `environment/requirements.txt`
3. Run the author's rebuild path (`rebuild_financebench.py --work-dir .`) — all SHA-256 checks must pass
4. Run retrieval: `run_eval.py --config ... --retrieval-only` (see the author's `reproduce.sh`)
5. Run generation with the `think: False` adaptation (below) — 145 questions, seed 42
6. Score with `eval/score.py`, compare against `results/definitive/`

This repository's `scripts/win_wrapper.py` and `scripts/compare_metrics.py` support steps 3 and 6 on Windows.

To re-run the **extension experiments** (dense retrieval baseline, cross-model generation), see `extension/README.md`: it contains the dense-retrieval module, the exact wiring into the author's `run_eval.py`, and the variant configuration files for every run behind `results/events/`.

## Repository layout

```
├── paper/kdaf-reproduction.tex   # manuscript source (PDF built locally, not committed)
├── scripts/win_wrapper.py        # Windows `resource` shim
├── scripts/compare_metrics.py    # behavioral-equivalence checker vs. deposited results
├── extension/                    # dense retriever module + wiring + variant configs
├── results/RESULTS.md            # numeric summary of all runs
└── results/events/               # per-question event logs, six generation runs
```

## REPRO-ADAPT (environment adaptations, documented for the community)

1. **`resource` module shim** (`win_wrapper.py`) — Windows lacks the Unix `resource` module; a shim is injected without modifying author code.
2. **Local tokenizer cache** — the codebase loads Qwen3-8B tokenizer with `local_files_only=True`; download the pinned revision to a local HuggingFace cache and repair Windows symlink failures by copying blobs.
3. **Offline transformers** — set `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` (transformers 4.57.6 issues a network call during tokenizer init that bypasses `local_files_only`).
4. **Qwen3 thinking-mode disable** — on Ollama 0.32.15, Qwen3 enters a reasoning mode for complex questions, consuming the `num_predict` budget (256) and yielding empty responses. One-line change in `mpr_a/llm.py`: add `"think": False` to the top level of the generation payload to match the author's no-think configuration.

## Content Notes

- FinanceBench data and the author's artifact are **not** redistributed here — obtain them under their own terms (artifact: Zenodo DOI above; data: https://github.com/patronus-ai/financebench).
- `results/RESULTS.md` contains numeric summaries only (no benchmark text).
- `results/events/` contains the per-question event logs for all six generation runs (answers, citations, timings, token counts, per-question scores). The benchmark question text was **redacted** from these logs at deposit time (the `inputs` field of each generation event was removed; a `redaction_note` on the first line documents this). Notes on two known log quirks — duplicate identical score rows in `events_full_go.jsonl` and 49 post-scoring retries in `events_gno.jsonl` — are in `extension/README.md`.

## License

MIT (this repository's own code). The author's artifact keeps its own dual license (MIT for code, CC BY 4.0 for docs/schema/prompts/results).

## Citation

```bibtex
@misc{zhang2026kdafrepro,
  title={Auditable by Construction, Reproduced: An Independent Replication of Ontology-Grounded Retrieval on FinanceBench},
  author={Zhang, Kevin},
  year={2026},
  note={arXiv preprint}
}
```
