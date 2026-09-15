# Chemistry Benchmarks

六个公开模型在 ChemBench、MASCQA 和 ChemBench4K 上的历史评测记录、统计脚本和复现代码。

- **模型**：Qwen3-0.6B、Qwen3-1.7B、Qwen3-4B、Qwen3-8B、ChemDFM-v1.0-13B、ChemLLM-7B-Chat。
- **规模**：66 份原始 CSV，44,669 条逐答案评测记录，18 个主表项，192 个子领域统计项。
- **评分**：Qwen3-8B LLM-as-judge，不是官方 benchmark 指标。主表计入全部记录，另提供历史有效判词分母口径。
- **内容**：不包含模型权重、完整数据集、训练产物或论文草稿。

## 结果与离线复现

完整表格见 [results/RESULTS.md](results/RESULTS.md)，统计口径见 [docs/AUDIT.md](docs/AUDIT.md)。所有分数由随附原始 CSV 重算，不使用手填结果。

在仓库根目录执行（Python 3.9+，无需 GPU、联网或第三方依赖）：

```bash
python scripts/summarize.py
python scripts/verify.py
```

第一条校验原始 CSV 哈希、行数、Truth 顺序和子领域，生成总表、子领域表、逐文件统计、JSON、Markdown、LaTeX 表格及未解析判词清单。第二条核验归档文件哈希，并在临时目录重算全部统计进行逐字节比较。

## 模型下载

| 模型 | 下载链接 |
|---|---|
| Qwen3-0.6B | https://huggingface.co/Qwen/Qwen3-0.6B |
| Qwen3-1.7B | https://huggingface.co/Qwen/Qwen3-1.7B |
| Qwen3-4B | https://huggingface.co/Qwen/Qwen3-4B |
| Qwen3-8B | https://huggingface.co/Qwen/Qwen3-8B |
| ChemDFM-v1.0-13B | https://huggingface.co/OpenDFM/ChemDFM-v1.0-13B |
| ChemLLM-7B-Chat | https://huggingface.co/AI4Chem/ChemLLM-7B-Chat |

ChemDFM 和 ChemLLM 是独立化学专用模型，非 Qwen 派生模型。本地模型配置分别记录 LlamaForCausalLM 和 InternLM2ForCausalLM。Qwen3-8B 同时作为所有实验的 judge。

`metadata/models.json` 固定本地下载缓存中的历史 revision；`metadata/source_verification.json` 保存 Hugging Face API 核验结果。下载脚本不会自动升级到当前 main 或其他型号。

## 数据来源与预处理

| Benchmark | 获取来源 | 实际使用部分 |
|---|---|---|
| ChemBench | https://huggingface.co/datasets/jablonkagroup/ChemBench | 九领域 train parquet，共 2,786 条，按历史实验用于评测 |
| MASCQA | https://huggingface.co/datasets/heegyu/mascqa | test parquet，650 条；本工程实际使用的分发版本 |
| ChemBench4K | https://huggingface.co/datasets/AI4Chem/ChemBench4K | test 九个 JSON，共 4,009 条，未加入 dev |

ChemBench 与 ChemBench4K 是不同数据集。固定版本、源文件哈希、拼接顺序和预处理内容哈希见 `metadata/datasets.json`；数据卡见 `metadata/dataset_cards/`。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-data.txt
python scripts/prepare_data.py
```

脚本通过固定 revision 的 HTTPS URL 下载，校验 SHA-256 并重建 `data/`。已有下载文件时可使用 `--source-root /path/to/datasets`。重建结果须与历史处理后数据的规范化内容哈希一致。

## 重新运行推理

需要支持 BF16 的 GPU 和足够显存，同时加载被测模型与 8B judge。依赖配置是移植运行环境，尚未进行完整 GPU 端到端验证；历史实验环境和种子并未完整保存，因此不承诺逐答案相同。

```bash
pip install -r requirements-inference.txt
python scripts/download_models.py --models Qwen3-0.6B Qwen3-8B
python scripts/evaluate.py --model Qwen3-0.6B --benchmark MASCQA --output outputs/qwen06-mascqa --dry-run
python scripts/evaluate.py --model Qwen3-0.6B --benchmark MASCQA --output outputs/qwen06-mascqa --seed 42
python scripts/evaluate.py --model Qwen3-0.6B --benchmark ChemBench4K --output outputs/qwen06-4k --seed 42
```

ChemBench 按九个领域执行：

```bash
for subject in analytical_chemistry chemical_preference general_chemistry inorganic_chemistry materials_science organic_chemistry physical_chemistry technical_chemistry toxicity_and_safety; do
  python scripts/evaluate.py --model Qwen3-0.6B --benchmark ChemBench --subject "$subject" --output "outputs/qwen06-chembench-$subject" --seed 42
done
```

其他模型先用 `download_models.py --models MODEL Qwen3-8B` 下载，再替换 `--model`。ChemLLM 使用自定义代码，审查固定版本源码后须显式添加 `--allow-remote-code`。`--model-path` 可指定已下载的模型目录。

`--limit 2` 用于烟雾检查，不代表完整测试。默认 SDPA；若设置 `--attention flash_attention_2`，需另安装匹配 CUDA/PyTorch ABI 的 FlashAttention。原提示和模型特定生成设置保留，seed=42 是新运行的明确设置，不是原实验种子的声明。

ChemLLM 原代码跳过 ChemBench4K 零基索引 3814，主表只有 4,008 行；移植代码默认保留这一行为。`--include-historically-skipped` 可用于完整覆盖的新实验，但会改变历史协议。

新推理写入 `outputs/`，拒绝覆盖已有运行，不会改动 `results/raw/`，也不会自动混入固定历史主表。

## 目录

| 路径 | 内容 |
|---|---|
| `results/RESULTS.md` | 六模型三 benchmark 的两种统计口径 |
| `results/raw/` | 66 份原始答案/判词 CSV |
| `results/overall.csv`、`subjects.csv`、`files.csv` | 总表、子领域与逐文件统计 |
| `results/summary.json`、`overall.tex` | 机器可读统计与 LaTeX 表格 |
| `scripts/` | 下载、预处理、推理、重算与核验 |
| `metadata/` | 固定版本、哈希、数据顺序及配置快照 |
| `legacy/` | 三个原测试脚本与三个原预处理脚本，保留历史路径仅供审计 |
| `docs/VALIDATION.md` | 已执行验证与复现边界 |

## 发布说明

未添加统一 LICENSE：代码、模型、数据及数据卡的授权须分别确认。所用 MASCQA 数据卡未声明 license，因此不打包完整问题文本；模型原始输出仍可能复述问题，公开分发前请审查相关许可。

不包含访问令牌、权重、环境目录或无关工程文件。仅提交本目录，不要将上级工程整体上传。
