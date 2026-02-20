# StoryClaw Skills

Claude Code 技能集合仓库，封装多种 AI 生成能力，包括音乐、图像、视频、MV 和剧本生成。

## 技能列表

| 技能 | 功能 | API 服务 |
|------|------|---------|
| [giggle-aimv](./giggle-aimv/) | AI 音乐视频生成 | giggle.pro 托管模式 |
| [giggle-aiwriter](./giggle-aiwriter/) | 姜文风格剧本生成 | 纯 LLM |
| [giggle-video](./giggle-video/) | 视频生成统一路由入口 | 路由至具体模型 |
| [gen-music](./gen-music/) | AI 音乐生成 | kie.ai / Suno V5 |
| [gen-image](./gen-image/) | AI 图像生成 | kie.ai / Nano Banana Pro |
| [gen-video](./gen-video/) | Grok-Imagine 视频生成 | kie.ai / grok-imagine |

## 技能结构

每个技能目录遵循统一结构：

```
skill-name/
├── SKILL.md              # 技能描述和交互流程（YAML frontmatter + Markdown）
├── scripts/              # API 调用 Python 脚本
├── .env.example          # API Key 配置模板
└── references/           # 辅助参考文档（可选）
```

## 快速开始

### 环境准备

```bash
# 安装依赖（以音乐生成技能为例）
pip install -r gen-music/requirements.txt

# 配置 API Key
cp gen-music/.env.example gen-music/.env
# 编辑 .env 填入你的 KIE_API_KEY
```

### API Key 获取

- **kie.ai**: https://kie.ai/api-key
- **giggle.pro**: 参考 giggle-aimv/SKILL.md 中的说明

### API Key 配置优先级

命令行参数 `--api-key` > 环境变量 `KIE_API_KEY` > `.env` 文件

### 使用示例

```bash
# AI 音乐生成
python3 gen-music/scripts/kie_suno_api.py --prompt "一首轻快的流行歌曲" --download

# AI 图像生成
python3 gen-image/scripts/kie_nano_banana_api.py --prompt "赛博朋克城市夜景" --download

# 文生视频
python3 gen-video/scripts/text_to_video.py --prompt "日落海滩"

# 图生视频
python3 gen-video/scripts/image_to_video.py --image ./input.jpg --prompt "缓慢推进"
```

### 通用参数

| 参数 | 说明 |
|------|------|
| `--api-key` | 指定 API Key |
| `--json` | 输出结构化 JSON |
| `--download` | 自动下载到 ~/Downloads/ |
| `--no-wait` | 异步模式，不等待结果 |
| `--query --task-id ID` | 查询异步任务状态 |

## 新增技能

1. 创建技能目录（kebab-case 命名）
2. 编写 `SKILL.md`（含 YAML frontmatter: name + description）
3. 在 `scripts/` 下编写 API 封装脚本
4. 创建 `.env.example` 配置模板
5. 视频类技能需在 `giggle-video/SKILL.md` 路由表中注册

## 许可证

私有仓库，仅限内部使用。
