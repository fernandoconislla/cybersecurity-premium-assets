"""Regression tests for offline/connector-friendly audit bootstrap."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bootstrap_audit as bootstrap

BUNDLE = ROOT / 'scripts/audit_runtime_bundle.json'
FIELDS = (
    'recognition', 'premium_curves', 'composition', 'geometry',
    'optical_balance', 'family_consistency', 'color_roles',
    'small_size', 'reference_fidelity', 'family_color_balance'
)


class BootstrapAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'work').mkdir()

    def call(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / 'scripts/bootstrap_audit.py'),
             '--repo-root', str(self.root), *args],
            capture_output=True, text=True
        )

    def test_01_bundle_verifies_all_masters_and_official_validator(self):
        payload = json.loads(BUNDLE.read_text(encoding='utf-8'))
        files, count = bootstrap.verify_bundle(payload)
        self.assertEqual(set(files), set(bootstrap.REQUIRED))
        self.assertEqual(count, 17)
        self.assertIn(b'VALIDATOR_BLOB_SHA', files['scripts/audit_workflow.py'])

    def test_02_offline_setup_no_local_assets_passes(self):
        result = self.call('--offline', '--bundle', str(BUNDLE))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('BOOTSTRAP PASS', result.stdout)
        for name in bootstrap.REQUIRED:
            self.assertTrue((self.root / name).is_file(), name)
        self.assertFalse((self.root / 'assets').exists())

    def test_03_tampered_bundle_fails_closed(self):
        data = json.loads(BUNDLE.read_text(encoding='utf-8'))
        data['files']['scripts/validate_asset.py']['content'] += '\\n# altered'
        modified = self.root / 'tampered.json'
        modified.write_text(json.dumps(data), encoding='utf-8')
        result = self.call('--offline', '--bundle', str(modified))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('TAMPERED_BUNDLE', result.stderr)
        self.assertFalse((self.root / 'scripts/validate_asset.py').exists())

    def test_04_stale_runtime_requires_explicit_repair(self):
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/validate_asset.py').write_text('bad')
        result = self.call('--offline', '--bundle', str(BUNDLE))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('STALE_RUNTIME', result.stderr)
        self.assertFalse((self.root / 'scripts/master_cache.py').exists())
        fixed = self.call('--offline', '--bundle', str(BUNDLE), '--repair')
        self.assertEqual(fixed.returncode, 0, fixed.stderr)
        self.assertEqual(
            (self.root / 'scripts/validate_asset.py').read_bytes(),
            (ROOT / 'scripts/validate_asset.py').read_bytes()
        )

    def test_05_missing_bundle_in_restricted_environment_is_explicit(self):
        result = self.call('--offline')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('BUNDLE_NOT_AVAILABLE', result.stderr)
        self.assertIn('GitHub app', result.stderr)

    def test_06_execution_requires_manifest(self):
        result = self.call('--offline', '--bundle', str(BUNDLE), '--execute')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('MANIFEST_MISSING', result.stderr)

    def test_07_wrong_candidate_hash_blocks_before_audit(self):
        self.prepare_manifest('0' * 64)
        result = self.call('--offline', '--bundle', str(BUNDLE),
                           '--manifest', 'work/manifest.json', '--execute')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('CANDIDATE_SHA_MISMATCH', result.stderr)
        self.assertFalse((self.root / 'work/audit/approval-authorization.json').exists())

    def prepare_manifest(self, invalid_sha=None):
        source = ROOT / 'assets/cloud.svg'
        candidate = self.root / 'work/candidate.svg'
        shutil.copyfile(source, candidate)
        sha = hashlib.sha256(candidate.read_bytes()).hexdigest()
        manifest = {
            'mode': 'new', 'asset': 'Offline fixture', 'version': 'V1',
            'candidate': 'work/candidate.svg', 'candidate_sha256': invalid_sha or sha,
            'output_dir': 'work/audit',
            'references': [
                {'url': 'https://lucide.dev/icons/cloud', 'visual_trait': 'shape', 'decision': 'shape'},
                {'url': 'https://icons.getbootstrap.com/icons/cloud/', 'visual_trait': 'volume', 'decision': 'volume'},
                {'url': 'https://fonts.google.com/icons', 'visual_trait': 'size', 'decision': 'size'},
            ],
            'chromatic_decision': {'split': False, 'rationale': 'Uniform cyan is coherent with a cloud.'},
            'visual_audit': {**{k: {'score': 8.0, 'finding': 'Test fixture only; subjective evidence is not implied.'}
                                  for k in FIELDS}, 'verdict': 'READY FOR USER APPROVAL'},
            'manual_evidence': {
                k: {'reviewed': True, 'finding': 'Fixture-only test evidence; not a real design review.'}
                for k in ('references_verified', 'previews_inspected', 'family_compared', 'critical_defects_checked')
            },
        }
        (self.root / 'work/manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def test_08_exact_offline_bundle_executes_all_three_official_scripts(self):
        self.prepare_manifest()
        result = self.call('--offline', '--bundle', str(BUNDLE),
                           '--manifest', 'work/manifest.json', '--execute')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ('validate_asset.py', 'audit_workflow.py', 'approval_gate.py'):
            self.assertIn('STEP ' + name + ': PASS', result.stdout)
        report = json.loads((self.root / 'work/audit/audit-report.json').read_text())
        self.assertEqual(report['automated_preflight'], 'PASS')
        self.assertEqual(sum(item['pass'] for item in report['hard_rules']), 8)
        receipt = json.loads((self.root / 'work/audit/approval-authorization.json').read_text())
        self.assertEqual(receipt['status'], 'READY_FOR_USER_REVIEW')
        self.assertFalse(receipt['publication_authorized'])
        self.assertTrue((self.root / 'work/audit/verified_masters/cloud.svg').exists())


if __name__ == '__main__':
    unittest.main()
