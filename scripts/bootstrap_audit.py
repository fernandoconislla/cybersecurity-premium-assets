#!/usr/bin/env python3
"""Fail-closed bootstrap for official cybersecurity premium SVG audits.

Usage:
    python scripts/bootstrap_audit.py --repo-root . --manifest work/manifest.json --audit-only
    # inspect the renders, complete truthful visual/manual evidence, re-audit if manifest changed
    python scripts/bootstrap_audit.py --repo-root . --manifest work/manifest.json --gate-only

Transport order:
  1) explicit --bundle PATH (a locally transferred audit_runtime_bundle.json);
  2) scripts/audit_runtime_bundle.json from an existing checkout;
  3) HTTPS download from the project's pinned GitHub repository (unless --offline).

In connector-only environments with no outbound HTTPS, retrieve ONE bundle with
the connected GitHub app and materialize it as a local file, then pass --bundle.
There is no implied filesystem bridge between a GitHub connector and Python.
Never use placeholder scripts, skip failed audits, or fabricate human evidence.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO = 'fernandoconislla/cybersecurity-premium-assets'
FORMAT = 'cybersecurity-premium-assets/audit-runtime-bundle-v1'
PACK_FORMAT = 'cybersecurity-premium-assets/verified-master-pack-v1'
REQUIRED = (
    'scripts/approved_masters.json',
    'scripts/approved_masters_pack.json',
    'scripts/master_cache.py',
    'scripts/audit_workflow.py',
    'scripts/approval_gate.py',
    'scripts/validate_asset.py',
    'skills/cybersecurity-premium-assets/VISUAL_STYLE.md',
)
URL = 'https://raw.githubusercontent.com/' + REPO + '/main/scripts/audit_runtime_bundle.json'


class BootstrapError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def within(root, path):
    dest = (root / path).resolve()
    if not dest.is_relative_to(root):
        raise BootstrapError('UNSAFE_PATH', str(path))
    return dest


def load_bundle(root, explicit=None, offline=False):
    sources = [Path(explicit)] if explicit else [root / 'scripts/audit_runtime_bundle.json']
    for source in sources:
        if source.is_file():
            try:
                return json.loads(source.read_text(encoding='utf-8')), str(source)
            except (UnicodeError, ValueError, OSError) as exc:
                raise BootstrapError('INVALID_BUNDLE', str(exc)) from exc
    if offline:
        raise BootstrapError('BUNDLE_NOT_AVAILABLE',
                             'Bundle absent locally and --offline enabled. '
                             'Transfer scripts/audit_runtime_bundle.json with the connected GitHub app '
                             'and pass --bundle PATH.')
    try:
        req = Request(URL, headers={'User-Agent': 'cybersecurity-premium-assets-bootstrap/1.0'})
        with urlopen(req, timeout=10) as response:
            payload = response.read(2_000_000)
        return json.loads(payload.decode('utf-8')), URL
    except (OSError, HTTPError, URLError, ValueError, UnicodeError) as exc:
        raise BootstrapError('NETWORK_AND_BUNDLE_UNAVAILABLE',
                             'No local verified bundle and GitHub HTTPS fetch failed: ' + str(exc) +
                             '. Transfer ONE scripts/audit_runtime_bundle.json via the connected '
                             'GitHub app, then re-run with --bundle PATH.') from exc


def verify_bundle(bundle):
    if not isinstance(bundle, dict) or bundle.get('format') != FORMAT or bundle.get('repo') != REPO:
        raise BootstrapError('INVALID_BUNDLE', 'Incorrect bundle format or repository')
    files = bundle.get('files')
    if not isinstance(files, dict) or set(files) != set(REQUIRED):
        raise BootstrapError('INCOMPLETE_BUNDLE', 'Seven required runtime files must appear exactly once')
    data = {}
    for name in REQUIRED:
        obj = files.get(name)
        if not isinstance(obj, dict) or not isinstance(obj.get('content'), str) or not isinstance(obj.get('git_blob'), str):
            raise BootstrapError('INVALID_BUNDLE', 'Malformed file entry: ' + name)
        encoded = obj['content'].encode('utf-8')
        if git_blob(encoded) != obj['git_blob']:
            raise BootstrapError('TAMPERED_BUNDLE', 'Git blob mismatch for ' + name)
        data[name] = encoded
    try:
        pinned = json.loads(data['scripts/approved_masters.json'])
        pack = json.loads(data['scripts/approved_masters_pack.json'])
    except (UnicodeError, ValueError, TypeError) as exc:
        raise BootstrapError('INVALID_BUNDLE', 'Unable to parse pinned masters: ' + str(exc)) from exc
    if not isinstance(pinned, dict) or not pinned or not isinstance(pack, dict):
        raise BootstrapError('INVALID_BUNDLE', 'Invalid master index/pack')
    if pack.get('format') != PACK_FORMAT or not isinstance(pack.get('assets'), dict):
        raise BootstrapError('INVALID_BUNDLE', 'Unsupported master pack format')
    if set(pinned) != set(pack['assets']):
        raise BootstrapError('STALE_MASTER_PACK', 'Master names differ between index and pack')
    for name, blob in pinned.items():
        if not re.fullmatch(r'[a-z0-9-]+', name) or not re.fullmatch(r'[a-f0-9]{40}', blob):
            raise BootstrapError('INVALID_BUNDLE', 'Unsafe master name or SHA')
        svg = pack['assets'][name]
        if not isinstance(svg, str) or git_blob(svg.encode('utf-8')) != blob:
            raise BootstrapError('STALE_MASTER_PACK', 'Master SHA mismatch: ' + name)
    audit_src = data['scripts/audit_workflow.py'].decode('utf-8')
    expected_validator = re.search(r"VALIDATOR_BLOB_SHA\s*=\s*'([a-f0-9]{40})'", audit_src)
    if not expected_validator or expected_validator.group(1) != git_blob(data['scripts/validate_asset.py']):
        raise BootstrapError('AUDITOR_PROVENANCE', 'Validator SHA pin disagrees with audit script')
    return data, len(pinned)


def install(root, verified, repair=False):
    staged, conflicts = [], []
    # Detect every conflict before writing ANY official file (atomic preflight).
    for name, raw in verified.items():
        dest = within(root, name)
        if dest.exists() and (not dest.is_file() or dest.read_bytes() != raw) and not repair:
            conflicts.append(name)
    if conflicts:
        raise BootstrapError('STALE_RUNTIME', 'Existing official files disagree with verified bundle: ' +
                             ', '.join(conflicts) + '. Use --repair only after reviewing the trusted bundle.')
    for name, raw in verified.items():
        dest = within(root, name)
        if dest.is_file() and dest.read_bytes() == raw:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix='.bootstrap-', dir=str(dest.parent))
        try:
            with os.fdopen(fd, 'wb') as out:
                out.write(raw)
            os.replace(tmp, dest)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        if dest.read_bytes() != raw:
            raise BootstrapError('WRITE_MISMATCH', 'Written file bytes differ: ' + name)
        staged.append(name)
    return staged


def check_dependencies():
    missing = [module for module in ('cairosvg', 'PIL') if importlib.util.find_spec(module) is None]
    if missing:
        raise BootstrapError('MISSING_DEPENDENCIES',
                             'Python dependencies missing: ' + ', '.join(missing) +
                             '. Install the repository requirements.txt in this environment.')
    return True


def check_candidate(root, manifest_path):
    manifest_file = within(root, manifest_path)
    if not manifest_file.is_file():
        raise BootstrapError('MANIFEST_MISSING', str(manifest_file))
    try:
        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
        candidate = within(root, manifest['candidate'])
        output = within(root, manifest['output_dir'])
    except (ValueError, KeyError, TypeError) as exc:
        raise BootstrapError('INVALID_MANIFEST', str(exc)) from exc
    if not candidate.is_file():
        raise BootstrapError('CANDIDATE_MISSING', str(candidate))
    actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if actual != manifest.get('candidate_sha256'):
        raise BootstrapError('CANDIDATE_SHA_MISMATCH', 'Expected ' +
                             str(manifest.get('candidate_sha256')) + '; got ' + actual)
    if manifest.get('mode') == 'revision':
        if not manifest.get('previous_candidate') or not manifest.get('previous_sha256'):
            raise BootstrapError('REVISION_SOURCE_MISSING', 'Exact previous candidate and hash required')
        previous = within(root, manifest['previous_candidate'])
        if not previous.is_file() or hashlib.sha256(previous.read_bytes()).hexdigest() != manifest['previous_sha256']:
            raise BootstrapError('REVISION_SHA_MISMATCH', 'Previous SVG missing or altered')
    return manifest_file, output, actual


def run_official(root, manifest_file, output, phase='full'):
    commands = [
        [sys.executable, str(root / 'scripts/validate_asset.py'),
         str(within(root, json.loads(manifest_file.read_text(encoding='utf-8'))['candidate']))],
        [sys.executable, str(root / 'scripts/audit_workflow.py'), '--repo-root',
         str(root), '--manifest', str(manifest_file)],
        [sys.executable, str(root / 'scripts/approval_gate.py'), '--repo-root',
         str(root), '--manifest', str(manifest_file),
         '--report', str(output / 'audit-report.json')],
    ]
    names = ['validate_asset.py', 'audit_workflow.py', 'approval_gate.py']
    if phase == 'audit':
        names, commands = names[:2], commands[:2]
    elif phase == 'gate':
        names, commands = names[2:], commands[2:]
    elif phase != 'full':
        raise BootstrapError('INVALID_PHASE', 'Unknown phase ' + phase)
    for name, cmd in zip(names, commands):
        proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
        print('STEP ' + name + ': ' + ('PASS' if proc.returncode == 0 else 'FAIL'))
        if proc.stdout.strip():
            print(proc.stdout.strip())
        if proc.stderr.strip():
            print(proc.stderr.strip(), file=sys.stderr)
        if proc.returncode:
            raise BootstrapError('OFFICIAL_STEP_FAILED',
                                 name + ' exited ' + str(proc.returncode) + '. No approval is authorized.')
    if phase == 'audit':
        print('AUDIT COMPLETE: inspect authentic 1024/128/64 renders and family comparison;')
        print('record truthful manual_evidence, rerun audit if manifest changes, THEN run --gate-only.')
        return None
    authorization = output / 'approval-authorization.json'
    if not authorization.is_file():
        raise BootstrapError('APPROVAL_RECEIPT_MISSING', 'Official approval receipt not created')
    receipt = json.loads(authorization.read_text(encoding='utf-8'))
    if receipt.get('status') != 'READY_FOR_USER_REVIEW' or receipt.get('publication_authorized') is not False:
        raise BootstrapError('APPROVAL_RECEIPT_INVALID', 'Unexpected official gate receipt')
    return authorization


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    cli.add_argument('--bundle', type=Path, help='Local bundle transferred through GitHub connector or filesystem')
    cli.add_argument('--offline', action='store_true', help='Never attempt outbound HTTPS')
    cli.add_argument('--repair', action='store_true', help='Replace stale official scripts from verified bundle')
    cli.add_argument('--manifest', type=Path, help='Candidate audit manifest relative to repository root')
    phases = cli.add_mutually_exclusive_group()
    phases.add_argument('--audit-only', action='store_true',
                        help='Run validator and auditor, then STOP for actual visual inspection')
    phases.add_argument('--gate-only', action='store_true',
                        help='Run approval gate only after inspection and an up-to-date audit')
    phases.add_argument('--execute', action='store_true',
                        help='Run all three steps ONLY if independent inspection was already completed')
    args = cli.parse_args(argv)
    root = args.repo_root.resolve()
    selected = 'audit' if args.audit_only else 'gate' if args.gate_only else 'full' if args.execute else None
    if selected and not args.manifest:
        print('BOOTSTRAP BLOCKED [MANIFEST_MISSING]: selected phase requires --manifest', file=sys.stderr)
        return 2
    try:
        bundle, source = load_bundle(root, args.bundle, args.offline)
        verified, total = verify_bundle(bundle)
        print('BUNDLE VERIFIED: ' + str(len(verified)) + ' official files, ' + str(total) + ' pinned masters; source=' + source)
        staged = install(root, verified, repair=args.repair)
        print('BOOTSTRAP PASS: ' + str(len(staged)) + ' official files staged')
        if selected:
            check_dependencies()
            manifest_file, output, sha = check_candidate(root, args.manifest)
            print('CANDIDATE VERIFIED: ' + sha)
            receipt = run_official(root, manifest_file, output, phase=selected)
            if receipt:
                print('APPROVAL GATE PASS: ' + str(receipt))
                print('PUBLICATION AUTHORIZED: false')
            else:
                print('APPROVAL GATE NOT RUN: manual inspection required')
        return 0
    except BootstrapError as exc:
        print('BOOTSTRAP BLOCKED [' + exc.code + ']: ' + str(exc), file=sys.stderr)
        print('NO APPROVAL / NO PUBLICATION', file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print('BOOTSTRAP BLOCKED [UNEXPECTED_ENVIRONMENT]: ' + str(exc), file=sys.stderr)
        print('NO APPROVAL / NO PUBLICATION', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
