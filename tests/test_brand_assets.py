import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.build_brand_assets import MARK, build_icon


class BrandAssetTests(unittest.TestCase):
    def test_native_icon_is_generated_without_system_graphics_libraries(self):
        with tempfile.TemporaryDirectory() as directory:
            icon = build_icon(MARK, Path(directory) / "vibehub.ico")
            with Image.open(icon) as image:
                self.assertEqual(image.format, "ICO")
                self.assertEqual(image.size, (256, 256))
            self.assertTrue(icon.with_suffix(".png").is_file())


if __name__ == "__main__":
    unittest.main()
