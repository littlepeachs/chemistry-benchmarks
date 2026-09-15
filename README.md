# Chemistry Benchmarks

A reproducible archive of six public models evaluated on **ChemBench**, **MASCQA**, and **ChemBench4K**, with raw predictions, scoring scripts, model download links, and dataset provenance.

- **Models:** Qwen3-0.6B, Qwen3-1.7B, Qwen3-4B, Qwen3-8B, ChemDFM-v1.0-13B, and ChemLLM-7B-Chat.
- **Coverage:** 66 raw CSV files, 44,669 evaluation records, 18 overall results, and 192 per-subject results.
- **Scoring:** Qwen3-8B as an LLM judge, not the official benchmark scoring implementations. Both all-record and valid-judgment denominators are reported.
- **Scope:** No model weights, complete datasets, training artifacts, or manuscript drafts are included.

## Results and Offline Reproduction

See [the results tables](results/RESULTS.md) and [the evaluation protocol](docs/AUDIT.md). Every score is recomputed from the included CSV files, without manually entered overrides.

Run from the repository root with Python 3.9 or later. No GPU, network access, or third-party packages are required:

```bash
python scripts/summarize.py
python scripts/verify.py
```

The first command verifies CSV checksums, row counts, reference-answer order, and subjects, then generates overall, per-subject, and per-file statistics in CSV, JSON, Markdown, and LaTeX, together with an ambiguous-judgment list. The second verifies archive checksums and compares regenerated summaries byte for byte in a temporary directory.

## Model Downloads

| Model | Download |
|---|---|
| Qwen3-0.6B | https://huggingface.co/Qwen/Qwen3-0.6B |
| Qwen3-1.7B | https://huggingface.co/Qwen/Qwen3-1.7B |
| Qwen3-4B | https://huggingface.co/Qwen/Qwen3-4B |
| Qwen3-8B | https://huggingface.co/Qwen/Qwen3-8B |
| ChemDFM-v1.0-13B | https://huggingface.co/OpenDFM/ChemDFM-v1.0-13B |
| ChemLLM-7B-Chat | https://huggingface.co/AI4Chem/ChemLLM-7B-Chat |

ChemDFM and ChemLLM are chemistry-specialized comparison models, not Qwen derivatives. Their local configurations identify LlamaForCausalLM and InternLM2ForCausalLM, respectively. Qwen3-8B also serves as the judge for every evaluation.

`metadata/models.json` pins the historical revisions found in the local download cache. `metadata/source_verification.json` records Hugging Face API verification. The download script does not silently upgrade to the current main branch or substitute another model version.

## Dataset Sources and Preparation

| Benchmark | Source | Evaluated subset |
|---|---|---|
| ChemBench | https://huggingface.co/datasets/jablonkagroup/ChemBench | Nine subject-specific train Parquet files, used for evaluation in the historical protocol; 2,786 records |
| MASCQA | https://huggingface.co/datasets/heegyu/mascqa | Test Parquet file from the distribution used in this project; 650 records |
| ChemBench4K | https://huggingface.co/datasets/AI4Chem/ChemBench4K | Nine test JSON files; 4,009 records; dev excluded |

ChemBench and ChemBench4K are separate datasets. Pinned revisions, source-file checksums, concatenation order, and prepared-content checksums are recorded in `metadata/datasets.json`. Dataset cards are included in `metadata/dataset_cards/`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-data.txt
python scripts/prepare_data.py
```

The script downloads files over HTTPS at the pinned revisions, verifies SHA-256 checksums, and rebuilds `data/`. To use existing downloads, pass `--source-root /path/to/datasets`. Prepared outputs must match the canonicalized content hashes of the historical evaluation inputs.

## Rerunning Inference

Inference requires a BF16-capable GPU and sufficient memory to load both the evaluated model and the 8B judge. The portable dependency configuration has not undergone a complete end-to-end GPU evaluation. Historical environments and seeds were not fully recorded, so identical regenerated answers are not guaranteed.

```bash
pip install -r requirements-inference.txt
python scripts/download_models.py --models Qwen3-0.6B Qwen3-8B
python scripts/evaluate.py --model Qwen3-0.6B --benchmark MASCQA --output outputs/qwen06-mascqa --dry-run
python scripts/evaluate.py --model Qwen3-0.6B --benchmark MASCQA --output outputs/qwen06-mascqa --seed 42
python scripts/evaluate.py --model Qwen3-0.6B --benchmark ChemBench4K --output outputs/qwen06-4k --seed 42
```

Run ChemBench separately for each of its nine subjects:

```bash
for subject in analytical_chemistry chemical_preference general_chemistry inorganic_chemistry materials_science organic_chemistry physical_chemistry technical_chemistry toxicity_and_safety; do
  python scripts/evaluate.py --model Qwen3-0.6B --benchmark ChemBench --subject "$subject" --output "outputs/qwen06-chembench-$subject" --seed 42
done
```

For another model, download it with `download_models.py --models MODEL Qwen3-8B` and change `--model`. ChemLLM requires custom code: review the pinned source before opting in with `--allow-remote-code`. Use `--model-path` to select an existing model directory.

`--limit 2` is for smoke checks, not full evaluation. SDPA is the default attention implementation. For `--attention flash_attention_2`, install FlashAttention compatible with your CUDA/PyTorch ABI. Historical prompts and model-specific generation settings are preserved; seed 42 is an explicit setting for new runs, not a claim about the original seed.

The original ChemLLM script skipped zero-based index 3814 in ChemBench4K, leaving 4,008 records. The portable script preserves this behavior by default. `--include-historically-skipped` enables full coverage for a new experiment but changes the historical protocol.

New runs go into `outputs/`. Existing runs cannot be overwritten, and new predictions neither replace `results/raw/` nor enter the fixed historical tables automatically.

## Repository Layout

| Path | Contents |
|---|---|
| `results/RESULTS.md` | Six models across three benchmarks, with both denominator conventions |
| `results/raw/` | 66 raw prediction and judgment CSV files |
| `results/overall.csv`, `subjects.csv`, `files.csv` | Overall, per-subject, and per-file statistics |
| `results/summary.json`, `overall.tex` | Machine-readable results and a LaTeX table |
| `scripts/` | Download, preparation, inference, aggregation, and verification tools |
| `metadata/` | Revisions, checksums, data ordering, and configuration snapshots |
| `legacy/` | Three historical evaluation scripts and three preprocessing scripts, with translated comments and console messages; historical paths retained for reference |
| `docs/VALIDATION.md` | Completed checks and reproduction limits |
| `docs/TRANSLATION.md` | English-language scope and preservation of original evidence |

## Distribution Notes

No blanket license has been assigned to this archive. Code, model, dataset, and model-card permissions must be checked separately. The MASCQA distribution used here does not declare a license in its dataset card, so complete question text is not bundled. Raw model outputs may still repeat parts of questions; review relevant permissions before public redistribution.

Access tokens, weights, environment directories, and unrelated project files are excluded. Only this repository directory should be uploaded, not its parent project.

Repository documentation, code comments, and console messages are in English. Raw predictions, judgments, reference answers, and configuration values retain their original content to preserve reproducibility; see [translation notes](docs/TRANSLATION.md).
