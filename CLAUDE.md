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

## 技能命名前缀规范

- **`giggle-`**: giggle.pro 组合工作流（AI导演），涉及多步编排
- **`gen-`**: 原子生成能力，单一 API 调用完成

新增技能时必须遵循此前缀规则。

## Claude Code 配置层级

| 文件 | 作用 | 是否提交 git |
|------|------|-------------|
| `./CLAUDE.md` | 团队共享的项目配置（本文件） | 是 |
| `./.claude/CLAUDE.md` | 个人项目配置（API Key 备忘、本地调试习惯等） | 否 |
| `~/.claude/CLAUDE.md` | 个人全局配置（所有项目通用偏好） | 否 |

优先级: `.claude/CLAUDE.md` > `CLAUDE.md` > `~/.claude/CLAUDE.md`

`.claude/` 目录已在 `.gitignore` 中忽略，个人配置不会提交到仓库。

## 环境变量文件命名规范

| 文件 | 用途 | 是否提交 git |
|------|------|-------------|
| `env.example` | 环境变量示例模板（无点号前缀） | 是 |
| `.env` | 实际环境变量配置（含敏感信息） | 否（已在 .gitignore） |

根目录 `env.example` 包含所有平台的 API Key 配置，各技能目录的 `env.example` 指向根目录。

### 环境变量一览

| 变量名 | 用途 | 使用技能 |
|--------|------|---------|
| `GIGGLE_API_KEY` | 所有技能共用的统一 API Key | 全部技能 |

## 技能目录结构规范

每个技能目录必须包含：

```
skill-name/
├── SKILL.md              # 必须：YAML frontmatter（name + description）+ 交互流程文档
├── scripts/              # API 调用 Python 脚本
├── env.example           # API Key 配置模板（指向根目录 env.example）
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
| `giggle-aimv` | MV 生成 | giggle.pro 托管模式 | `scripts/trustee_api.py` |
| `giggle-aiwriter` | 姜文风格剧本生成 | 纯 LLM（无外部 API） | 无脚本 |
| `giggle-video` | 视频生成路由入口 | 路由至具体模型 | 无脚本 |
| `gen-music` | AI 音乐生成 | kie.ai / Suno V5 | `scripts/kie_suno_api.py` |
| `gen-image` | AI 图像生成 | kie.ai / Nano Banana Pro | `scripts/kie_nano_banana_api.py` |
| `gen-video` | Grok-Imagine 视频生成 | kie.ai / grok-imagine | `text_to_video.py`, `image_to_video.py` |

## 架构要点

### API Key 配置三级优先级

命令行参数 `--api-key` > 环境变量 > `.env` 文件

### .env 文件搜索路径

所有脚本统一使用三级搜索路径加载 `.env` 文件：

1. 当前工作目录 `./.env`
2. 技能根目录 `<skill-dir>/.env`
3. 项目根目录 `<skill-dir>/../.env`（推荐）

### 视频技能路由架构

`giggle-video` 是统一入口路由，根据模型类型分发到具体实现目录（如 `gen-video`）。添加新视频模型只需：创建模型目录 + 在路由 SKILL.md 注册表中添加一行。

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
4. 创建 `env.example` 配置模板（指向根目录）
5. 如果是视频类技能，在 `giggle-video/SKILL.md` 路由表中注册
