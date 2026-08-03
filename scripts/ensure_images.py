#!/usr/bin/env python3
"""Retry missing downloads slowly; synthesize labeled stand-ins if needed."""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "images" / "originals"
MANIFEST = ROOT / "images" / "_manifest.json"

# Corrected / alternate Commons FilePath URLs
ALT = {
    "piero-flagellation": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Piero%2C_flagellazione.jpg",
    "pozzo-sant-ignazio": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Andrea_Pozzo_-_Allegory_of_the_Jesuits%27_Missionary_Work_-_WGA18376.jpg",
    "degas-absinthe": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Edgar_Germain_Hilaire_Degas_012.jpg",
    "leonardo-rocks-london": "https://upload.wikimedia.org/wikipedia/commons/4/42/Leonardo_da_Vinci_Virgin_of_the_Rocks_%28National_Gallery_London%29.jpg",
    "caravaggio-emmaus": "https://upload.wikimedia.org/wikipedia/commons/9/9d/Caravaggio_-_Cena_in_Emmaus.jpg",
    "rembrandt-night-watch": "https://upload.wikimedia.org/wikipedia/commons/5/5c/The_Nightwatch_by_Rembrandt_-_Rijksmuseum.jpg",
    "reynolds-nelsons": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Joshua_Reynolds_-_The_Age_of_Innocence_-_Google_Art_Project.jpg",
    "monet-sunrise": "https://upload.wikimedia.org/wikipedia/commons/5/59/Claude_Monet%2C_Impression%2C_soleil_levant.jpg",
    "cezanne-apples": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Paul_C%C3%A9zanne_185.jpg",
    "botticelli-venus": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg",
    "manet-olympia": "https://upload.wikimedia.org/wikipedia/commons/5/5c/Edouard_Manet_-_Olympia_-_Google_Art_Project_3.jpg",
    "delacroix-liberty": "https://upload.wikimedia.org/wikipedia/commons/5/5d/Eug%C3%A8ne_Delacroix_-_Le_28_Juillet._La_Libert%C3%A9_guidant_le_peuple.jpg",
    "van-gogh-bedroom": "https://upload.wikimedia.org/wikipedia/commons/7/76/Vincent_van_Gogh_-_De_slaapkamer_-_Google_Art_Project.jpg",
    "seurat-grande-jatte": "https://upload.wikimedia.org/wikipedia/commons/6/67/Georges_Seurat_-_A_Sunday_on_La_Grande_Jatte_--_1884_-_Google_Art_Project.jpg",
    "constable-hay-wain": "https://upload.wikimedia.org/wikipedia/commons/d/d0/John_Constable_The_Hay_Wain.jpg",
    "titian-early-hand": "https://upload.wikimedia.org/wikipedia/commons/8/86/Tiziano_-_Uomo_col_guanto.jpg",
    "titian-late-hand": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Titian_-_Piet%C3%A0_-_WGA22755.jpg",
}

HEADERS = {
    "User-Agent": "PaintingTechniqueGenealogyBot/1.0 (research site build; contact: local)",
    "Accept": "image/*,*/*",
}


def font(size: int):
    for c in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\arial.ttf"]:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def placeholder(slug: str, title: str, dest: Path) -> None:
    w, h = 1600, 1200
    im = Image.new("RGB", (w, h), (34, 31, 27))
    d = ImageDraw.Draw(im)
    # atmospheric gradients per chapter feel
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(34 + 40 * t), int(31 + 20 * t), int(27 + 10 * t)))
    d.rectangle([80, 80, w - 80, h - 80], outline=(176, 82, 44), width=4)
    f1, f2 = font(42), font(28)
    d.text((120, 160), title[:60], fill=(247, 243, 234), font=f1)
    d.text((120, 230), f"stand-in · {slug}", fill=(176, 82, 44), font=f2)
    d.text((120, 300), "Replace via fetch_images.py when network allows", fill=(180, 170, 150), font=f2)
    # fake composition blocks
    d.ellipse([500, 400, 1100, 1000], outline=(62, 95, 128), width=3)
    d.line([(200, 900), (1400, 900)], fill=(109, 122, 78), width=2)
    im.save(dest, quality=90)


def ok_file(p: Path) -> bool:
    return p.exists() and p.stat().st_size > 2000


def download(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=90, stream=True)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}")
            return False
        data = r.content
        if len(data) < 2000 or data[:100].lstrip().startswith(b"<"):
            print("  not an image")
            return False
        dest.write_bytes(data)
        print(f"  saved {len(data)}")
        return True
    except Exception as e:
        print(f"  err {e}")
        return False


def main() -> None:
    ORIG.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    titles = {k: v.get("note", k) for k, v in manifest.items()}

    for slug, meta in manifest.items():
        dest = ORIG / meta["filename"]
        if ok_file(dest):
            print(f"[have] {slug}")
            continue
        url = ALT.get(slug) or meta.get("download_url")
        print(f"[get] {slug}")
        if url and download(url, dest):
            time.sleep(8)
            continue
        time.sleep(3)
        # second try with Special:FilePath if ALT failed
        if slug in ALT and meta.get("download_url"):
            print("  retry original")
            if download(meta["download_url"], dest):
                time.sleep(8)
                continue
        print(f"[placeholder] {slug}")
        placeholder(slug, titles.get(slug, slug), dest)
        time.sleep(1)

    # tempera schematic always generated in bootstrap; ensure exists
    schem = ORIG / "tempera-panel-schematic.jpg"
    if not ok_file(schem):
        placeholder("tempera-panel-schematic", "Cennini tempera schematic", schem)
    print("ensure_images done")


if __name__ == "__main__":
    main()
