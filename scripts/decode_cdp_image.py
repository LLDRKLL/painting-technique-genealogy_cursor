#!/usr/bin/env python3
"""Decode a CDP Runtime.evaluate JSON response containing {n,b64} into an image file."""
import json
import base64
import sys
from pathlib import Path

src = Path(sys.argv[1])
dest = Path(sys.argv[2])
data = json.loads(src.read_text(encoding="utf-8"))
# handle wrapped result
val = data
if "result" in data and isinstance(data["result"], dict):
    val = data["result"].get("value") or data["result"].get("result", {}).get("value")
    if isinstance(data["result"].get("result"), dict) and "value" in data["result"]["result"]:
        val = data["result"]["result"]["value"]
# also try nested forms
if not isinstance(val, dict) or "b64" not in val:
    # search recursively
    def find(o):
        if isinstance(o, dict):
            if "b64" in o:
                return o
            for v in o.values():
                r = find(v)
                if r:
                    return r
        if isinstance(o, list):
            for v in o:
                r = find(v)
                if r:
                    return r
        return None
    val = find(data)
if not val or "b64" not in val:
    raise SystemExit(f"no b64 in {src}")
raw = base64.b64decode(val["b64"])
dest.write_bytes(raw)
print(f"wrote {dest} ({len(raw)} bytes, claimed {val.get('n')})")
