import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    entries = (ROOT/'metadata/SHA256SUMS').read_text().splitlines()
    for entry in entries:
        expected, relative = entry.split('  ', 1)
        path = ROOT/relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Archive checksum mismatch: {relative}')
    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory)
        subprocess.run([sys.executable, str(ROOT/'scripts/summarize.py'), '--output', directory], check=True)
        for path in destination.iterdir():
            if path.read_bytes() != (ROOT/'results'/path.name).read_bytes():
                raise ValueError(f'Non-reproducible summary: {path.name}')
    print(f'PASS: {len(entries)} archive checksums and regenerated summaries match')


if __name__ == '__main__':
    main()
