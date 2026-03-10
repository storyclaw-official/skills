#!/bin/bash
# OpenClaw 技能加载排查脚本
# 在服务器上执行: bash openclaw-skills-check.sh
# 或: chmod +x openclaw-skills-check.sh && ./openclaw-skills-check.sh

SKILLS_DIR="${HOME}/.openclaw/skills"
CONFIG_FILE="${HOME}/.openclaw/openclaw.json"

echo "========== 1. 检查技能目录结构 =========="
ls -la "$SKILLS_DIR" 2>/dev/null || { echo "错误: $SKILLS_DIR 不存在"; exit 1; }

echo ""
echo "========== 2. 检查每个技能是否有 SKILL.md =========="
for dir in "$SKILLS_DIR"/*/; do
  name=$(basename "$dir")
  if [ -f "${dir}SKILL.md" ]; then
    echo "✓ $name - 有 SKILL.md"
  else
    echo "✗ $name - 缺少 SKILL.md (Agent 无法加载此技能)"
  fi
done

echo ""
echo "========== 3. 检查 SKILL.md name 与目录名是否一致 =========="
for dir in "$SKILLS_DIR"/*/; do
  [ -f "${dir}SKILL.md" ] || continue
  name=$(basename "$dir")
  skill_name=$(grep '^name:' "${dir}SKILL.md" 2>/dev/null | head -1 | sed 's/name:\s*//' | tr -d ' ')
  if [ -n "$skill_name" ] && [ "$skill_name" = "$name" ]; then
    echo "✓ $name - name 一致"
  elif [ -n "$skill_name" ]; then
    echo "✗ $name - name 不一致 (目录=$name, SKILL.md name=$skill_name)"
  else
    echo "✗ $name - SKILL.md 缺少 name 字段"
  fi
done

echo ""
echo "========== 4. 检查 openclaw.json 配置 =========="
if [ -f "$CONFIG_FILE" ]; then
  echo "配置文件存在，检查 skills 相关配置..."
  if grep -q "skills" "$CONFIG_FILE"; then
    echo "--- skills 相关配置 ---"
    grep -A 20 '"skills"' "$CONFIG_FILE" | head -30
  else
    echo "未找到 skills 配置块（使用默认行为）"
  fi
else
  echo "未找到 $CONFIG_FILE"
fi

echo ""
echo "========== 5. 检查 python3 是否存在 =========="
if command -v python3 &>/dev/null; then
  echo "✓ python3: $(which python3)"
else
  echo "✗ python3 未安装（大部分技能需要 python3）"
fi

echo ""
echo "========== 6. 检查 .env 配置 =========="
if [ -f "${SKILLS_DIR}/.env" ]; then
  echo "✓ ${SKILLS_DIR}/.env 存在"
  echo "  包含的 KEY: $(grep -E '^[A-Z_]+=' "${SKILLS_DIR}/.env" 2>/dev/null | cut -d= -f1 | tr '\n' ' ')"
else
  echo "⚠ ${SKILLS_DIR}/.env 不存在（部分技能需要 API Key）"
fi

echo ""
echo "========== 7. 检查 generating-videos 目录内容 =========="
if [ -d "${SKILLS_DIR}/generating-videos" ]; then
  echo "generating-videos 目录内容:"
  ls -la "${SKILLS_DIR}/generating-videos/"
fi
