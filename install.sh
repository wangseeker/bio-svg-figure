#!/usr/bin/env bash
# bio-svg-figure 一键安装（供 Codex / Claude Code / 任意 agent 使用）
# 用法：bash install.sh [--target <skills 目录>]
#   --target 缺省时自动检测：$CODEX_HOME/skills → ~/.codex/skills → ~/.claude/skills →
#                            ~/.config/claude/skills → ./skills （找不到用 ~/.codex/skills）
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
NAME="bio-svg-figure"

echo "== 检查 Python 与 cairosvg =="
PY="${PYTHON:-python3}"
if "$PY" -c "import cairosvg" 2>/dev/null; then
  echo "   cairosvg 已装"
else
  echo "   安装 cairosvg..."
  "$PY" -m pip install --quiet cairosvg || echo "   !! pip 失败，请手动: pip install cairosvg"
fi

TARGET=""
while [ $# -gt 0 ]; do case "$1" in
  --target) TARGET="$2"; shift 2 ;;
  *) shift ;;
esac; done
if [ -z "$TARGET" ]; then
  for c in "${CODEX_HOME:-}/skills" "$HOME/.codex/skills" "$HOME/.claude/skills" "$HOME/.config/claude/skills" "./skills"; do
    if [ -n "$c" ] && [ -d "${c%/skills}" ]; then TARGET="$c"; break; fi
  done
  [ -z "$TARGET" ] && TARGET="$HOME/.codex/skills"
fi
mkdir -p "$TARGET"
echo "== 部署到: $TARGET/$NAME =="
rm -rf "$TARGET/$NAME"
mkdir -p "$TARGET/$NAME/references"
cp -R "$DIR/SKILL.md" "$DIR/elements.py" "$TARGET/$NAME/"
cp -R "$DIR/references/." "$TARGET/$NAME/references/"
[ -d "$DIR/examples" ] && cp -R "$DIR/examples" "$TARGET/$NAME/"
[ -f "$DIR/SOP-教材矢量作图指南.md" ] && cp "$DIR/SOP-教材矢量作图指南.md" "$TARGET/$NAME/"

echo
echo "✅ 安装完成：$TARGET/$NAME"
cat <<'USAGE'
────────────────────────────────────────────────────────────
  在 Codex / Claude 中如何用：
    直接对 agent 说，例如：
      「用 bio-svg-figure 画一张《XX 通路》示意图」
      「/bio-svg-figure 画 XX 机制图」
    agent 会读 SKILL.md（含 G1 元件映射 / G6 字体分派 / G7 重叠自检），
    用 elements.py 元件函数 + cairosvg 生成三件套（svg / pdf / 300dpi png）。

  手动跑示例：
    python3 <skill>/examples/figure_example.py   # 用 elements.py 的 render() 导出
  G7 自检（元素不重叠）：
    python3 <skill>/references/overlap-check.py <fN_pub.svg>

  依赖：python3 + cairosvg；中文字体黑体(系统 Heiti/SimHei)+英文 Arial（G6 自动分派）。
────────────────────────────────────────────────────────────
USAGE
