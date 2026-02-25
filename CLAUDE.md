# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Claude Code / OpenClaw Agent 技能集合，每个技能目录是独立的 Skill 单元，向 Agent 提供 AI 创意内容生成能力（视频、MV、图像、音乐、剧本）。

## 技能目录命名规范

| 前缀 | 含义 |
|------|------|
| `giggle-*` | 调用 Giggle.pro Trustee Mode API（AI 导演工作流） |
| `kie-*` | 调用 kie.ai 平台 API |
| `generating-*` | 路由入口，不直接调用 API |

当前技能：`giggle-drama`、`giggle-aimv`、`giggle-music`、`giggle-image`、`giggle-screenplay`（纯 LLM）、`kie-nano-banana`、`kie-grok-imagine`、`generating-videos`（路由）。

## 架构

### 每个技能目录的结构

```
<skill-name>/
├── SKILL.md          # Skill 定义：frontmatter + Agent 执行指令
├── env.example       # 独立部署时的环境变量参考（无 API Key 的技能无此文件）
└── scripts/          # Python API 客户端（直接可执行）
```

**SKILL.md frontmatter** 格式（必需字段）：
```yaml
---
name: <与目录名完全一致>
description: <触发条件和功能描述，直接影响 Agent 选择此 Skill>
user-invocable: true
metadata: {"openclaw": {"requires": {"env": ["API_KEY"], "bins": ["python3"]}, ...}}
---
```

`name` 字段必须与目录名一致，不一致会导致 Skill 无法正确注册。

### 两层 API 调用模式

**giggle-\* 技能**（Trustee Mode）：长耗时工作流，采用「同步等待 + Cron 兜底」双路径：

- **Phase 1**：`start` 子命令（< 10 秒），创建项目 + 提交任务，stdout 返回 `project_id`
- **Phase 2**：Cron 兜底（每 3 分钟），调用 `query --project-id <id>` 轮询进度
- **Phase 3**：`query --poll`，同步等待完成（乐观路径，短任务直接完成）

完整工作流：`start → [Cron 注册] → query --poll → 返回结果（含支付、下载、.sent 防重复）`

旧接口 `execute_workflow()` 仍可用（阻塞，最长 1 小时），不推荐 Agent 使用。

**kie-\* 技能**：提交 → 轮询 → 返回结果（等待最长 10 分钟）。

### generating-videos 路由模式

`generating-videos/SKILL.md` 是纯路由入口：收到请求后读取模型注册表，按用户指定的模型或生成模式跳转到对应的 `kie-*/SKILL.md` 执行。添加新视频模型只需：① 建目录 `kie-<model>/` ② 在注册表追加一行。

### 脚本统一约定

所有 Python 脚本均遵循：
- `--json`：输出结构化 JSON 到 stdout；进度/日志统一输出到 stderr
- `--no-wait`：异步提交，立即返回 `{"status": "started", "task_id": "...", "log_file": "..."}` 到 stdout
- `--query --poll`（giggle-image / giggle-drama）：同步轮询等待，每 5 秒查询一次，超时静默退出交给 Cron
- `--query`（giggle-music）exit code：`0` = 完成，`1` = 失败，`2` = 进行中（processing/pending）
- `.sent` 文件防重复：`~/.openclaw/skills/<skill>/logs/<id>.sent`，完成推送后创建，防止 Cron 与同步路径双重推送
- API Key 从环境变量或项目根目录 `.env` 文件读取（`python-dotenv`）

## 环境配置

### API Key 管理策略

**统一配置（推荐）**：根目录一个 `.env`，所有技能共用，python-dotenv 自动向上查找。

```bash
cp env.example .env
# 编辑 .env 填入：
# GIGGLE_API_KEY=...   （giggle-* 技能）
# KIE_API_KEY=...      （kie-* 技能）
```

**OpenClaw 部署**：用户在 `~/.openclaw/openclaw.json` 配置一次即可，技能通过 `SKILL.md` 的 `metadata.openclaw.requires.env` 声明所需变量，OpenClaw 运行时自动注入。无需在技能目录放 `.env`。

**独立使用单个技能**：参考该技能目录下的 `env.example`（各技能独立模板，非隐藏文件），复制到根目录 `.env` 后填入对应 Key。

依赖安装（各技能独立）：
```bash
pip install requests python-dotenv
```

## 常用测试命令

```bash
# giggle-drama：Phase 1 提交任务（< 10 秒，返回 project_id）
python3 giggle-drama/scripts/trustee_api.py start \
  --story "测试故事" --aspect 16:9 --project-name "test"

# giggle-drama：Phase 3 同步等待（含支付、下载、.sent 防重复）
python3 giggle-drama/scripts/trustee_api.py query \
  --project-id <project_id> --poll

# giggle-drama：旧接口，阻塞等待（最长 1 小时，不推荐 Agent 使用）
python3 giggle-drama/scripts/trustee_api.py workflow \
  --story "测试故事" --aspect 16:9 --project-name "test"

# giggle-aimv：MV 生成
python3 giggle-aimv/scripts/trustee_api.py --help

# giggle-music：Phase 1 提交任务（返回 task_id 到 stdout）
python3 giggle-music/scripts/giggle_music_api.py --prompt "测试" --no-wait

# giggle-music：Phase 3 查询结果（exit 0=完成, 1=失败, 2=进行中）
python3 giggle-music/scripts/giggle_music_api.py --query --task-id <task_id> --json

# giggle-image：Phase 1 提交任务（返回 task_id）
python3 giggle-image/scripts/seedream_api.py --prompt "测试" --no-wait --json

# giggle-image：Phase 3 同步等待（含 .sent 防重复）
python3 giggle-image/scripts/seedream_api.py --query --task-id <task_id> --poll --max-wait 180

# kie-nano-banana：图像生成
python3 kie-nano-banana/scripts/kie_nano_banana_api.py --prompt "测试" --aspect-ratio 1:1 --resolution 2K --json

# kie-grok-imagine：文生视频
python3 kie-grok-imagine/scripts/text_to_video.py --prompt "测试" --duration 6

# kie-grok-imagine：图生视频
python3 kie-grok-imagine/scripts/image_to_video.py --image ./test.jpg --prompt "测试"
```

## 维护检查

```bash
# 验证所有 SKILL.md 的 name 字段与目录名一致
for dir in giggle-* kie-*; do
  name=$(grep '^name:' "$dir/SKILL.md" | awk '{print $2}')
  [ "$name" != "$dir" ] && echo "不一致: 目录=$dir, name=$name"
done
```

## 本地调试限制

- `giggle-drama` / `giggle-aimv` 的 `trustee_api.py` 需要 Giggle.pro 账号余额，本地无法完整走通
- `giggle-screenplay` 是纯 LLM 技能，无脚本，无需 API Key
- kie-grok-imagine 视频生成耗时 60-120s，测试可用 `--no-wait` 异步模式
