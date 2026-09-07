# 生物医学教材矢量作图 SOP（程序化 SVG · Nature Reviews 风）

> 一套可复制的、从"教材知识点"到"可出版矢量图"的完整作图方法论。
> 经《生命药学》第十二章 F1–F18（脂质代谢）全程实战打磨。
> 许可证：CC-BY-4.0（可自由分享、改编，保留署名）。

---

## ⭐ 中心原则（每图必守，全篇前提）

> **每章配 15–20 张图**，追求"读者只看图就能读懂本章节内容"——图即讲解，文字只作补充（图注进 Word、图内只留短标签）。
> 图的美观与质量**对标 Nature Reviews 系列作图要求**：程序化 SVG · NR 矢量风 · 固定出版规范（尺寸/字号三档/色板/字体按内容分派）· 图例用图形徽标 · 附图注。达不到 NR 标准的图不交付。

---

## 0. 核心决策（先想清楚再动笔）

**用"程序化 SVG"，不用 AI 生图、不用 BioGDP/BioRender 手拖。**
| 方案 | 结论 | 原因 |
|------|------|------|
| **程序化 SVG**（python 脚本生成）| ✅ **主路线** | 零漂移（坐标=代码）、真矢量（可编辑/可出版）、统一风格（常量色板）、可批量、可版本控制 |
| AI 生图（DALL·E/Midjourney 等）| ❌ 弃 | 错字（关键术语漂移）、位置漂移、位图（不满足矢量出版）|
| image-to-image（改一处必全漂）| ❌ 弃 | 局部改动导致整体漂移，不可控 |
| BioGDP / BioRender 手拖 | ❌ 弃 | 太慢，难批量统一，版权/导出受限 |
| 数据图表（matplotlib/R）| ➖ 另一条线 | 用 nature-figure（数据驱动），示意图才走本 SOP |
| **SOP/文档 → PDF** | **pandoc + typst**（`/opt/homebrew/bin/pandoc`）| `pandoc <md> -o <pdf> --pdf-engine=typst -f markdown-citations`；封装 `md2pdf.sh`；中文=黑体 SIL-Hei，代码/表格自动排版 |

**一句话**：示意图 → 程序化 SVG；数据图 → matplotlib/R；分子结构 → RDKit。

---

## 1. 环境与工具

| 工具 | 作用 | 位置/命令 |
|------|------|----------|
| Python 3 | 拼装 SVG 脚本 | `python3` |
| **cairosvg** | SVG → PNG(300dpi) / PDF | `cairosvg.svg2png(url=..., output_width=1772)`；`svg2pdf(...)` |
| **vtracer** | PNG 位图 → 矢量描摹（复刻用户给的图标/线稿）| `vtracer.convert_image_to_svg_py(png, svg)` |
| RDKit（可选）| 真实分子结构（SMILES→SVG/PNG）| `from rdkit import Chem; Chem.MolToSVGFile(...)` |
| Illustrator / AI | 打开 & 微调（**用 PDF，不用 SVG**）| — |
| Word | 图注 / 排版（图不放图内文字）| — |

> 建议先手测一次"生成→渲染→AI 打开"闭环，确认 cairosvg + PDF 通路无问题再批量。

### 1.1 本作者的参考系统（复现用，可据此搭建你的环境）

| 项 | 本机 | 说明 |
|----|------|------|
| 硬件 | Apple Silicon（M4 Pro）| 渲染快，SVG 转 PDF/PNG 秒级 |
| 系统 | macOS（darwin/arm64）| 中文黑体 `Heiti SC` 与 `PingFang SC` 均系统自带（黑体=Heiti SC），无需另装 |
| 运行环境 | **Reasonix / Claude Code 类 agent 环境** | 由 agent 直接写 Python 脚本并执行，自动生成 SVG + 导出 PDF/PNG |
| Python | 3.9（系统）+ 3.13（venv）| 渲染依赖用独立 venv，避免污染系统 |
| venv | `~/.reasonix/venvs/pdf/`（`pip install cairosvg vtracer`）| cairosvg＝SVG→PNG/PDF；vtracer＝PNG→矢量描摹 |
| 调用 | 通过 init.d PATH 注入，`~/.reasonix/bin/` 有 wrapper；venv 的 shebang 若移动目录需同步修 | 保证新会话 `pdf-inspector/opendataloader-pdf` 等可直呼 |
| 字体 | **按内容分派**：含中文 → 黑体 `FONT_CN='Heiti SC', STHeiti, 'PingFang SC'`；纯英文/数字 → **Arial** `FONT_EN=Arial, Helvetica` | 中文黑体+英文 Arial，勿用单一混合列表（G6）|
| PDF 转换 | `cairosvg.svg2pdf(...)` 生成 `fN_pub.pdf`（给 AI 开）| **AI 用 PDF、出版用 PNG、编辑源用 SVG** |
| 数据图 | matplotlib/R（若需，另走 nature-figure）| 与示意图分流 |

> **核心可移植点**：所有依赖仅需 `pip install cairosvg vtracer`（+可选 `weasyprint markdown` 用于 SOP/文档转 PDF）；不依赖付费闭源软件，权重全在"代码即坐标、常量即规范"。

---

## 2. 固定出版规范（常量全章统一，不临时改）

| 项 | 固定值 |
|----|--------|
| 图幅 | **150×100mm**（3:2 通栏），viewBox `0 0 1500 1000`（或按 3:2 缩放）|
| 分辨率 | SVG 矢量无损；PNG 导出 **≥300dpi**（1772×1181 对应 150mm）|
| 字号 | **三档分级（7.5/6/5pt，@1500×1000 → fs 26/21/17）**：7.5pt=图题/阶段大字；6pt=面板标题·酶/蛋白名·主通路（**默认档**）；5pt=引线标注·图例名·缩写（最短）。**禁止 <17px** |
| 字体 | 按内容分派：含中文→黑体 `'Heiti SC', STHeiti, 'PingFang SC'`；纯英文→Arial `Arial, Helvetica`（禁止单一混合列表，见 G6）|
| 色板（NR 风） | 蓝`#4A7DBF` 橙`#E8A87C` 紫`#9B7FC0` 绿`#8FBF8F` 粉`#D98A8A` 灰`#5A5A5A` **抑制红`#C0392B`** |
| 分区底块 | 用标准色**浅色调**（如浅蓝`#EDF1F8`/浅紫`#F3F0F8`/浅橙`#FDF0E0`）+ 同色系描边 |
| 图注 | 放 **Word** 图下方（**宋体 6pt**），**不在图内** |
| SVG 样式 | 用**标准属性**（`fill`/`stroke`/`stroke-width` 直接写元素上），**禁止内联 `style`/`class`** |
| **AI 修图（Illustrator 人工）** | 打开 `fN_pub.pdf` 修图时：**字体统一改 `Arial Bold`**；**所有描边（stroke）统一 `0.75pt`**；其余样式不改，另存覆盖 |

---

## 3. 流水线（多 Agent 五步 + 验收，每张图走一遍）

```
Retriever → Planner → Stylist → Visualizer → Critic
```

| 阶段 | 做什么 | 产出 |
|------|--------|------|
| **Retriever** | 从教材原文检索要素：物质、酶、调控、去向、器官 | 要素清单（术语对齐课本）|
| **Planner** | 布局：分区（胞质/线粒体/器官）、主线、标注位置 | 草图布局 |
| **Stylist** | 套固定规范：标准色板、字号、箭头、循环画法 | 配色/样式约束 |
| **Visualizer** | 用元件函数拼装 SVG（程序生成，非 AI 生图）| `fN_pub.svg` |
| **Critic** | 程序校验（XML/150mm/无style/渲染）+ **G3密度·G6字体·G7重叠自查（overlap-check.py）** + **人眼验收** | 通过/返工 |

> 关键差异：Visualizer 是**程序生成**（零漂移/矢量/可编辑）；Critic 是**程序校验 + 人眼**（矢量放大看，**不要依赖 LLM/机器视觉判设计**——不可靠）。

---

## 4. 元件函数库（可复用，定义一次全章用）

核心函数示例（Python 生成 SVG 片段）：

```python
def txt(x,y,s,size,fill,weight="normal",anchor="start"):
    w=f' font-weight="{weight}"' if weight!="normal" else ""
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}"{w} text-anchor="{anchor}" fill="{fill}">{s}</text>'

def arrow(x0,y0,x1,y1,c,w=3):
    # 带三角头的标准箭头
    ...

def rrect(x,y,w,h,rx,fill,stroke,sw=2):   # 圆角矩形节点/酶
def ball(cx,cy,r,fill,stroke):              # 分子球（带高光）
def enzyme(x,y,w,h,label,fill,edge,tc):     # 酶模块
def cycle(cx,cy,r,color,label,n=16):        # 完整循环箭头环（n 段）
def membrane_band(x0,x1,y):                 # 磷脂双分子层带
def mito(x,y,w,h):                          # 细线纯色线粒体（外膜+内膜+嵴）
def organ_icon(x,y,label):                  # 器官图标
def region(x,y,w,h,title,fill,edge):        # 分区底块
```

### 关键标准（易错点）
- **磷脂双分子层**：间距 **21px**（@1500 宽画布）、头 `r=7`、尾部偏移 **±5**；上下两排头朝外、尾对尾（标准密度，全章一致）。
- **β-氧化循环**：**4 箭头**代表四步（脱氢→加水→再脱氢→硫解），每步旁标辅酶（FAD→FADH₂/H₂O/NAD⁺→NADH）。
- **线粒体**：细线（2–3px）+ **纯色基质**（好上色），外膜+内膜+发夹状嵴；**不要**用粗描摹。
- **抑制**：用标准抑制红 `#C0392B`，可加 T 头 / 虚线。

---

## 5. 三类图源策略（很重要）

| 图源 | 处理 | 注意 |
|------|------|------|
| **示意图**（通路/机制/分类）| 程序化 SVG（如上）| 主路线 |
| **真实分子结构** | RDKit（SMILES→结构，官能团橙高亮）| SVG 内嵌 rdkit 进 AI **不显示** → 输出**独立结构 PNG** 供手工插入 |
| **扫描/现成图标（Bioicons PNG）** | **vtracer 描摹**（100% 复刻用户给的图）+ re-color | 描摹器输出可能**未闭合标签** → 校验/补全/改用细线自绘 |
| **数据图**（量值/统计）| matplotlib/R（nature-figure）| 另一条线，不混用 |

---

## 6. 交付三件套（每张图）

```
textbook/figures/F0N/
  ├── fN_pub.svg           # 矢量源（可编辑）
  ├── fN_pub.pdf           # 给 AI/Illustrator 打开编辑用（100% 显示）
  └── fN_出版300dpi.png    # 出版用（≥300dpi）
```

**给 AI 打开用 PDF，不是 SVG**（Illustrator 直接开 SVG 会失真/不显示某些元素——rdkit/内嵌/大描摹 path 都踩过坑）。

---

## 7. 关键坑与避坑（实战踩过，务必记）

| 坑 | 症状 | 对策 |
|----|------|------|
| AI 生图 | 错字/漂移/位图 | 弃，走程序化 SVG |
| SVG 内嵌本不存在/未闭合 | Illustrator "no element found / 未闭合" | 输出前校验 XML；rdkit 补 `</svg>`；vtracer 缺闭合→重画 |
| 内联 `style`/`class` | Illustrator 不显示该元素 | 改**标准属性**（fill/stroke 直接写）|
| 给 AI 直接开 SVG | 失真/结构丢 | **转 PDF 给 AI** |
| `.format` 遇 `{y+30}` 表达式 | KeyError | 用 f-string 而非 `.format` |
| 缩放除号（如 `scale(334/360)`）| SVG 非法乱码 | 预计算数值，写入具体数字 |
| **后绘元素盖住先绘元素** | 下层内容被新图块盖住 | 底图**先画**，上层文字/环**后画**（讲 z 顺序）|
| 机械评审/LLM 判视觉 | 误判"好看" | **人眼 + 矢量放大**为准 |
| 磷脂头尾太密/太疏 | 膜不像双分子层 | 固定 **21px 间距 / 头 r7 / 尾±5** |
| 线粒体用粗描摹 | 又粗又脏、难上色 | **细线 + 纯色基质**，自绘替代 |
| 色块装整句（提纲化） | 大段句子进矩形、图形≈0，用户判“没有图只有文字” | 概念→元件映射(G1) + 短标签(G2)；图形:文本 ≥5:1 |
| 中文整体消失 | font-family 列表首位是无中文的 Arial/Helvetica | 按内容分派：含中文走黑体(Heiti SC)、纯英文走 Arial（G6）|
| 元素重叠 / 箭头悬空 | 文本压图、箭头离节点 8-15px | 几何自检：间距 ≥20px、箭头贴节点边 0–3px（G7）；用 `references/overlap-check.py` 一键跑 |
| 图例只给纯色块 | 读者无法按“形状”对号元素 | 图例每项用**与图中一致的图形徽标** + 名称（颜色+形状双标注，F15）|
| 解剖层次画错 | 脂质画在内皮上方 / 管腔随斑块整体缩小 | 内壁/内皮**固定**、斑块自下壁**突入管腔**占位；脂质在内皮**下方**（F15 经典解剖）|

---

### 7.1 G7 几何自检脚本（出图必跑，可执行校验）

**位置**：`~/.reasonix/skills/bio-svg-figure/references/overlap-check.py`（随 skill 更新）
**用法**：`python3 overlap-check.py <fN_pub.svg> [--tol=2] [--quiet]`

| 输出 | 含义 | 处置 |
|---|---|---|
| **FAIL**（exit 1）| text–text 相交 / text 出界 / 箭头端点悬空(离所有节点 >12px) | **禁止交付**，回 Planner |
| **HINT**（人眼确认）| text 中心落入非自带色块 / 箭头深入形状 >25px（入胞箭头等） | 人眼判，非自动阻断 |
| ✔ FAIL=0（exit 0）| 无重叠/无出界/无悬空 | 交人眼终审 |

只依赖 `re/math`（无第三方包）。Critic 阶段**先跑它、FAIL 归零后再交人眼**。

## 8. 目录/命名/批量管理（建议）

```
textbook/figures/
  ├── 教材矢量作图SOP指南.md     # 本 SOP
  ├── 教材作图批量方法.md        # 定稿复盘
  ├── 第十二章配图指令.md        # F1–F18 每张要素/图注
  ├── bioicons/                 # 原始图标 + 描绘矢量/
  └── F0N/  fN_pub.svg · fN_pub.pdf · fN_出版300dpi.png
```
- 每图一个 `F0N/` 目录，命名 `fN_pub` / `fN_出版300dpi`。
- 每张在 `配图指令.md` 记：要素、布局、图注草稿、状态（定稿/待审视）。
- 生成脚本放各自目录或 `/tmp`（可复用就归档到 `元件函数库.py`）。

---

## 9. 复用与分享

- 本 SOP 以 **CC-BY-4.0** 发布，可自由复制/改编。
- 已封装为 skill：`bio-svg-figure`（含 `SKILL.md` + `references/`），调用 `/bio-svg-figure` 即可按本流水线出图。
- 分享方式：把本 SOP + `元件函数库` + 一个成品示例（如 F5 脂蛋白）打包，别人即可复现。

---

## 10. 一分钟速查表

```
主题 → Retriever 要素 → Planner 布局 → Stylist 色板/字号 → Visualizer 程序拼装
→ 导出 SVG + PDF + 300dpi PNG → Critic 校验 + 人眼 → 三件套进 F0N/
规范：150×100mm · 7.5/6/5pt(三档) · NR色板 · 无style · 字体按内容分派(G6) · PDF交付AI · 图注进Word(6pt)
避坑：AI生图✗ 手拖✗ 内联style✗ 直接开SVG✗ 机评视觉✗；描摹校验✓ 底图先画✓
```

---

# 附录 A　完整实践案例：第十二章《脂质代谢》F1–F20（照着做即可复现）

> 本附录以真实完成的《生命药学》第十二章《脂质代谢的平衡与失调及药物干预》为例，从知识点到可出版矢量图**逐步**演示，读者按 A.1→A.9 操作即可复制。文中命令为实际使用过的，路径以 `textbook/figures/` 为根。

## A.0 案例概览
- 章：第十二章，脂质代谢；成品图 **F1–F20**（F6 并入 F5）
- 产出每图三件套：`F0N/fN_pub.svg`（矢量源）、`fN_pub.pdf`（给 Illustrator 开）、`fN_出版300dpi.png`（1772×1181 出版）
- 后缀文件：`F0N/fN_gen.py`（生成脚本，可改）、`第十二章-图注-Figure-Legends.docx`（图注，宋体 6pt）
- 环境：`python3` + `~/.reasonix/venvs/pdf/`（`pip install cairosvg`），系统自带 `Heiti SC`/`PingFang SC`/`Arial`

## A.1 准备教材底稿
1. 用**最新精简全章**为准（本例 `…-定稿版.docx`，41,827 字），勿用旧轮次。
2. 提取正文（按节标题切）：
```bash
~/.reasonix/venvs/pdf/bin/python3 - <<'EOF'
import docx; d=docx.Document("第十二章：脂质代谢…-定稿版.docx")
for i,p in enumerate(d.paragraphs):
    t=p.text.strip()
    if t: print(f"[{i}] {t}")
EOF
```
3. 先写**配图指令**（Retriever 的产物）：`第十二章配图指令.md`——每图记录 `布局 / 要素 / 图注草稿 / 状态`。

## A.2 Retriever：从教材提取本图要素（忠术语）
以 **F16 代谢综合征（12.4.4）** 为例，从原文抽出：
- [143] 定义：多重危险因素聚集，"共同土壤"；[145] IDF 诊断；[147] CETP→TG↑/HDL-C↓/sdLDL↑；[149] 中心性肥胖→门静脉FFA→肝IR+VLDL↑、促炎因子→外周IR→"自我强化闭环"
→ 得到要素清单：中心性肥胖(内脏脂肪)、胰岛素抵抗+炎症、脂质紊乱(CETP/三联征)、加重闭环、IDF 标准、结局(2型糖尿病/CVD)。**术语严格照原文，勿编造。**

## A.3 Planner：布局 + G1 概念→元件映射
- 布局（F16）：中心"中心性肥胖" → 右下"胰岛素抵抗+炎症" → 右上"脂质代谢紊乱" → 虚线"加重"回中心，成闭环；底部 IDF 诊断带、结局行。
- **G1 强制**：每个概念先指派元件再画（见 §四 G1 表）。如 肥胖→细胞/器官图标、FFA→橙色小球、CETP→酶块、三联征→小球阵、闭环→弧线箭头。
- 产出"布局方案（草图）"，**先给用户审**再生成（避免画错返工）。

## A.4 Stylist：固定规范常量（全章统一）
```python
# 尺寸 150×100mm = viewBox 1500×1000；字号三档 7.5/6/5pt → fs 26/21/17
FONT_CN = "'Heiti SC', STHeiti, 'PingFang SC', sans-serif"   # 中文→黑体
FONT_EN = "Arial, Helvetica, sans-serif"                       # 英文→Arial
NR = {"蓝":"#4A7DBF","橙":"#E8A87C","紫":"#9B7FC0","绿":"#8FBF8F","粉":"#D98A8A","灰":"#5A5A5A","抑制红":"#C0392B"}
```
**字体按内容分派（G6）**——因 cairosvg 取列表第一个字体渲染整段、不做逐字回退：`txt()` 内 `fam = FONT_CN if re.search(r"[\u4e00-\u9fff]", s) else FONT_EN`（含中文走黑体、纯英文走 Arial，单一混合列表会致中文消失）。

## A.5 Visualizer：程序化 SVG（元件函数 + 生成脚本）
最小可运行框架（`fN_gen.py`）：
```python
import math, os, re
E=[]
def txt(x,y,s,size,fill,weight="normal",anchor="middle"):
    fam=FONT_CN if re.search(r"[\u4e00-\u9fff]",s) else FONT_EN
    w=f' font-weight="{weight}"' if weight!="normal" else ""
    E.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}"{w} text-anchor="{anchor}" fill="{fill}">{s}</text>')
def ell(cx,cy,rx,ry,fill,stroke=None,sw=1.5): E.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke or fill}" stroke-width="{sw}"/>')
def rrect(x,y,w,h,rx,fill,stroke,sw=2): E.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def arrow(x0,y0,x1,y1,color="#5A5A5A",w=3,head=12):
    import math as _m
    E.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{w}"/>')
    a=_m.atan2(y1-y0,x1-x0); pts=[]
    for da in (0,_m.pi*150/180,_m.pi*210/180):
        pts.append(f"{x1+head*_m.cos(a+da):.1f},{y1-head*_m.sin(a+da):.1f}")
    E.append(f'<polygon points="{" ".join(pts)}" fill="{color}"/>')
def ball(x,y,r,fill,edge=None): E.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{edge or fill}" stroke-width="2"/>')
# 元件库（按 §4 / 各实图扩展）：enzyme/protein/pdot/tee/ring4/foam/smc/fibcap/thrombus……
# —— 拼装本图（示意）——
E.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="100mm" viewBox="0 0 1500 1000">')
E.append('<rect width="1500" height="1000" fill="#FFFFFF"/>')
# ……（your 布局代码）……
svg="\n".join(E)+"\n</svg>"
open("fN_pub.svg","w",encoding="utf-8").write(svg)
import cairosvg
cairosvg.svg2png(url="fN_pub.svg",write_to="fN_出版300dpi.png",output_width=1772,output_height=1181)
cairosvg.svg2pdf(url="fN_pub.svg",write_to="fN_pub.pdf")
```
> 关键：**坐标=代码**（零漂移）、**标准属性**（勿 style/class）、**先底图后上层**（z 顺序）、`scale()` 先算成数字。

## A.6 Critic：四道校验（出图必跑）
```bash
# ① XML 良构 + 无内联 style/class
python3 -c "import xml.dom.minidom,sys; xml.dom.minidom.parse('fN_pub.svg')"; grep -c 'style=\|class=' fN_pub.svg   # 应 0
# ② G3 图形密度 与 ③ G6 字体
python3 -c "
import re;raw=open('fN_pub.svg',encoding='utf8').read()
s=len(re.findall(r'<(circle|ellipse|path|polygon|rect|line)\b',raw));t=re.findall(r'>([^<>]{2,})</text>',raw)
print('图形:文本≈%.1f:1 均长≈%.0f 最长=%d'%(s/len(t),sum(map(len,t))/len(t),max(map(len,t))))"   # 应 ≥5:1、均长≤8
# ④ G7 几何自检（元素不重叠 → 脚本）
python3 ~/.reasonix/skills/bio-svg-figure/references/overlap-check.py fN_pub.svg   # FAIL=0 才可交付
# 300dpi 尺寸
sips -g pixelWidth -g pixelHeight fN_出版300dpi.png   # 1772 × 1181
```
失败→回 Planner 元件化；**全过才交人眼**。

## A.7 人眼验收与真实迭代（不要靠机械评审）
| 图 | 问题（用户反馈） | 迭代方向 |
|---|---|---|
| F13 | "没有图只有文字" | 色块文字 → 细胞级机制图（球/酶/蛋白条/P/⊣/膜）|
| F12 | 内容分散/总览缺失 | 横带散排 → 中心辐射四去向总览 + 图形徽标图例 |
| F15 | 管腔过小 / 脂质位置 / 斑块圆形等 | 内壁固定、斑块自下壁突入管腔占位；脂质在内皮下方；纤维帽在腔面；细胞放大 |
| F16 | 看不懂 / 无箭头 | 文字块 → 自我强化闭环（实线触发+虚线加重）+ IDF 标注 |
经验：视觉终审**只信人眼+矢量放大**（不要在无视觉时交付文字墙图）；布局先出草图给用户审再精修。

## A.8 交付三件套 + 图注
- 落位 `F0N/{fN_pub.svg, fN_pub.pdf, fN_出版300dpi.png}`（AI 用 PDF、出版用 PNG、源用 SVG）
- 图注进 Word（宋体 6pt、图号+标题加粗）：`第十二章-图注-Figure-Legends.docx`，内容与图上一一对应
- 人眼验收通过 → 定稿

## A.9 可复制性检查清单（一键跑）
1. 教材底稿 = 最新精简全章（勿用旧轮次）
2. 配图指令 md（Retriever 产物）
3. 布局草图（Planner）先给用户审
4. Stylist 常量统一（尺寸/三档字号/色板/字体分派）
5. Visualizer 生成（元件库 + gen.py 归档）
6. Critic：XML/无style + G3 密度 + G6 字体 + **G7 overlap-check.py（FAIL=0）** + 300dpi
7. 人眼终审（矢量放大）
8. 交付三件套 + 图注 Word（宋体 6pt）
9. `fN_gen.py` 归档进 `F0N/`（可复现编辑）
