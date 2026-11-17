#!/usr/bin/env python3
"""Regressions: exact pinned masters, reference evidence and revision continuity."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('recognition', 'premium_curves', 'composition', 'geometry',
          'optical_balance', 'family_consistency', 'color_roles',
          'small_size', 'reference_fidelity', 'family_color_balance')


class WorkflowAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        (self.root / 'assets').mkdir()
        (self.root / 'work').mkdir()
        for filename in ('audit_workflow.py', 'validate_asset.py', 'approved_masters.json'):
            shutil.copyfile(SOURCE_ROOT / 'scripts' / filename, self.root / 'scripts' / filename)
        index = json.loads((self.root / 'scripts/approved_masters.json').read_text())
        for name in index:
            shutil.copyfile(SOURCE_ROOT / 'assets' / (name + '.svg'),
                            self.root / 'assets' / (name + '.svg'))
        candidate = self.root / 'work/candidate.svg'
        shutil.copyfile(self.root / 'assets/cloud.svg', candidate)
        self.manifest = {
            'mode': 'new', 'asset': 'Cloud test', 'version': 'V1',
            'candidate': 'work/candidate.svg',
            'candidate_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
            'output_dir': 'work/audit',
            'references': [
                {'url': 'https://lucide.dev/icons/cloud', 'visual_trait': 'silhouette', 'decision': 'reference'},
                {'url': 'https://icons.getbootstrap.com/icons/cloud/', 'visual_trait': 'outline', 'decision': 'reference'},
                {'url': 'https://fonts.google.com/icons', 'visual_trait': 'shape', 'decision': 'reference'}
            ],
            'chromatic_decision': {'split': False, 'rationale': 'Uniform cyan is suitable for the original cloud silhouette.'},
            'visual_audit': {**{k: {'score': 8, 'finding': 'Fixture finding: independent inspection needed.'}
                                  for k in FIELDS}, 'verdict': 'READY FOR USER APPROVAL'}
        }

    def execute(self):
        manifest_path = self.root / 'work/manifest.json'
        manifest_path.write_text(json.dumps(self.manifest, indent=2))
        result = subprocess.run([sys.executable, str(self.root / 'scripts/audit_workflow.py'),
                                 '--repo-root', str(self.root), '--manifest', str(manifest_path)],
                                capture_output=True, text=True)
        report = json.loads((self.root / 'work/audit/audit-report.json').read_text())
        return result, report

    def test_01_valid_artifacts_pass(self):
        run, report = self.execute()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(report['automated_preflight'], 'PASS')
        self.assertTrue(all(item['pass'] for item in report['hard_rules']))
        self.assertTrue(all(Path(report['renders'][k]).is_file()
                            for k in ('1024', '128', '64', 'family')))
        self.assertFalse(report['publication_authorized'])
        self.assertTrue(report['human_review_required'])

    def test_02_modified_master_fails(self):
        with (self.root / 'assets/cloud.svg').open('ab') as f:
            f.write(b'\n<!-- unapproved change -->\n')
        run, report = self.execute()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('Approved master: cloud', '\n'.join(report['failures']))

    def test_03_missing_reference_fails(self):
        self.manifest['references'] = self.manifest['references'][:2]
        run, report = self.execute()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('Three distinct documented references', '\n'.join(report['failures']))

    def test_04_revision_without_previous_fails(self):
        self.manifest['mode'] = 'revision'
        run, report = self.execute()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('Previous candidate SHA-256', '\n'.join(report['failures']))

    def test_05_wrong_candidate_hash_fails(self):
        self.manifest['candidate_sha256'] = '0'*64
        run, report = self.execute()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('Candidate SHA-256', '\n'.join(report['failures']))


if __name__ == '__main__':
    unittest.main()
