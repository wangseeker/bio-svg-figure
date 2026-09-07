#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G7 空间不重叠几何自检（bio-svg-figure / overlap-check）
用法：python3 overlap-check.py <fN_pub.svg> [--tol=N] [--quiet]
FAIL = 硬阻断：①text-text 相交 ②text 出画布 ③箭头端点完全悬空(离所有节点>12px且不在任何形状内)
HINT = 提示（不计失败，防误报）：④text 中心落入色块（已排除 enzyme/protein 等自带标签容器）⑤箭头深入形状内部>25px
exit：FAIL=0 →0；有 FAIL →1。仅依赖 re/math。
"""
import re, math, sys

def load(path): return open(path, encoding="utf-8").read()

def cw(ch, fs):
    o = ord(ch)
    if ch == " ": return 0.32 * fs
    return fs if o > 0x2E7F else 0.58 * fs

def tbox(x, y, fs, s, anchor):
    w = sum(cw(c, fs) for c in s)
    x0 = x - w/2 if anchor == "middle" else (x - w if anchor == "end" else x)
    return (x0, y - fs, x0 + w, y)

def parse(raw):
    texts = []
    for m in re.finditer(r'<text\b[^>]*?x="([\d.-]+)"[^>]*?y="([\d.-]+)"[^>]*?>([^<]*)</text>', raw):
        seg, t = m.group(0), m.group(3)
        fs = float(re.search(r'font-size="([\d.]+)"', seg).group(1)) if re.search(r'font-size="([\d.]+)"', seg) else 15.0
        an = (re.search(r'text-anchor="(\w+)"', seg) or [None, "middle"])[1]
        texts.append((t, tbox(float(m.group(1)), float(m.group(2)), fs, t, an)))
    shapes = []
    for m in re.finditer(r'<(rect|ellipse|circle)\b([^>]*?)/?>', raw):
        tag, at = m.group(1), m.group(2)
        g = lambda k: (lambda mm: float(mm.group(1)) if mm else None)(re.search(k + r'="([\d.]+)"', at))
        if tag == "rect":
            x, y, w, h = g('x'), g('y'), g('width'), g('height')
            if None in (x, y, w, h) or w < 1: continue
            shapes.append(("rect", x, y, x + w, y + h))
        elif tag == "ellipse":
            cx, cy, rx, ry = g('cx'), g('cy'), g('rx'), g('ry')
            if None in (cx, cy, rx, ry): continue
            shapes.append(("ellipse", cx, cy, rx, ry))
        else:
            cx, cy, r = g('cx'), g('cy'), g('r')
            if None in (cx, cy, r): continue
            shapes.append(("circle", cx, cy, r, r))
    lines = []
    for m in re.finditer(r'<line\b([^>]*?)/?>', raw):
        at = m.group(1)
        g = lambda k: (lambda mm: float(mm.group(1)) if mm else None)(re.search(k + r'="([\d.-]+)"', at))
        x1, y1, x2, y2 = g('x1'), g('y1'), g('x2'), g('y2')
        wm = re.search(r'stroke-width="([\d.]+)"', at)
        if None in (x1, y1, x2, y2): continue
        if wm and float(wm.group(1)) < 1.5: continue
        lines.append(((x1, y1), (x2, y2)))
    return texts, shapes, lines

def boundary(px, py, sh):
    """点到形状边界的带符号距离（<0 在内部）"""
    if sh[0] == "rect":
        _, x0, y0, x1, y1 = sh
        if x0 <= px <= x1 and y0 <= py <= y1:
            return -min(px - x0, x1 - px, py - y0, y1 - py)
        dx = max(x0 - px, 0, px - x1); dy = max(y0 - py, 0, py - y1)
        return math.hypot(dx, dy)
    else:
        _, cx, cy, rx, ry = sh
        e = math.sqrt(((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2)
        return (e - 1) * min(rx, ry)

def is_label_holder(sh):
    """是否是承载自带标签的小块（enzyme/protein/小圆）"""
    if sh[0] == "rect":
        _, x0, y0, x1, y1 = sh
        return (x1 - x0) < 220 and (y1 - y0) < 75
    if sh[0] == "circle":
        return sh[3] < 14
    return max(sh[3], sh[4]) < 14

def check(path, tol=2.0):
    raw = load(path)
    texts, shapes, lines = parse(raw)
    fails, hints = [], []
    # 1 text-text 相交 (FAIL)
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            (ta, a), (tb, b) = texts[i], texts[j]
            ox = min(a[2], b[2]) - max(a[0], b[0]); oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > tol and oy > tol:
                fails.append(f"[重叠] '{ta}' 与 '{tb}' 交叠 {ox:.0f}x{oy:.0f}px")
    # 2 出画布 (FAIL)
    for t, b in texts:
        if b[0] < -tol or b[2] > 1500 + tol or b[1] < -tol or b[3] > 1000 + tol:
            fails.append(f"[出界] '{t}' ({b[0]:.0f},{b[1]:.0f})-({b[2]:.0f},{b[3]:.0f})")
    # 3 text 中心落入"非自带"色块 (HINT)
    for t, b in texts:
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        for sh in shapes:
            if is_label_holder(sh): continue
            if boundary(cx, cy, sh) < 0 and sh[0] == "rect" and (sh[3]-sh[1]) < 700 and (sh[4]-sh[2]) < 400:
                hints.append(f"[text在块内] '{t}' 中心({cx:.0f},{cy:.0f}) ∈ rect({sh[1]:.0f},{sh[2]:.0f},{sh[3]-sh[1]:.0f}x{sh[4]-sh[2]:.0f})")
            elif boundary(cx, cy, sh) < 0 and sh[0] in ("ellipse", "circle") and max(sh[3], sh[4]) <= 120:
                hints.append(f"[text在块内] '{t}' 中心({cx:.0f},{cy:.0f}) ∈ {sh[0]}({sh[2]:.0f},{sh[3]:.0f},r{sh[4]:.0f})")
    # 4 箭头端点：悬空(FAIL) / 深扎(HINT)
    for (p0, p1) in lines:
        for pt in (p0, p1):
            inside_flag, min_gap = False, None
            for sh in shapes:
                d = boundary(pt[0], pt[1], sh)
                if d < 0: inside_flag = True
                ad = abs(d)
                if min_gap is None or (ad < min_gap): 
                    # 记录最小绝对距离，同时保留"最近的是内部"的判断
                    pass
            # 直接计算：最近边界 gap 与 是否在某形状内
            gaps = [abs(boundary(pt[0], pt[1], s)) for s in shapes]
            if not gaps: continue
            gap = min(gaps)
            if not inside_flag and gap > 12:
                fails.append(f"[箭头悬空] 端点({pt[0]:.0f},{pt[1]:.0f}) 距最近节点 {gap:.0f}px")
            elif inside_flag and gap > 25:
                hints.append(f"[箭头入块] 端点({pt[0]:.0f},{pt[1]:.0f}) 深入形状 {gap:.0f}px（可能是入胞设计，请人眼确认）")
    return fails, hints

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tol, quiet = 2.0, False
    for a in sys.argv[1:]:
        if a == "--quiet": quiet = True
        elif a.startswith("--tol="): tol = float(a.split("=")[1])
    if not args:
        print("用法: python3 overlap-check.py <fN_pub.svg> [--tol=N] [--quiet]"); return 1
    fails, hints = check(args[0], tol)
    print(f"=== G7 自检 {args[0]}  (tol={tol}) ===")
    if not fails: print("✔ FAIL：0（无重叠/无出界/无悬空）")
    else:
        print(f"✘ FAIL：{len(fails)} 处——禁止直接交付："); [print("  " + f) for f in fails] if not quiet else None
    if hints:
        print(f"◐ HINT：{len(hints)} 处（人眼确认）："); [print("  " + h) for h in hints] if not quiet else None
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
