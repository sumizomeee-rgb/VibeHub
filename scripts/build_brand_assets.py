"""Generate native assets from the small, code-owned VibeHub SVG mark.

The renderer intentionally supports only the SVG primitives used by the mark. This
keeps Windows builds portable instead of requiring a system Cairo installation.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageColor, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
MARK = ROOT / "frontend/public/vibehub-mark.svg"
ICON = ROOT / "build/branding/vibehub.ico"
ICON_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
RENDER_SIZE = 1024


def _color(value: str, opacity: float = 1.0) -> tuple[int, int, int, int]:
    red, green, blue = ImageColor.getrgb(value)
    return red, green, blue, round(255 * opacity)


def _number(value: str) -> float:
    return float(value.rstrip("px"))


def _points(path_data: str) -> list[tuple[float, float]]:
    """Parse the mark's deliberately simple M/L polyline path."""
    tokens = re.findall(r"[MLml]|-?(?:\d+(?:\.\d*)?|\.\d+)", path_data)
    points: list[tuple[float, float]] = []
    index = 0
    while index < len(tokens):
        command = tokens[index]
        if command not in {"M", "L"} or index + 2 >= len(tokens):
            raise ValueError(f"Unsupported brand-mark path: {path_data}")
        points.append((float(tokens[index + 1]), float(tokens[index + 2])))
        index += 3
    return points


def render_mark(source: Path, size: int = RENDER_SIZE) -> Image.Image:
    root = ET.fromstring(source.read_text(encoding="utf-8"))
    view_box = [_number(part) for part in root.attrib["viewBox"].split()]
    if view_box[:2] != [0, 0] or view_box[2] != view_box[3]:
        raise ValueError("Brand mark must use a square viewBox starting at 0,0")
    scale = size / view_box[2]
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    for element in root:
        tag = element.tag.rsplit("}", 1)[-1]
        opacity = float(element.attrib.get("opacity", "1"))
        if tag == "rect":
            x, y = _number(element.attrib.get("x", "0")), _number(element.attrib.get("y", "0"))
            width, height = _number(element.attrib["width"]), _number(element.attrib["height"])
            radius = _number(element.attrib.get("rx", "0"))
            draw.rounded_rectangle(
                (x * scale, y * scale, (x + width) * scale, (y + height) * scale),
                radius=radius * scale,
                fill=_color(element.attrib["fill"], opacity),
            )
        elif tag == "path":
            points = [(x * scale, y * scale) for x, y in _points(element.attrib["d"])]
            width = round(_number(element.attrib["stroke-width"]) * scale)
            fill = _color(element.attrib["stroke"], opacity)
            draw.line(points, fill=fill, width=width, joint="curve")
            if element.attrib.get("stroke-linecap") == "round":
                radius = width / 2
                for x, y in points:
                    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)
        elif tag == "circle":
            x, y, radius = (_number(element.attrib[name]) * scale for name in ("cx", "cy", "r"))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                         fill=_color(element.attrib["fill"], opacity))
        else:
            raise ValueError(f"Unsupported brand-mark element: {tag}")
    return image


def build_icon(source: Path = MARK, target: Path = ICON) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    image = render_mark(source).resize((256, 256), Image.Resampling.LANCZOS)
    image.save(target.with_suffix(".png"), format="PNG")
    image.save(target, format="ICO", sizes=ICON_SIZES)
    return target


if __name__ == "__main__":
    print(build_icon())
