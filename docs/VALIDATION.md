# Validation Record

## Data and Statistics

- Six models, 66 original CSV files, 44,669 rows, 18 overall results, and 192 per-subject results.
- Each CSV was checked against its local source for SHA-256, row count, reference-answer order, and subjects.
- All 19 pinned source files across the three datasets were downloaded online. The 11 prepared JSON files matched the historical input hashes exactly; removing an out-of-scope model did not change data conversion.
- Pinned revisions of all six models and three datasets were verified through the Hugging Face API; see `metadata/source_verification.json`.
- Five Python scripts passed syntax checks, and all 66 inference dry-run combinations (six models across 11 data partitions) were checked.
- `scripts/verify.py` checks archive hashes and compares regenerated statistics byte for byte. Verification was also performed in an independent copy of the archive.
- Release files were scanned for common access-token patterns. Model weights and complete datasets are not bundled.

Data reconstruction used Python 3.12, pandas 2.3.0, and pyarrow 24.0.0. Offline aggregation uses only the standard library. The dependency lists are not complete historical environment locks.

## English-Language Update

Documentation, generated result-table text, historical code comments, and console messages were translated into English. Two upstream card passages were also translated, as documented in `docs/TRANSLATION.md`.

Preservation checks compare raw CSV files, reference-answer metadata, machine-readable statistics, and generation configurations with the preceding commit. Historical Python code is compared at the AST level after excluding console-print statements, ensuring that prompts and evaluation logic remain unchanged. Archive checksums are regenerated only after these checks.

## Not Performed

GPU generation and judging have not been rerun. Training has not been reproduced, answers have not been manually adjudicated, and benchmarks have not been rescored with their official implementations. New seed and attention settings are not claims about original experimental parameters.

## Verification Commands

```bash
python scripts/summarize.py
python scripts/verify.py
python scripts/prepare_data.py --output /tmp/chemistry-data-check
python scripts/evaluate.py --model Qwen3-0.6B --benchmark MASCQA --data-root /tmp/chemistry-data-check --output /tmp/chemistry-dry-run --dry-run
```

SHA256SUMS reports intentional archive modifications by design. Review changes before updating the manifest; do not use regenerated hashes to conceal unverified changes to raw CSV files.
