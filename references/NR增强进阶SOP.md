# 既有图 NR 标准「配色增强 + 进阶质感」SOP（复盘定稿版）

> **适用范围**：对 AI 导出的**已有图 SVG**（如《生命药学》第十二章 f1–f17）做 Nature Reviews 标准处理——**不重新作图、不改排版**，只增强质感与修正配色。
> **定稿时间**：2026-09（含整章 17 图实操复盘）。文中每一参数均为**复盘后定稿值**，勿凭感觉改回。

---

## 一、两步主流程（对每张已有图）

```bash
# ① 配色审计 + 校正（NR 配色）
python3 nr_color_audit.py <f>.svg --prefix=<f>       # → <f>_NR配色.svg + <f>_色彩审计.md

# ② 进阶质感（光影/底色/描边，默认极浅暖白底、无标尺）
python3 nr_enhance.py <f>_NR配色.svg --prefix=<f>    # → <f>_NR进阶.svg
```

- ①输出**配色调好版**（供比对/再调）；②输出**最终版**。
- 批处理：`python3 nr_color_audit.py *.svg`；`python3 nr_enhance.py *_NR配色.svg`。
- ②可选：`--no-bg`（纯白底，默认已是极浅暖白）；`--scalebar`（加比例尺，默认关）。

---

## 二、定稿参数（NR 规范，勿改）

| 项 | 定稿值 |
|---|---|
| 背景 | **极浅暖白** `#FFFFFF→#FCFAF6→#F4F0E9`（径向，居中略亮）——**绝不偏灰偏暗** |
| 饱和度 | 只对 **S>0.62** 的明显高饱和色**适度降彩**，其余保色相；不全局压 |
| 明度 | 只救极暗（V<0.35→0.40）；**不压亮** |
| 光影体积 | **通用光影**：对每个非文字/非灰/非白主填充色生成 `gx_*` 径向渐变（高光→主色→暗），元素 fill→`url(#gx_*)` |
| 描边 | 统一 **0.75pt** |
| 字号 | 三档 7.5/6/5pt（对应 @1500×1000→26/21/17px；图内禁 <17px）|
| 字体 | 中文→`SimHei`（黑体）、英文→`Arial`；粗体用 `font-weight="bold"` |
| 标尺 | **默认关**（`--scalebar` 才加，仅结构图需要时）|
| 导出 | 300dpi：1772×1181（=150×100mm）|

---

## 三、复盘：踩过的坑 → 定稿决定（重点，防止再犯）

| # | 坑 | 现象 | 定稿决定 |
|---|---|---|---|
| 1 | 背景渐晕**做太深** | 边缘灰褐 `#E7DFD2` → 整图"灰蒙蒙" | 改**极浅暖白**（近白），绝不用深灰褐 |
| 2 | 全局**降饱和+压明度** | 色彩发灰、不通透 | 只降 **S>0.62** 高饱和；明度只救极暗 |
| 3 | 光影只映射**解剖色**（F15 血管红/脂黄）| 其余 15 张**光影引用=0**（只有莫兰迪+底色，没体积感）| 改**通用光影**：对任意主填充色生成 `gx_*` 渐变；自检：`grep -c 'url(#gx_' f_NR进阶.svg` 应>0 |
| 4 | AI 导出**内嵌字体名** `Arial-BoldMT`/`ArialMT`/`STHeitiSC-Light`/`KozGoPr6N-83pv-RKSJ-H` | cairosvg **不识别 → 转 PNG 乱码** | **字体归一**：中文→`SimHei`、英文→`Arial`（bold 用 `font-weight`）；非常规名全部替换 |
| 5 | 比例尺**误加**（分类/通路图不加）| 突兀 | **默认关**，仅结构图 `--scalebar` |
| 6 | 中间产物/旧文件过多（_NR配色/_原vs进阶/pdf/审计/总览…）| 文件夹杂乱 | 只留**最新 `_NR进阶.svg`**（改文字用）+ 正式 `_出版300dpi.png`；原始 SVG 另存 `原始/` 备份 |
| 7 | 图号/图注**错位** | 图文对不上 | 按**内容**对齐重排为连续 f1–f17；正文定稿版"图12-1~12-17"天然对应；`Figure-Legends.docx` 需同步重排（删无独图条目）|

---

## 四、字体归一（AI 导出后必做，防乱码）

替换以下非常规名到标准名（`SimHei`/`Arial`）：
- `Arial-BoldMT` → `Arial`（**加 `font-weight="bold"`**）
- `ArialMT` → `Arial`
- `STHeitiSC-Light` → `SimHei`
- `KozGoPr6N-Regular-83pv-RKSJ-H` → `SimHei`
> 注：AI 导出 CSS 常为单引号 `font-family:'Arial-BoldMT';`，替换时须带引号处理。
> 自检：`grep -lE "ArialMT|Arial-BoldMT|STHeitiSC|KozGo" *_NR进阶.svg` 应**无输出**。

---

## 五、定稿文件约定

- `最终图/svg/`：**17 张 `f1–f17 *_NR进阶.svg`**（最新版，可直接改 `<text>`）+ `_出版300dpi.png`
- `最终图/svg/原始/`：原始 SVG 备份（重排后同步改名）
- 图注：`第十二章-图注-Figure-Legends-重排17条.docx`（17 条，与新 f 序号对应）
- 正文定稿版：已是"图12-1~12-17"，**无需改**

---

## 六、工具文件位置

- `nr_color_audit.py` / `nr_enhance.py`：`textbook/figures/`（本机）+ `bio-svg-figure-dist/`（GitHub 分发包 `wangseeker/bio-svg-figure`）
- venv：`~/.reasonix/venvs/pdf/bin/python3`（含 cairosvg / docx）
