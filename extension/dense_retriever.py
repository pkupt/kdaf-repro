from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import numpy as np
from transformers import AutoConfig, AutoTokenizer

from retrieval.base import RetrievalResult

_MODEL_CACHE_DIR = os.environ.get(
    "KDAF_HF_CACHE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cache", "huggingface"),
)


class DenseRetriever:
    """bge-small-en dense (vector) retrieval baseline.

    Reuses the same FinanceBench evidence index as the BM25/CARP retrievers
    (same 189-page source corpus + same citation/trace plumbing) but ranks
    evidence by embedding cosine similarity instead of lexical overlap.

    This module is OUR addition for the extension experiments (paper Section 4.4).
    It is not part of the author's artifact; wiring it in requires the
    three-line registration described in extension/README.md.
    """

    name = "dense_bge"

    def __init__(
        self,
        source_index_path: str,
        system: str = "dense_bge",
        top_k: int = 3,
        context_bound_source_record_id: bool = False,
        model_name: str = "BAAI/bge-small-en-v1.5",
    ):
        self.system = system
        self.top_k = top_k
        self.context_bound_source_record_id = context_bound_source_record_id
        self.model_name = model_name
        self.sources = list(json.loads(Path(source_index_path).read_text(encoding="utf-8")).values())
        self.searchable_texts = [self._prepare_source(source) for source in self.sources]
        self._model = None
        self._tokenizer = None
        self._doc_vecs = None

    def _prepare_source(self, source: dict[str, Any]) -> str:
        evidence_text = str(source.get("evidence_text", ""))
        full_page = str(source.get("evidence_text_full_page", ""))
        doc_name = str(source.get("doc_name") or source.get("source_document") or "")
        company = str(source.get("company", ""))
        table_text = " ".join(str(v) for v in (source.get("table") or []))
        return f"{company} {doc_name} {evidence_text} {full_page[:1600]} {table_text[:1000]}"

    def _load_model(self):
        if self._model is not None:
            return
        config = AutoConfig.from_pretrained(
            self.model_name, cache_dir=_MODEL_CACHE_DIR, local_files_only=True
        )
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, cache_dir=_MODEL_CACHE_DIR, local_files_only=True
        )
        from transformers import BertModel

        self._model = BertModel.from_pretrained(
            self.model_name,
            config=config,
            cache_dir=_MODEL_CACHE_DIR,
            local_files_only=True,
        )
        self._model.eval()

    def _embed(self, texts: list[str]) -> np.ndarray:
        self._load_model()
        batch_size = 8
        all_vecs: list[np.ndarray] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            encoded = self._tokenizer(
                batch, padding=True, truncation=True, max_length=512, return_tensors="pt"
            )
            with _no_grad():
                out = self._model(
                    input_ids=encoded["input_ids"],
                    attention_mask=encoded["attention_mask"],
                )
            vec = out.last_hidden_state[:, 0, :].detach().numpy()
            vec = vec / (np.linalg.norm(vec, axis=1, keepdims=True) + 1e-9)
            all_vecs.append(vec)
        return np.vstack(all_vecs)

    def _scored(self, query_vec: np.ndarray, doc_vecs: np.ndarray) -> list[tuple[float, int, dict[str, Any]]]:
        scores = (doc_vecs @ query_vec).ravel()
        return [(float(scores[i]), i, self.sources[i]) for i in range(len(self.sources))]

    def _doc_vectors(self) -> np.ndarray:
        if self._doc_vecs is None:
            self._doc_vecs = self._embed(self.searchable_texts)
        return self._doc_vecs

    def run_question(self, question: dict[str, Any]) -> RetrievalResult:
        start = time.perf_counter()
        query = str(question["question"])
        query_vec = self._embed([query])[0]
        scored = self._scored(query_vec, self._doc_vectors())

        source_record_id = question.get("source_record_id")
        if self.context_bound_source_record_id and source_record_id:
            scored = [
                (score + 1000.0 if str(doc.get("source_record_id")) == str(source_record_id) else score, idx, doc)
                for score, idx, doc in scored
            ]
        scored.sort(key=lambda item: (-item[0], item[1]))
        selected = [doc for _score, _idx, doc in scored[: self.top_k]]

        retrieval_ms = (time.perf_counter() - start) * 1000
        citations = [str(item["id"]) for item in selected]
        evidence_blocks = [self._format_evidence(item) for item in selected]
        trace = {
            "trace_schema_version": "retrieval-trace-v1",
            "algorithm": "dense-bge-v1",
            "system": self.system,
            "parameters": {
                "top_k": self.top_k,
                "model": self.model_name,
                "similarity": "cosine",
            },
            "seed_nodes": [],
            "traversal_decisions": [],
            "ranked_candidates": [
                {
                    "rank": rank,
                    "citation": str(doc["id"]),
                    "score": round(float(score), 6),
                    "threshold": 0.0,
                    "decision": "selected_top_k" if rank <= self.top_k else "not_selected",
                }
                for rank, (score, _idx, doc) in enumerate(scored, start=1)
            ],
            "selected_evidence": [
                {
                    "citation": str(doc["id"]),
                    "score": round(float(score), 6),
                    "selection_decision": "selected_top_k",
                }
                for score, _idx, doc in scored[: self.top_k]
            ],
        }
        return RetrievalResult(
            answer="unknown",
            citations=citations,
            retrieved_sources=citations,
            evidence_blocks=evidence_blocks,
            retrieval_ms=retrieval_ms,
            generation_ms=6.0,
            token_prompt=sum(len(block.split()) for block in evidence_blocks),
            token_completion=8,
            trace=trace,
        )

    def run(self, question: str) -> RetrievalResult:
        return self.run_question({"question": question})

    def _format_evidence(self, source: dict[str, Any]) -> str:
        text = " ".join(str(source.get("evidence_text", "")).split())
        doc_name = source.get("doc_name") or source.get("source_document")
        page = source.get("evidence_page_num")
        source_key = source.get("source_key")
        if page is not None:
            location = f"{doc_name} page {page}"
        elif source_key:
            location = f"{doc_name} support {source_key}"
        else:
            location = str(doc_name)
        return f"[{source['id']}] {location}: {text}"


class _no_grad:
    def __enter__(self):
        import torch

        self._ctx = torch.no_grad()
        self._ctx.__enter__()
        return self

    def __exit__(self, *exc):
        self._ctx.__exit__(*exc)
        return False
