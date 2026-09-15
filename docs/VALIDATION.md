# 验证记录

## 数据与统计

- 六模型 66 份原始 CSV，44,669 行，18 个主表项、192 个子领域项。
- 每份 CSV 的 SHA-256、行数、Truth 顺序和子领域与本地来源核对。
- 三个数据集的 19 个固定版本源文件已在线下载，11 个处理后 JSON 的哈希与原输入完全一致；数据转换未因本次移除模型而改变。
- 六个模型及三个数据集的固定 revision 已通过 Hugging Face API 核实，见 `metadata/source_verification.json`。
- 五个 scripts Python 文件语法检查；六模型 × 11 个数据分片，共 66 个推理 dry-run 组合。
- `scripts/verify.py` 校验归档哈希并逐字节比较重新生成的统计；独立目录复制后再次验证。
- 发布文件执行常见访问令牌模式扫描，不打包权重或完整数据集。

数据重建使用 Python 3.12、pandas 2.3.0、pyarrow 24.0.0。离线统计仅依赖标准库；依赖列表不是完整历史环境锁。

## 未执行

未重新运行 GPU 生成或 judge，未复现训练，未人工重判答案，未按各 benchmark 官方协议重新打分。新 seed/attention 设置不代表原实验参数。

## 复核

```bash
python scripts/summarize.py
python scripts/verify.py
python scripts/prepare_data.py --output /tmp/chemistry-data-check
python scripts/evaluate.py --model Qwen3-0.6B --benchmark MASCQA --data-root /tmp/chemistry-data-check --output /tmp/chemistry-dry-run --dry-run
```

若主动修改归档文件，SHA256SUMS 会按设计报告变化；检查后再更新清单，不要以更新哈希掩盖未经核对的原始 CSV 改动。
