# ad-generating-ai-music 技能

## 安装
claude skills install ad-generating-ai-music.skill

## 输出字段（已确认）
✅ title      - 音乐标题
✅ prompt     - 提示词/歌词
✅ audioUrl   - 下载链接
✅ tags       - 风格标签

## 快速测试
export KIE_API_KEY="your-api-key"
python3 scripts/kie_suno_api.py --prompt "测试" --json

## 文档
- SKILL.md               : 完整使用文档
- TEST_OUTPUT_EXAMPLE.md : 输出格式示例
- UPDATE_SUMMARY.md      : 更新记录

版本: v1.2 | 日期: 2026-02-11
