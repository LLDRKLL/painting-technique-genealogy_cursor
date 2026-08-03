# 通往塞尚之前：西方绘画技法与公认原则的谱系

静态长读站点。以技法与成文规范为切口，追溯西方绘画「公认原则」约 1390–1906 的形成、强制执行与松动，作为塞尚绘画逻辑研究的前传。

## 本地预览

```bash
python -m pip install -r requirements.txt
python fetch_images.py          # 按清单拉取公有域原图（可跳过，已提交派生图）
python build_assets.py          # 原图 → 派生图 + 裁切标注
python build_site.py            # Markdown → site/index.html 等
cd site && python -m http.server 8080
```

打开 <http://localhost:8080>。

## 仓库结构

见研究计划 `brief`（Downloads 中的实施说明）。正文在 `notes/`，检索笔记在 `research/`，图版索引在 `references/sources.csv`。

## 构建产物

托管平台无需跑 Python：`site/` 下的 `index.html`、`style.css`、`app.js`、`img/`、子页均已提交。

## 许可与图像

正文版权归仓库所有者。图像优先 Wikimedia Commons / 机构开放接口的公有域或 CC 资源；元数据见 `images/_manifest.json` 与 `references/sources.csv`。原图目录默认不入 Git。

若 Wikimedia 限流导致个别原图未拉取成功，`scripts/ensure_images.py` 会写入带标题的占位图；稍后重新运行即可替换为真图，再执行 `build_assets.py`。

## GitHub

私有仓库托管；构建产物已提交于 `site/`，可直接静态预览。CI 在 push 时校验 Markdown 图版 slug 与 `build_site.py`。
