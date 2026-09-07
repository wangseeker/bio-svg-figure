# -*- coding: utf-8 -*-
"""bio-svg-figure 运行示例：脂肪酸从头合成（一小段通路）
直接运行：python3 examples/figure_example.py  → 在当前目录生成 figure_example.svg/pdf/出版300dpi.png
用 elements.py 的元件函数 + render() 导出；G7 重叠自检可选调 g7_check()。
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 让 examples 找到上级 elements.py
from elements import *   # noqa

if __name__ == "__main__":
    E.clear()  # 重置元素容器
    # 画一个简单通路：乙酰CoA → ACC(限速) → 丙二酰CoA → FASN → 软脂酸
    # 面板
    rrect(40, 120, 1420, 400, 16, "#F3F0F8", "#C7BCDC")
    txt(100, 160, "脂肪酸从头合成（示例）", 26, "#6F54A0", "bold", "start")
    # 节点（球/酶块/蛋白条）
    xs = [200, 430, 680, 940, 1200]
    cy = 320
    ball(xs[0], cy, 16, "#E8A87C", "#C87F4A"); txt(xs[0], cy+34, "乙酰CoA", 17, "#7A4A12")
    arrow(xs[0]+22, cy, xs[1]-52, cy, "#6F54A0", 3, 12)
    enzyme(xs[1], cy, 110, 48, "ACC", "#9B7FC0", "#6F54A0", "#fff", 17)
    txt(xs[1], cy+44, "限速酶", 15, "#4A2F6A")
    arrow(xs[1]+60, cy, xs[2]-52, cy, "#6F54A0", 3, 12)
    ball(xs[2], cy, 14, "#E8A87C", "#C87F4A"); txt(xs[2], cy+32, "丙二酰CoA", 16, "#7A4A12")
    arrow(xs[2]+20, cy, xs[3]-52, cy, "#6F54A0", 3, 12)
    enzyme(xs[3], cy, 110, 48, "FASN", "#4A7DBF", "#2F5A8F", "#fff", 17)
    txt(xs[3], cy+44, "每次+2C · 耗NADPH", 14, "#2F5A8F")
    arrow(xs[3]+60, cy, xs[4]-40, cy, "#6F54A0", 3, 12)
    protein(xs[4], cy, 150, 36, "软脂酸 C16:0", "#8FBF8F", "#3A5F2D", "#fff", 16)
    # 底部一句话（G2：图底 ≤2 行）
    txt(750, 470, "以乙酰CoA为底物，ACC为限速酶，FASN 每轮延长2碳、消耗NADPH。", 16, "#6B5A45")

    out = render("figure_example")   # 生成 figure_example.svg/pdf/出版300dpi.png
    print("✅ 已生成:", out)
    # G7 自检（可选）：元素不重叠
    rc, msg = g7_check(out)
    print(msg)
