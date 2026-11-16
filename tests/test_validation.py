import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_asset import inspect_svg

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / 'assets/escudo-candado.svg'

class ValidateAssetTests(unittest.TestCase):
    def test_master(self):
        errors, bbox = inspect_svg(MASTER, check_visual=True)
        self.assertEqual(errors, [], errors)
        self.assertTrue(bbox)

    def test_fourth_color_rejected(self):
        src = MASTER.read_text().replace('</style>', '.extra{fill:#123456}</style>')
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'bad.svg'
            f.write_text(src)
            errors, _ = inspect_svg(f, check_visual=False)
            self.assertTrue(any('Extra colors' in e for e in errors))

    def test_raster_rejected(self):
        src = MASTER.read_text().replace('</svg>', '<image href="data:image/png;base64,AAAA"/></svg>')
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'bad.svg'
            f.write_text(src)
            errors, _ = inspect_svg(f, check_visual=False)
            self.assertTrue(any('Forbidden element: image' in e for e in errors))

    def test_geometry_with_wrong_canvas_rejected(self):
        src = MASTER.read_text().replace('width="1024"', 'width="2048"', 1)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'bad.svg'
            f.write_text(src)
            errors, _ = inspect_svg(f, check_visual=False)
            self.assertTrue(any('Canvas' in e for e in errors))

if __name__ == '__main__':
    unittest.main()
