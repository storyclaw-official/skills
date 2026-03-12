---
name: giggle-generation-video
description: 通过 Generation API 使用 AI 模型（grok 等）生成视频。支持文生视频和图生视频（首帧/尾帧）。当用户需要生成视频、制作短视频、文字转视频时使用。使用场景：(1) 根据文字描述生成视频，(2) 使用参考图作为首帧/尾帧生成视频，(3) 自定义模型、画幅比例、时长、分辨率。触发词：生成视频、制作视频、文生视频、图生视频、AI 视频、text-to-video、image-to-video。
version: "0.0.1"
license: MIT
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires": { "bins": ["python3"], "env": ["GIGGLE_API_KEY"] },
        "primaryEnv": "GIGGLE_API_KEY",
      },
  }
---

# Giggle 视频生成

通过 giggle.pro 平台的 Generation API 生成 AI 视频，支持文生视频和图生视频。

**API Key**：从环境变量 `GIGGLE_API_KEY` 或项目根目录 `.env` 文件中读取。

> **禁止内联 Python**：所有命令必须通过 `exec` 工具直接执行。**切勿**使用 `python3 << 'EOF'` 或 heredoc 内联代码。

## 支持的模型

| 模型 | 支持时长（秒） | 默认时长 | 说明 |
|------|--------------|---------|------|
| grok | 6, 10 | 6 | 综合能力强，推荐 |
| grok-fast | 6, 10 | 6 | grok 快速版 |
| sora2 | 4, 8, 12 | 4 | OpenAI Sora 2 |
| sora2-pro | 4, 8, 12 | 4 | Sora 2 Pro 版 |
| sora2-fast | 10, 15 | 10 | Sora 2 快速版 |
| sora2-pro-fast | 10, 15 | 10 | Sora 2 Pro 快速版 |
| kling25 | 5, 10 | 5 | 快影视频模型 |
| seedance15-pro | 4, 8, 12 | 4 | Seedance Pro（含音频） |
| seedance15-pro-no-audio | 4, 8, 12 | 4 | Seedance Pro（无音频） |
| veo31 | 4, 6, 8 | 4 | Google Veo 3.1（含音频） |
| veo31-no-audio | 4, 6, 8 | 4 | Google Veo 3.1（无音频） |
| minimax23 | 6 | 6 | MiniMax 模型 |
| wan25 | 5, 10 | 0 | 万象模型 |

**注意**：`--duration` 必须从对应模型的「支持时长」中选择，否则 API 会报错。

---

## 帧引用方式（图生视频）

图生视频的 `--start-frame` 和 `--end-frame` 支持三种互斥方式：

| 方式 | 格式 | 示例 |
|------|------|------|
| asset_id | `asset_id:<ID>` | `asset_id:lkllv0yv81` |
| url | `url:<URL>` | `url:https://example.com/img.jpg` |
| base64 | `base64:<DATA>` | `base64:iVBORw0KGgo...` |

每个帧参数只能选择其中一种方式。

---

## 执行流程（三阶段双路径）

视频生成通常需要 60–300 秒。采用「快速提交 + Cron 轮询 + 同步兜底」三阶段架构。

> **重要**：**切勿**在 exec 的 `env` 参数中传递 `GIGGLE_API_KEY`。API Key 通过系统环境配置，脚本会自动读取。

---

### 阶段 1：提交任务（exec 在 10 秒内完成）

**先向用户发送消息**：「视频生成进行中，通常需要 1–5 分钟，结果将自动发送。」

```bash
# 文生视频（默认 grok-fast）
python3 scripts/generation_api.py \
  --prompt "相机缓缓向前推进，人物在画面中微笑" \
  --model grok-fast --duration 6 \
  --aspect-ratio 16:9 --resolution 720p \
  --no-wait --json

# 图生视频 - 使用 asset_id 作为首帧
python3 scripts/generation_api.py \
  --prompt "人物缓缓转身" \
  --start-frame "asset_id:lkllv0yv81" \
  --model grok-fast --duration 6 \
  --aspect-ratio 16:9 --resolution 720p \
  --no-wait --json

# 图生视频 - 使用 URL 作为首帧
python3 scripts/generation_api.py \
  --prompt "风景从静止到运动" \
  --start-frame "url:https://example.com/img.jpg" \
  --model grok-fast --duration 6 \
  --no-wait --json

# 图生视频 - 同时指定首帧和尾帧
python3 scripts/generation_api.py \
  --prompt "场景过渡" \
  --start-frame "asset_id:abc123" \
  --end-frame "url:https://example.com/end.jpg" \
  --model grok --duration 6 \
  --no-wait --json
```

响应示例：
```json
{"status": "started", "task_id": "55bf24ca-e92a-4d9b-a172-8f585a7c5969"}
```

**立即将 task_id 存入记忆**（`addMemory`）：
```
giggle-generation-video task_id: xxx (submitted: YYYY-MM-DD HH:mm)
```

---

### 阶段 2：注册 Cron（60 秒间隔）

使用 `cron` 工具注册轮询任务。**必须严格遵循参数格式**：

```json
{
  "action": "add",
  "job": {
    "name": "giggle-generation-video-<task_id 前 8 位>",
    "schedule": {
      "kind": "every",
      "everyMs": 60000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "视频任务轮询：执行 exec python3 scripts/generation_api.py --query --task-id <完整 task_id>，按 Cron 逻辑处理 stdout。若 stdout 为非 JSON 纯文本，发送给用户并移除 Cron。若 stdout 为 JSON，不发送消息，继续等待。若 stdout 为空，立即移除 Cron。"
    },
    "sessionTarget": "main"
  }
}
```

**Cron 触发处理**（根据 exec stdout 判断）：

| stdout 模式 | 动作 |
|------------|------|
| 非空纯文本（不以 `{` 开头） | **原样转发给用户**，**移除 Cron** |
| stdout 为空 | 已推送，**立即移除 Cron，不发送消息** |
| JSON（以 `{` 开头，含 `"status"` 字段） | 不发送消息，不移除 Cron，继续等待 |

---

### 阶段 3：同步等待（乐观路径，Cron 未触发时的兜底）

**无论 Cron 是否注册成功，都必须执行此步骤。**

```bash
python3 scripts/generation_api.py --query --task-id <task_id> --poll --max-wait 300
```

**处理逻辑**：

- 返回纯文本（视频就绪/失败消息） → **原样转发给用户**，移除 Cron
- stdout 为空 → Cron 已推送，移除 Cron，不发送消息
- exec 超时 → Cron 继续轮询

---

## 新请求 vs 查询旧任务

**当用户发起新的视频生成请求**时，**必须执行阶段 1 提交新任务**，不要复用记忆中的旧 task_id。

**仅当用户明确询问之前任务的进度**时，才从记忆中查询旧 task_id。

---

## 参数速查

| 参数 | 默认值 | 说明 |
|-----|--------|------|
| `--prompt` | 必填 | 视频描述 prompt |
| `--model` | grok | 见「支持的模型」表 |
| `--duration` | 模型默认 | 必须从模型支持的时长中选择 |
| `--aspect-ratio` | 16:9 | 16:9、9:16、1:1、3:4、4:3 |
| `--resolution` | 720p | 分辨率：480p、720p、1080p |
| `--start-frame` | - | 图生视频首帧，格式：`asset_id:ID`、`url:URL` 或 `base64:DATA` |
| `--end-frame` | - | 图生视频尾帧，格式同首帧 |

---

## 交互引导流程

**当用户请求较模糊时，按以下步骤引导。若用户已提供足够信息，可直接执行命令。**

### 步骤 1：选择模型（必须）

在生成前，**必须先向用户介绍可用模型**，再让用户选择。展示如下：

> 请选择视频生成模型：
>
> **推荐模型：**
> - **grok** — 综合能力强，支持 6/10 秒（推荐）
> - **grok-fast** — grok 快速版，支持 6/10 秒
>
> **Sora 系列：**
> - **sora2** — OpenAI Sora 2，支持 4/8/12 秒
> - **sora2-pro** — Sora 2 Pro 版，支持 4/8/12 秒
> - **sora2-fast** — Sora 2 快速版，支持 10/15 秒
> - **sora2-pro-fast** — Sora 2 Pro 快速版，支持 10/15 秒
>
> **其他模型：**
> - **kling25** — 快影，支持 5/10 秒
> - **seedance15-pro** — Seedance Pro（含音频），支持 4/8/12 秒
> - **seedance15-pro-no-audio** — Seedance Pro（无音频），支持 4/8/12 秒
> - **veo31** — Google Veo 3.1（含音频），支持 4/6/8 秒
> - **veo31-no-audio** — Google Veo 3.1（无音频），支持 4/6/8 秒
> - **minimax23** — MiniMax，仅支持 6 秒
> - **wan25** — 万象，支持 5/10 秒

等待用户明确选择后再继续。

### 步骤 2：视频时长

根据用户选择的模型，展示该模型支持的时长选项让用户选择。默认使用模型的默认时长。

### 步骤 3：生成模式

```
问题：「需要使用参考图片作为首帧/尾帧吗？」
标题：「生成模式」
选项：
- "不需要 - 仅文生视频"
- "需要 - 图生视频（设置首帧/尾帧）"
multiSelect: false
```

### 步骤 4：画幅比例

```
问题：「需要什么画幅比例？」
标题：「画幅比例」
选项：
- "16:9 - 横屏（推荐）"
- "9:16 - 竖屏（短视频）"
- "1:1 - 方形"
multiSelect: false
```

### 步骤 5：执行并展示

按执行流程：发送消息 → 阶段 1 提交 → 阶段 2 注册 Cron → 阶段 3 同步等待。

结果到达后将 exec stdout 原样转发给用户。

**链接返回规范**：结果中的视频链接必须为**完整签名 URL**（含 Policy、Key-Pair-Id、Signature 等查询参数）。正确示例：`https://assets.giggle.pro/...?Policy=...&Key-Pair-Id=...&Signature=...`。错误：不要返回仅含基础路径的未签名 URL（无查询参数）。
