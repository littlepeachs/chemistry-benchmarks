# 评测协议与统计口径

## 统计

- 六个公开模型、三个 benchmark，共 66 份 CSV、44,669 条记录。
- `accuracy_all_pct`：沿用历史 yes/no 解析器，以全部已记录行数为分母；未明确解析的判词不计正确。
- `accuracy_valid_pct`：同一解析器，仅明确判词作分母，供追溯历史汇总。
- `historical_yes_pct`：原推理脚本的 yes 子串判分 / CSV 行数，不等同于严格 yes/no 或官方答案匹配。
- 全部统计从随附 CSV 生成；`ambiguous.json` 列出未解析判词，未经人工裁决。
- 旧汇总对被测模型同样为 Qwen3-8B 的文件名拆分存在歧义，当前改用固定后缀和显式模型清单；不沿用手填覆盖的汇总。

## 推理协议

所有模型使用 Qwen3-8B 判分，属于 LLM-as-judge。被测 Qwen3-8B 与 judge 同源，结果不能直接等同于官方 benchmark 指标。

Qwen 使用 non-thinking chat template，生成上限 1024 token，其他参数继承固定版本的 generation config。所见配置为 do_sample=true、temperature=0.6、top_p=0.95、top_k=20。

ChemDFM 使用 `User: ...\nAssistant:`，temperature=0.9、top_p=0.9、top_k=20、repetition_penalty=1.05、1024 token。ChemLLM 直接传原问题，temperature=0.9、top_k=1、repetition_penalty=1.5、500 token。

Qwen 原脚本用被测 tokenizer 构造 judge 提示，再用 judge tokenizer 编码；另两个模型使用 judge tokenizer 构造提示。移植代码保留这些差异，未将协议描述为统一提示策略。

## 数据转换与覆盖

ChemBench 旧预处理取每行 `examples[0]`，多正确选项取首个得分 1.0 的项，最多输出 A–H；这不等价于官方多选/数值评分。固定版本下载后已重建出与原处理结果一致的内容哈希。

ChemBench4K 九个文件按历史拼接顺序处理，不依赖 `os.listdir()` 的环境顺序。ChemLLM 原代码跳过索引 3814，因此 4,008 行，而其余模型有 4,009 行。原因没有记录；原控制台分母仍为 4,009，CSV 行数口径不同。删除对应输入位置后，Truth 顺序与现有 CSV 完全一致。

## 复现边界

原始 CSV 未记录问题 ID、运行时模型哈希、种子、GPU 或完整环境。当前行索引由处理后数据与 Truth 顺序核对得到，不是补造的原始元数据。缓存 revision 证明下载来源，不代替运行时权重身份记录。

统计可在离线环境精确重算。移植推理会固定新 seed 并记录环境和配置，但默认 SDPA 与原 FlashAttention 不同，且未重跑 GPU 测试，不承诺逐答案重现。

原测试和预处理代码在 `legacy/`；原始论文、旧图、训练产物和不在本次范围内的模型不纳入仓库。
