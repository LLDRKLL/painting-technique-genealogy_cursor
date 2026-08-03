#!/usr/bin/env python3
"""Resolve fractional crop boxes against actual image sizes; sync sources.csv."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CROPS = ROOT / "images" / "crops.json"
MANIFEST = ROOT / "images" / "_manifest.json"
ORIG = ROOT / "images" / "originals"
SOURCES = ROOT / "references" / "sources.csv"


def main() -> None:
    crops = json.loads(CROPS.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    for slug, spec in crops.items():
        src = spec["source"]
        path = ORIG / manifest[src]["filename"]
        if not path.exists():
            print(f"[skip] {slug}: missing {path}")
            continue
        with Image.open(path) as im:
            W, H = im.size

        box = spec["box"]
        if spec.get("box_units") == "fraction":
            x, y, w, h = box
            box = [int(x * W), int(y * H), int(w * W), int(h * H)]
            spec["box"] = box
            del spec["box_units"]

        x, y, w, h = box
        # clamp
        x = max(0, min(x, W - 2))
        y = max(0, min(y, H - 2))
        w = max(1, min(w, W - x))
        h = max(1, min(h, H - y))
        spec["box"] = [x, y, w, h]

        if "annotations_frac" in spec:
            anns = []
            for a in spec["annotations_frac"]:
                na = {"type": a["type"], "label": a.get("label", "")}
                if a["type"] == "box":
                    rx, ry, rw, rh = a["rect"]
                    na["rect"] = [int(rx * w), int(ry * h), int(rw * w), int(rh * h)]
                elif a["type"] == "arrow":
                    na["from"] = [int(a["from"][0] * w), int(a["from"][1] * h)]
                    na["to"] = [int(a["to"][0] * w), int(a["to"][1] * h)]
                elif a["type"] == "line":
                    na["points"] = [[int(p[0] * w), int(p[1] * h)] for p in a["points"]]
                anns.append(na)
            spec["annotations"] = anns
            del spec["annotations_frac"]

        print(f"{slug}: {spec['box']} from {W}x{H}")

    CROPS.write_text(json.dumps(crops, ensure_ascii=False, indent=2), encoding="utf-8")

    # sync sources.csv crop coords
    rows = []
    with SOURCES.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for row in reader:
            slug = row["编号"]
            if slug in crops:
                b = crops[slug]["box"]
                row["裁切坐标"] = f"{b[0]},{b[1]},{b[2]},{b[3]}"
                row["母图编号"] = crops[slug]["source"]
            rows.append(row)
    with SOURCES.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("materialized")


if __name__ == "__main__":
    main()
