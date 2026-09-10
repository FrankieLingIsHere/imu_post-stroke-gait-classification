"""Screen a provider JSON dictionary. Exit 0=ready, 2=hold, 1=invalid JSON/input."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.recruitment_gate import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('schema', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Preserve the existing decision; select a new output path')
    raw = args.schema.read_bytes()
    record = json.loads(raw)
    if not isinstance(record, dict):
        raise ValueError('Provider schema must be a JSON object')
    result = evaluate(record)
    result['schema_sha256'] = hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0 if not result['blockers'] else 2


if __name__ == '__main__':
    sys.exit(main())
