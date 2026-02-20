# gen-music 技能

## 安装
claude skills install gen-music.skill

## 核心功能
✅ title      - 音乐标题
✅ prompt     - 提示词/歌词
✅ audioUrl   - MP3 下载链接
✅ tags       - 风格标签
✅ 跨平台下载 - Mac/Windows/Linux 自动下载到本地

## 快速测试

### 1. 设置 API 密钥（推荐使用 .env 文件）

**方法 1: 使用 .env 文件（推荐）**
```bash
# 复制示例文件并编辑
cp .env.example .env
# 编辑 .env，添加: KIE_API_KEY=your-api-key

# 安装依赖
pip install python-dotenv
```

**方法 2: 设置环境变量**
```bash
# macOS/Linux
export KIE_API_KEY="your-api-key"

# Windows (PowerShell)
$env:KIE_API_KEY="your-api-key"
```

### 2. 生成音乐
```bash
# 最简单方式（推荐）
python3 scripts/kie_suno_api.py --prompt "一首关于夏天的欢快流行歌"

# 自动下载到本地
python3 scripts/kie_suno_api.py --prompt "一首关于夏天的欢快流行歌" --download

# JSON 格式输出
python3 scripts/kie_suno_api.py --prompt "测试" --json
```

## 核心原则
智能分析 → 简化优先 → 按需升级 → 自动下载

## 文档
- SKILL.md : 完整使用文档（推荐阅读）
- TEST_OUTPUT_EXAMPLE.md : 输出格式示例

## 版本信息
- 版本: v2.2
- 日期: 2026-02-13
- 主要更新:
  - ✅ 重构文档结构，实施渐进式披露
  - ✅ 添加跨平台 MP3 下载功能
  - ✅ 优化交互式引导流程
  - ✅ 简化模式优先推荐
  - 🐛 修复下载功能：使用已返回的 audioUrl，不重新生成
  - ✅ 统一文件命名：{title}_1.mp3, {title}_2.mp3
  - ✨ 支持 .env 文件配置 API 密钥（推荐方式）
