# bio-svg-figure
**生物医学/药学教材示意图（程序化 SVG · Nature Reviews 风）一键可用的作图 skill**

把"教材知识点"直接变成可出版矢量图：通路图 / 机制图 / 分类图 / 知识地图。用**程序化 SVG**（零漂移、真矢量、可进 Illustrator），风格对齐 Nature Reviews，含固定出版规范与验收 Gate。

## 包含什么
```
bio-svg-figure/
├── SKILL.md             # skill 主文件（流程 / G1 元件映射 / G3 密度 / G6 字体 / G7 重叠 / 踩坑）
├── elements.py          # 通用元件函数库（txt/rrect/arrow/ball/enzyme/protein/pdot/tee/ring4/foam/smc/cell/membrane/fibcap + render 导出三件套 + g7_check）
├── references/
│   ├── overlap-check.py     # G7 几何自检（元素不重叠）可执行脚本
│   ├── pattern-examples.md  # 标杆（通路/细胞机制/器官流程）与指标
│   ├── core-rules.md        # SVG 技术规范
│   └── troubleshooting.md   # 常见故障（中文消失/文字墙/重叠等）
├── SOP-教材矢量作图指南.md   # 完整方法论（中心原则 → 规范 → 流水线 → 附录实践案例）
├── examples/figure_example.py  # 一个完整示例（可直接跑出三件套）
└── install.sh            # 一键安装（装依赖 + 部署 skill 到 agent 目录）
```

## 快速开始
```bash
bash install.sh                # 自动装 cairosvg 并部署到 ~/.codex/skills（或自动检测）
# 或指定目录：
bash install.sh --target /path/to/skills
```

装好后，对你的 Codex / Claude 说：
> 「用 bio-svg-figure 画一张《脂肪酸从头合成》通路图」

agent 会自动读 `SKILL.md` 并按流程（Retriever 要素 → Planner 布局 → Stylist 常量 → Visualizer 用 `elements.py` 生成 → Critic 校验 + 人眼）产出**三件套**：
`fN_pub.svg`（可编辑源）、`fN_pub.pdf`（给 Illustrator 开）、`fN_出版300dpi.png`（1772×1181 出版）。

## 手动跑示例（验证环境）
```bash
python3 examples/figure_example.py     # 生成 figure_example.svg/pdf/出版300dpi.png
python3 references/overlap-check.py figure_example.svg   # G7 自检：FAIL=0 才可交付
```

## 核心规范速览
- 图幅 150×100mm（viewBox 1500×1000）；PNG ≥300dpi
- 字号三档 **7.5/6/5pt**（fs 26/21/17）；图注放 Word（宋体 6pt）
- 字体**按内容分派**：含中文 → 黑体（Heiti SC/SimHei），纯英文 → Arial
- 色板 NR 风（蓝/橙/紫/绿/粉/灰 + 抑制红）
- **每图 15–20 张、读图即懂**；验收：G3 密度（图形:文本≥5:1）+ G6 字体 + **G7 重叠=0**，达标才交人眼

## 依赖
- `python3` + `pip install cairosvg`
- 中文字体：系统 `Heiti SC`/`SimHei`（mac 自带；Windows 用 SimHei，Linux 可装 Noto Sans CJK）
- （可选）`fpdf2` 供 SOP→PDF；标准转 PDF 用 `pandoc --pdf-engine=typst`

## 避坑（详见 SKILL.md）
AI 生图✗ · 手拖✗ · 内联 style✗ · 直接开 SVG✗ · 机评视觉✗；字体勿用单一混合列表（中文消失）· 元素勿重叠（G7 脚本查）
