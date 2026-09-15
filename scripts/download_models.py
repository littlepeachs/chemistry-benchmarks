import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    models = json.loads((ROOT/'metadata/models.json').read_text())
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', nargs='+', choices=[name for name, entry in models.items() if entry['repo_id']],
                        default=['Qwen3-0.6B', 'Qwen3-8B'])
    parser.add_argument('--output', type=Path, default=ROOT/'models')
    args = parser.parse_args()
    from huggingface_hub import snapshot_download
    for name in args.models:
        entry = models[name]
        snapshot_download(repo_id=entry['repo_id'], revision=entry['revision'], local_dir=args.output/name)


if __name__ == '__main__':
    main()
