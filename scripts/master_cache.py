#!/usr/bin/env python3
"""Resolve hash-pinned approved masters for OFFLINE technical QA.

Style design must consult VISUAL_STYLE.md, not master SVGs. The verified pack is
a transport/cache for the official auditor's exact-byte integrity checks and
contact sheet, not a source of design inspiration.

Fail-closed rules:
* Original local master with wrong blob SHA cannot be silently replaced.
* If a pack is supplied, ALL contents and the full pinned index must match.
* A missing master or a stale/corrupt cache is a hard audit failure.
* Recovered SVGs are written only under the audit output directory.
"""
import hashlib
import json
import re
from pathlib import Path

PACK_FORMAT = 'cybersecurity-premium-assets/verified-master-pack-v1'


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def resolve_masters(root: Path, output: Path, pinned: dict) -> tuple:
    """Return ([(name, path, origin, blob_sha)], issues).

    Output contains files for every valid original, or recovered exact bytes for
    those missing locally. Never treats unverified bytes as originals.
    """
    root = Path(root).resolve()
    output = Path(output).resolve()
    issues = []
    records = []
    if not pinned or not isinstance(pinned, dict):
        return records, ['Approved master index missing/invalid']
    if any(not re.fullmatch(r'[a-z0-9-]+', str(n)) for n in pinned):
        return records, ['Unsafe master name in index']

    pack_file = root / 'scripts' / 'approved_masters_pack.json'
    pack = None
    if pack_file.exists():
        try:
            payload = json.loads(pack_file.read_text(encoding='utf-8'))
            if payload.get('format') != PACK_FORMAT:
                issues.append('Unknown master pack format')
            pack = payload.get('assets')
            if not isinstance(pack, dict):
                issues.append('Master pack assets must be an object')
                pack = None
            elif set(pack) != set(pinned):
                issues.append('Master pack is stale: asset names differ from pinned index')
            if pack is not None:
                for name in sorted(pinned):
                    svg = pack.get(name)
                    if not isinstance(svg, str):
                        issues.append('Master pack missing or invalid: ' + name)
                    elif git_blob(svg.encode('utf-8')) != pinned[name]:
                        issues.append('Master pack SHA mismatch: ' + name)
        except (UnicodeError, ValueError, TypeError, OSError) as exc:
            issues.append('Unable to read master pack: ' + str(exc))
    if issues:
        return records, issues

    cache = output / 'verified_masters'
    for name, sha_expected in sorted(pinned.items()):
        original = root / 'assets' / (name + '.svg')
        if original.is_file():
            data = original.read_bytes()
            origin = 'original'
            path = original
        elif pack is not None:
            data = pack[name].encode('utf-8')
            origin = 'verified-pack'
            cache.mkdir(parents=True, exist_ok=True)
            path = cache / (name + '.svg')
            path.write_bytes(data)
        else:
            issues.append('Missing approved master without verified pack: ' + name)
            continue

        actual = git_blob(data)
        if actual != sha_expected:
            issues.append('Approved master hash mismatch: ' + name)
            continue
        records.append((name, path, origin, actual))

    if len(records) != len(pinned):
        issues.append('Master coverage incomplete: ' + str(len(records)) + '/' + str(len(pinned)))
    return records, issues
