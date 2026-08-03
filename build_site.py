#!/usr/bin/env python3
"""Compile notes/*.md into site/index.html and companion pages."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
NOTES = ROOT / "notes"
SITE = ROOT / "site"
SOURCES = ROOT / "references" / "sources.csv"
CROPS = ROOT / "images" / "crops.json"
PLATES_OUT = SITE / "plates.json"

MD_EXTS = ["extra", "sane_lists", "toc", "tables", "fenced_code"]

CHAPTER_ORDER = [
    "ch00-intro.md",
    "ch01-overview.md",
    "ch02-space.md",
    "ch03-chiaroscuro.md",
    "ch04-color.md",
    "ch05-brushwork.md",
    "ch06-hierarchy.md",
    "ch07-institutions.md",
    "ch08-lab.md",
    "ch09-debates.md",
    "ch10-handoff.md",
    "ch11-glossary.md",
    "ch12-index.md",
]

TAG_RE = re.compile(
    r"^>\s*\[([^\]]+)\]\s*(.*)$",
    re.MULTILINE,
)
EMBED_RE = re.compile(r"\[\[(PLATE|CROP|COMPARE|LAYERS|GRID|TIMELINE|TEMP):([^\]]+)\]\]")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


def load_sources() -> dict[str, dict]:
    if not SOURCES.exists():
        return {}
    with SOURCES.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return {row["编号"].strip(): row for row in rows if row.get("编号")}


def tag_class(label: str) -> str:
    if label == "公论":
        return "consensus"
    if label == "本文推断":
        return "inference"
    caution_keys = ("唯一出处", "转述", "回忆录", "孤证", "史料提示")
    if any(k in label for k in caution_keys):
        return "caution"
    return "scholar"


def transform_tags(md_text: str) -> str:
    def repl(m: re.Match) -> str:
        label, rest = m.group(1), m.group(2)
        cls = tag_class(label)
        return f'> <span class="tag {cls}">[{label}]</span> {rest}'

    return TAG_RE.sub(repl, md_text)


def plate_html(slug: str, caption: str, sources: dict) -> str:
    meta = sources.get(slug, {})
    title = caption or meta.get("中文标题", slug)
    img = f"img/{slug}-2000.jpg"
    hi = f"img/{slug}-2000.jpg"
    museum = meta.get("馆藏页URL", "")
    museum_link = f'<a href="{museum}" target="_blank" rel="noopener">馆藏页</a>' if museum else ""
    role = meta.get("在报告中的角色", "")
    return f"""
<figure class="plate" data-loupe id="plate-{slug}">
  <div class="plate-frame"><img src="{img}" data-hires="{hi}" alt="{title}" loading="lazy" /></div>
  <figcaption class="plate-caption">{title}</figcaption>
  <p class="plate-meta">{role} · {museum_link}</p>
</figure>
""".strip()


def crop_html(slug: str, caption: str, sources: dict) -> str:
    meta = sources.get(slug, {})
    title = caption or meta.get("中文标题", slug)
    annotated = f"img/crops/{slug}.jpg"
    clean = f"img/crops/{slug}-clean.jpg"
    coords = meta.get("裁切坐标", "")
    parent = meta.get("母图编号", "")
    return f"""
<figure class="crop" data-crop id="crop-{slug}">
  <div class="widget-toolbar">
    <button type="button" data-annot-toggle class="active">隐藏标注</button>
  </div>
  <div class="crop-frame">
    <img src="{annotated}" data-annotated="{annotated}" data-clean="{clean}" alt="{title}" loading="lazy" />
  </div>
  <figcaption class="crop-caption">{title}</figcaption>
  <p class="plate-meta">母图 <code>{parent}</code> · 原图坐标 <code>{coords}</code></p>
</figure>
""".strip()


def compare_html(args: str) -> str:
    parts = args.split("|")
    a, b = parts[0], parts[1]
    label_a = parts[2] if len(parts) > 2 else a
    label_b = parts[3] if len(parts) > 3 else b
    note = parts[4] if len(parts) > 4 else ""
    return f"""
<div class="compare" data-compare>
  <div class="compare-stage">
    <img src="img/{a}-2000.jpg" alt="{label_a}" />
    <img class="compare-after" src="img/{b}-2000.jpg" alt="{label_b}" />
  </div>
  <input class="compare-range" type="range" min="0" max="100" value="50" aria-label="对比滑块" />
  <div class="compare-labels"><span>{label_a}</span><span>{label_b}</span></div>
  <p class="widget-caption">{note}</p>
</div>
""".strip()


def layers_html(slug: str) -> str:
    layers = [
        ("ground", "底子"),
        ("drawing", "素描稿"),
        ("underpaint", "底色层"),
        ("modeling", "塑形"),
        ("glaze", "罩染"),
        ("lights", "提亮"),
    ]
    imgs = "\n".join(
        f'<img data-layer-img="{key}" src="img/layers/{slug}-{key}.png" alt="{label}" style="opacity:1" />'
        for key, label in layers
    )
    checks = "\n".join(
        f'<label><input type="checkbox" data-layer="{key}" checked /> {label}</label>'
        for key, label in layers
    )
    return f"""
<div class="layers" data-layers id="layers-{slug}">
  <div class="layers-stage">{imgs}</div>
  <div class="layers-controls">{checks}</div>
  <p class="widget-caption">分层剖面：勾选以显隐各层（示意，非该画精确断面）。</p>
</div>
""".strip()


def load_grids() -> dict:
    path = ROOT / "images" / "grids.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def grid_html(slug: str) -> str:
    """Perspective overlay using per-painting VP from images/grids.json."""
    grids = load_grids()
    conf = grids.get(slug, {
        "vp": [0.5, 0.6],
        "horizon_y": 0.6,
        "orthogonals_from": [[0.1, 1.0], [0.3, 1.0], [0.7, 1.0], [0.9, 1.0]],
    })
    vpx, vpy = conf["vp"]
    hy = conf.get("horizon_y", vpy)
    # SVG user space 0-1000
    sx, sy = vpx * 1000, vpy * 1000
    hy_s = hy * 1000
    lines = []
    for i, (fx, fy) in enumerate(conf.get("orthogonals_from", [])):
        opacity = 0.85 if i < 4 else 0.55
        color = "#b0522c" if fy >= 0.5 else "#3e5f80"
        lines.append(
            f'<line x1="{fx*1000:.1f}" y1="{fy*1000:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
            f'stroke="{color}" stroke-width="1.6" opacity="{opacity}" />'
        )
    lines_svg = "\n  ".join(lines)
    svg = f"""
<svg viewBox="0 0 1000 1000" preserveAspectRatio="none" aria-hidden="true">
  <line x1="0" y1="{hy_s:.1f}" x2="1000" y2="{hy_s:.1f}" stroke="#b0522c" stroke-width="2.2" stroke-dasharray="10 7" />
  {lines_svg}
  <circle cx="{sx:.1f}" cy="{sy:.1f}" r="8" fill="#b0522c" />
  <text x="{sx+12:.1f}" y="{sy-10:.1f}" fill="#b0522c" font-size="28" font-family="sans-serif">VP</text>
  <text x="16" y="{hy_s-12:.1f}" fill="#b0522c" font-size="24" font-family="sans-serif">视平线</text>
</svg>
""".strip()
    return f"""
<div class="grid-widget" data-grid id="grid-{slug}">
  <div class="widget-toolbar">
    <button type="button" data-grid-toggle>显示透视网格</button>
  </div>
  <div class="grid-stage">
    <img src="img/{slug}-2000.jpg" alt="透视网格叠加底图" loading="lazy" />
    {svg}
  </div>
  <p class="widget-caption">透视网格叠加：灭点、视平线与正交线按该作几何标定（可开关）。</p>
</div>
""".strip()


def timeline_html() -> str:
    pigments = [
        (1400, "铅白", "#f4f0e6"),
        (1400, "天然群青", "#2a3f8f"),
        (1400, "雌黄", "#e3b13b"),
        (1400, "朱红", "#c23b2a"),
        (1704, "普鲁士蓝", "#003153"),
        (1802, "钴蓝", "#0047ab"),
        (1817, "镉黄", "#fff200"),
        (1826, "人造群青", "#4166f5"),
        (1841, "锡管颜料", "#8a7a62"),
        (1868, "合成茜素", "#b31b1b"),
    ]
    swatches = "\n".join(
        f'<div class="pigment-swatch" data-year="{y}"><div class="pigment-chip" style="background:{c}"></div>{n}<br><span>{y if y > 1400 else "传统"}</span></div>'
        for y, n, c in pigments
    )
    return f"""
<div class="timeline-widget" data-timeline="pigments">
  <p class="pigment-year">1841</p>
  <input type="range" min="1400" max="1906" value="1841" aria-label="调色板年份" />
  <div class="pigment-grid">{swatches}</div>
  <p class="widget-caption">调色板年表：拖动年份，点亮当时可用的代表性颜料（示意，非完整色谱）。</p>
</div>
""".strip()


def temp_html(slug: str) -> str:
    return f"""
<div class="temp-switch" data-temp id="temp-{slug}">
  <div class="widget-toolbar">
    <button type="button" data-temp-mode="color" class="active">原图</button>
    <button type="button" data-temp-mode="gray">明暗读法</button>
    <button type="button" data-temp-mode="temp">冷暖读法</button>
  </div>
  <div class="temp-stage" data-mode="color">
    <img class="base" src="img/{slug}-2000.jpg" alt="明暗与冷暖对照" loading="lazy" />
    <img class="channel temp" src="img/{slug}-temp.jpg" alt="色温映射" loading="lazy" />
  </div>
  <p class="widget-caption">同一局部三通道：原色 / 去色明暗 / 预生成色温映射。</p>
</div>
""".strip()


def expand_embeds(md_text: str, sources: dict) -> str:
    missing = []

    def repl(m: re.Match) -> str:
        kind, payload = m.group(1), m.group(2)
        if kind == "PLATE":
            slug, _, caption = payload.partition("|")
            if slug not in sources:
                missing.append(slug)
            return plate_html(slug, caption, sources)
        if kind == "CROP":
            slug, _, caption = payload.partition("|")
            if slug not in sources:
                missing.append(slug)
            return crop_html(slug, caption, sources)
        if kind == "COMPARE":
            return compare_html(payload)
        if kind == "LAYERS":
            return layers_html(payload)
        if kind == "GRID":
            if payload not in sources:
                missing.append(payload)
            return grid_html(payload)
        if kind == "TIMELINE":
            return timeline_html()
        if kind == "TEMP":
            return temp_html(payload)
        return m.group(0)

    out = EMBED_RE.sub(repl, md_text)
    if missing:
        uniq = sorted(set(missing))
        raise SystemExit(f"Missing slugs in sources.csv: {', '.join(uniq)}")
    return out


def wrap_tables(html: str) -> str:
    return re.sub(
        r"(<table>.*?</table>)",
        r'<div class="table-scroll">\1</div>',
        html,
        flags=re.DOTALL,
    )


def chapter_id(filename: str) -> str:
    return filename.replace(".md", "")


def extract_toc(sections: list[tuple[str, str, str]]) -> str:
    items = []
    for cid, title, _html in sections:
        items.append(f'<li><a href="#{cid}">{title}</a></li>')
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def first_h1(md_text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def strip_first_h1(md_text: str) -> str:
    return re.sub(r"^#\s+.+\n+", "", md_text, count=1, flags=re.MULTILINE)


def build_main(sources: dict) -> tuple[str, str, list[dict]]:
    sections = []
    plate_index = []
    for name in CHAPTER_ORDER:
        path = NOTES / name
        if not path.exists():
            print(f"skip missing {name}", file=sys.stderr)
            continue
        raw = path.read_text(encoding="utf-8")
        title = first_h1(raw, name)
        body = strip_first_h1(raw)
        body = transform_tags(body)
        body = expand_embeds(body, sources)
        html = markdown.markdown(body, extensions=MD_EXTS)
        html = wrap_tables(html)
        # Promote reading materials section class
        html = html.replace("<h3>延伸材料</h3>", '<h3>延伸材料</h3><div class="reading-list">', 1)
        if '<div class="reading-list">' in html:
            # close before next h2/h3 if any — simplest: append close at end of chapter
            html += "</div>"
        cid = chapter_id(name)
        if name == "ch00-intro.md":
            section = f'<section class="hero" id="{cid}"><h1>{title}</h1>{html}</section>'
        else:
            section = f'<section class="chapter" id="{cid}"><h2>{title}</h2>{html}</section>'
        sections.append((cid, title, section))

    toc = extract_toc(sections)
    content = "\n\n".join(s[2] for s in sections)
    for slug, row in sources.items():
        plate_index.append(
            {
                "id": slug,
                "type": row.get("类型"),
                "title": row.get("中文标题"),
                "artist": row.get("艺术家"),
                "year": row.get("年代"),
                "museum_url": row.get("馆藏页URL"),
                "coords": row.get("裁切坐标"),
                "parent": row.get("母图编号"),
            }
        )
    return toc, content, plate_index


def render_template(toc: str, content: str, title: str, description: str, subpage: bool = False) -> str:
    tpl = (SITE / "template.html").read_text(encoding="utf-8")
    html = (
        tpl.replace("{{TITLE}}", title)
        .replace("{{DESCRIPTION}}", description)
        .replace("{{TOC}}", toc)
        .replace("{{CONTENT}}", content)
    )
    if subpage:
        html = html.replace("<body>", '<body class="subpage">')
    return html


def build_subpages(sources: dict) -> None:
    # Glossary
    gloss_path = NOTES / "ch11-glossary.md"
    if gloss_path.exists():
        raw = gloss_path.read_text(encoding="utf-8")
        title = first_h1(raw, "术语表")
        body = markdown.markdown(strip_first_h1(transform_tags(raw)), extensions=MD_EXTS)
        toc = "<ul><li><a href=\"index.html\">返回正文</a></li></ul>"
        html = render_template(toc, f"<section class='chapter'><h2>{title}</h2>{body}</section>", f"{title} · 通往塞尚之前", "术语表", True)
        (SITE / "glossary.html").write_text(html, encoding="utf-8")

    # Plates index from CSV
    rows = []
    for slug, row in sources.items():
        rows.append(
            f"<tr><td><code>{slug}</code></td><td>{row.get('类型','')}</td>"
            f"<td>{row.get('中文标题','')}</td><td>{row.get('艺术家','')}</td>"
            f"<td>{row.get('裁切坐标','')}</td><td>{row.get('母图编号','')}</td>"
            f"<td><a href=\"{row.get('馆藏页URL','')}\" target=\"_blank\" rel=\"noopener\">馆藏</a></td></tr>"
        )
    table = (
        "<section class='chapter'><h2>图版索引</h2>"
        "<p>与 <code>references/sources.csv</code> / <code>plates.json</code> 同步生成。</p>"
        "<div class='table-scroll'><table><thead><tr>"
        "<th>编号</th><th>类型</th><th>标题</th><th>艺术家</th><th>裁切坐标</th><th>母图</th><th>馆藏</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div></section>"
    )
    toc = "<ul><li><a href=\"index.html\">返回正文</a></li></ul>"
    (SITE / "plates.html").write_text(
        render_template(toc, table, "图版索引 · 通往塞尚之前", "图版索引", True),
        encoding="utf-8",
    )

    # Reading map
    reading_md = NOTES / "reading-map.md"
    if reading_md.exists():
        raw = reading_md.read_text(encoding="utf-8")
        title = first_h1(raw, "阅读路线图")
        body = markdown.markdown(strip_first_h1(raw), extensions=MD_EXTS)
        html = render_template(
            toc,
            f"<section class='chapter'><h2>{title}</h2><div class='reading-list'>{body}</div></section>",
            f"{title} · 通往塞尚之前",
            "阅读路线图",
            True,
        )
        (SITE / "reading.html").write_text(html, encoding="utf-8")


def main() -> None:
    sources = load_sources()
    toc, content, plate_index = build_main(sources)
    PLATES_OUT.write_text(json.dumps(plate_index, ensure_ascii=False, indent=2), encoding="utf-8")
    html = render_template(
        toc,
        content,
        "通往塞尚之前：西方绘画技法与公认原则的谱系",
        "以技法与成文规范追溯西方绘画公认原则（约 1390–1906）",
    )
    (SITE / "index.html").write_text(html, encoding="utf-8")
    build_subpages(sources)
    print(f"Built site/index.html with {len(plate_index)} plate records.")


if __name__ == "__main__":
    main()
