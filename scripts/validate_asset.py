#!/usr/bin/env python3
"""Enforce the hard SVG asset invariants and visible geometry normalization."""
import argparse
import io
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

COLORS = {"PRIMARY": "#092B60", "SECONDARY": "#38BDF8", "CONTRAST": "#FFFFFF"}
ROLES = {"primary", "secondary", "contrast"}
NS = "{http://www.w3.org/2000/svg}"
DRAWABLE = {"path", "rect", "circle", "ellipse", "polygon", "polyline", "line", "use"}
FORBIDDEN = {"image", "foreignObject", "linearGradient", "radialGradient", "filter", "mask",
             "pattern", "script", "animate", "animateTransform"}
BAD_ATTRS = {"opacity", "fill-opacity", "stroke-opacity", "filter", "style", "mask", "clip-rule"}

def inspect_svg(path, check_visual=True):
    raw = Path(path).read_text(encoding="utf-8")
    root = ET.fromstring(raw)
    issues = []
    if root.tag != NS + "svg":
        issues.append("Root must be SVG")
    if (root.get("width"), root.get("height"), root.get("viewBox")) != ("1024", "1024", "0 0 1024 1024"):
        issues.append("Canvas must be exactly 1024 x 1024")
    style = "".join((e.text or "") for e in root.iter(NS + "style"))
    for token, expected in COLORS.items():
        found = re.search(r"--" + token + r"\s*:\s*(#[0-9a-fA-F]{6})\s*;", style)
        if not found or found.group(1).upper() != expected:
            issues.append("Missing/incorrect token " + token)
        if not re.search(r"\." + token.lower() + r"\s*\{\s*fill:\s*var\(--" + token + r"\)\s*;?\s*\}", style):
            issues.append("Missing token class " + token.lower())
    cleaned = re.sub(r"--(?:PRIMARY|SECONDARY|CONTRAST)\s*:\s*#[0-9a-fA-F]{6}\s*;", "", style)
    if re.search(r"#[0-9a-fA-F]{3,8}\b|\brgb\s*\(|\bhsl\s*\(", cleaned, re.I):
        issues.append("Extra colors outside token definitions")
    cleaned = re.sub(r":root\s*\{\s*\}", "", cleaned)
    cleaned = re.sub(r"\.(?:primary|secondary|contrast)\s*\{\s*fill:\s*var\(--(?:PRIMARY|SECONDARY|CONTRAST)\)\s*;?\s*\}", "", cleaned)
    if cleaned.strip() or len(re.findall(r"--[A-Za-z][\w-]*\s*:", style)) != 3:
        issues.append("Unexpected CSS: exactly three token classes allowed")
    painted = set()
    parent = {c: p for p in root.iter() for c in p}
    for e in root.iter():
        kind = e.tag.split("}")[-1]
        if kind in FORBIDDEN:
            issues.append("Forbidden element: " + kind)
        for attr, value in e.attrib.items():
            key = attr.split("}")[-1]
            if key in BAD_ATTRS or key.lower().startswith("on"):
                issues.append("Forbidden attribute: " + key)
            if key in ("fill", "stroke", "color") and value.lower() != "none":
                issues.append("Hard-coded color: " + key)
            if key == "href" and (value.startswith("http") or value.startswith("data:")):
                issues.append("External/embedded reference")
        if kind in DRAWABLE:
            role = e.get("class")
            if role in ROLES:
                painted.add(role)
            else:
                cur = e
                in_reference = False
                while cur in parent:
                    cur = parent[cur]
                    if cur.tag in (NS + "defs", NS + "clipPath"):
                        in_reference = True
                        break
                if not in_reference:
                    issues.append("Unclassified painted shape " + kind)
    if painted != ROLES:
        issues.append("All three roles must appear")
    visual = None
    if check_visual and not issues:
        try:
            import cairosvg
            from PIL import Image
            copied = ET.fromstring(raw)
            for e in copied.iter():
                if e.get("class") in ROLES:
                    e.set("fill", COLORS[e.get("class").upper()])
            for p in copied.iter():
                for child in list(p):
                    if child.tag == NS + "style":
                        p.remove(child)
            image = Image.open(io.BytesIO(cairosvg.svg2png(
                bytestring=ET.tostring(copied), output_width=1024, output_height=1024
            ))).convert("RGBA")
            alpha = image.getchannel("A").point(lambda x: 255 if x > 96 else 0)
            box = alpha.getbbox()
            if box is None:
                issues.append("No visible geometry")
            else:
                x0, y0, x1, y1 = box
                dominant = max(x1 - x0, y1 - y0)
                center = ((x0+x1)/2, (y0+y1)/2)
                visual = {"bbox": box, "dominant": dominant, "center": center}
                if not 901 <= dominant <= 943:
                    issues.append("Dominant size must be 922 ±21")
                if abs(center[0]-512) > 12 or abs(center[1]-512) > 12:
                    issues.append("Visible geometry not centered")
                if min(x0, y0, 1024-x1, 1024-y1) < 20:
                    issues.append("Insufficient safety margin")
        except Exception as exc:
            issues.append("Visual render failed: " + str(exc))
    return issues, visual

def main():
    p = argparse.ArgumentParser()
    p.add_argument("paths", nargs="+")
    p.add_argument("--skip-visual", action="store_true")
    args = p.parse_args()
    failed = False
    for path in args.paths:
        issues, metrics = inspect_svg(path, not args.skip_visual)
        print(("FAIL" if issues else "PASS"), path, metrics or "")
        for issue in issues:
            print(" -", issue)
        failed = failed or bool(issues)
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
