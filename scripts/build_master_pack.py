#!/usr/bin/env python3
"""Build or check the exact-byte offline QA pack from approved original SVGs.

Run on an authorized full repository checkout when a new approved master is
published. This command never approves or publishes any new asset.
"""
import argparse
import json
import sys
from pathlib import Path
from master_cache import PACK_FORMAT, git_blob


def expected_pack(root):
    index = json.loads((root / 'scripts' / 'approved_masters.json').read_text(encoding='utf-8'))
    assets = {}
    for name, expected_hash in sorted(index.items()):
        path = root / 'assets' / (name + '.svg')
        if not path.is_file():
            raise ValueError('Missing original asset: ' + str(path))
        raw = path.read_bytes()
        got = git_blob(raw)
        if got != expected_hash:
            raise ValueError('Approved original hash mismatch: ' + name + ' (' + got + ')')
        assets[name] = raw.decode('utf-8')
    return {
        'format': PACK_FORMAT,
        'source': 'Exact immutable approved SVGs from GitHub; used only for reproducible technical audit, not visual design reference',
        'assets': assets
    }


def main():
    cli = argparse.ArgumentParser()
    mode = cli.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true', help='verify existing pack is exact and complete')
    mode.add_argument('--write', action='store_true', help='regenerate pack from SHA-verified originals')
    cli.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    args = cli.parse_args()
    root = args.repo_root.resolve()
    destination = root / 'scripts' / 'approved_masters_pack.json'
    try:
        expected = expected_pack(root)
        if args.check:
            if not destination.exists():
                raise ValueError('Master pack missing')
            actual = json.loads(destination.read_text(encoding='utf-8'))
            if actual != expected:
                raise ValueError('Master pack is stale or differs from approved originals')
            print('MASTER PACK PASS: ' + str(len(expected['assets'])) + ' exact approved SVGs')
            return 0
        destination.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('MASTER PACK WRITTEN: ' + str(len(expected['assets'])) + ' exact approved SVGs')
        return 0
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print('MASTER PACK FAIL: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
