#!/usr/bin/env python3
"""Derive web images and annotated crops from originals / schematics."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent
ORIG = ROOT / "images" / "originals"
MANIFEST = ROOT / "images" / "_manifest.json"
CROPS_DEF = ROOT / "images" / "crops.json"
OUT = ROOT / "site" / "img"
CROPS_OUT = OUT / "crops"
LAYERS_OUT = OUT / "layers"
ACCENT = (176, 82, 44, 255)


def ensure_dirs() -> None:
    for p in (OUT, CROPS_OUT, LAYERS_OUT, ORIG):
        p.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def font(size: int):
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def resize_max(im: Image.Image, max_side: int) -> Image.Image:
    w, h = im.size
    scale = max_side / max(w, h)
    if scale >= 1:
        return im.copy()
    return im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)


def save_jpeg(im: Image.Image, path: Path, quality: int = 88) -> None:
    rgb = im.convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass
    rgb.save(tmp, "JPEG", quality=quality, optimize=True)
    tmp.replace(path)


def make_temp_map(im: Image.Image) -> Image.Image:
    """Pseudo temperature map: warm=reddish, cool=bluish from hue/value heuristic."""
    rgb = im.convert("RGB")
    small = resize_max(rgb, 1600)
    px = small.load()
    w, h = small.size
    out = Image.new("RGB", (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            warmth = (r + g * 0.5) - b
            if warmth > 20:
                op[x, y] = (min(255, int(180 + warmth * 0.4)), int(90 + g * 0.2), 70)
            elif warmth < -15:
                op[x, y] = (70, int(90 + b * 0.25), min(255, int(160 - warmth * 0.3)))
            else:
                v = (r + g + b) // 3
                op[x, y] = (v, v, int(v * 0.95))
    return out.filter(ImageFilter.SMOOTH_MORE)


def stroke_width(im: Image.Image) -> int:
    return max(2, int(min(im.size) * 0.004))


def draw_label(draw: ImageDraw.ImageDraw, xy, text: str, fnt, pad: int = 4):
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=fnt)
    draw.rectangle(
        [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad],
        fill=(20, 16, 12, 170),
    )
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=fnt)


def annotate(im: Image.Image, annotations: list) -> Image.Image:
    base = im.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    sw = stroke_width(base)
    fnt = font(max(14, int(min(base.size) * 0.028)))
    for ann in annotations:
        t = ann.get("type")
        if t == "box":
            x, y, w, h = ann["rect"]
            draw.rectangle([x, y, x + w, y + h], outline=ACCENT, width=sw)
            if ann.get("label"):
                draw_label(draw, (x + 6, y + 6), ann["label"], fnt)
        elif t == "arrow":
            x1, y1 = ann["from"]
            x2, y2 = ann["to"]
            draw.line([x1, y1, x2, y2], fill=ACCENT, width=sw)
            ang = math.atan2(y2 - y1, x2 - x1)
            ah = sw * 4
            draw.polygon(
                [
                    (x2, y2),
                    (x2 - ah * math.cos(ang - 0.4), y2 - ah * math.sin(ang - 0.4)),
                    (x2 - ah * math.cos(ang + 0.4), y2 - ah * math.sin(ang + 0.4)),
                ],
                fill=ACCENT,
            )
            if ann.get("label"):
                draw_label(draw, (x2 + 8, y2 - 10), ann["label"], fnt)
        elif t == "line":
            pts = [tuple(p) for p in ann["points"]]
            draw.line(pts, fill=ACCENT, width=sw)
            if ann.get("label"):
                draw_label(draw, pts[0], ann["label"], fnt)
    return Image.alpha_composite(base, overlay).convert("RGB")


def ensure_min_short_side(im: Image.Image, minimum: int = 1200) -> Image.Image:
    w, h = im.size
    short = min(w, h)
    if short >= minimum:
        return im
    scale = minimum / short
    return im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)


def process_originals(manifest: dict) -> None:
    for slug, meta in manifest.items():
        src = ORIG / meta["filename"]
        if not src.exists():
            print(f"[skip] missing original {src}")
            continue
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            save_jpeg(resize_max(im, 2000), OUT / f"{slug}-2000.jpg")
            save_jpeg(resize_max(im, 640), OUT / f"{slug}-640.jpg", quality=82)
            save_jpeg(make_temp_map(im), OUT / f"{slug}-temp.jpg", quality=85)
            print(f"[ok] derivatives {slug}")


def process_crops(crops: dict, manifest: dict) -> None:
    for slug, spec in crops.items():
        source = spec["source"]
        meta = manifest.get(source)
        if not meta:
            print(f"[skip] crop {slug}: no source {source}")
            continue
        src = ORIG / meta["filename"]
        if not src.exists():
            print(f"[skip] crop {slug}: missing {src}")
            continue
        x, y, w, h = spec["box"]
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            # Clamp box to image
            iw, ih = im.size
            x = max(0, min(x, iw - 1))
            y = max(0, min(y, ih - 1))
            w = max(1, min(w, iw - x))
            h = max(1, min(h, ih - y))
            crop = im.crop((x, y, x + w, y + h))
            crop = ensure_min_short_side(crop, 1200)
            # Scale annotations if upsampled
            scale = crop.size[0] / w
            anns = []
            for ann in spec.get("annotations", []):
                a = dict(ann)
                if a.get("type") == "box":
                    rx, ry, rw, rh = a["rect"]
                    a["rect"] = [int(rx * scale), int(ry * scale), int(rw * scale), int(rh * scale)]
                elif a.get("type") == "arrow":
                    a["from"] = [int(a["from"][0] * scale), int(a["from"][1] * scale)]
                    a["to"] = [int(a["to"][0] * scale), int(a["to"][1] * scale)]
                elif a.get("type") == "line":
                    a["points"] = [[int(p[0] * scale), int(p[1] * scale)] for p in a["points"]]
                anns.append(a)
            clean = crop
            annotated = annotate(crop, anns)
            save_jpeg(clean, CROPS_OUT / f"{slug}-clean.jpg")
            save_jpeg(annotated, CROPS_OUT / f"{slug}.jpg")
            print(f"[ok] crop {slug}")


def make_layer_schematic(slug: str = "venetian-buildup") -> None:
    w, h = 1200, 800
    layers = {
        "ground": (210, 190, 150),
        "drawing": (160, 140, 120),
        "underpaint": (90, 70, 55),
        "modeling": (140, 95, 70),
        "glaze": (120, 40, 35),
        "lights": (240, 220, 190),
    }
    order = ["ground", "drawing", "underpaint", "modeling", "glaze", "lights"]
    for i, key in enumerate(order):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        # cumulative silhouette
        for j in range(i + 1):
            k = order[j]
            color = layers[k] + (255 if j == i else 0,)
            # only draw current layer opaque for stacking
        color = layers[key]
        # body oval + drapery band
        alpha = 230 if key != "lights" else 200
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        if key == "ground":
            d.rectangle([0, 0, w, h], fill=color + (255,))
        elif key == "drawing":
            d.ellipse([350, 80, 850, 720], outline=color + (255,), width=4)
            d.line([500, 250, 700, 250], fill=color + (255,), width=3)
        elif key == "underpaint":
            d.ellipse([360, 100, 840, 700], fill=color + (220,))
        elif key == "modeling":
            d.ellipse([420, 180, 620, 420], fill=color + (200,))
            d.ellipse([580, 220, 780, 480], fill=(color[0] - 30, color[1] - 20, color[2] - 10, 180))
        elif key == "glaze":
            d.rectangle([380, 300, 820, 680], fill=color + (120,))
        elif key == "lights":
            d.ellipse([470, 200, 560, 260], fill=color + (220,))
            d.ellipse([640, 240, 720, 300], fill=color + (200,))
        fnt = font(28)
        d2 = ImageDraw.Draw(layer)
        d2.text((40, 40 + i * 36), key, fill=(255, 255, 255, 230), font=fnt)
        layer.save(LAYERS_OUT / f"{slug}-{key}.png")
    print(f"[ok] layer schematic {slug}")


def main() -> None:
    ensure_dirs()
    manifest = load_json(MANIFEST, {})
    crops = load_json(CROPS_DEF, {})
    process_originals(manifest)
    process_crops(crops, manifest)
    make_layer_schematic("venetian-buildup")
    print("Asset build complete.")


if __name__ == "__main__":
    main()
