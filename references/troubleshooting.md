# SVG Troubleshooting

## Broken Image

Checks:

1. Path is relative to the Markdown file.
2. SVG root includes `xmlns="http://www.w3.org/2000/svg"`.
3. XML parses with `svglint file.svg` or in a browser.

## Cropped or Tiny SVG

Cause: `viewBox` does not match content bounds.

Fix: set `viewBox="0 0 width height"` to the actual visible drawing area, then size in Marp with `![bg fit]` or `![w:...]`.

## Text Missing

Checks:

- `font-size` is explicit.
- `fill` contrasts with the background.
- Text does not rely on an unavailable embedded or system font.
- XML characters are escaped.

## Arrows Missing

Checks:

- Marker `id` exists in `<defs>`.
- Line/path uses `marker-end="url(#id)"`.
- Marker fill/stroke contrasts with the background.

## Inconsistent Visual Style

Fix by normalizing these values across all SVGs in the deck:

- palette
- stroke width
- corner radius
- font family and sizes
- shadow/filter use

## Validation

```shell
svglint path/to/file.svg
```

If `svglint` flags XML escaping, replace `&` with `&amp;`, `<` with `&lt;`, and `>` with `&gt;` inside text nodes.

## Text-Wall Drift（文字化漂移——最常见返工）
症状：输出像“色块排句子/提纲页”，图形元件≈0；用户：“没有图，只有文字，全都错了”。
自查（G3 统计）：
- 图形:文本 <5:1（标杆 5–12:1）
- text 均长 >8 字；出现 >12 字框内文本
修复：
1. 回 references/pattern-examples.md 看标杆 A/B/C，选对应类型
2. 每个概念转成元件（G1）：句子→球/酶块/蛋白条/细胞/膜/箭头 + ≤8 字标签
3. 删句成标签；整句移图注或图底 ≤2 行
4. 重跑 G3，达标再交人眼

## 中文整体消失（cairosvg 渲染）
症状：改字体后 PNG 中文全部消失。
原因：cairo 按 font-family 取**第一个字体**渲染整段文本；Arial/Helvetica 无 CJK → 中文缺字（Arial 渲染「代谢」墨迹≈466 vs Heiti 2016）。
修复：按内容分派——含 [\u4e00-\u9fff] 用 FONT_CN（'Heiti SC', STHeiti, 'PingFang SC'），纯拉丁用 FONT_EN（Arial）；勿把无 CJK 字体放首位。

## 排版重叠 / 箭头悬空
症状：元素重叠、文字压线、箭头没接节点（悬空 8-15px 或深扎）；人眼多轮返工。
修复：交付前跑几何自检（text-text 包围盒、text 出界、text 撞非所属色块、箭头端点贴节点边 0-3px）；跨面板箭头走预留缝隙；箭头旁标签放线中点上方 ≥18px；元素间距 20-60px 均匀（过散=容器化收纳，过挤=放大间距）。
