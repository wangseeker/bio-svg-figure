# -*- coding: utf-8 -*-
"""bio-svg-figure 通用元件函数库（可复用，一次 import 全章用）
用法：复制/import，先 E=[]，用元件函数拼装，最后 render() 导出三件套。
依赖：cairosvg（pip install cairosvg）。字体按内容分派（G6）：中文黑体、英文 Arial。
"""
import math, os, re
try:
    import cairosvg
except ImportError:
    cairosvg = None

FONT_CN = "'Heiti SC', STHeiti, 'PingFang SC', SimHei, sans-serif"   # 中文 -> 黑体
FONT_EN = "Arial, Helvetica, sans-serif"                             # 英文 -> Arial
E = []   # 元素容器（每个图重置=[]）

def txt(x, y, s, size, fill, weight="normal", anchor="middle"):
    fam = FONT_CN if re.search(r"[\u4e00-\u9fff]", s) else FONT_EN
    w = f' font-weight="{weight}"' if weight != "normal" else ""
    E.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}"{w} text-anchor="{anchor}" fill="{fill}">{s}</text>')

def rrect(x, y, w, h, rx, fill, stroke, sw=2):
    E.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def ell(cx, cy, rx, ry, fill, stroke=None, sw=1.5):
    E.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke or fill}" stroke-width="{sw}"/>')
def circle(cx, cy, r, fill, stroke=None, sw=1):
    E.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke or fill}" stroke-width="{sw}"/>')
def line(x0, y0, x1, y1, color="#5A5A5A", w=3):
    E.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{w}"/>')
def _head(x, y, ang, size, color):
    pts = []
    for da in (0, math.pi*150/180, math.pi*210/180):
        pts.append(f"{x+size*math.cos(ang+da):.1f},{y-size*math.sin(ang+da):.1f}")
    E.append(f'<polygon points="{" ".join(pts)}" fill="{color}"/>')
def arrow(x0, y0, x1, y1, color="#5A5A5A", w=3, head=11, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    E.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{w}"{d}/>')
    _head(x1, y1, math.atan2(y1-y0, x1-x0), head, color)
def rot(cx, cy, ang, inner):
    E.append(f'<g transform="rotate({ang} {cx} {cy})">'); E.extend(inner); E.append('</g>')
def on_ell(cx, cy, rx, ry, a_deg, dr=0):
    r = math.radians(a_deg)
    return (cx + (rx+dr)*math.cos(r), cy + (ry+dr)*math.sin(r))

# 元件：分子球 / 酶 / 蛋白条 / P 磷酸化 / ⊣ 抑制 / 甾核 / 细胞
def ball(x, y, r, fill, edge=None):
    E.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{edge or fill}" stroke-width="2"/>')
    E.append(f'<circle cx="{x-r*0.3}" cy="{y-r*0.36}" r="{r*0.27}" fill="#fff" opacity="0.6"/>')
def lipid(x, y, s):
    circle(x, y, s, "#EBB63C", "#C8912A", 0.8)
    E.append(f'<ellipse cx="{x-s*0.3}" cy="{y-s*0.35}" rx="{s*0.3}" ry="{s*0.2}" fill="#fff" opacity="0.5"/>')
def enzyme(cx, cy, w, h, label, fill, edge, tc, ls=16):
    rrect(cx-w/2, cy-h/2, w, h, 8, fill, edge); txt(cx, cy+5, label, ls, tc, "bold")
def protein(cx, cy, w, h, label, fill, edge, tc, ls=15):
    rrect(cx-w/2, cy-h/2, w, h, 6, fill, edge); txt(cx, cy+5, label, ls, tc)
def pdot(cx, cy):
    E.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="#C0392B"/>'); txt(cx, cy+3, "P", 12, "#fff", "bold")
def tee(x, y, color="#C0392B", size=12, vert=False):
    if vert: E.append(f'<line x1="{x}" y1="{y-size}" x2="{x}" y2="{y+size}" stroke="{color}" stroke-width="4"/>'); E.append(f'<line x1="{x-size}" y1="{y}" x2="{x+size}" y2="{y}" stroke="{color}" stroke-width="4"/>')
    else:    E.append(f'<line x1="{x-size}" y1="{y}" x2="{x+size}" y2="{y}" stroke="{color}" stroke-width="4"/>'); E.append(f'<line x1="{x}" y1="{y-size}" x2="{x}" y2="{y+size}" stroke="{color}" stroke-width="4"/>')
def ring4(cx, cy, col, edge, s=8, r=7):   # 甾核四环簇
    for dx, dy in ((-s, -s), (s, -s), (-s, s), (s, s)):
        E.append(f'<circle cx="{cx+dx}" cy="{cy+dy}" r="{r}" fill="{col}" stroke="{edge}" stroke-width="2"/>')
def foam(cx, cy, s):   # 泡沫细胞
    circle(cx, cy, s, "#EBC98A", "#C69A4E", 1.3); circle(cx-s*0.2, cy-s*0.25, s*0.36, "#B98A3E", "#B98A3E", 0.5)
def smc(cx, cy, s):    # 平滑肌（粉纺锤）
    E.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{s*2.3}" ry="{s*0.9}" fill="#DE9E9E" stroke="#B97A7A" stroke-width="0.9" transform="rotate(40 {cx} {cy})"/>')
def cell(cx, cy, rx, ry, fill, edge, sw=3):
    ell(cx, cy, rx, ry, fill, edge, sw)
def nucleus(cx, cy, r):
    ell(cx, cy, r*1.2, r, "#fff", "#8FA8C8", 2)
def membrane(x0, x1, y, col="#9FB6D0"):
    line(x0, y, x1, y, col, 3); line(x0, y+9, x1, y+9, col, 3)
def fibcap(cx, cy, rx, ry, a0, a1, w, color="#A9BFD0"):
    import math as _m
    E.append(f'<path d="M {cx+rx*_m.cos(_m.radians(a0)):.1f} {cy+ry*_m.sin(_m.radians(a0)):.1f} A {rx:.1f} {ry:.1f} 0 0 1 {cx+rx*_m.cos(_m.radians(a1)):.1f} {cy+ry*_m.sin(_m.radians(a1)):.1f}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')

def render(out_base="figure", canvas=(1500, 1000), mm=(150, 100), width_px=1772, height_px=1181):
    """拼 SVG 并导出三件套：{out_base}.svg / {out_base}.pdf / {out_base}_出版300dpi.png"""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{mm[0]}mm" height="{mm[1]}mm" viewBox="0 0 {canvas[0]} {canvas[1]}">\n'
           f'<rect width="{canvas[0]}" height="{canvas[1]}" fill="#FFFFFF"/>\n' + "\n".join(E) + "\n</svg>")
    with open(out_base + ".svg", "w", encoding="utf-8") as f:
        f.write(svg)
    if cairosvg:
        cairosvg.svg2pdf(url=out_base + ".svg", write_to=out_base + ".pdf")
        cairosvg.svg2png(url=out_base + ".svg", write_to=out_base + "_出版300dpi.png",
                         output_width=width_px, output_height=height_px)
    return out_base + ".svg"

def g7_check(svg_path):
    """G7 几何自检（元素不重叠），返回 (fails, hints)"""
    import subprocess, os
    ref = os.path.join(os.path.dirname(os.path.abspath(__file__)), "references", "overlap-check.py")
    if os.path.exists(ref):
        r = subprocess.run(["python3", ref, svg_path], capture_output=True, text=True)
        return r.returncode, r.stdout
    return 0, "(未找到 overlap-check.py，跳过)"
