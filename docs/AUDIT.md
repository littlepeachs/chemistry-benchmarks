# Evaluation Protocol and Scoring Conventions

## Statistics

- Six public models and three benchmarks, covering 66 CSV files and 44,669 records.
- `accuracy_all_pct`: the historical yes/no parser, with all recorded rows in the denominator. Ambiguous judgments are not counted as correct.
- `accuracy_valid_pct`: the same parser, using only unambiguous judgments in the denominator, for comparison with historical summaries.
- `historical_yes_pct`: the original inference script's substring-based yes count divided by CSV row count. This is neither strict yes/no parsing nor official answer matching.
- All statistics are generated from the included CSV files. `ambiguous.json` lists unresolved judgments; no manual adjudication has been performed.
- The old summary code ambiguously split filenames when the evaluated model was also Qwen3-8B. The current implementation uses a fixed suffix and an explicit model list instead of manually overridden summaries.

## Inference Protocol

Qwen3-8B judges all models. Because the evaluated Qwen3-8B and its judge share the same model identity, these LLM-as-judge results should not be equated with official benchmark metrics.

Qwen uses a non-thinking chat template and a limit of 1,024 generated tokens. Other settings are inherited from the pinned generation configuration: do_sample=true, temperature=0.6, top_p=0.95, and top_k=20 in the observed configuration.

ChemDFM uses `User: ...\nAssistant:` with temperature=0.9, top_p=0.9, top_k=20, repetition_penalty=1.05, and a 1,024-token limit. ChemLLM receives the prompt directly, with temperature=0.9, top_k=1, repetition_penalty=1.5, and a 500-token limit.

The original Qwen script constructs judge prompts with the evaluated model's tokenizer, then encodes them with the judge tokenizer. The other two model families construct prompts with the judge tokenizer. The portable implementation preserves these differences; this is not a uniform prompting protocol.

## Data Conversion and Coverage

Historical ChemBench preprocessing selects `examples[0]` from each row, takes the first option with a score of 1.0 when multiple options are correct, and emits at most labels A-H. This differs from official multiple-answer or numerical scoring. Rebuilding the pinned source data reproduces the historical prepared-content hashes.

The nine ChemBench4K files follow the recorded historical concatenation order, not environment-dependent `os.listdir()` order. The original ChemLLM script skips index 3814 and records 4,008 rows, compared with 4,009 for other models. The reason was not recorded. Its original console denominator remains 4,009, unlike the CSV-row denominator. Removing that input position aligns reference answers exactly with the existing CSV.

## Reproduction Limits

The original CSV files do not record question IDs, runtime model hashes, seeds, GPU details, or complete environments. The current row index was reconstructed by checking prepared inputs against reference-answer order; it is not newly invented historical metadata. Cached revisions establish download provenance but do not replace runtime weight-identity records.

Statistics can be recomputed exactly offline. The portable inference script sets a new seed and records configuration and environment details. However, its default SDPA differs from the original FlashAttention setup, and GPU evaluation has not been rerun. Identical regenerated answers are not guaranteed.

Historical evaluation and preprocessing code is available in `legacy/`, with English translations of comments and console messages. Model prompts, control flow, and generation settings are unchanged. Manuscript drafts, old figures, training artifacts, and out-of-scope models are excluded.
