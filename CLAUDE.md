# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

storyclaw-skills 是 Claude Code Skills 技能集合仓库，封装多种 AI 生成能力（音乐、图像、视频、MV、剧本），每个技能目录独立自洽，通过 SKILL.md 对外暴露能力描述，通过 Python 脚本封装 API 调用。

## 技术栈

- **语言**: Python 3
- **HTTP**: requests 库
- **环境变量**: python-dotenv（可选）
- **API 平台**: kie.ai（Suno、Nano Banana、Grok-Imagine）、giggle.pro（MV 托管）
- **技能格式**: SKILL.md（YAML frontmatter + Markdown）

## 技能目录结构规范

每个技能目录必须包含：

```
skill-name/
├── SKILL.md              # 必须：YAML frontmatter（name + description）+ 交互流程文档
├── scripts/              # API 调用 Python 脚本
├── .env.example          # API Key 配置模板
└── references/           # 可选：辅助参考文档
```

### SKILL.md frontmatter 格式

```yaml
---
name: skill-name
description: 中文描述，包含触发场景和关键词
---
```

## 技能一览

| 技能目录 | 功能 | API 服务 | 核心脚本 |
|---------|------|---------|---------|
| `ad-generating-ai-music` | AI 音乐生成 | kie.ai / Suno V5 | `scripts/kie_suno_api.py` |
| `ad-nano-banana` | AI 图像生成 | kie.ai / Nano Banana Pro | `scripts/kie_nano_banana_api.py` |
| `generate-mv` | MV 生成 | giggle.pro 托管模式 | `scripts/trustee_api.py` |
| `generating-scripts` | 姜文风格剧本生成 | 纯 LLM（无外部 API） | 无脚本 |
| `generating-videos` | 视频生成路由入口 | 路由至具体模型 | 无脚本 |
| `generating-videos-with-grok-imagine` | Grok-Imagine 视频生成 | kie.ai / grok-imagine | `text_to_video.py`, `image_to_video.py` |

## 架构要点

### API Key 配置三级优先级

命令行参数 `--api-key` > 环境变量 `KIE_API_KEY` > `.env` 文件

### 视频技能路由架构

`generating-videos` 是统一入口路由，根据模型类型分发到具体实现目录（如 `generating-videos-with-grok-imagine`）。添加新视频模型只需：创建模型目录 + 在路由 SKILL.md 注册表中添加一行。

### Python 脚本规范

- 使用 `argparse` 处理命令行参数
- 支持 `--json` 输出结构化 JSON
- 支持 `--download` 自动下载到 `~/Downloads/`
- 支持 `--no-wait` 异步模式 + `--query --task-id` 查询任务状态
- 错误信息输出到 stderr
- 使用 `Enum` 类定义常量

### 交互引导规范

技能通过 `AskUserQuestion` 工具引导用户：智能分析输入，信息充足直接执行，不足则分步询问，每步只问一个维度，提供选项列表。

## 新增技能流程

1. 创建技能目录，命名使用 kebab-case
2. 编写 SKILL.md（含 YAML frontmatter）
3. 在 `scripts/` 下编写 API 封装脚本
4. 创建 `.env.example` 配置模板
5. 如果是视频类技能，在 `generating-videos/SKILL.md` 路由表中注册
