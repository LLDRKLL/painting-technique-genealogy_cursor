#!/usr/bin/env python3
"""Generate chapter markdown, research notes, sources.csv, crops, and manifest."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
RESEARCH = ROOT / "research"
REFS = ROOT / "references"
IMAGES = ROOT / "images"

# Wikimedia Commons FilePath URLs (public domain / CC works used for research education)
# Prefer reasonably large JPEG derivatives.
WIKI = "https://commons.wikimedia.org/wiki/Special:FilePath/"

MANIFEST = {
    "giotto-lamentation": {
        "filename": "giotto-lamentation.jpg",
        "download_url": WIKI + "Giotto_-_Scrovegni_-_-36-_-_Lamentation_(The_Mourning_of_Christ)_adj.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Giotto_-_Scrovegni_-_-36-_-_Lamentation_(The_Mourning_of_Christ)_adj.jpg",
        "note": "Arena Chapel Lamentation",
    },
    "masaccio-trinity": {
        "filename": "masaccio-trinity.jpg",
        "download_url": WIKI + "Masaccio,_trinit%C3%A0.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Masaccio,_trinit%C3%A0.jpg",
        "note": "Masaccio Trinity",
    },
    "piero-flagellation": {
        "filename": "piero-flagellation.jpg",
        "download_url": WIKI + "Piero,_flagellazione.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Piero,_flagellazione.jpg",
        "note": "Piero Flagellation",
    },
    "raphael-school-of-athens": {
        "filename": "raphael-school-of-athens.jpg",
        "download_url": WIKI + "Raphael_School_of_Athens.jpg?width=2500",
        "source_page": "https://commons.wikimedia.org/wiki/File:Raphael_School_of_Athens.jpg",
        "note": "Raphael School of Athens",
    },
    "van-eyck-arnolfini": {
        "filename": "van-eyck-arnolfini.jpg",
        "download_url": WIKI + "Van_Eyck_-_Arnolfini_Portrait.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Van_Eyck_-_Arnolfini_Portrait.jpg",
        "note": "Arnolfini Portrait",
    },
    "holbein-ambassadors": {
        "filename": "holbein-ambassadors.jpg",
        "download_url": WIKI + "Hans_Holbein_the_Younger_-_The_Ambassadors_-_Google_Art_Project.jpg?width=2500",
        "source_page": "https://commons.wikimedia.org/wiki/File:Hans_Holbein_the_Younger_-_The_Ambassadors_-_Google_Art_Project.jpg",
        "note": "Holbein Ambassadors",
    },
    "pozzo-sant-ignazio": {
        "filename": "pozzo-sant-ignazio.jpg",
        "download_url": WIKI + "Andrea_Pozzo_-_Apoteosi_di_sant%27Ignazio_-_Google_Art_Project.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Andrea_Pozzo_-_Apoteosi_di_sant%27Ignazio_-_Google_Art_Project.jpg",
        "note": "Pozzo Sant'Ignazio",
    },
    "velazquez-meninas": {
        "filename": "velazquez-meninas.jpg",
        "download_url": WIKI + "Las_Meninas,_by_Diego_Vel%C3%A1zquez,_from_Prado_in_Google_Earth.jpg?width=2500",
        "source_page": "https://commons.wikimedia.org/wiki/File:Las_Meninas,_by_Diego_Vel%C3%A1zquez,_from_Prado_in_Google_Earth.jpg",
        "note": "Las Meninas",
    },
    "vermeer-milkmaid": {
        "filename": "vermeer-milkmaid.jpg",
        "download_url": WIKI + "Johannes_Vermeer_-_Het_melkmeisje_-_Google_Art_Project.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Johannes_Vermeer_-_Het_melkmeisje_-_Google_Art_Project.jpg",
        "note": "Vermeer Milkmaid",
    },
    "degas-absinthe": {
        "filename": "degas-absinthe.jpg",
        "download_url": WIKI + "Edgar_Germain_Hilaire_Degas_012.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Edgar_Germain_Hilaire_Degas_012.jpg",
        "note": "Degas L'Absinthe",
    },
    "leonardo-rocks-london": {
        "filename": "leonardo-rocks-london.jpg",
        "download_url": WIKI + "Leonardo_da_Vinci_-_Virgin_of_the_Rocks_(National_Gallery_London).jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Leonardo_da_Vinci_-_Virgin_of_the_Rocks_(National_Gallery_London).jpg",
        "note": "Virgin of the Rocks NG",
    },
    "titian-bacchus-ariadne": {
        "filename": "titian-bacchus-ariadne.jpg",
        "download_url": WIKI + "Titian_-_Bacchus_and_Ariadne_-_Google_Art_Project.jpg?width=2500",
        "source_page": "https://commons.wikimedia.org/wiki/File:Titian_-_Bacchus_and_Ariadne_-_Google_Art_Project.jpg",
        "note": "Titian Bacchus and Ariadne",
    },
    "caravaggio-emmaus": {
        "filename": "caravaggio-emmaus.jpg",
        "download_url": WIKI + "Caravaggio_-_Cena_in_Emmaus.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Caravaggio_-_Cena_in_Emmaus.jpg",
        "note": "Caravaggio Emmaus NG",
    },
    "rembrandt-night-watch": {
        "filename": "rembrandt-night-watch.jpg",
        "download_url": WIKI + "The_Nightwatch_by_Rembrandt_-_Rijksmuseum.jpg?width=2500",
        "source_page": "https://commons.wikimedia.org/wiki/File:The_Nightwatch_by_Rembrandt_-_Rijksmuseum.jpg",
        "note": "Night Watch",
    },
    "reynolds-nelsons": {
        "filename": "reynolds-health-of-the-nation.jpg",
        "download_url": WIKI + "Joshua_Reynolds_-_The_Age_of_Innocence_-_Google_Art_Project.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Joshua_Reynolds_-_The_Age_of_Innocence_-_Google_Art_Project.jpg",
        "note": "Reynolds Age of Innocence (bitumen discussion proxy)",
    },
    "monet-sunrise": {
        "filename": "monet-sunrise.jpg",
        "download_url": WIKI + "Claude_Monet,_Impression,_soleil_levant.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Claude_Monet,_Impression,_soleil_levant.jpg",
        "note": "Impression Sunrise",
    },
    "cezanne-apples": {
        "filename": "cezanne-apples.jpg",
        "download_url": WIKI + "Paul_C%C3%A9zanne_-_Still_Life_with_Apples_-_Google_Art_Project.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Paul_C%C3%A9zanne_-_Still_Life_with_Apples_-_Google_Art_Project.jpg",
        "note": "Cezanne apples",
    },
    "botticelli-venus": {
        "filename": "botticelli-venus.jpg",
        "download_url": WIKI + "Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg?width=2500",
        "source_page": "https://commons.wikimedia.org/wiki/File:Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg",
        "note": "Birth of Venus",
    },
    "manet-olympia": {
        "filename": "manet-olympia.jpg",
        "download_url": WIKI + "Edouard_Manet_-_Olympia_-_Google_Art_Project.jpg?width=2500",
        "source_page": "https://commons.wikimedia.org/wiki/File:Edouard_Manet_-_Olympia_-_Google_Art_Project.jpg",
        "note": "Manet Olympia",
    },
    "turner-slave-ship": {
        "filename": "turner-slave-ship.jpg",
        "download_url": WIKI + "Slave-ship.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Slave-ship.jpg",
        "note": "Turner Slave Ship",
    },
    "delacroix-liberty": {
        "filename": "delacroix-liberty.jpg",
        "download_url": WIKI + "Eug%C3%A8ne_Delacroix_-_Le_28_Juillet._La_Libert%C3%A9_guidant_le_peuple.jpg?width=2500",
        "source_page": "https://commons.wikimedia.org/wiki/File:Eug%C3%A8ne_Delacroix_-_Le_28_Juillet._La_Libert%C3%A9_guidant_le_peuple.jpg",
        "note": "Delacroix Liberty",
    },
    "van-gogh-bedroom": {
        "filename": "van-gogh-bedroom.jpg",
        "download_url": WIKI + "Vincent_van_Gogh_-_De_slaapkamer_-_Google_Art_Project.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:Vincent_van_Gogh_-_De_slaapkamer_-_Google_Art_Project.jpg",
        "note": "Van Gogh Bedroom (Amsterdam version; Chicago XRF discussed in text)",
    },
    "seurat-grande-jatte": {
        "filename": "seurat-grande-jatte.jpg",
        "download_url": WIKI + "Georges_Seurat_-_A_Sunday_on_La_Grande_Jatte_--_1884_-_Google_Art_Project.jpg?width=2500",
        "source_page": "https://commons.wikimedia.org/wiki/File:Georges_Seurat_-_A_Sunday_on_La_Grande_Jatte_--_1884_-_Google_Art_Project.jpg",
        "note": "Seurat Grande Jatte",
    },
    "constable-hay-wain": {
        "filename": "constable-hay-wain.jpg",
        "download_url": WIKI + "John_Constable_The_Hay_Wain.jpg?width=2000",
        "source_page": "https://commons.wikimedia.org/wiki/File:John_Constable_The_Hay_Wain.jpg",
        "note": "Constable Hay Wain",
    },
    "titian-early-hand": {
        "filename": "titian-early-hand.jpg",
        "download_url": WIKI + "Titian_-_Man_with_a_Glove_-_Google_Art_Project.jpg?width=1600",
        "source_page": "https://commons.wikimedia.org/wiki/File:Titian_-_Man_with_a_Glove_-_Google_Art_Project.jpg",
        "note": "Titian early hand proxy",
    },
    "titian-late-hand": {
        "filename": "titian-late-hand.jpg",
        "download_url": WIKI + "Titian_-_Piet%C3%A0_-_WGA22755.jpg?width=1600",
        "source_page": "https://commons.wikimedia.org/wiki/File:Titian_-_Piet%C3%A0_-_WGA22755.jpg",
        "note": "Titian late brushwork proxy",
    },
    "tempera-panel-schematic": {
        "filename": "tempera-panel-schematic.jpg",
        "download_url": "",
        "source_page": "generated",
        "note": "Generated Cennini tempera schematic",
        "generated": True,
    },
}

CROPS = {
    "masaccio-trinity-coffers": {
        "source": "masaccio-trinity",
        "box": [280, 40, 900, 700],
        "note": "藻井方格收缩序列",
        "annotations": [
            {"type": "box", "rect": [120, 40, 200, 140], "label": "近景格"},
            {"type": "arrow", "from": [200, 220], "to": [480, 420], "label": "收缩方向"},
            {"type": "line", "points": [[0, 520], [900, 520]], "label": "视平线附近"},
        ],
    },
    "raphael-orthogonals": {
        "source": "raphael-school-of-athens",
        "box": [600, 400, 1100, 800],
        "note": "地砖与拱肋正交线",
        "annotations": [
            {"type": "arrow", "from": [100, 700], "to": [550, 250], "label": "地砖缝"},
            {"type": "line", "points": [[0, 280], [1100, 280]], "label": "视平线"},
        ],
    },
    "arnolfini-mirror": {
        "source": "van-eyck-arnolfini",
        "box": [420, 380, 520, 520],
        "note": "凸面镜第二空间",
        "annotations": [
            {"type": "box", "rect": [140, 140, 240, 240], "label": "镜面空间"},
        ],
    },
    "holbein-skull": {
        "source": "holbein-ambassadors",
        "box": [400, 900, 1400, 500],
        "note": "前景变形骷髅",
        "annotations": [
            {"type": "arrow", "from": [200, 250], "to": [700, 280], "label": "anamorphosis"},
        ],
    },
    "leonardo-sfumato-jaw": {
        "source": "leonardo-rocks-london",
        "box": [520, 420, 700, 600],
        "note": "下颌与手背 sfumato",
        "annotations": [
            {"type": "box", "rect": [180, 80, 220, 160], "label": "过渡带"},
            {"type": "arrow", "from": [120, 400], "to": [300, 350], "label": "几乎无笔痕"},
        ],
    },
    "caravaggio-hand-edge": {
        "source": "caravaggio-emmaus",
        "box": [900, 500, 700, 550],
        "note": "手部亮直落黑",
        "annotations": [
            {"type": "arrow", "from": [120, 200], "to": [320, 260], "label": "缺中间调"},
        ],
    },
    "rembrandt-armor": {
        "source": "rembrandt-night-watch",
        "box": [900, 400, 800, 700],
        "note": "铠甲高光堆塑",
        "annotations": [
            {"type": "box", "rect": [220, 180, 200, 160], "label": "厚涂高光"},
        ],
    },
    "monet-shadow-color": {
        "source": "monet-sunrise",
        "box": [200, 300, 900, 600],
        "note": "影中无黑",
        "annotations": [
            {"type": "box", "rect": [300, 200, 260, 180], "label": "冷色影"},
        ],
    },
    "botticelli-hatching": {
        "source": "botticelli-venus",
        "box": [900, 500, 700, 700],
        "note": "蛋彩排线",
        "annotations": [
            {"type": "arrow", "from": [100, 200], "to": [280, 320], "label": "排线方向"},
        ],
    },
    "meninas-mirror": {
        "source": "velazquez-meninas",
        "box": [900, 300, 600, 500],
        "note": "镜中王室",
        "annotations": [
            {"type": "box", "rect": [180, 120, 220, 180], "label": "镜面"},
        ],
    },
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.lstrip("\n"), encoding="utf-8")


def make_sources_and_crops():
    fields = [
        "编号", "类型", "中文标题", "原文标题", "艺术家", "年代", "尺寸", "媒材", "收藏机构",
        "藏品编号", "馆藏页URL", "在报告中的角色", "图像来源页", "原图直链",
        "本地文件", "本地原图分辨率", "裁切坐标", "母图编号", "机构技术影像URL", "版权状态",
    ]
    rows = []
    meta_titles = {
        "giotto-lamentation": ("乔托《哀悼基督》", "Lamentation", "Giotto", "c.1305", "湿壁画", "Scrovegni Chapel"),
        "masaccio-trinity": ("马萨乔《三位一体》", "Holy Trinity", "Masaccio", "1427", "湿壁画", "Santa Maria Novella"),
        "piero-flagellation": ("皮耶罗《鞭刑》", "Flagellation of Christ", "Piero della Francesca", "c.1455", "板面油画", "Galleria Nazionale delle Marche"),
        "raphael-school-of-athens": ("拉斐尔《雅典学院》", "School of Athens", "Raphael", "1509–1511", "湿壁画", "Vatican Museums"),
        "van-eyck-arnolfini": ("扬·凡·艾克《阿尔诺芬尼夫妇》", "Arnolfini Portrait", "Jan van Eyck", "1434", "板面油画", "National Gallery, London"),
        "holbein-ambassadors": ("霍尔拜因《大使们》", "The Ambassadors", "Hans Holbein the Younger", "1533", "板面油画", "National Gallery, London"),
        "pozzo-sant-ignazio": ("波佐《圣依纳爵的荣耀》", "Apotheosis of St Ignatius", "Andrea Pozzo", "1691–1694", "天顶画", "Sant'Ignazio, Rome"),
        "velazquez-meninas": ("委拉斯开兹《宫娥》", "Las Meninas", "Diego Velázquez", "1656", "布面油画", "Museo del Prado"),
        "vermeer-milkmaid": ("维米尔《倒牛奶的女仆》", "The Milkmaid", "Johannes Vermeer", "c.1660", "布面油画", "Rijksmuseum"),
        "degas-absinthe": ("德加《苦艾酒》", "L'Absinthe", "Edgar Degas", "1875–1876", "布面油画", "Musée d'Orsay"),
        "leonardo-rocks-london": ("达·芬奇《岩间圣母》（伦敦）", "Virgin of the Rocks", "Leonardo da Vinci", "c.1491–1508", "板面油画", "National Gallery, London"),
        "titian-bacchus-ariadne": ("提香《巴克斯与阿里阿德涅》", "Bacchus and Ariadne", "Titian", "1520–1523", "布面油画", "National Gallery, London"),
        "caravaggio-emmaus": ("卡拉瓦乔《以马忤斯的晚餐》", "Supper at Emmaus", "Caravaggio", "1601", "布面油画", "National Gallery, London"),
        "rembrandt-night-watch": ("伦勃朗《夜巡》", "The Night Watch", "Rembrandt", "1642", "布面油画", "Rijksmuseum"),
        "reynolds-nelsons": ("雷诺兹《纯真年代》", "The Age of Innocence", "Joshua Reynolds", "c.1788", "布面油画", "Tate"),
        "monet-sunrise": ("莫奈《印象·日出》", "Impression, soleil levant", "Claude Monet", "1872", "布面油画", "Musée Marmottan Monet"),
        "cezanne-apples": ("塞尚《苹果静物》", "Still Life with Apples", "Paul Cézanne", "c.1893–1894", "布面油画", "J. Paul Getty Museum"),
        "botticelli-venus": ("波提切利《维纳斯的诞生》", "Birth of Venus", "Sandro Botticelli", "c.1485", "布面蛋彩", "Uffizi"),
        "manet-olympia": ("马奈《奥林匹亚》", "Olympia", "Édouard Manet", "1863", "布面油画", "Musée d'Orsay"),
        "turner-slave-ship": ("透纳《奴隶船》", "The Slave Ship", "J. M. W. Turner", "1840", "布面油画", "MFA Boston"),
        "delacroix-liberty": ("德拉克洛瓦《自由引导人民》", "Liberty Leading the People", "Eugène Delacroix", "1830", "布面油画", "Louvre"),
        "van-gogh-bedroom": ("梵高《卧室》", "The Bedroom", "Vincent van Gogh", "1888", "布面油画", "Van Gogh Museum / Art Institute of Chicago (讨论)"),
        "seurat-grande-jatte": ("修拉《大碗岛的星期日下午》", "A Sunday on La Grande Jatte", "Georges Seurat", "1884–1886", "布面油画", "Art Institute of Chicago"),
        "constable-hay-wain": ("康斯特勃《干草车》", "The Hay Wain", "John Constable", "1821", "布面油画", "National Gallery, London"),
        "titian-early-hand": ("提香《持手套的男子》（早期笔触对照）", "Man with a Glove", "Titian", "c.1520", "布面油画", "Louvre"),
        "titian-late-hand": ("提香《哀悼基督》（晚期笔触对照）", "Pietà", "Titian", "1575–1576", "布面油画", "Gallerie dell'Accademia"),
        "tempera-panel-schematic": ("十四世纪蛋彩板（Cennini 系统示意图）", "Tempera schematic", "schematic", "c.1390 system", "示意图", "generated"),
    }
    for slug, m in MANIFEST.items():
        zh, en, artist, year, medium, museum = meta_titles[slug]
        rows.append({
            "编号": slug,
            "类型": "示意图" if m.get("generated") else "全图",
            "中文标题": zh,
            "原文标题": en,
            "艺术家": artist,
            "年代": year,
            "尺寸": "",
            "媒材": medium,
            "收藏机构": museum,
            "藏品编号": "",
            "馆藏页URL": m.get("source_page", ""),
            "在报告中的角色": "主范例全图",
            "图像来源页": m.get("source_page", ""),
            "原图直链": m.get("download_url", ""),
            "本地文件": f"images/originals/{m['filename']}",
            "本地原图分辨率": "",
            "裁切坐标": "",
            "母图编号": "",
            "机构技术影像URL": "",
            "版权状态": "public-domain-or-cc / generated",
        })
    crop_titles = {
        "masaccio-trinity-coffers": "马萨乔《三位一体》藻井收缩",
        "raphael-orthogonals": "拉斐尔《雅典学院》正交线",
        "arnolfini-mirror": "阿尔诺芬尼凸面镜",
        "holbein-skull": "大使们变形骷髅",
        "leonardo-sfumato-jaw": "岩间圣母 sfumato 过渡",
        "caravaggio-hand-edge": "以马忤斯手部边缘",
        "rembrandt-armor": "夜巡铠甲高光",
        "monet-shadow-color": "印象日出影色",
        "botticelli-hatching": "维纳斯蛋彩排线",
        "meninas-mirror": "宫娥镜面",
    }
    for slug, spec in CROPS.items():
        box = spec["box"]
        rows.append({
            "编号": slug,
            "类型": "细节裁切",
            "中文标题": crop_titles[slug],
            "原文标题": spec["note"],
            "艺术家": "",
            "年代": "",
            "尺寸": "",
            "媒材": "",
            "收藏机构": "",
            "藏品编号": "",
            "馆藏页URL": "",
            "在报告中的角色": "细节精读",
            "图像来源页": "",
            "原图直链": "",
            "本地文件": f"site/img/crops/{slug}.jpg",
            "本地原图分辨率": "",
            "裁切坐标": f"{box[0]},{box[1]},{box[2]},{box[3]}",
            "母图编号": spec["source"],
            "机构技术影像URL": "",
            "版权状态": "derived-from-parent",
        })
    REFS.mkdir(parents=True, exist_ok=True)
    with (REFS / "sources.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    IMAGES.mkdir(parents=True, exist_ok=True)
    (IMAGES / "_manifest.json").write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")
    (IMAGES / "crops.json").write_text(json.dumps(CROPS, ensure_ascii=False, indent=2), encoding="utf-8")
    (IMAGES / "originals").mkdir(exist_ok=True)
    (IMAGES / "originals" / ".gitkeep").write_text("", encoding="utf-8")


def chapters():
    write(NOTES / "ch00-intro.md", """
# 通往塞尚之前

<p class="lede">以技法与成文规范为唯一切口，追问西方绘画的「公认原则」从哪里来、如何被强制执行、又在什么条件下松动，最终汇向 1860–1906 年。</p>

<p class="meta">时间跨度约 1390–1906 · 主线：意大利—荷兰—西班牙—法国 · 塞尚绘画逻辑研究前传</p>

## 为什么锁定技法层

> [公论] 颜料分析、X 光／红外／断面与元素分布图、画论原文，均可指向可核查出处；「现代主义兴起」通论则不可避免大量二手转述。

> [公论] 「公认原则」在技法层是写下来的：Cennini（约 1390）、Alberti《论绘画》（1435）、Leonardo 笔记、法兰西学院教条、Chevreul（1839）、Charles Blanc（1867）——「公认」可以指着页码说。

纯技法解释不了「为什么这些规则有约束力」，故另设制度史一章。整体对比不以通史重写，而以「对照实验室」给出跨四百年并列图版。

## 阅读约定

- **四类标记**：公论 / 学者观点（署名署年） / 本文推断 / 史料提示
- **来源优先级**：馆藏官方页 > 机构技术公报 > 学者专著论文 > 展览图录 > 教学性百科
- 画论引用给版本与页码，并区分原文与后人转述
- 每个技术概念先给一句话功能定义

建议先读第 1 章总览，再以第 3 章「明暗与体积」作为样章体验完整七段式模板与交互。
""")

    write(NOTES / "ch01-overview.md", """
# 第 1 章　五套系统总览

五条并行技术线贯穿全稿：**空间** · **明暗与体积** · **色彩与材料** · **笔触与表面** · **题材等级与构图规范**。

| 系统 | 核心问题 | 成文节点（示例） | 松动信号 |
| --- | --- | --- | --- |
| 空间 | 如何把三维关系写成可教规则 | Alberti 1435 | 多视点、摄影裁切、变形画 |
| 明暗与体积 | 如何让形体「鼓起来」 | Cennini 三色阶；威尼斯暗底 | 冷暖轴取代明暗轴 |
| 色彩与材料 | 调色板允许画什么 | 颜料年表；Chevreul / Blanc | 合成颜料、锡管、光学混色误读 |
| 笔触与表面 | 手的痕迹是否应被看见 | 间接画法教条 | alla prima、构成性笔触 |
| 题材等级 | 什么值得画、如何排座位 | 学院画种等级 | 静物／风景翻身 |

<div class="system-tracks" data-tracks>
  <div class="track-toggle widget-toolbar">
    <button type="button" data-track-btn="space">空间</button>
    <button type="button" data-track-btn="light">明暗</button>
    <button type="button" data-track-btn="color">色彩</button>
    <button type="button" data-track-btn="touch">笔触</button>
    <button type="button" data-track-btn="genre">题材</button>
  </div>
  <div class="track on" data-track="space" style="--accent:#3e5f80">
    <div class="track-name">空间</div>
    <div class="track-bar"><div class="track-fill" style="--w:100%"></div><div class="track-nodes"><span>1390</span><span>Alberti</span><span>Pozzo</span><span>Degas</span><span>1906</span></div></div>
  </div>
  <div class="track on" data-track="light" style="--accent:#b0522c">
    <div class="track-name">明暗</div>
    <div class="track-bar"><div class="track-fill" style="--w:100%"></div><div class="track-nodes"><span>Cennini</span><span>sfumato</span><span>tenebrism</span><span>莫奈影</span><span>塞尚</span></div></div>
  </div>
  <div class="track on" data-track="color" style="--accent:#6d7a4e">
    <div class="track-name">色彩</div>
    <div class="track-bar"><div class="track-fill" style="--w:100%"></div><div class="track-nodes"><span>群青</span><span>1704</span><span>锡管1841</span><span>Chevreul</span><span>修拉</span></div></div>
  </div>
  <div class="track on" data-track="touch" style="--accent:#8c6028">
    <div class="track-name">笔触</div>
    <div class="track-bar"><div class="track-fill" style="--w:100%"></div><div class="track-nodes"><span>蛋彩</span><span>间接</span><span>alla prima</span><span>马奈</span><span>塞尚</span></div></div>
  </div>
  <div class="track on" data-track="genre" style="--accent:#5a4a3a">
    <div class="track-name">题材</div>
    <div class="track-bar"><div class="track-fill" style="--w:100%"></div><div class="track-nodes"><span>历史画</span><span>沙龙</span><span>风景</span><span>静物</span><span>苹果</span></div></div>
  </div>
</div>

> [公论] 五套系统并非彼此替代的「进步阶梯」，而是可并行、可冲突的约束集合；后文每一章回答同一问题：规则如何被写下、如何操作、何时失效。
""")

    write(NOTES / "ch02-space.md", """
# 第 2 章　空间：从平面到几何，再到几何的崩解

## 这套系统要解决什么问题

如何让平面上的形状让人相信「有前后、有远近、有可站立的地面」——并把这套信念写成可教、可检查的规则。

**关键词功能定义**

- **视平线**：与观者眼睛同高的水平线，决定「仰视／平视／俯视」。
- **灭点**：平行线在画面上汇聚的点。
- **正交线**：指向灭点、用来「铺深度」的线（地砖缝、梁柱、屋顶）。
- **大气透视**：远景因空气散射而变淡、变蓝、对比变弱。
- **变形画（anamorphosis）**：只有从特定角度／站点才还原的图像。

## 规则是怎么被写下来的

> [公论] Leon Battista Alberti《论绘画》（Della pittura, 1435）把线透视写成可操作程序：以视点、截平面与视觉金字塔组织画面。英译本可参 Cecil Grayson 编注本； receding squares 与 pavement 方法是教学核心。

> [学者观点] Martin Kemp（1990）《The Science of Art》从光学史贯通透视工具与绘画实践，强调透视既是数学也是工作室装置史。

> [史料提示] 乔托年代尚未有 Alberti 式成文透视；其深度多靠叠压、地面坡度与人物尺度——不可倒读为「不会透视」。

## 操作步骤拆解

典型单点透视施工顺序（教学示意）：

1. 定视平线（常约在画幅高度 2/5–1/2，视题材而定）
2. 定主灭点（常落在重要人物眼高附近）
3. 铺地网格：正交线汇入灭点，横向分割用距离点或经验分割
4. 竖立建筑／家具的竖直边（保持铅直）
5. 人物脚位锚定在网格交点上
6. 远处减弱对比（大气透视）

[[LAYERS:venetian-buildup]]

## 范例逐幅精读

[[PLATE:giotto-lamentation|乔托《哀悼基督》，约 1305，湿壁画，阿雷纳礼拜堂]]

> [公论] 透视成文之前，深度常靠身体叠压、斜坡地面与哀恸人群的尺度差来「挤」出空间。

[[PLATE:masaccio-trinity|马萨乔《三位一体》，1427，湿壁画，圣母大殿]]

[[CROP:masaccio-trinity-coffers|藻井方格的收缩序列。注意每一格的纵深压缩比]]

[[GRID:masaccio-trinity]]

> [公论] 拱顶方格藻井提供教科书级收缩序列；灭点大致落在观者站立时的眼高，柱础与礼拜堂真实台阶的视觉接续强化「可进入」。

[[PLATE:piero-flagellation|皮耶罗《鞭刑》，约 1455]]

> [学者观点] 对《鞭刑》前景／后景两套尺度，学界长期争论其象征与空间逻辑；由铺地网格反推平面图是常见技术史练习（参 Kemp 及相关测绘图）。

[[PLATE:raphael-school-of-athens|拉斐尔《雅典学院》，1509–1511]]

[[CROP:raphael-orthogonals|地砖缝、拱肋与脚位的锚定]]

[[GRID:raphael-school-of-athens]]

[[PLATE:van-eyck-arnolfini|扬·凡·艾克《阿尔诺芬尼夫妇》，1434，伦敦国家美术馆]]

[[CROP:arnolfini-mirror|凸面镜内第二套空间、镜框微缩景]]

> [公论] 北方绘画常呈现「经验透视」：多灭点并存、对局部真实细节极度敏感；凸面镜同时是光学物与叙事装置。

[[PLATE:holbein-ambassadors|霍尔拜因《大使们》，1533]]

[[CROP:holbein-skull|前景变形骷髅：侧向站点才还原]]

[[PLATE:pozzo-sant-ignazio|波佐《圣依纳爵的荣耀》天顶画，1690s]]

> [公论] 天顶幻觉依赖单一站点；偏离站点后柱式与建筑衔接会出现可见畸变——这是透视作为「强制观看位置」的极端案例。

[[PLATE:velazquez-meninas|委拉斯开兹《宫娥》，1656]]

[[CROP:meninas-mirror|镜面与画外空间的悖论]]

[[PLATE:vermeer-milkmaid|维米尔《倒牛奶的女仆》，约 1660]]

> [学者观点] Hockney–Falco 论争把维米尔高光珠化、边缘失焦等读作光学器械痕迹；主流技术史多主张更复杂的多因素解释（见第 9 章）。

[[PLATE:degas-absinthe|德加《苦艾酒》，1875–1876]]

> [公论] 德加的桌面裁切与非中心视点，把「完整舞台盒」式构图让位给摄影式截取。

## 什么时候开始失效

当画家不再承诺单一站点的可还原世界：多视点并置、故意裁切、平面化色块、或把透视暴露为修辞而非真理时，几何空间的强制力下降。

## 众声

> [学者观点] Svetlana Alpers（1983）《The Art of Describing》主张北方「描述」传统不必以意大利中心透视叙事为唯一标尺。

> [学者观点] E. H. Gombrich 图式—修正叙事常被后来社会史与技术史批评为过度线性。

## 延伸材料

**入门**

- **Hockney–Falco 光学器械说及史学界反驳** — 训练对单因解释的警惕。难度：★★☆☆☆。获取：免费
  https://en.wikipedia.org/wiki/Hockney%E2%80%93Falco_thesis

**进阶**

- **The Science of Art**（Martin Kemp, 1990）— 光学史贯通透视技术的标准参考。难度：★★★★☆。获取：需购买／图书馆

**原始文献**

- **《论绘画》**（Leon Battista Alberti, 1435）— 线透视第一次被写成可操作规则。难度：★★★☆☆。获取：多种英译本，部分免费

**技术检测**

- **National Gallery Technical Bulletin** — 含凡·艾克等专文，全卷免费。难度：★★★★☆。获取：免费开放
  https://www.nationalgallery.org.uk/research/publications/technical-bulletin
""")

    # Chapter 3 — flagship sample
    write(NOTES / "ch03-chiaroscuro.md", """
# 第 3 章　明暗与体积：从纯色加白，到冷暖代替明暗

## 这套系统要解决什么问题

如何在平面上让物体显得有体积——鼓起来、转过去、沉进暗里——并规定「暗部该有多暗、亮部该怎么亮」。

**关键词功能定义**

- **三色阶法**：同一固有色取纯色作最暗，再两级加白，最后用近白提亮（Cennini 系统）。
- **verdaccio**：绿灰底层，用来垫肤色，使上层肉色更稳。
- **sfumato**：以极薄、多层次过渡消去轮廓线，使明暗如烟。
- **tenebrism**：强烈单光源，大面积暗底，中间调被压缩。
- **罩染（glaze）**：透明色叠在已干下层上，改色不立刻改形。
- **冷暖轴**：用偏冷／偏暖的并置暗示转折，而非只靠黑白梯度。

## 规则是怎么被写下来的

> [公论] Cennino Cennini《艺人手册》（Il libro dell'arte，约 1390）记录作坊操作：以纯色为暗部，逐级加白塑形。Daniel V. Thompson 英译（Dover 等版本）是常用教学文本；引用时应标注章节（论肤色与衣褶塑形诸章）而非只凭转述。

> [公论] 达·芬奇笔记反复强调阴影的连续性与空气感；后人「sfumato」一词是对这种薄层过渡实践的概括，不完全是他自用的严格术语。

> [学者观点] National Gallery《Art in the Making》系列（Bomford 等）以断面、红外与清洗档案把「看不见的工序」变成可核对证据链，是本项目方法范本。

> [史料提示] 沥青（bitumen）在十八世纪英国肖像中的使用与后期龟裂／变暗，见 National Gallery Technical Bulletin 相关雷诺兹研究；不可把「所有龟裂」都归因于沥青。

## 操作步骤拆解

间接画法常见层级（可与下图示意对照）：

1. **底子** — 石膏地／油画底，决定吸油与色彩倾向  
2. **素描稿** — 轮廓与大明暗  
3. **底色层** — 单色或有限色垫形（含 verdaccio／暗底）  
4. **塑形** — 不透明色建立体积  
5. **罩染** — 透明色修正色相与深度  
6. **提亮** — 厚一点的亮部／高光收口  

[[LAYERS:venetian-buildup]]

## 范例逐幅精读

[[PLATE:tempera-panel-schematic|十四世纪蛋彩板：Cennini 系统示意图（可见排线与纯色暗部）]]

> [公论] 在蛋彩系统中，暗部常保持较高纯度，体积主要靠加白阶梯与排线方向建成，而不是靠大面积「染黑」。

[[PLATE:leonardo-rocks-london|达·芬奇《岩间圣母》（伦敦国家美术馆）]]

[[CROP:leonardo-sfumato-jaw|手背与下颌：过渡处几乎无笔痕]]

[[TEMP:leonardo-rocks-london]]

> [学者观点] 伦敦版《岩间圣母》的红外与分层研究（National Gallery）显示反复调整与薄层过渡；阅读细节时应对照机构技术影像，而非只凭成品照片想象「一次画成」。

[[PLATE:titian-bacchus-ariadne|提香《巴克斯与阿里阿德涅》，伦敦国家美术馆]]

> [学者观点] National Gallery Technical Bulletin 第 34 卷（提香 1540 年前技法专号）提供分层与颜料证据，可作威尼斯系统逐层拆解入口。

[[PLATE:caravaggio-emmaus|卡拉瓦乔《以马忤斯的晚餐》，1601]]

[[CROP:caravaggio-hand-edge|手部边缘由亮直落黑，中间调被吃掉]]

> [公论] tenebrism 不是「会画影子」而已，而是主动删掉中间调，让形体以光斑方式跳进暗场。

[[PLATE:rembrandt-night-watch|伦勃朗《夜巡》，1642，Rijksmuseum]]

[[CROP:rembrandt-armor|铠甲高光的堆塑；暗部透明褐层需对照高分辨率与研究页]]

> [公论] Rijksmuseum Operation Night Watch 提供超高分辨率图像与研究入口，可在铠甲高光处观察厚涂的物理性；元素分布图回答的是材料分布，不等于直接读出「意图」。

[[PLATE:reynolds-nelsons|雷诺兹《纯真年代》（沥青问题的材料史入口）]]

> [学者观点] 雷诺兹对实验性媒介的兴趣与部分作品后期状况，是「技法失败可被材料证据指认」的教学案例；细节以 NG Technical Bulletin 第 35 卷等报告为准。

[[PLATE:monet-sunrise|莫奈《印象·日出》，1872]]

[[CROP:monet-shadow-color|阴影由蓝紫等冷色构成，而非直黑]]

[[TEMP:monet-sunrise]]

> [公论] 印象派语境中，「影子里没有黑」是对学院棕黑阴影习惯的实践反抗；具体作品仍需看调色与保存状况。

[[PLATE:cezanne-apples|塞尚《苹果静物》]]

> [本文推断] 在塞尚静物中，冷暖并置常常承担过去由明暗渐变承担的结构功能——体积变成色彩关系问题（详见交接章与后续塞尚研究）。

## 什么时候开始失效

当体积不再主要依赖「暗—亮阶梯」，而改由色相对置、笔触方向或平面色块支撑时，Cennini—学院明暗轴的强制力松动。沥青等材料事故也从反面证明：规则的物理载体会背叛意图。

## 众声

> [学者观点] Marcia B. Hall 等学者强调文艺复兴色彩／底层选择与观念意图联动，不宜把明暗仅写成光学进步史。

> [学者观点] 技术影像（红外、X 光、宏观 XRF）显示工序，但「看不见的修改」如何翻译成艺术意图，始终需要历史语境约束。

## 延伸材料

**入门**

- **Rijksmuseum Operation Night Watch 研究页 / 超高像素《夜巡》** — 可自行放大验证厚涂与表面。难度：★★☆☆☆。获取：免费开放
  https://www.rijksmuseum.nl/en/press/press-releases/rijksmuseum-publishes-717-gigapixel-photograph-of-the-night-watch

**进阶**

- **Art in the Making 系列**（David Bomford 等，National Gallery）— 逐幅拆解技法层次。难度：★★★☆☆。获取：需购买／图书馆

**原始文献**

- **《艺人手册》**（Cennino Cennini，约 1390；Daniel V. Thompson 英译）— 三色阶法出处。难度：★★☆☆☆。获取：英译本易得

**技术检测**

- **NG Technical Bulletin 第 34 卷（提香）与第 35 卷** — 分层技法与雷诺兹材料问题。难度：★★★★☆。获取：免费开放
  https://www.nationalgallery.org.uk/research/publications/technical-bulletin
""")

    write(NOTES / "ch04-color.md", """
# 第 4 章　色彩与材料：调色板决定了什么可以被画出来

## 这套系统要解决什么问题

画家手上的颜料、媒介与价格，决定了哪些颜色「付得起、稳得住、画得开」——色彩史首先是材料限制史。

**关键词功能定义**

- **固有色**：物体「本身的颜色」优先于条件色。
- **透明色／覆盖色**：前者适合罩染改色，后者适合塑形盖住下层。
- **光学混色**：小色点在视距上混合，而非调色板上事先调匀。
- **同时对比**：相邻色互相改变对方外观（Chevreul 核心论题）。

## 规则是怎么被写下来的

> [公论] 合成颜料年表提供硬锚点：普鲁士蓝 1704、钴蓝 1802、镉 1817、人造群青 1826、锡管 1841、茜素合成 1868。

> [学者观点] Philip Ball《Bright Earth》把化学史与绘画史接通，是可读性最好的材料史入门之一。

> [公论] Michel Eugène Chevreul《同时对比律》（1839）是十九世纪色彩理论源头；画家接受史常呈现「看图版、略正文」的误读路径。

> [公论] Charles Blanc《素描艺术语法》（1867）自 1870s 进入法国教学管道，是理论传到 Seurat、Signac、Gauguin、van Gogh 一代的实际通道之一。

## 操作步骤拆解

材料约束下的决策顺序（示意）：

1. 确认底子与媒介（蛋彩／油／混合）
2. 按价格与稳定性分配「昂贵色」的位置（如天然群青）
3. 不透明色塑形 → 透明色罩染
4. 十九世纪起：管装颜料改变户外写生的可携带调色板
5. 新理论（同时对比、互补）进入并被简化为工作室口诀

[[TIMELINE:pigments]]

## 范例逐幅精读

[[PLATE:van-eyck-arnolfini|凡·艾克：昂贵蓝色的位置政治（对照圣母像传统）]]

> [公论] 天然群青（lapis）昂贵，常被保留给圣像体系中的关键服饰；价格进入构图伦理学。

[[PLATE:titian-bacchus-ariadne|提香：高饱和色块与矿物色颗粒感]]

[[PLATE:vermeer-milkmaid|维米尔：群青使用策略（表层／底层需对照断面文献）]]

> [学者观点] 对维米尔蓝色层位的技术研究显示「贵色」不一定只出现在最终可见层；阅读需回到机构报告。

[[PLATE:turner-slave-ship|透纳：铬黄等现代色的冒险与保存风险]]

[[PLATE:delacroix-liberty|德拉克洛瓦：补色并置的早期实践入口]]

[[PLATE:van-gogh-bedroom|梵高《卧室》：材料改变「我们看见的历史」]]

> [学者观点] 芝加哥艺术学院对《阿尔勒的卧室》所作 macro-XRF 等研究，复原墙面原为偏紫而非今所见蓝色——材料退化改写了大众记忆中的「梵高蓝房间」。

[[PLATE:seurat-grande-jatte|修拉：点彩与 Chevreul／Blanc 接受史]]

> [本文推断] 修拉式互补并置，更多是对教学化色彩口诀的操作，而非对 Chevreul 正文的严格实验复现。

[[PLATE:cezanne-apples|塞尚：色块关系承担结构]]

## 什么时候开始失效

当合成颜料与锡管让「稀缺」不再主导，色彩理论又被简化为可背诵公式时，旧调色板等级松动；同时，误读的理论也可能长出新教条。

## 众声

> [学者观点] 对 Seurat 与科学色彩的关系，艺术史写作经历了「科学英雄」到「选择性误读」的修正。

> [史料提示] 颜料商品广告与厂家配方书是重要一手材料，但常夸张稳定性。

## 延伸材料

**入门**

- **Bright Earth / Philip Ball 颜料史长文** — 化学史与绘画史接口。难度：★★☆☆☆。获取：书需购买，长文免费
  https://publicdomainreview.org/essay/primary-sources/

**进阶**

- **Tate：十九世纪英国油画材料研究** — 锡管、颜料商与实践。难度：★★★☆☆。获取：免费开放
  https://www.tate.org.uk/research/tate-papers/02/the-materials-used-by-british-oil-painters-in-the-nineteenth-century

**原始文献**

- **《同时对比律》**（Chevreul, 1839）— 重点读接受史。难度：★★★★☆。获取：法文原版免费
  https://books.openedition.org/mnhn/637
- **《素描艺术语法》**（Charles Blanc, 1867）— 教学管道文本。难度：★★★☆☆。获取：Gallica 等

**技术检测**

- **Jo Kirby / Marika Spring 等 NG 颜料专文** — 单颜料鉴定方法。难度：★★★★☆。获取：免费开放
""")

    write(NOTES / "ch05-brushwork.md", """
# 第 5 章　笔触、表面与媒介：可见的手如何取得合法性

## 这套系统要解决什么问题

笔触该不该被看见？表面应该光滑如镜，还是保留手的时间痕迹？媒介（蛋彩／油）决定了「手」能留下什么。

**关键词功能定义**

- **排线**：以平行或交叉短线塑形（蛋彩常见）。
- **间接画法**：多层等待干燥的工序链。
- **alla prima**：在颜料未干时尽量一次画完。
- **厚涂（impasto）**：颜料堆起，具有真实起伏。
- **构成性笔触**：笔触不只描述物表，还组织画面结构。

## 规则是怎么被写下来的

> [公论] 学院话语长期偏向「隐藏笔触」的完成度理想；素描与罩染程序服务于光滑的色阶过渡。

> [学者观点] Jill Dunkerton 等《Giotto to Dürer》以馆藏技术知识重述早期意北方面层与笔法差异。

> [公论] 十九世纪风景与现代生活绘画中，「未完成感」逐渐获得审美合法性（康斯特勃草稿性、马奈平涂省略）。

## 操作步骤拆解

[[LAYERS:venetian-buildup]]

从间接到直接的光谱：蛋彩排线 → 油性透明堆叠 → 湿接湿 → 厚涂／刮刀 → 构成性短笔触。

## 范例逐幅精读

[[PLATE:botticelli-venus|波提切利《维纳斯的诞生》]]

[[CROP:botticelli-hatching|蛋彩细排线：放大后可数方向]]

[[PLATE:van-eyck-arnolfini|凡·艾克：罩染透明堆叠的表面平静]]

[[COMPARE:titian-early-hand|titian-late-hand|约 1520|1570s|同一传统内，笔触由紧到松]]

[[PLATE:velazquez-meninas|委拉斯开兹：远看成形、近看笔尖起落]]

[[PLATE:rembrandt-night-watch|伦勃朗：厚涂的物理高度]]

[[PLATE:constable-hay-wain|康斯特勃：户外感与笔触活力]]

[[PLATE:manet-olympia|马奈：平涂与中间调省略]]

[[PLATE:cezanne-apples|塞尚：短促同向笔触既描述又组织]]

## 什么时候开始失效

当「完成」不再等于「抹平」，笔触从缺陷变为内容；规则的合法性从作坊／学院转移到展览与批评话语。

## 众声

> [学者观点] 对委拉斯开兹「一笔成形」的赞美传统，需与近距表面研究对照，避免把修辞当工序。

## 延伸材料

**入门**

- **Art in the Making: Rembrandt**（National Gallery）— 厚涂与透明层证据。难度：★★★☆☆。获取：需购买／图书馆

**进阶**

- **Color and Meaning**（Marcia B. Hall）— 技法选择与观念意图。难度：★★★★☆。获取：需购买／图书馆

**原始文献**

- **Giotto to Dürer**（Jill Dunkerton 等）— 早期技法通览。难度：★★★☆☆。获取：图书馆

**技术检测**

- **Getty 保护研究出版物** — 媒介、油、树脂分析，多为免费 PDF。难度：★★★★☆。获取：免费开放
""")

    write(NOTES / "ch06-hierarchy.md", """
# 第 6 章　题材等级与构图规范

## 问题

在学院体系中，不是所有题材都有同等尊严。历史画居于顶端，静物长期垫底——直到十九世纪下半叶，苹果也可以承担结构实验。

## 规则如何被写下

> [公论] 法兰西学院与沙龙实践强化画种等级：历史画 > 肖像 > 风俗 > 风景 > 静物。评审标准绑定题材、素描功夫、理想化身体与可读叙事。

> [学者观点] 风景与静物的「翻身」与艺术市场、独立展览机制同步，不只是审美口味突变。

## 范例

[[PLATE:cezanne-apples|塞尚选择苹果：低题材、高结构]]

[[PLATE:manet-olympia|《奥林匹亚》：沙龙叙事冲突的表面与题材政治]]

## 失效条件

当展览渠道不再唯一依赖沙龙，题材等级的强制力下降；静物成为现代绘画的实验室。

## 众声

> [本文推断] 「塞尚为什么选苹果」在技法谱系中的位置是：题材约束松动后，笔触、冷暖与形色关系得以成为主战场。

## 延伸材料

**入门**

- 沙龙与独立展通识条目（博物馆教育页）。难度：★★☆☆☆。获取：免费

**进阶**

- 关于法国学院制度与画种等级的社会史专著。难度：★★★★☆。获取：图书馆

**原始文献**

- 十九世纪沙龙评论选辑。难度：★★★☆☆。获取：Gallica 等

**技术检测**

- 与静物保存相关的变色案例（如铬黄）。难度：★★★☆☆。获取：机构开放论文
""")

    write(NOTES / "ch07-institutions.md", """
# 第 7 章　制度：规则如何被强制执行

## 问题

技法规则若只写在书里，约束力有限。工坊契约、学院摹本、沙龙评审与画商—独立展，才是「公认」得以强制执行的制度轨道。

## 机制

1. **工坊**：分工、学徒年限、配方保密与交付标准  
2. **学院**：素描石膏／人体、历史画课题、摹本等级  
3. **沙龙**：可见性垄断与趣味攻击的公开舞台  
4. **独立展与画商**：另建观众与价格形成机制  

> [公论] 没有制度章，技法史会变成英雄发明史；有了制度章，才能解释为何某些「不正确」的画法长期画不出去。

## 延伸材料

**入门** — 博物馆「学院与沙龙」教育文案。难度：★★☆☆☆。获取：免费  
**进阶** — 艺术市场与画商研究。难度：★★★★☆。获取：图书馆  
**原始文献** — 学院章程、沙龙 livret。难度：★★★☆☆。获取：档案／Gallica  
**技术检测** — 学徒复制与原作的材料对照案例。难度：★★★★☆。获取：技术公报  
""")

    write(NOTES / "ch08-lab.md", """
# 第 8 章　对照实验室

每套系统给一组跨世纪同题并列：同一母题或同一部位，在不同规则体系下的解法。

## 空间：可进入的盒子 → 被裁切的片段

[[COMPARE:masaccio-trinity|degas-absinthe|1427 站点空间|1876 摄影式裁切|从强制站点到故意不完整]]

## 明暗：阶梯塑形 → 冷暖结构

[[COMPARE:leonardo-rocks-london|cezanne-apples|薄层烟雾过渡|色块冷暖结构|体积语言的替换]]

## 笔触：应被隐藏 → 即内容

[[COMPARE:botticelli-venus|manet-olympia|排线融入形体|平涂与可见笔触|手的合法性]]

> [公论] 对照实验室不提供「进步排名」，只提供可并置的证据，供读者自己看规则如何改口。
""")

    write(NOTES / "ch09-debates.md", """
# 第 9 章　尚有争议

## Hockney–Falco 光学器械说

> [学者观点] David Hockney 与 Charles Falco 主张文艺复兴以来部分写实效果依赖光学装置；反对者指出透视几何、训练有素的眼手与工作室传统足以解释多数证据，且「光学痕迹」常被过度解读。

## 北方「描述」vs 意大利透视中心

> [学者观点] Svetlana Alpers（1983）挑战以意大利叙事—透视为唯一中心的叙事框架。

## 图式—修正 vs 社会史

> [学者观点] Gombrich 式进步叙事提供强认知模型，但可能低估行会、市场、宗教功能与材料限制。

## 技术检测的解释限度

> [公论] 元素分布 ≠ 意图。XRF 地图说明「何处有何元素」，不能单独为「画家想表达什么」签字。
""")

    write(NOTES / "ch10-handoff.md", """
# 第 10 章　交接：汇向 1860–1906

五条技术线在塞尚时代的状态（接入后续塞尚研究）：

| 系统 | 1860–1906 状态 | 交给塞尚研究的问题 |
| --- | --- | --- |
| 空间 | 单点透视不再是唯一真理；摄影裁切已合法化 | 如何用多注视与形色重构深度 |
| 明暗 | 冷暖／色彩开始替代棕黑阴影 | 体积如何由色差建成 |
| 色彩 | 合成颜料与理论口诀并行 | 调色板如何服务结构而非描摹 |
| 笔触 | 可见笔触已获现代合法性 | 短笔触如何既描述又构成 |
| 题材 | 静物／风景可承载最大雄心 | 为何苹果足够 |

[[PLATE:cezanne-apples|交接图像：低题材上的高约束实验]]
""")

    write(NOTES / "ch11-glossary.md", """
# 术语表

每条先给功能定义。完整 50+ 条；正文首次出现处应链到本页锚点。

<div class="glossary-grid">

<div class="glossary-item" id="term-horizon"><h3>视平线</h3><p>与观者眼睛同高的水平参照，决定仰视／平视／俯视。</p></div>
<div class="glossary-item" id="term-vanishing-point"><h3>灭点</h3><p>平行线在画面上汇聚之点。</p></div>
<div class="glossary-item" id="term-orthogonal"><h3>正交线</h3><p>导向灭点、铺设深度的线段（地砖缝、梁柱等）。</p></div>
<div class="glossary-item" id="term-distance-point"><h3>距离点</h3><p>用于确定网格横向分割的辅助灭点法。</p></div>
<div class="glossary-item" id="term-aerial"><h3>大气透视</h3><p>远景因空气介质而淡化、偏蓝、对比下降。</p></div>
<div class="glossary-item" id="term-anamorphosis"><h3>变形画</h3><p>需特定站点或镜子才还原的透视畸变图像。</p></div>
<div class="glossary-item" id="term-three-tone"><h3>三色阶法</h3><p>Cennini：纯色最暗，逐级加白，近白提亮。</p></div>
<div class="glossary-item" id="term-verdaccio"><h3>Verdaccio</h3><p>绿灰底层，常用于垫肤色。</p></div>
<div class="glossary-item" id="term-sfumato"><h3>Sfumato</h3><p>薄层烟雾般的明暗过渡，弱化硬轮廓。</p></div>
<div class="glossary-item" id="term-tenebrism"><h3>Tenebrism</h3><p>强单光源与大面积暗场，中间调被压缩。</p></div>
<div class="glossary-item" id="term-glaze"><h3>罩染</h3><p>透明色叠上层，改色相／深度。</p></div>
<div class="glossary-item" id="term-underpainting"><h3>底色层</h3><p>最终色之前用于垫形与色调的涂层。</p></div>
<div class="glossary-item" id="term-impasto"><h3>厚涂</h3><p>颜料堆起形成可触起伏。</p></div>
<div class="glossary-item" id="term-alla-prima"><h3>Alla prima</h3><p>趁湿尽量一次完成的直接画法。</p></div>
<div class="glossary-item" id="term-hatching"><h3>排线</h3><p>以线族塑形的笔法，蛋彩尤常见。</p></div>
<div class="glossary-item" id="term-local-color"><h3>固有色</h3><p>物象被认定的「本色」，相对条件色而言。</p></div>
<div class="glossary-item" id="term-optical-mix"><h3>光学混色</h3><p>色点在视网膜／视距上混合。</p></div>
<div class="glossary-item" id="term-simultaneous-contrast"><h3>同时对比</h3><p>相邻色互相改变外观的知觉效应。</p></div>
<div class="glossary-item" id="term-ultramarine"><h3>天然群青</h3><p>由青金石制的昂贵蓝色颜料。</p></div>
<div class="glossary-item" id="term-prussian-blue"><h3>普鲁士蓝</h3><p>1704 前后出现的重要合成蓝。</p></div>
<div class="glossary-item" id="term-cobalt-blue"><h3>钴蓝</h3><p>十九世纪初合成蓝，稳定而偏冷。</p></div>
<div class="glossary-item" id="term-cadmium"><h3>镉黄／镉红</h3><p>十九世纪亮色家族，有毒性与保存议题。</p></div>
<div class="glossary-item" id="term-french-ultramarine"><h3>人造群青</h3><p>1826 年前后工业化的群青替代。</p></div>
<div class="glossary-item" id="term-tube"><h3>锡管颜料</h3><p>1841 前后普及，改变户外写生物流。</p></div>
<div class="glossary-item" id="term-alizarin"><h3>合成茜素</h3><p>1868 合成，冲击天然茜草红淀。</p></div>
<div class="glossary-item" id="term-bitumen"><h3>沥青</h3><p>有机棕色料，易导致后期皱裂变暗。</p></div>
<div class="glossary-item" id="term-tempera"><h3>蛋彩</h3><p>以蛋黄等为媒介的水性快干技法。</p></div>
<div class="glossary-item" id="term-oil"><h3>油画媒介</h3><p>干性油使开放时间与透明堆叠成为可能。</p></div>
<div class="glossary-item" id="term-chiaroscuro"><h3>明暗法</h3><p>以光暗组织体积与戏剧性的体系。</p></div>
<div class="glossary-item" id="term-genre-hierarchy"><h3>画种等级</h3><p>学院对题材尊卑的排序制度。</p></div>
<div class="glossary-item" id="term-salon"><h3>沙龙</h3><p>官方／主导性展览评审机制。</p></div>
<div class="glossary-item" id="term-academy"><h3>学院</h3><p>以素描与历史画为中心的教学—评审机构。</p></div>
<div class="glossary-item" id="term-workshop"><h3>工坊</h3><p>学徒制生产单位，配方与分工所在。</p></div>
<div class="glossary-item" id="term-cartoon"><h3>底稿／卡通</h3><p>放大转绘用的全尺寸素描稿。</p></div>
<div class="glossary-item" id="term-infrared"><h3>红外成像</h3><p>揭示底层素描与改动的技术影像。</p></div>
<div class="glossary-item" id="term-xray"><h3>X 光成像</h3><p>显示含重金属颜料的结构与隐藏层。</p></div>
<div class="glossary-item" id="term-xrf"><h3>宏观 XRF</h3><p>扫描元素分布以推断颜料种类。</p></div>
<div class="glossary-item" id="term-cross-section"><h3>断面显微</h3><p>取样观察层序与颗粒。</p></div>
<div class="glossary-item" id="term-pentimento"><h3>修改痕迹</h3><p>画家改动后仍可被技术或肉眼察觉的遗迹。</p></div>
<div class="glossary-item" id="term-scumble"><h3>薄擦</h3><p>不透明或半透明色轻擦以激活下层。</p></div>
<div class="glossary-item" id="term-ground"><h3>底子</h3><p>支撑物上的准备层，影响吸油与色彩。</p></div>
<div class="glossary-item" id="term-imprimatura"><h3>有色底</h3><p>单色薄染底，统一画心色调。</p></div>
<div class="glossary-item" id="term-complementary"><h3>补色</h3><p>色轮上相对、并置时对比最强的一对。</p></div>
<div class="glossary-item" id="term-cool-warm"><h3>冷暖</h3><p>色相的温度倾向，可替代部分明暗功能。</p></div>
<div class="glossary-item" id="term-facture"><h3>表面肌理／制作感</h3><p>由笔触与媒介形成的可见制作痕迹。</p></div>
<div class="glossary-item" id="term-finish"><h3>完成度</h3><p>学院语境中常等同于光滑与细节充足。</p></div>
<div class="glossary-item" id="term-plein-air"><h3>户外写生</h3><p>在母题现场绘制，受锡管与便携画箱支撑。</p></div>
<div class="glossary-item" id="term-pointillism"><h3>点彩</h3><p>以点状笔触并置色，追求光学混合效果。</p></div>
<div class="glossary-item" id="term-camera-obscura"><h3>暗箱</h3><p>光学投影装置，相关于写实辅助工具争论。</p></div>
<div class="glossary-item" id="term-orthogonals-grid"><h3>铺地网格</h3><p>用透视网格标定人物脚位与家具深度。</p></div>
<div class="glossary-item" id="term-foreshortening"><h3>缩短法</h3><p>对伸向观者方向的形体做透视压缩。</p></div>
<div class="glossary-item" id="term-modeling"><h3>塑形</h3><p>以明暗或色彩使平面形获得体积感。</p></div>
<div class="glossary-item" id="term-highlight"><h3>高光</h3><p>最亮的镜面反射点，常最后提。 </p></div>
<div class="glossary-item" id="term-middle-tone"><h3>中间调</h3><p>介于亮部与暗部之间的过渡值。</p></div>
<div class="glossary-item" id="term-lake-pigment"><h3>色淀颜料</h3><p>染料沉淀于底质而成的颜料，常偏透明。</p></div>
<div class="glossary-item" id="term-support"><h3>支撑物</h3><p>木板、画布等承载绘画的物理基底。</p></div>
<div class="glossary-item" id="term-varnish"><h3>光油</h3><p>表面保护层，影响饱和度与老化外观。</p></div>
<div class="glossary-item" id="term-cleaning"><h3>清洗</h3><p>去除老化光油／污垢的保护处理，可能改变外观。</p></div>
<div class="glossary-item" id="term-copy-practice"><h3>摹本制度</h3><p>通过复制大师作品学习规范的学院机制。</p></div>
<div class="glossary-item" id="term-dealer"><h3>画商机制</h3><p>以画廊与藏家网络形成价格与声誉的通道。</p></div>

</div>
""")

    write(NOTES / "ch12-index.md", """
# 图版索引与参考文献

完整可排序表见子页 [图版索引](plates.html)。延伸材料按四档汇总见 [阅读路线图](reading.html)。

## 关键机构资源

- National Gallery Technical Bulletin（全卷开放）
- Rijksmuseum Operation Night Watch
- Tate Papers（十九世纪英国材料）
- Getty Conservation Institute 出版物
- Art Institute of Chicago 关于梵高《卧室》的技术研究报道

## 引用规范（本站）

正文事实性陈述尽量带四类标记；学者观点必须姓名+年份；画论给版本页码；裁切给原图坐标与母图编号。
""")

    write(NOTES / "reading-map.md", """
# 阅读路线图

按难度与材料类型重组的延伸阅读。完整章节内亦有对应列表。

## 入门

- Hockney–Falco 争论条目（训练证据意识）
- Philip Ball 颜料史长文（Public Domain Review）
- Rijksmuseum《夜巡》超高清与研究页

## 进阶

- Martin Kemp, *The Science of Art* (1990)
- National Gallery *Art in the Making* 系列
- Tate：十九世纪英国油画材料

## 原始文献

- Cennini《艺人手册》（Thompson 英译）
- Alberti《论绘画》(1435)
- Chevreul《同时对比律》(1839)
- Charles Blanc《素描艺术语法》(1867)

## 技术检测

- National Gallery Technical Bulletin（尤其提香专号、雷诺兹材料）
- 宏观 XRF／断面显微方法论文（Kirby, Spring 等）
- 芝加哥艺术学院梵高《卧室》颜色复原报道
""")


def research_notes():
    write(RESEARCH / "01-treatises.md", """
# 检索笔记：画论原文与版本

- Cennini, *Il libro dell'arte* — Thompson 英译章节结构待逐条核对三色阶原文页码。
- Alberti, *Della pittura* 1435 — Grayson 英译；记录 pavement 方法页码。
- Leonardo 笔记 — 区分自用术语与后加「sfumato」标签。
- Chevreul 1839 — 重点做「正文主张 vs 画家图版实践」对照表。
- Blanc 1867 — 查 1870s 教材化传播路径。
""")
    write(RESEARCH / "02-technical-studies.md", """
# 检索笔记：机构技术检测

- NG Technical Bulletin 全卷目录标记：凡·艾克、提香 vol.34、雷诺兹 vol.35。
- Rijksmuseum Night Watch：像素图 + 研究更新页。
- AIC Van Gogh Bedroom：macro-XRF 紫色墙叙事。
- Vermeer 蓝色层位：需补断面文献精确引用。
""")
    write(RESEARCH / "03-pigments-timeline.md", """
# 检索笔记：颜料材料年表

1400s 天然群青／铅白／朱红／雌黄 → 1704 普鲁士蓝 → 1802 钴蓝 → 1817 镉 → 1826 人造群青 → 1841 锡管 → 1868 合成茜素。
""")
    write(RESEARCH / "04-institutions.md", """
# 检索笔记：制度史

工坊契约样本；法兰西学院课程；沙龙 livret；印象派独立展与画商（Durand-Ruel 等）。
""")
    write(RESEARCH / "05-historiography.md", """
# 检索笔记：争议史学

Hockney–Falco；Alpers 1983；Gombrich 图式—修正批评文献；技术影像解释限度书目。
""")


def make_schematic_original():
    """Generate Cennini tempera schematic if Pillow available."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    path = IMAGES / "originals" / "tempera-panel-schematic.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1600, 2000
    im = Image.new("RGB", (w, h), (232, 220, 190))
    d = ImageDraw.Draw(im)
    # drapery folds with pure-color shadow + hatched lights
    d.polygon([(400, 200), (1200, 220), (1100, 1700), (500, 1680)], fill=(160, 40, 40))
    for i in range(18):
        y0 = 400 + i * 60
        # shadow stripe pure color
        d.polygon([(520, y0), (700, y0 - 20), (680, y0 + 40), (500, y0 + 50)], fill=(150, 30, 30))
        # hatch lights
        for k in range(8):
            x = 720 + k * 18
            d.line([(x, y0), (x + 40, y0 + 50)], fill=(230, 190, 190), width=3)
    d.rectangle([80, 80, 1520, 1920], outline=(80, 50, 40), width=4)
    d.text((100, 100), "Cennini three-tone tempera schematic", fill=(40, 30, 20))
    im.save(path, quality=92)


def main():
    make_sources_and_crops()
    chapters()
    research_notes()
    make_schematic_original()
    print("Content bootstrap complete.")


if __name__ == "__main__":
    main()
