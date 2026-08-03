#!/usr/bin/env python3
"""Re-download placeholders via Wikimedia API; leave good files untouched."""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "images" / "originals"
MANIFEST_PATH = ROOT / "images" / "_manifest.json"

HEADERS = {
    "User-Agent": "PaintingTechniqueGenealogy/1.1 (research education; local rebuild)",
    "Accept": "application/json,image/*",
}

# Commons filenames (exact File: titles without prefix)
COMMONS_FILES = {
    "piero-flagellation": "Flagellation of Christ (Piero della Francesca).jpg",
    "pozzo-sant-ignazio": "Glorification of Saint Ignatius - Andrea Pozzo - 1685 - Chiesa di Sant'Ignazio - Rome 2016.jpg",
    "degas-absinthe": "Edgar Degas - In a Café - Google Art Project.jpg",
    "leonardo-rocks-london": "Leonardo da Vinci - Virgin of the Rocks - Google Art Project.jpg",
    "caravaggio-emmaus": "1602-3 Caravaggio,Supper at Emmaus National Gallery, London.jpg",
    "reynolds-nelsons": "Sir Joshua Reynolds - The Age of Innocence - Google Art Project.jpg",
    "monet-sunrise": "Monet - Impression, Sunrise.jpg",
    "constable-hay-wain": "John Constable The Hay Wain.jpg",
    "titian-early-hand": "Tiziano - Uomo col guanto.jpg",
    "titian-late-hand": "Titian - Pietà - Accademia Venice.jpg",
}

# Fallback direct URLs if API fails
DIRECT = {
    "piero-flagellation": [
        "https://upload.wikimedia.org/wikipedia/commons/4/4e/Flagellation_of_Christ_%28Piero_della_Francesca%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Flagellation_of_Christ_%28Piero_della_Francesca%29.jpg/2000px-Flagellation_of_Christ_%28Piero_della_Francesca%29.jpg",
    ],
    "degas-absinthe": [
        "https://upload.wikimedia.org/wikipedia/commons/2/20/Edgar_Degas_-_In_a_Caf%C3%A9_-_Google_Art_Project.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Edgar_Degas_-_In_a_Caf%C3%A9_-_Google_Art_Project.jpg/2000px-Edgar_Degas_-_In_a_Caf%C3%A9_-_Google_Art_Project.jpg",
    ],
    "leonardo-rocks-london": [
        "https://upload.wikimedia.org/wikipedia/commons/e/eb/Leonardo_da_Vinci_-_Virgin_of_the_Rocks_-_Google_Art_Project.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/42/Leonardo_da_Vinci_-_Vergine_delle_Rocce_%28Londra%29.jpg",
    ],
    "caravaggio-emmaus": [
        "https://upload.wikimedia.org/wikipedia/commons/9/9d/1602-3_Caravaggio%2CSupper_at_Emmaus_National_Gallery%2C_London.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/1602-3_Caravaggio%2CSupper_at_Emmaus_National_Gallery%2C_London.jpg/2000px-1602-3_Caravaggio%2CSupper_at_Emmaus_National_Gallery%2C_London.jpg",
    ],
    "monet-sunrise": [
        "https://upload.wikimedia.org/wikipedia/commons/5/59/Monet_-_Impression%2C_Sunrise.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/5/5c/Claude_Monet%2C_Impression%2C_soleil_levant.jpg",
    ],
    "constable-hay-wain": [
        "https://upload.wikimedia.org/wikipedia/commons/d/d0/John_Constable_The_Hay_Wain.jpg",
    ],
    "reynolds-nelsons": [
        "https://upload.wikimedia.org/wikipedia/commons/c/c5/Sir_Joshua_Reynolds_-_The_Age_of_Innocence_-_Google_Art_Project.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8a/The_Age_of_Innocence_Reynolds.jpg",
    ],
    "titian-early-hand": [
        "https://upload.wikimedia.org/wikipedia/commons/8/86/Tiziano_-_Uomo_col_guanto.jpg",
    ],
    "titian-late-hand": [
        "https://upload.wikimedia.org/wikipedia/commons/c/c5/Titian_-_Piet%C3%A0_-_WGA22755.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/5/52/Titian_-_Piet%C3%A0_-_Google_Art_Project.jpg",
    ],
    "pozzo-sant-ignazio": [
        "https://upload.wikimedia.org/wikipedia/commons/1/15/Sant%27Ignazio_%28Rome%29_-_Ceiling.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/84/PozzoPerspective.jpg",
    ],
}


def is_placeholder(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 150_000:
        return True
    try:
        from PIL import Image

        with Image.open(path) as im:
            w, h = im.size
            if (w, h) == (1600, 1200) and path.stat().st_size < 120_000:
                return True
    except Exception:
        return True
    return False


def commons_thumb_url(filename: str, width: int = 2500) -> str | None:
    api = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": width,
        "format": "json",
    }
    r = requests.get(api, params=params, headers=HEADERS, timeout=60)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo")
        if not info:
            continue
        return info[0].get("thumburl") or info[0].get("url")
    return None


def save_url(url: str, dest: Path) -> bool:
    r = requests.get(url, headers=HEADERS, timeout=120)
    if r.status_code != 200:
        print(f"    HTTP {r.status_code}")
        return False
    data = r.content
    if len(data) < 50_000 or data[:20].lstrip().startswith(b"<"):
        print(f"    bad payload ({len(data)} bytes)")
        return False
    dest.write_bytes(data)
    print(f"    saved {len(data)} bytes")
    return True


def fetch_one(slug: str, dest: Path) -> bool:
    print(f"[fetch] {slug}")
    title = COMMONS_FILES.get(slug)
    if title:
        try:
            url = commons_thumb_url(title)
            print(f"    api -> {url}")
            if url and save_url(url, dest):
                return True
        except Exception as e:
            print(f"    api err: {e}")
        time.sleep(2)
    for url in DIRECT.get(slug, []):
        print(f"    try {url[:90]}...")
        if save_url(url, dest):
            return True
        time.sleep(3)
    return False


def make_tempera_schematic(dest: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    w, h = 1400, 1800
    im = Image.new("RGB", (w, h), (235, 222, 195))
    d = ImageDraw.Draw(im)
    # panel
    d.rectangle([120, 100, 1280, 1700], fill=(210, 185, 145), outline=(90, 60, 40), width=4)
    # garment pure-color shadows (no black)
    d.polygon([(420, 280), (980, 300), (920, 1500), (480, 1480)], fill=(150, 35, 40))
    for i in range(14):
        y = 420 + i * 70
        # pure dark red shadow band
        d.polygon([(500, y), (640, y - 30), (620, y + 50), (480, y + 70)], fill=(145, 28, 34))
        # white-admixed hatch strokes
        for k in range(10):
            x = 660 + k * 22
            col = (220, 170 + k * 3, 170)
            d.line([(x, y - 10), (x + 55, y + 55)], fill=col, width=3)
    # highlight near-white
    d.ellipse([780, 520, 860, 600], fill=(245, 230, 220))
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 36)
        font2 = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 26)
    except OSError:
        font = font2 = ImageFont.load_default()
    d.text((160, 140), "Cennini 三色阶示意", fill=(40, 30, 20), font=font)
    d.text((160, 200), "暗部=纯色  ·  中间=加白  ·  高光=近白排线", fill=(80, 50, 40), font=font2)
    im.save(dest, quality=93)
    print(f"[generated] tempera schematic -> {dest}")


def main() -> None:
    ORIG.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    needed = []
    for slug, meta in manifest.items():
        dest = ORIG / meta["filename"]
        if slug == "tempera-panel-schematic":
            make_tempera_schematic(dest)
            continue
        if is_placeholder(dest):
            needed.append(slug)
        else:
            print(f"[keep] {slug}")

    print(f"\nNeed fetch: {needed}\n")
    failed = []
    for slug in needed:
        dest = ORIG / manifest[slug]["filename"]
        # remove placeholder first
        if dest.exists():
            dest.unlink()
        ok = fetch_one(slug, dest)
        if not ok:
            failed.append(slug)
            print(f"[FAIL] {slug}")
        time.sleep(10)

    # update manifest download urls for successes
    for slug in needed:
        if slug in failed:
            continue
        title = COMMONS_FILES.get(slug)
        if title:
            manifest[slug]["source_page"] = (
                "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_")
            )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nFailed:", failed or "none")


if __name__ == "__main__":
    main()
