#!/usr/bin/env python3
"""Rewrite crop boxes as fractions of each source image, then materialize pixel boxes."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "images" / "_manifest.json").read_text(encoding="utf-8"))
CROPS_PATH = ROOT / "images" / "crops.json"
ORIG = ROOT / "images" / "originals"
SOURCES = ROOT / "references" / "sources.csv"

# Relative boxes: x,y,w,h as 0-1 fractions of source image
REL = {
    "masaccio-trinity-coffers": (0.18, 0.02, 0.64, 0.55),
    "raphael-orthogonals": (0.25, 0.35, 0.50, 0.55),
    "arnolfini-mirror": (0.38, 0.35, 0.28, 0.30),
    "holbein-skull": (0.15, 0.70, 0.70, 0.25),
    "leonardo-sfumato-jaw": (0.30, 0.35, 0.40, 0.40),
    "caravaggio-hand-edge": (0.45, 0.40, 0.40, 0.40),
    "rembrandt-armor": (0.35, 0.25, 0.35, 0.45),
    "monet-shadow-color": (0.15, 0.35, 0.55, 0.45),
    "botticelli-hatching": (0.40, 0.35, 0.35, 0.45),
    "meninas-mirror": (0.45, 0.20, 0.25, 0.30),
}


def main() -> None:
    crops = json.loads(CROPS_PATH.read_text(encoding="utf-8"))
    for slug, frac in REL.items():
        if slug not in crops:
            continue
        source = crops[slug]["source"]
        fn = MANIFEST[source]["filename"]
        path = ORIG / fn
        with Image.open(path) as im:
            W, H = im.size
        x = int(frac[0] * W)
        y = int(frac[1] * H)
        w = int(frac[2] * W)
        h = int(frac[3] * H)
        crops[slug]["box"] = [x, y, w, h]
        # Scale annotations roughly into new crop space
        anns = []
        for ann in crops[slug].get("annotations", []):
            a = dict(ann)
            if a["type"] == "box":
                a["rect"] = [int(w * 0.15), int(h * 0.12), int(w * 0.25), int(h * 0.2)]
            elif a["type"] == "arrow":
                a["from"] = [int(w * 0.15), int(h * 0.35)]
                a["to"] = [int(w * 0.55), int(h * 0.45)]
            elif a["type"] == "line":
                a["points"] = [[0, int(h * 0.7)], [w, int(h * 0.7)]]
            anns.append(a)
        crops[slug]["annotations"] = anns
        print(slug, crops[slug]["box"], f"from {W}x{H}")

    CROPS_PATH.write_text(json.dumps(crops, ensure_ascii=False, indent=2), encoding="utf-8")

    # Update sources.csv crop coords
    rows = []
    with SOURCES.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for row in reader:
            slug = row["编号"]
            if slug in crops:
                box = crops[slug]["box"]
                row["裁切坐标"] = f"{box[0]},{box[1]},{box[2]},{box[3]}"
            rows.append(row)
    with SOURCES.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("normalized")


if __name__ == "__main__":
    main()
