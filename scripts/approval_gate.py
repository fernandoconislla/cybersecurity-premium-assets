#!/usr/bin/env python3
"""Fail-closed presentation gate for premium SVG candidates.

Run only after audit_workflow.py. A PASS is permission to request user approval,
never permission to publish. Human attestations are explicitly self-reported.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

CRITERIA = ('recognition', 'premium_curves', 'composition', 'geometry',
            'optical_balance', 'family_consistency', 'color_roles',
            'small_size', 'reference_fidelity', 'family_color_balance')
REQUIRED_REVIEWS = ('references_verified', 'previews_inspected',
                    'family_compared', 'critical_defects_checked')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def within(root, relative):
    result = (root / relative).resolve()
    if not result.is_relative_to(root):
        raise ValueError('Path escapes repository: ' + str(relative))
    return result


def verify(root, manifest_path, report_path):
    errors = []
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    report = json.loads(report_path.read_text(encoding='utf-8'))
    candidate = within(root, manifest['candidate'])
    output = within(root, manifest['output_dir'])
    if not candidate.is_file():
        errors.append('Candidate missing')
    else:
        actual = digest(candidate)
        if actual != manifest.get('candidate_sha256') or actual != report.get('sha256'):
            errors.append('Candidate hash mismatch')
    if report.get('candidate') != str(candidate):
        errors.append('Report references another candidate')
    if report.get('asset') != manifest.get('asset') or report.get('version') != manifest.get('version'):
        errors.append('Asset/version mismatch')
    if report.get('manifest_sha256') != digest(manifest_path):
        errors.append('Report is stale: manifest changed')
    if report.get('automated_preflight') != 'PASS' or report.get('failures'):
        errors.append('Automated preflight failed')
    if not report.get('ready_for_approval'):
        errors.append('Auditor did not mark candidate ready')
    checks = report.get('checks', [])
    if not checks or any(c.get('status') != 'PASS' for c in checks):
        errors.append('Missing or failed audit checks')
    rules = report.get('hard_rules', [])
    if len(rules) != 8 or sorted(r.get('number') for r in rules) != list(range(1, 9)) or any(r.get('pass') is not True for r in rules):
        errors.append('Eight hard rules not satisfied')
    visual = manifest.get('visual_audit', {})
    if visual.get('verdict') != 'READY FOR USER APPROVAL':
        errors.append('Visual audit verdict not ready')
    for criterion in CRITERIA:
        entry = visual.get(criterion)
        if not isinstance(entry, dict) or not isinstance(entry.get('score'), (int, float)) or isinstance(entry.get('score'), bool) or not 0 <= entry['score'] <= 10 or len(str(entry.get('finding', '')).strip()) < 12:
            errors.append('Visual criterion incomplete: ' + criterion)
    evidence = manifest.get('manual_evidence', {})
    for name in REQUIRED_REVIEWS:
        entry = evidence.get(name)
        if not isinstance(entry, dict) or entry.get('reviewed') is not True or len(str(entry.get('finding', '')).strip()) < 20:
            errors.append('Manual review missing: ' + name)
    renders = report.get('renders', {})
    hashes = report.get('render_sha256', {})
    required = ('1024', '128', '64', 'family') + (('previous',) if manifest.get('mode') == 'revision' else ())
    for name in required:
        raw = renders.get(name)
        if not raw:
            errors.append('Render missing: ' + name)
            continue
        path = Path(raw).resolve()
        if not path.is_relative_to(output) or not path.is_file() or digest(path) != hashes.get(name):
            errors.append('Render missing, altered or outside audit directory: ' + name)
    index = within(root, 'scripts/approved_masters.json')
    if not index.is_file():
        errors.append('Master index missing')
    else:
        pinned = json.loads(index.read_text(encoding='utf-8'))
        expected_master_checks = {'Approved master: ' + key for key in pinned}
        passed_master_checks = {c.get('rule') for c in checks if c.get('status') == 'PASS'}
        if not pinned or not expected_master_checks.issubset(passed_master_checks):
            errors.append('Incomplete approved-master checks')
    return errors, manifest, report, candidate, output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path('.'))
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    manifest_path = args.manifest.resolve()
    report_path = args.report.resolve()
    errors = []
    receipt = None
    try:
        manifest_output = json.loads(manifest_path.read_text(encoding='utf-8')).get('output_dir', '')
        output = within(root, manifest_output)
        receipt = output / 'approval-authorization.json'
        if receipt.is_file():
            receipt.unlink()  # stale authorization must never survive failed recheck
        errors, manifest, report, candidate, output = verify(root, manifest_path, report_path)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    if errors:
        print('APPROVAL GATE BLOCKED')
        for error in errors:
            print('FAIL ' + error)
        return 1
    data = {
        'status': 'READY_FOR_USER_REVIEW',
        'publication_authorized': False,
        'candidate': str(candidate),
        'candidate_sha256': report['sha256'],
        'manifest_sha256': digest(manifest_path),
        'audit_report_sha256': digest(report_path),
        'render_sha256': {key: report['render_sha256'][key] for key in report['renders']},
        'manual_review_attested': True,
        'note': 'Human findings are declarations, not independently machine-verified evidence.'
    }
    receipt.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('APPROVAL GATE PASS')
    print('Candidate SHA256 ' + report['sha256'])
    print('Receipt: ' + str(receipt))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
