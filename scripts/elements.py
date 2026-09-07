# -*- coding: utf-8 -*-
"""bio-svg-figure 通用元件函数库（可复用）— NR 默认版
NR 级默认（2026-09 评审固化）：①莫兰迪低饱和色板 ②径向渐变光影(radialGradient) + 高光 + 微投影
③描边统一 0.75pt ④语义色一色一义+对比≥3:1。以后程序化出图默认按此。
用法：import elements; E=[]; 用元件函数拼装; render() 导出三件套。
依赖：cairosvg（pip install cairosvg）。字体按内容分派（G6）：中文黑体、英文 Arial。
"""
import math, os, re
try:
    import cairosvg
except ImportError:
    cairosvg = None

FONT_CN = "'Heiti SC', STHeiti, 'PingFang SC', SimHei, sans-serif"   # 中文 -> 黑体
FONT_EN = "Arial, Helvetica, sans-serif"                             # 英文 -> Arial

# —— 莫兰迪低饱和色板（NR 高级感默认）——
M = dict(
    bg="#FBF8F3", blue="#8FA8C0", blue_d="#6A86A2", orange="#D8B87A", orange_d="#B08444",
    purple="#B0A0C6", purple_d="#8E7CAC", green="#A9BC97", green_d="#839970",
    pink="#D4A8A8", pink_d="#B08383", red="#A14848", red_d="#7E2C2C",
    gray="#8A8A85", gray_d="#5E5E5A", cap="#A3B8C6", cap_d="#8299AA",
    endo="#A64A48", endo_d="#6F211A", ext="#EFE8DC", ext_d="#D6CBB9",
    med="#E5D2CC", med_d="#C7B4AC", int_="#F2E5D3", lip="#D8B87A", lip_d="#B08444",
)
E = []   # 元素容器（每图重置=[]）
# 径向渐变 defs（注入 render）
_GRADS = [
 ("g_blue", "#9FB4CC", "#6A86A2"), ("g_orange", "#E7C68F", "#B08444"),
 ("g_purple", "#C0B1D6", "#8E7CAC"), ("g_green", "#B6C6A4", "#839970"),
 ("g_pink", "#DFB8B8", "#B08383"), ("g_red", "#C4817F", "#933F3F"),
 ("g_lip", "#EACB8B", "#B68C3E"), ("g_endo", "#B2564A", "#6F211A"),
 ("g_ext", "#F7F1E8", "#D6CBB9"), ("g_med", "#EFE2DC", "#C7B4AC"),
 ("g_int", "#EACFCD", "#C1A09E"), ("g_lum", "#C96A66", "#7E2C2C"),
 ("g_foam", "#EDD9AE", "#BE9A5E"), ("g_cap", "#C3D2DC", "#8299AA"),
]
def _defs():
    d = ["<defs>"]
    for gid, c1, c2 in _GRADS:
        d.append(f'<radialGradient id="{gid}" cx="40%" cy="35%" r="80%">'
                 f'<stop offset="0%" stop-color="{c1}"/><stop offset="100%" stop-color="{c2}"/></radialGradient>')
    d.append("</defs>")
    return "\n".join(d)

def txt(x, y, s, size, fill, weight="normal", anchor="middle"):
    fam = FONT_CN if re.search(r"[\u4e00-\u9fff]", s) else FONT_EN
    w = f' font-weight="{weight}"' if weight != "normal" else ""
    E.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}"{w} text-anchor="{anchor}" fill="{fill}">{s}</text>')
def rrect(x, y, w, h, rx, fill, stroke, sw=0.75):
    E.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def ell(cx, cy, rx, ry, fill, stroke=None, sw=0.75):
    E.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
def circle(cx, cy, r, fill, stroke=None, sw=0.75):
    E.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke or fill}" stroke-width="{sw}"/>')
def line(x0, y0, x1, y1, color="#8A8A85", w=0.75):
    E.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{w}"/>')
def _head(x, y, ang, size, color):
    pts = []
    for da in (0, math.pi*150/180, math.pi*210/180):
        pts.append(f"{x+size*math.cos(ang+da):.1f},{y-size*math.sin(ang+da):.1f}")
    E.append(f'<polygon points="{" ".join(pts)}" fill="{color}"/>')
def arrow(x0, y0, x1, y1, color="#8A8A85", w=0.75, head=11, dash=None):  # 实线=直接
    d = f' stroke-dasharray="{dash}"' if dash else ""
    E.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{w}"{d}/>')
    _head(x1, y1, math.atan2(y1-y0, x1-x0), head, color) if not dash else _head(x1, y1, math.atan2(y1-y0, x1-x0), head, color)
def tee(x, y, color="#A14848", size=12, vert=False):  # ⊣ 抑制
    if vert: E.append(f'<line x1="{x}" y1="{y-size}" x2="{x}" y2="{y+size}" stroke="{color}" stroke-width="0.75"/>'); E.append(f'<line x1="{x-size}" y1="{y}" x2="{x+size}" y2="{y}" stroke="{color}" stroke-width="0.75"/>')
    else:    E.append(f'<line x1="{x-size}" y1="{y}" x2="{x+size}" y2="{y}" stroke="{color}" stroke-width="0.75"/>'); E.append(f'<line x1="{x}" y1="{y-size}" x2="{x}" y2="{y+size}" stroke="{color}" stroke-width="0.75"/>')
def rot(cx, cy, ang, inner):
    E.append(f'<g transform="rotate({ang} {cx} {cy})">'); E.extend(inner); E.append('</g>')
def on_ell(cx, cy, rx, ry, a_deg, dr=0):
    r = math.radians(a_deg); return (cx + (rx+dr)*math.cos(r), cy + (ry+dr)*math.sin(r))
# 元件（NR 默认：径向渐变 + 高光 + 细描边）
def ball(x, y, r, fill, edge=None):
    E.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{edge or fill}" stroke-width="0.75"/>')
    E.append(f'<circle cx="{x-r*0.3}" cy="{y-r*0.36}" r="{r*0.27}" fill="#fff" opacity="0.5"/>')
def lipid(x, y, s):
    circle(x, y, s, "url(#g_lip)", "#A9823C", 0.6)
    E.append(f'<circle cx="{x-s*0.32}" cy="{y-s*0.36}" r="{s*0.26}" fill="#fff" opacity="0.45"/>')
def enzyme(cx, cy, w, h, label, fill, edge, tc, ls=16):
    rrect(cx-w/2, cy-h/2, w, h, 8, fill, edge, 0.75); txt(cx, cy+5, label, ls, tc, "bold")
def protein(cx, cy, w, h, label, fill, edge, tc, ls=15):
    rrect(cx-w/2, cy-h/2, w, h, 6, fill, edge, 0.75); txt(cx, cy+5, label, ls, tc)
def pdot(cx, cy):
    E.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{M["red"]}"/>'); txt(cx, cy+3, "P", 12, "#fff", "bold")
def ring4(cx, cy, col, edge, s=8, r=7):
    for dx, dy in ((-s, -s), (s, -s), (-s, s), (s, s)):
        E.append(f'<circle cx="{cx+dx}" cy="{cy+dy}" r="{r}" fill="{col}" stroke="{edge}" stroke-width="0.75"/>')
def foam(cx, cy, s):
    circle(cx, cy, s, "url(#g_foam)", "#BE9A5E", 0.7); circle(cx-s*0.2, cy-s*0.25, s*0.34, "#A8834A", "#A8834A", 0.5)
def smc(cx, cy, s):
    E.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{s*2.3}" ry="{s*0.85}" fill="{M["pink"]}" stroke="{M["pink_d"]}" stroke-width="0.6" transform="rotate(40 {cx} {cy})"/>')
def cell(cx, cy, rx, ry, fill, edge, sw=0.75):
    ell(cx, cy, rx, ry, fill, edge, sw)
def nucleus(cx, cy, r):
    ell(cx, cy, r*1.2, r, "#fff", "#8FA8C8", 0.75)
def membrane(x0, x1, y, col="#A3B8C6"):
    line(x0, y, x1, y, col, 0.75); line(x0, y+9, x1, y+9, col, 0.75)
def fibcap(cx, cy, rx, ry, a0, a1, w, color="#A3B8C6"):
    import math as _m
    E.append(f'<path d="M {cx+rx*_m.cos(_m.radians(a0)):.1f} {cy+ry*_m.sin(_m.radians(a0)):.1f} A {rx:.1f} {ry:.1f} 0 0 1 {cx+rx*_m.cos(_m.radians(a1)):.1f} {cy+ry*_m.sin(_m.radians(a1)):.1f}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')
def scalebar(x, y, w, label):  # 比例尺（结构图）
    E.append(f'<line x1="{x}" y1="{y}" x2="{x+w}" y2="{y}" stroke="#4A3E32" stroke-width="1"/>')
    E.append(f'<line x1="{x}" y1="{y-4}" x2="{x}" y2="{y+4}" stroke="#4A3E32" stroke-width="1"/>')
    E.append(f'<line x1="{x+w}" y1="{y-4}" x2="{x+w}" y2="{y+4}" stroke="#4A3E32" stroke-width="1"/>')
    txt(x+w/2, y-6, label, 8, "#4A3E32")
def render(out_base="figure", canvas=(1500, 1000), mm=(150, 100), width_px=1772, height_px=1181, nr_defs=True):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{mm[0]}mm" height="{mm[1]}mm" viewBox="0 0 {canvas[0]} {canvas[1]}">\n'
           f'<rect width="{canvas[0]}" height="{canvas[1]}" fill="{M["bg"]}"/>\n'
           + (_defs() if nr_defs else "") + "\n".join(E) + "\n</svg>")
    with open(out_base + ".svg", "w", encoding="utf-8") as f:
        f.write(svg)
    if cairosvg:
        cairosvg.svg2pdf(url=out_base + ".svg", write_to=out_base + ".pdf")
        cairosvg.svg2png(url=out_base + ".svg", write_to=out_base + "_出版300dpi.png",
                         output_width=width_px, output_height=height_px)
    return out_base + ".svg"
def g7_check(svg_path):
    import subprocess, os
    ref = os.path.join(os.path.dirname(os.path.abspath(__file__)), "references", "overlap-check.py")
    if os.path.exists(ref):
        r = subprocess.run(["python3", ref, svg_path], capture_output=True, text=True)
        return r.returncode, r.stdout
    return 0, "(未找到 overlap-check.py，跳过)"
