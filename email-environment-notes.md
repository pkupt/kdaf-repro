# Email draft — send environment notes to author (Sergiy Lunyakin)

**Subject:** Reproduction environment notes, as promised

---

Sergiy,

Here are the environment notes and inspection summary I mentioned — attached as a
single Markdown file.

The short version: full reproduction on Windows 11 (x64), Python 3.13.12, **CPU-only**,
transformers 4.57.6, HF_HUB_OFFLINE=1, Qwen3-8B digest `500a1f067a9f` — same as yours.
Four Windows/CPU adaptations were needed (resource shim, local tokenizer cache, offline
transformers, symlink repair); none of them touch your source behavior.

Everything on the verification side lined up to the digit:
- All three SHA-256 data checks PASS
- M1–M8 retrieval inspection: cross-entity leakage, off-period evidence, hop
  distribution, graph scale, context tokens — all exact
- Generation layer: KDAF minus BM25 traceability comes out to **+0.0522** (your **+0.052**)

The one real finding is worth flagging separately: on my stack the generation payload
didn't include an explicit `"think": False`, and under Ollama Qwen3 enters a reasoning
mode on complex questions that burns the `num_predict` budget and returns empty. Adding
that one line reproduces your no-think behavior and the recorded numbers. Since it was
implicit in your environment it's absent from the README — happy to work with you on
how best to note it there.

Use whatever's useful. If anything looks off, flag it and I'll dig in.

Best,
Kevin

---

## Self-review (what I deliberately avoided)

- No filler ("I hope this finds you well"), no stacked thanks, no checklist tone.
- The thinking-mode finding is stated factually and claimed only as *our* observation
  ("on my stack"), not as a criticism — matches the author's own framing.
- One concrete number (+0.0522 vs +0.052) anchors the whole note; everything else is
  secondary.
- Ends with an open, low-friction invitation rather than a demand.