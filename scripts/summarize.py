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
    lines = ['# Results Recomputed from Raw CSV Files', '',
             'The main table uses the historical yes/no parser with all recorded samples in the denominator. Ambiguous judgments are not counted as correct.',
             'Scores use Qwen3-8B as an LLM judge; they are not official benchmark metrics or strict answer-matching scores.', '',
             '| Model | ChemBench | MASCQA | ChemBench4K |', '|---|---:|---:|---:|']
    latex = ['\\begin{tabular}{lrrr}', '\\hline', 'Model & ChemBench & MASCQA & ChemBench4K \\\\', '\\hline']
    for model in models:
        selected = [lookup[benchmark, model] for benchmark in benchmarks]
        cells = [f"{row['accuracy_all_pct']:.2f}% ({row['correct']}/{row['total']})" for row in selected]
        lines.append('| '+model+' | '+' | '.join(cells)+' |')
        latex.append(model+' & '+' & '.join(f"{row['accuracy_all_pct']:.2f}" for row in selected)+r' \\')
    latex += ['\\hline', '\\end{tabular}']
    lines += ['', '## Historical Metric: Valid Judgments Only', '',
              'Provided for historical comparison; do not mix this denominator with the main table. All values are recomputed from the included CSV files.', '',
              '| Model | ChemBench | MASCQA | ChemBench4K |', '|---|---:|---:|---:|']
    for model in models:
        selected = [lookup[benchmark, model] for benchmark in benchmarks]
        cells = [f"{row['accuracy_valid_pct']:.2f}% ({row['correct']}/{row['valid']})" for row in selected]
        lines.append('| '+model+' | '+' | '.join(cells)+' |')
    lines += ['', '## Metrics and Limitations', '',
              '- `accuracy_all_pct`: the main-table metric, using all recorded rows; `ambiguous` counts unresolved judgments.',
              '- `accuracy_valid_pct`: the historical-summary metric, excluding unresolved judgments.',
              '- `historical_yes_pct`: the original substring-based `yes` count divided by CSV rows; not strict yes/no parsing.',
              '- ChemLLM has only 4,008 ChemBench4K rows because its script skips index 3814; other models have 4,009. The original console denominator was still 4,009, unlike the CSV-row denominator.',
              '- `subjects.csv` covers all recorded subjects across the three benchmarks; `files.csv` provides per-file statistics.',
              '- Inference has not been rerun. Historical environments and random seeds were not fully recorded, so identical regenerated answers are not guaranteed.']
    (args.output/'RESULTS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (args.output/'overall.tex').write_text('\n'.join(latex)+'\n')
    print('\n'.join(lines[:15]))
    print(f'Verified {len(manifest)} CSVs; wrote results to {args.output}')


if __name__ == '__main__':
    main()
