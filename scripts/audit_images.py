#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json

orig = Path("images/originals")
manifest = json.loads(Path("images/_manifest.json").read_text(encoding="utf-8"))
print(f"{'slug':28} {'bytes':>10} {'WxH':>14} status")
for slug, m in manifest.items():
    p = orig / m["filename"]
    if not p.exists():
        print(f"{slug:28} MISSING")
        continue
    with Image.open(p) as im:
        w, h = im.size
        sample = im.convert("RGB").resize((8, 8))
    avg = sum(sum(c) for c in sample.getdata()) / (8 * 8 * 3)
    status = "PLACEHOLDER" if (w, h) == (1600, 1200) and avg < 90 else "ok"
    print(f"{slug:28} {p.stat().st_size:10} {w:4}x{h:<8} {status} avg={avg:.0f}")
