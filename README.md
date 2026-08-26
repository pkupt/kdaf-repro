# KDAF Reproduction

Independent replication of **Lunyakin (2026), "Auditable by Construction: An Ontology-Driven Framework for Trustworthy LLM Analytics in Enterprise Finance"** (arXiv:2608.20661), evaluated on FinanceBench.

**Result: the paper's central claim reproduces to the digit.**

| System | Traceability F1 (ours) | Traceability F1 (author) | Correctness (ours) | Correctness (author) |
|---|---|---|---|---|
| KDAF (graph_ontology) | **0.5147** | **0.5147** | 0.1241 | 0.1103 |
| BM25 | **0.4625** | **0.4625** | 0.1310 | 0.1172 |
| KDAF − BM25 | **+0.0522** | **+0.052** | — | −0.007 |

All data-layer SHA-256 checks and retrieval-layer M1–M8 audit metrics also match the author's deposited values exactly.

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

## REPRO-ADAPT (environment adaptations, documented for the community)

1. **`resource` module shim** (`win_wrapper.py`) — Windows lacks the Unix `resource` module; a shim is injected without modifying author code.
2. **Local tokenizer cache** — the codebase loads Qwen3-8B tokenizer with `local_files_only=True`; download the pinned revision to a local HuggingFace cache and repair Windows symlink failures by copying blobs.
3. **Offline transformers** — set `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` (transformers 4.57.6 issues a network call during tokenizer init that bypasses `local_files_only`).
4. **Qwen3 thinking-mode disable** — on Ollama 0.32.15, Qwen3 enters a reasoning mode for complex questions, consuming the `num_predict` budget (256) and yielding empty responses. One-line change in `mpr_a/llm.py`: add `"think": False` to the top level of the generation payload to match the author's no-think configuration.

## Content Notes

- FinanceBench data and the author's artifact are **not** redistributed here — obtain them under their own terms (artifact: Zenodo DOI above; data: https://github.com/patronus-ai/financebench).
- `results/` contains numeric summaries only (no benchmark text).

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
