# Results Recomputed from Raw CSV Files

The main table uses the historical yes/no parser with all recorded samples in the denominator. Ambiguous judgments are not counted as correct.
Scores use Qwen3-8B as an LLM judge; they are not official benchmark metrics or strict answer-matching scores.

| Model | ChemBench | MASCQA | ChemBench4K |
|---|---:|---:|---:|
| Qwen3-0.6B | 34.67% (966/2786) | 18.92% (123/650) | 25.14% (1008/4009) |
| Qwen3-1.7B | 44.15% (1230/2786) | 37.85% (246/650) | 29.93% (1200/4009) |
| Qwen3-4B | 53.88% (1501/2786) | 59.54% (387/650) | 46.30% (1856/4009) |
| Qwen3-8B | 57.50% (1602/2786) | 68.46% (445/650) | 51.66% (2071/4009) |
| ChemDFM-v1.0-13B | 47.31% (1318/2786) | 52.92% (344/650) | 38.41% (1540/4009) |
| ChemLLM-7B-Chat | 53.98% (1504/2786) | 36.77% (239/650) | 30.99% (1242/4008) |

## Historical Metric: Valid Judgments Only

Provided for historical comparison; do not mix this denominator with the main table. All values are recomputed from the included CSV files.

| Model | ChemBench | MASCQA | ChemBench4K |
|---|---:|---:|---:|
| Qwen3-0.6B | 34.67% (966/2786) | 18.95% (123/649) | 25.14% (1008/4009) |
| Qwen3-1.7B | 44.18% (1230/2784) | 37.85% (246/650) | 29.95% (1200/4007) |
| Qwen3-4B | 53.88% (1501/2786) | 59.72% (387/648) | 46.31% (1856/4008) |
| Qwen3-8B | 57.52% (1602/2785) | 68.89% (445/646) | 51.71% (2071/4005) |
| ChemDFM-v1.0-13B | 47.51% (1318/2774) | 53.83% (344/639) | 38.41% (1540/4009) |
| ChemLLM-7B-Chat | 54.24% (1504/2773) | 37.70% (239/634) | 30.99% (1242/4008) |

## Metrics and Limitations

- `accuracy_all_pct`: the main-table metric, using all recorded rows; `ambiguous` counts unresolved judgments.
- `accuracy_valid_pct`: the historical-summary metric, excluding unresolved judgments.
- `historical_yes_pct`: the original substring-based `yes` count divided by CSV rows; not strict yes/no parsing.
- ChemLLM has only 4,008 ChemBench4K rows because its script skips index 3814; other models have 4,009. The original console denominator was still 4,009, unlike the CSV-row denominator.
- `subjects.csv` covers all recorded subjects across the three benchmarks; `files.csv` provides per-file statistics.
- Inference has not been rerun. Historical environments and random seeds were not fully recorded, so identical regenerated answers are not guaranteed.
