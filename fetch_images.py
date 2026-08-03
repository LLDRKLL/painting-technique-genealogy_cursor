#!/usr/bin/env python3
"""Download public-domain / open originals listed in images/_manifest.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
ORIG = ROOT / "images" / "originals"
MANIFEST = ROOT / "images" / "_manifest.json"

HEADERS = {
    "User-Agent": "painting-technique-genealogy/1.0 (research; local build)"
}


def main() -> None:
    ORIG.mkdir(parents=True, exist_ok=True)
    if not MANIFEST.exists():
        sys.exit("Missing images/_manifest.json")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for slug, meta in manifest.items():
        url = meta.get("download_url")
        filename = meta["filename"]
        dest = ORIG / filename
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"[have] {slug}")
            continue
        if not url:
            print(f"[skip] {slug}: no download_url")
            continue
        print(f"[get] {slug} <- {url[:80]}...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=120)
            r.raise_for_status()
            dest.write_bytes(r.content)
            print(f"      saved {dest} ({len(r.content)} bytes)")
        except Exception as e:
            print(f"[fail] {slug}: {e}")
    print("Fetch finished.")


if __name__ == "__main__":
    main()
