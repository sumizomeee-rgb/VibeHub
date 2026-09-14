"""Generate native application assets from the single VibeHub SVG mark."""
from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MARK = ROOT / "frontend/public/vibehub-mark.svg"
ICON = ROOT / "build/branding/vibehub.ico"
ICON_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def build_icon(source: Path = MARK, target: Path = ICON) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    png = cairosvg.svg2png(bytestring=source.read_bytes(), output_width=256, output_height=256)
    target.with_suffix(".png").write_bytes(png)
    with Image.open(BytesIO(png)) as image:
        image.convert("RGBA").save(target, format="ICO", sizes=ICON_SIZES)
    return target


if __name__ == "__main__":
    print(build_icon())
