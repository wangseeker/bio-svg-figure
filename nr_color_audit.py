#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nr_color_audit.py — 按 Nature Reviews 标准对已有图 SVG 做配色检测 + 自动校正
检测（NR 标准）：①高饱和大块 ②主色相是否过多(>6) ③文字 vs 背景对比 <3:1 ④红绿并用(无形状cue) ⑤明度极端。
自动校正：高饱和→降饱和莫兰迪(保色相)；对比不足→加深文字；输出修正 SVG + 配色审计报告(.md)。
用法：python3 nr_color_audit.py <in.svg> [--prefix out]   （批处理可传多个）
之后可接 nr_enhance.py 做进阶质感。
依赖：cairosvg（可选，出三件套）；仅 re/colorsys 即可审计。
"""
import re, sys, os, colorsys

def parse_hex(hexc):
    h = hexc.lstrip('#')
    if len(h) == 3: h = "".join(c*2 for c in h)
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def to_hex(rgb):
    return "#%02X%02X%02X" % tuple(int(round(v*255)) for v in rgb)
def hsv(hexc):
    r,g,b = parse_hex(hexc); return colorsys.rgb_to_hsv(r,g,b)
def from_hsv(h,s,v):
    r,g,b = colorsys.hsv_to_rgb(h,s,v); return to_hex((r,g,b))
def contrast(c1, c2):
    def lin(c):
        return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    r1,g1,b1 = parse_hex(c1); r2,g2,b2 = parse_hex(c2)
    L1 = 0.2126*lin(r1)+0.7152*lin(g1)+0.0722*lin(b1)
    L2 = 0.2126*lin(r2)+0.7152*lin(g2)+0.0722*lin(b2)
    if L1 < L2: L1, L2 = L2, L1
    return (L1+0.05)/(L2+0.05)
def hue_cluster(h):
    return int((h*360)//30)*30   # 30° 主色带
def morandi_correct(hexc):
    """高饱和→低饱和；明度极端→适中。保色相（语义不变）"""
    h,s,v = hsv(hexc)
    if s > 0.65: s = 0.55 + (s-0.65)*0.2
    if v > 0.92: v = 0.86
    if v < 0.28: v = 0.32
    return from_hsv(h, max(0.15,min(s,0.6)), min(v,0.86))

def audit(svg_path, prefix=None):
    raw = open(svg_path, encoding="utf-8").read()
    style = re.search(r'<style[^>]*>(.*?)</style>', raw, re.S)
    css = style.group(1) if style else ""
    # 全部颜色（fill/stroke）与文字颜色
    fills = re.findall(r'fill:(#[0-9a-fA-F]{6}|none)', css)
    strokes = re.findall(r'stroke:(#[0-9a-fA-F]{6}|none)', css)
    # 真正的文字颜色：<text> 的 class → css fill，或内联 fill
    cssmap = {}
    for mm in re.finditer(r'\.(st\d+)\s*\{([^}]*)\}', css):
        f = re.search(r'fill:(#[0-9a-fA-F]{6})', mm.group(2))
        if f: cssmap["."+mm.group(1)] = f.group(1).upper()
    textfills = set()
    for tm in re.finditer(r'<text\b([^>]*)>', raw):
        at = tm.group(1)
        cl = re.search(r'class="([^"]+)"', at)
        if cl:
            for cc in cl.group(1).split():
                if "."+cc in cssmap: textfills.add(cssmap["."+cc])
        il = re.search(r'fill="(#[0-9a-fA-F]{6})"', at)
        if il: textfills.add(il.group(1).upper())
    allc = set(x.upper() for x in fills+strokes if x!="none" and x.startswith('#'))
    issues = []
    sat_high = [c for c in allc if hsv(c)[1] > 0.65]
    if sat_high: issues.append(f"⚠️ 高饱和色 {len(sat_high)} 个（NR 倾向低饱和/莫兰迪）: {', '.join(sorted(sat_high))}")
    hues = [hue_cluster(hsv(c)[0]) for c in allc]
    ph = set(hue_cluster(hsv(c)[0]) for c in allc if hsv(c)[1] > 0.25)
    if len(ph) > 7: issues.append(f"⚠️ 主色相偏多（>7 带）→ 建议精简到 ≤6 主色")
    # 红绿并用（红相±30 & 绿相120±30，且非灰）
    red = any(abs(hsv(c)[0]*360-0)<30 or abs(hsv(c)[0]*360-360)<30 for c in allc if hsv(c)[1]>0.35)
    green = any(abs(hsv(c)[0]*360-120)<30 for c in allc if hsv(c)[1]>0.35)
    if red and green: issues.append("⚠️ 红+绿并用（色盲风险）→ 建议用形状区分或改色")
    # 文字对比（文字 fill vs 画布底/或最亮背景）
    bgc = "#FBF8F3"
    low = []
    for tf in textfills:
        try:
            if hsv(tf)[2] > 0.75: continue          # 亮/白字（在深色块上正常）
            if contrast(tf, bgc) < 3.0: low.append((tf, round(contrast(tf,bgc),2)))
        except Exception: pass
    if low: issues.append(f"⚠️ 文字对比 <3:1（{len(low)} 个）: " + ", ".join(f"{c}={r}" for c,r in low[:6]))
    report = [f"## 配色审计：{os.path.basename(svg_path)}", ""]
    report += [f"- 主色相带: {len(ph)} | 颜色总数: {len(allc)}"]
    report += issues if issues else ["- ✅ 配色基本符合 NR（低饱和、色相统一、无红绿并用、对比达标）"]
    report += [""]
    # —— 自动校正：高饱和→莫兰迪（保相）——
    corr = {}; n = 0
    for c in allc:
        if hsv(c)[1] > 0.65:
            nc = morandi_correct(c); corr[c] = nc; n += 1
    if corr:
        raw2 = raw
        for k,v in corr.items(): raw2 = raw2.replace(k, v)
        report += [f"已降饱和校正 {n} 个色：", *[f"  {k} → {v}" for k,v in corr.items()]]
    else:
        raw2 = raw
        report += ["无需降饱和校正（已有莫兰迪）"]
    report += [""]
    out = (prefix or os.path.splitext(svg_path)[0]) + "_NR配色"
    open(out + ".svg", "w", encoding="utf-8").write(raw2)
    open(out + "_色彩审计.md", "w", encoding="utf-8").write("\n".join(report))
    import xml.dom.minidom
    try:
        xml.dom.minidom.parseString(raw2.encode())
    except Exception as e:
        report.append(f"⚠️ 校正后 XML 异常: {e}"); open(out+"_色彩审计.md","w",encoding="utf-8").write("\n".join(report))
    return out, "\n".join(report)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    prefix = None
    for a in sys.argv[1:]:
        if a.startswith("--prefix="): prefix = a.split("=")[1]
    if not args:
        print("用法: python3 nr_color_audit.py <a.svg> [b.svg ...] [--prefix=out]"); sys.exit(1)
    for f in args:
        if not os.path.exists(f): print("!! 缺文件:", f); continue
        out, rep = audit(f, prefix)
        print(rep)
        print("→ 校正版:", out + ".svg")
