import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_critic(text):
    value = text.lower().strip()
    if value in ('yes', 'yes.', 'correct', 'true'):
        return True
    if value in ('no', 'no.', 'incorrect', 'false', 'wrong'):
        return False
    if 'yes' in value and 'no' not in value:
        return True
    if 'no' in value and 'yes' not in value:
        return False
    return None


def metrics(rows):
    parsed = [parse_critic(row['Critic']) for row in rows]
    total = len(rows)
    correct = sum(value is True for value in parsed)
    valid = sum(value is not None for value in parsed)
    historical_yes = sum('yes' in row['Critic'].lower().strip() for row in rows)
    return dict(total=total, correct=correct, valid=valid, ambiguous=total-valid,
                accuracy_all_pct=100*correct/total if total else None,
                accuracy_valid_pct=100*correct/valid if valid else None,
                historical_yes=historical_yes,
                historical_yes_pct=100*historical_yes/total if total else None)


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description='Recompute all tables without GPU or third-party packages.')
    parser.add_argument('--output', type=Path, default=ROOT/'results')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'metadata/result_files.json').read_text())
    row_index = json.loads((ROOT/'metadata/row_index.json').read_text())
    main_groups = defaultdict(list)
    subject_groups = defaultdict(list)
    files = []
    ambiguous = []
    for entry in manifest:
        path = ROOT/entry['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'Checksum mismatch: {path}')
        with path.open(newline='', encoding='utf-8') as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames not in (['Truth', 'Model', 'Critic'], ['Truth', 'Model', 'Critic', 'Subject']):
                raise ValueError(f'Unexpected CSV schema: {path}')
            rows = list(reader)
        key = entry['benchmark']
        if key == 'ChemBench':
            key += '/'+path.stem.split('_Qwen3-8B_', 1)[1]
        expected = row_index[key]
        if entry['model'] == 'ChemLLM-7B-Chat' and entry['benchmark'] == 'ChemBench4K':
            expected = expected[:3814]+expected[3815:]
        if len(rows) != len(expected):
            raise ValueError(f'Dataset coverage mismatch: {path}')
        for row, reference in zip(rows, expected):
            if row['Truth'] != reference['truth'] or ('Subject' in row and row['Subject'] != reference['subject']):
                raise ValueError(f'Truth/subject alignment mismatch: {path}')
            row['Subject'] = reference['subject']
        if len(rows) != entry['rows']:
            raise ValueError(f'Row count mismatch: {path}')
        info = dict(benchmark=entry['benchmark'], model=entry['model'], run=entry['run'])
        files.append(dict(**info, path=entry['path'], **metrics(rows)))
        if entry['run'] != 'main':
            raise ValueError('Only main runs belong in this archive')
        main_groups[entry['benchmark'], entry['model']].extend(rows)
        for row in rows:
            subject_groups[entry['benchmark'], entry['model'], row['Subject']].append(row)
        for index, row in enumerate(rows):
            if parse_critic(row['Critic']) is None:
                ambiguous.append(dict(path=entry['path'], row_index=index, critic=row['Critic']))
    overall = [dict(benchmark=key[0], model=key[1], **metrics(rows))
               for key, rows in sorted(main_groups.items())]
    detailed = [dict(benchmark=key[0], model=key[1], subject=key[2], **metrics(rows))
                for key, rows in sorted(subject_groups.items())]
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in [('overall', overall), ('subjects', detailed), ('files', files)]:
        write_csv(args.output/f'{name}.csv', rows)
    (args.output/'ambiguous.json').write_text(json.dumps(ambiguous, indent=2, ensure_ascii=False)+'\n')
    payload = dict(overall=overall, subjects=detailed)
    (args.output/'summary.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False)+'\n')
    benchmarks = ['ChemBench', 'MASCQA', 'ChemBench4K']
    models = json.loads((ROOT/'metadata/models.json').read_text())
    lookup = {(row['benchmark'], row['model']): row for row in overall}
    lines = ['# 从原始 CSV 重算的结果', '',
             '主表：沿用旧汇总的 yes/no 解析器，但所有已记录样本进入分母；无法明确解析的判词不计正确。',
             '这是 Qwen3-8B LLM-as-judge 判分，不是官方 benchmark 指标或严格答案匹配。', '',
             '| 模型 | ChemBench | MASCQA | ChemBench4K |', '|---|---:|---:|---:|']
    latex = ['\\begin{tabular}{lrrr}', '\\hline', 'Model & ChemBench & MASCQA & ChemBench4K \\\\', '\\hline']
    for model in models:
        selected = [lookup[benchmark, model] for benchmark in benchmarks]
        cells = [f"{row['accuracy_all_pct']:.2f}% ({row['correct']}/{row['total']})" for row in selected]
        lines.append('| '+model+' | '+' | '.join(cells)+' |')
        latex.append(model+' & '+' & '.join(f"{row['accuracy_all_pct']:.2f}" for row in selected)+r' \\')
    latex += ['\\hline', '\\end{tabular}']
    lines += ['', '## 旧汇总口径：仅有效判词作分母', '',
              '用于追溯历史汇总，不能和主表混用。全部数值均由随附 CSV 重算。', '',
              '| 模型 | ChemBench | MASCQA | ChemBench4K |', '|---|---:|---:|---:|']
    for model in models:
        selected = [lookup[benchmark, model] for benchmark in benchmarks]
        cells = [f"{row['accuracy_valid_pct']:.2f}% ({row['correct']}/{row['valid']})" for row in selected]
        lines.append('| '+model+' | '+' | '.join(cells)+' |')
    lines += ['', '## 指标与限制', '',
              '- `accuracy_all_pct`：主表，全记录分母；`ambiguous` 显示未明确解析判词数。',
              '- `accuracy_valid_pct`：旧汇总口径，排除未明确解析判词，用于核对论文。',
              '- `historical_yes_pct`：原推理脚本的子串 `yes` 判分 / CSV 行数；不是严格 yes/no。',
              '- ChemLLM 的 ChemBench4K 仅 4,008 行：代码跳过索引 3814；其他模型 4,009 行。原控制台分母仍是 4,009，与此 CSV 行数口径不同。',
              '- `subjects.csv` 包含三个 benchmark 的所有已记录子领域；`files.csv` 可逐文件核对。',
              '- 未进行重新推理；原始推理无完整运行环境/随机种子，不能承诺逐答案重现。']
    (args.output/'RESULTS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (args.output/'overall.tex').write_text('\n'.join(latex)+'\n')
    print('\n'.join(lines[:15]))
    print(f'Verified {len(manifest)} CSVs; wrote results to {args.output}')


if __name__ == '__main__':
    main()
