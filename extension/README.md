# Extension experiments: dense retrieval + cross-model generation

Everything needed to re-run the extension conditions reported in the paper
(Section "Extension Experiments: Dense Retrieval and Cross-Model Generation").
None of these files alter the reproduction path: the author's artifact runs
unmodified for all reproduced conditions; the items below are additive.

## Contents

- `dense_retriever.py` — dense (vector) retrieval baseline using
  `BAAI/bge-small-en-v1.5` embeddings with cosine ranking. It reuses the
  author's evidence index and citation/trace plumbing, so its outputs are
  scored by the same pipeline as every other system.
- `configs/` — the variant configuration files used for our runs (see mapping
  below). Drop them into the artifact's `configs/variants/` directory.

## Wiring the dense retriever into the author's artifact

1. Copy `dense_retriever.py` into `<artifact>/scripts/retrieval/dense_retriever.py`.

2. In `<artifact>/scripts/runner/run_eval.py`, add one import next to the
   other retriever imports (top of file):

   ```python
   from retrieval.dense_retriever import DenseRetriever
   ```

3. In the same file's `make_retrievers(...)` registry dict, add one entry:

   ```python
   "dense_bge": DenseRetriever(
       real_source_index,
       "dense_bge",
       top_k=top_k,
       context_bound_source_record_id=context_bound_source_record_id,
   ),
   ```

That is the entire code delta for the extensions. The module loads the
embedding model with `local_files_only=True` from a local HuggingFace cache;
point the `KDAF_HF_CACHE` environment variable at your cache directory
(defaults to `<repo>/.cache/huggingface`).

## Config → event log mapping

| Config (`configs/`) | Purpose | Event log (`../results/events/`) |
|---|---|---|
| `real_financebench_kdaf_carp_qwen_full_go.yaml` | reproduction: graph_ontology, Qwen3 | `events_full_go.jsonl` |
| `real_financebench_kdaf_carp_qwen_gno.yaml` | reproduction: graph_no_ontology, Qwen3 | `events_gno.jsonl` |
| `real_financebench_kdaf_carp_qwen_bm25.yaml` | reproduction: bm25_text, Qwen3 | `events_bm25.jsonl` |
| `real_financebench_kdaf_carp_dense.yaml` | extension: dense_bge retrieval-only, writes retrieval cache | (cache only, no generation events) |
| `real_financebench_kdaf_carp_qwen_dense_gen.yaml` | extension: dense_bge + Qwen3 generation | `events_dense_gen.jsonl` |
| `real_financebench_kdaf_carp_llama3.yaml` | extension: graph_ontology + Llama-3 generation | `events_llama3.jsonl` |
| `real_financebench_kdaf_carp_llama3_dense.yaml` | extension: dense_bge + Llama-3 generation | `events_dense_llama3.jsonl` |
| `real_financebench_kdaf_carp_qwen_kdaf_score.yaml` | re-scoring pass over an existing run's outputs | appends score rows |
| `real_financebench_kdaf_carp_llama3_score.yaml` | re-scoring pass | appends score rows |
| `real_financebench_kdaf_carp_qwen_dense_score.yaml` | re-scoring pass | appends score rows |

The first three are single-system convenience variants used for the
reproduction runs; the next four are the extension conditions; the last three
re-score existing event logs without regenerating (they produced the second,
identical scoring pass recorded in `events_full_go.jsonl`).

## Notes on the deposited event logs

- **Question text redacted.** The `inputs` field of each generation event was
  removed at deposit time (FinanceBench redistribution terms; see the root
  README). Everything else — per-question answers, citations, timings, token
  counts, and per-question scores — is the run record, unmodified. Full
  unredacted logs remain in the run environment.
- **`events_full_go.jsonl`** contains two identical score rows per question
  (in-run scoring plus one re-scoring pass with `..._score.yaml`); both passes
  agree on every digit.
- **`events_gno.jsonl`** contains 49 questions with two generation events: a
  later retry pass appended events after scoring. The recorded scores
  correspond to the first event per question, and citations are identical
  across both attempts (traceability is unaffected either way).
