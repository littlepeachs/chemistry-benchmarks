import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def normalized_hash(rows):
    content = json.dumps(rows, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(content.encode()).hexdigest()


def download_sources(dataset):
    directory = ROOT/'.cache'/dataset['local_name']/dataset['revision']
    for source in dataset['sources']:
        destination = directory/source['path']
        if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() == source['sha256']:
            continue
        url = f"https://huggingface.co/datasets/{dataset['repo_id']}/resolve/{dataset['revision']}/{source['path']}"
        with urllib.request.urlopen(url, timeout=120) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != source['sha256']:
            raise ValueError(f'Download hash mismatch: {url}')
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    return directory


def convert(benchmark, sources, directory):
    import pandas as pd

    result = []
    for source in sources:
        path = directory/source['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError(f'Upstream content differs: {path}')
        if benchmark == 'ChemBench4K':
            for item in json.loads(path.read_text()):
                options = [f'({option}) {item[option]}' for option in 'ABCD' if option in item]
                result.append(dict(question=item['question']+'\n'+'\n'.join(options),
                                   answer=item['answer'], subject=path.stem))
        elif benchmark == 'MASCQA':
            for item in pd.read_parquet(path).to_dict('records'):
                result.append(dict(question=item['questions'], answer=item['label'],
                                   subject=item['subject'], qstr=item['qstr'],
                                   qids=item['qids'], num_words=item['num_words']))
        else:
            for item in pd.read_parquet(path).to_dict('records'):
                example = item['examples'][0]
                question = example['input']
                answer = example['target']
                if example['target_scores']:
                    scores = json.loads(example['target_scores'])
                    correct = next((option for option, score in scores.items() if score == 1.0), None)
                    labels = 'ABCDEFGH'
                    if correct is None or list(scores).index(correct) >= len(labels):
                        raise ValueError('Unsupported answer: refuse silent historical label carry-over')
                    question += '\n'
                    for index, option in enumerate(scores):
                        if index < len(labels):
                            question += f'({labels[index]}) {option}\n'
                    answer = labels[list(scores).index(correct)]
                result.append(dict(question=question.strip(), answer=answer,
                                   subject=path.parent.name, num_words=len(question.split())))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, help='Existing downloaded datasets root; disables downloading')
    parser.add_argument('--output', type=Path, default=ROOT/'data')
    args = parser.parse_args()
    for dataset in json.loads((ROOT/'metadata/datasets.json').read_text()):
        if args.source_root:
            source_dir = args.source_root/dataset['local_name']
        else:
            source_dir = download_sources(dataset)
        for output in dataset['outputs']:
            sources = [next(item for item in dataset['sources'] if item['path'] == name)
                       for name in output['source_order']]
            rows = convert(dataset['benchmark'], sources, source_dir)
            if len(rows) != output['rows'] or normalized_hash(rows) != output['normalized_sha256']:
                raise ValueError(f"Prepared data mismatch: {output['path']}")
            destination = args.output/output['path']
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(rows, indent=2, ensure_ascii=False)+'\n')
            print(f'Verified {destination}: {len(rows)} rows')


if __name__ == '__main__':
    main()
