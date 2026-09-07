#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nr_enhance.py — 对 AI 导出的已有图 SVG 做「NR 进阶」质感增强（不改动排版）
在已有图上叠加：①莫兰迪低饱和 ②结构色→径向渐变 ③多层光影(4层stop) ④背景渐晕 ⑤通透+细描边0.75 ⑥比例尺(自适应viewBox)。
用法：python3 nr_enhance.py <in.svg> [另一个.svg ...] [--prefix <out前缀>] [--no-scalebar]
说明：只改质感（颜色/渐变/描边/背景/加比例尺），保留全部排版/文字/结构。基于 F15 验证流程固化。
依赖：cairosvg（~/.reasonix/venvs/pdf/bin/python3）。"""
import re, sys, os, colorsys
try:
    import cairosvg
except ImportError:
    cairosvg = None

# —— 莫兰迪映射（已知解剖色）——
MAP = {"#F4EDE3":"#EFE8DC","#F0D8D8":"#E5D2CC","#F7EADB":"#F2E5D3","#A32C2C":"#A14848",
"#B24949":"#A64A48","#EBB63C":"#D8B87A","#EBC98A":"#DDC79C","#B98A3E":"#B5935C",
"#DE9E9E":"#D4A8A8","#8E2222":"#933F3F","#4A3A2A":"#4A3E32","#B04A4A":"#A64A4A",
"#6B5A45":"#6B5E4C","#F0D6D6":"#E9CFCF","#FFFFFF":"#FFFFFF","#C69A4E":"#B9975E",
"#B97A7A":"#AE8A8A","#C8912A":"#B8923C","#A9BFD0":"#A3B8C6","#7E1F1F":"#7E2C2C",
"#7E2828":"#7E3030","#DBD0C0":"#CDC3B2","#E0B9B9":"#D4B1AC"}
# —— 结构色（莫兰迪后）→ 径向渐变 gid ——
FILL_URL = {"#A14848":"g_lum","#A64A48":"g_endo","#D8B87A":"g_lip","#DDC79C":"g_foam",
"#EFE8DC":"g_ext","#E5D2CC":"g_med","#F2E5D3":"g_int","#D4A8A8":"g_pink",
"#933F3F":"g_red","#A3B8C6":"g_cap"}

def hsl_morandi(hexc):
    """任意 hex → 低饱和莫兰迪（保色相，降饱和、控明度）"""
    h = hexc.lstrip('#')
    if len(h) == 3: h = "".join(c*2 for c in h)
    r, g, b = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
    hh, s, v = colorsys.rgb_to_hsv(r, g, b)
    if s > 0.62: s = 0.5 + (s - 0.62) * 0.4       # 仅高饱和适度降彩（保明快）
    v = min(v, 0.9)
    if v < 0.35: v = 0.4                           # 只救极暗，不压亮
    rr, gg, bb = colorsys.hsv_to_rgb(hh, s, v)
    return "#%02X%02X%02X" % (int(rr*255), int(gg*255), int(bb*255))

# 多层光影 defs（4 层 stop：高光→亮面→主色→暗反射）+ 背景渐晕
def defs(vbw, vbh):
    def g(gid, c1, c2, c3, c4):
        return (f'<radialGradient id="{gid}" cx="38%" cy="33%" r="82%">'
                f'<stop offset="0%" stop-color="{c1}"/><stop offset="32%" stop-color="{c2}"/>'
                f'<stop offset="72%" stop-color="{c3}"/><stop offset="100%" stop-color="{c4}"/></radialGradient>')
    return ("<defs>"
    + f'<radialGradient id="g_bg" cx="50%" cy="42%" r="92%"><stop offset="0%" stop-color="#FFFFFF"/><stop offset="72%" stop-color="#FCFAF6"/><stop offset="100%" stop-color="#F4F0E9"/></radialGradient>'
    + g("g_lum","#DC8B85","#C96A66","#A04848","#6E2323") + g("g_endo","#C96B5E","#B2564A","#8A3A30","#5E1812")
    + g("g_lip","#F2DCA4","#EACB8B","#C79A4C","#9C6F28") + g("g_foam","#F4E3BC","#EDD9AE","#C4A269","#9A7742")
    + g("g_ext","#FBF6EE","#F1EAE0","#DFD4C5","#D0C3B2") + g("g_med","#F2E6E0","#E9DBD4","#D3C0B8","#BCA79E")
    + g("g_int","#F0D9D6","#E8CECD","#CFB0AE","#B69896") + g("g_pink","#E8C6C6","#DCC0C0","#C2A0A0","#A58585")
    + g("g_red","#CF8F8D","#B67270","#9A4A48","#6E2323") + g("g_cap","#D3DFE5","#BCCDD8","#9FB4C2","#8299AA")
    + "</defs>")

def enhance(svg_path, prefix=None, scalebar=False, bg=True):
    raw = open(svg_path, encoding="utf-8").read()
    # viewBox
    vb = re.search(r'viewBox="([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)"', raw)
    if not vb: vbx, vby, vbw, vbh = 0, 0, 425, 283
    else: vbx, vby, vbw, vbh = map(float, vb.groups())
    # 莫兰迪映射（已知 + HSL 兜底全局 hex）
    hexes = set(re.findall(r'#[0-9A-Fa-f]{6}', raw))
    for hx in hexes:
        hu = hx.upper()
        tgt = MAP.get(hu) or MAP.get(hx.lower())
        if tgt: raw = raw.replace(hx, tgt)
        elif hu != "#FFFFFF": raw = raw.replace(hx, hsl_morandi(hu))
    # 通用光影：对每个非文字主填充色生成径向渐变并引用（保证全图有体积感）
    def gcol(h, dv):
        r,g,b=[int(h[i:i+2],16)/255 for i in (1,3,5)]
        return "#%02X%02X%02X"%(int(min(1,max(0,r+dv))*255),int(min(1,max(0,g+dv))*255),int(min(1,max(0,b+dv))*255))
    gx=[]
    for m in re.finditer(r'fill:(#[0-9a-fA-F]{6})', raw):
        h=m.group(1).upper()
        if h=="#FFFFFF": continue
        rr,gg,bb=[int(h[i:i+2],16)/255 for i in (1,3,5)]
        _s,_v=colorsys.rgb_to_hsv(rr,gg,bb)[1],colorsys.rgb_to_hsv(rr,gg,bb)[2]
        if _s<0.16 or _v<0.42 or _v>0.92: continue      # 暗文字/灰线/近白 不加渐变
        gid="gx_"+h[1:]
        gx.append((gid,h))
        raw=raw.replace("fill:"+h, f"fill:url(#{gid})")
    # 描边 0.75pt
    raw = re.sub(r'stroke-width:\s*([\d.]+)', 'stroke-width: 0.75', raw)
    # defs 组装（解剖渐变 + 通用光影渐变）
    d=defs(vbw,vbh)
    gx_str="".join(
        f'<radialGradient id="{gid}" cx="38%" cy="33%" r="82%">'
        f'<stop offset="0%" stop-color="{gcol(h,0.22)}"/><stop offset="33%" stop-color="{h}"/>'
        f'<stop offset="100%" stop-color="{gcol(h,-0.3)}"/></radialGradient>' for gid,h in gx)
    if gx_str: d=d.replace("</defs>", gx_str+"</defs>")
    if "<radialGradient id=\"g_bg\"" not in raw:
        raw=re.sub(r'(<svg[^>]*>)', r'\1\n'+d, raw, count=1)
    # 背景（默认不画整幅底色，纯白；--bg 才加，仅覆盖内容底的极浅渐晕）
    if bg:
        raw = re.sub(r'(<svg[^>]*>)', rf'\1\n<rect x="{vbx}" y="{vby}" width="{vbw}" height="{vbh}" fill="url(#g_bg)"/>', raw, count=1)
    # 比例尺（左下 8%宽，自适应）
    if scalebar:
        sw = vbw * 0.13; sx = vbx + vbw * 0.05; sy = vby + vbh * 0.9
        sb = (f'<g stroke="#4A3E32" stroke-width="0.9">'
              f'<line x1="{sx}" y1="{sy}" x2="{sx+sw}" y2="{sy}"/>'
              f'<line x1="{sx}" y1="{sy-4}" x2="{sx}" y2="{sy+4}"/>'
              f'<line x1="{sx+sw}" y1="{sy-4}" x2="{sx+sw}" y2="{sy+4}"/></g>')
        raw = raw.replace("</svg>", sb + "\n</svg>")
    import xml.dom.minidom; xml.dom.minidom.parseString(raw.encode())
    out = (prefix or os.path.splitext(svg_path)[0]) + "_NR进阶"
    open(out + ".svg", "w", encoding="utf-8").write(raw)
    if cairosvg:
        cairosvg.svg2png(url=out+".svg", write_to=out+"_出版300dpi.png", output_width=1772, output_height=1181)
        cairosvg.svg2pdf(url=out+".svg", write_to=out+".pdf")
    return out + ".svg"

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    prefix = None; sb = False; bgv = True
    for a in sys.argv[1:]:
        if a.startswith("--prefix="): prefix = a.split("=")[1]
        elif a == "--scalebar": sb = True
        elif a == "--no-bg": bgv = False
    if not args:
        print("用法: python3 nr_enhance.py <a.svg> [b.svg ...] [--prefix=out] [--scalebar] [--no-bg]"); sys.exit(1)
    for f in args:
        if not os.path.exists(f): print("!! 缺文件:", f); continue
        print("✅", enhance(f, prefix, sb, bgv))
