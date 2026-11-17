"""Regression tests for the official auditor's offline exact-master recovery."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from master_cache import PACK_FORMAT, git_blob, resolve_masters


class MasterCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'scripts').mkdir()
        self.output = self.root / 'work' / 'audit'
        self.assets = {
            'first': '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>\n',
            'second': '<svg xmlns="http://www.w3.org/2000/svg"><path d="M1 1"/></svg>\n',
        }
        self.pinned = {k: git_blob(v.encode('utf-8')) for k, v in self.assets.items()}

    def pack(self, assets=None):
        content = {'format': PACK_FORMAT, 'assets': self.assets if assets is None else assets}
        (self.root / 'scripts' / 'approved_masters_pack.json').write_text(
            json.dumps(content, ensure_ascii=False), encoding='utf-8'
        )

    def originals(self):
        (self.root / 'assets').mkdir()
        for name, content in self.assets.items():
            (self.root / 'assets' / (name + '.svg')).write_bytes(content.encode('utf-8'))

    def test_missing_local_masters_recover_exact_bytes_from_verified_pack(self):
        self.pack()
        records, errors = resolve_masters(self.root, self.output, self.pinned)
        self.assertEqual([], errors)
        self.assertEqual(2, len(records))
        for name, path, source, actual in records:
            self.assertEqual(source, 'verified-pack')
            self.assertEqual(path.read_bytes(), self.assets[name].encode('utf-8'))
            self.assertEqual(actual, self.pinned[name])

    def test_existing_originals_pass_without_pack(self):
        self.originals()
        records, errors = resolve_masters(self.root, self.output, self.pinned)
        self.assertEqual([], errors)
        self.assertEqual({x[2] for x in records}, {'original'})
        self.assertFalse((self.output / 'verified_masters').exists())

    def test_incomplete_pack_must_fail(self):
        self.pack({'first': self.assets['first']})
        records, errors = resolve_masters(self.root, self.output, self.pinned)
        self.assertEqual([], records)
        self.assertTrue(any('stale' in x for x in errors))

    def test_changed_pack_svg_must_fail(self):
        broken = dict(self.assets)
        broken['second'] += '<!-- tampered -->'
        self.pack(broken)
        records, errors = resolve_masters(self.root, self.output, self.pinned)
        self.assertEqual([], records)
        self.assertTrue(any('SHA mismatch: second' in x for x in errors))

    def test_tampered_original_never_silently_falls_back(self):
        self.pack()
        self.originals()
        (self.root / 'assets' / 'first.svg').write_bytes(b'changed')
        records, errors = resolve_masters(self.root, self.output, self.pinned)
        self.assertTrue(any('hash mismatch: first' in x for x in errors))
        self.assertEqual({x[0] for x in records}, {'second'})

    def test_missing_pack_and_missing_masters_must_fail(self):
        records, errors = resolve_masters(self.root, self.output, self.pinned)
        self.assertEqual([], records)
        self.assertTrue(any('Missing approved master' in x for x in errors))

    def test_stale_pack_fails_even_with_valid_originals(self):
        self.originals()
        self.pack({'first': self.assets['first']})
        records, errors = resolve_masters(self.root, self.output, self.pinned)
        self.assertEqual([], records)
        self.assertTrue(errors)


if __name__ == '__main__':
    unittest.main()
