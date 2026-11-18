#!/usr/bin/env python3
"""Rebuild/check the single-file, SHA-pinned offline audit runtime bundle.

Run after changing an official audit script, master index, or master pack.
This operation never publishes SVG candidates or bypasses approval.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from master_cache import PACK_FORMAT, git_blob

FORMAT = 'cybersecurity-premium-assets/audit-runtime-bundle-v1'
REPO = 'fernandoconislla/cybersecurity-premium-assets'
FILES = (
    'scripts/approved_masters.json',
    'scripts/approved_masters_pack.json',
    'scripts/master_cache.py',
    'scripts/audit_workflow.py',
    'scripts/approval_gate.py',
    'scripts/validate_asset.py',
    'skills/cybersecurity-premium-assets/VISUAL_STYLE.md',
)


def expected_bundle(root):
    file_data = {}
    for path in FILES:
        b = (root / path).read_bytes()
        file_data[path] = {'content': b.decode('utf-8'), 'git_blob': git_blob(b)}

    pinned = json.loads(file_data['scripts/approved_masters.json']['content'])
    pack = json.loads(file_data['scripts/approved_masters_pack.json']['content'])
    if pack.get('format') != PACK_FORMAT or set(pack.get('assets', {})) != set(pinned):
        raise ValueError('Master pack does not match master index')
    for name, pinned_sha in pinned.items():
        svg = pack['assets'][name]
        if git_blob(svg.encode('utf-8')) != pinned_sha:
            raise ValueError('Master pack SHA mismatch: ' + name)

    audited = file_data['scripts/audit_workflow.py']['content']
    marker = re.search(r"VALIDATOR_BLOB_SHA\s*=\s*'([a-f0-9]{40})'", audited)
    if not marker or marker.group(1) != file_data['scripts/validate_asset.py']['git_blob']:
        raise ValueError('Official validator pin mismatch')

    return {
        'format': FORMAT,
        'repo': REPO,
        'source': 'Pinned exact official audit scripts, master index and verified master pack. Does not authorize publication.',
        'files': file_data,
    }


def main(argv=None):
    cli = argparse.ArgumentParser()
    choice = cli.add_mutually_exclusive_group(required=True)
    choice.add_argument('--check', action='store_true')
    choice.add_argument('--write', action='store_true')
    cli.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    args = cli.parse_args(argv)
    root = args.repo_root.resolve()
    dest = root / 'scripts/audit_runtime_bundle.json'
    try:
        expected = expected_bundle(root)
        if args.check:
            if not dest.is_file() or json.loads(dest.read_text(encoding='utf-8')) != expected:
                raise ValueError('Runtime bundle is missing or stale; run --write')
            print('AUDIT RUNTIME BUNDLE PASS: 7 official files and ' +
                  str(len(json.loads(expected['files']['scripts/approved_masters.json']['content']))) +
                  ' SHA-pinned masters')
        else:
            dest.write_text(json.dumps(expected, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            print('AUDIT RUNTIME BUNDLE WRITTEN')
        return 0
    except (ValueError, TypeError, OSError, UnicodeError) as exc:
        print('AUDIT RUNTIME BUNDLE FAIL: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
