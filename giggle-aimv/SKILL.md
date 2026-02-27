---
name: giggle-aimv
description: 用户在有生成 MV、生成音乐视频、根据歌词/提示词/上传音乐生成视频等需求时使用。支持三种音乐生成模式（提示词、自定义、上传），调用 MV 托管 API 完成完整工作流。
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🎵","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/scripts/requirements.txt"]},"version":"2.0.0","author":"姜式伙伴"}
---

# MV 托管模式 API Skill

此 skill 用于调用 MV 托管模式 API，执行 MV 生成工作流（通常 3-10 分钟）。

## 三种音乐生成模式

| 模式 | music_generate_type | 必需参数 | 说明 |
|------|---------------------|----------|------|
| **提示词模式** | `prompt` | prompt, vocal_gender | 用文字描述生成音乐 |
| **自定义模式** | `custom` | lyrics, style, title | 提供歌词、风格、歌名 |
| **上传模式** | `upload` | music_asset_id | 上传已有音乐资产 |

### 共用参数（所有模式必须）

- **reference_image** 或 **reference_image_url**：参考图，至少提供一个（asset_id 或下载链接），此字段同时支持base64编码的图片，示例："iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
- **aspect**：宽高比，`16:9` 或 `9:16`
- **scene_description**：场景描述，**默认空**，仅当用户明确提到场景描述时设置（最长 200 字）
- **subtitle_enabled**：是否启用字幕，**默认 false**

### 模式专属参数

**提示词模式 (prompt)**：
- `prompt`：音乐描述提示词（必需）
- `vocal_gender`：人声性别，`male` / `female` / `auto`（可选，默认 `auto`）
- `instrumental`：是否纯音乐（可选，默认 false）

**自定义模式 (custom)**：
- `lyrics`：歌词内容（必需）
- `style`：音乐风格（必需）
- `title`：歌名（必需）

**上传模式 (upload)**：
- `music_asset_id`：已有音乐资产 ID（必需）

## 执行流程（三阶段双路径）

MV 生成通常需要 3-10 分钟。采用「同步等待 + Cron 兜底」双路径，确保用户一定收到结果。

---

### 第零步：参数确认（必须先完成，再执行 Phase 1）

MV 生成耗时且消耗积分，**提交前必须确认关键参数**。

#### 1. 检查参考图（必填）

- **用户已提供**图片（asset_id / 图片链接 / base64）→ 直接进入第 2 步
- **用户未提供** → 发送以下消息：

> 生成 MV 需要一张参考图片作为视觉基调（画面风格的参考）。您可以：
> - **让我帮您生成**：告诉我想要什么风格的画面，我用 giggle-image 生成一张
> - **自行提供**：发一张图片或图片链接给我

  - 用户选「帮我生成」→ **调用 giggle-image 生成图片** → 展示结果 → 问：「这张图满意吗？用它来生成 MV？」
    - 满意 → 用此图的 URL 作为 `--reference-image-url` 继续
    - 不满意 → 重新生成或让用户上传
  - 用户提供图片 → 使用该图继续

#### 2. 确认其他核心参数（AskUserQuestion，一次问完）

以下参数**未明确时必须询问**：

| 参数 | 询问内容 | 已明确则跳过 |
|------|----------|-------------|
| 音乐模式 | 「用文字描述生成音乐」/「提供歌词」/「上传已有音乐」 | 用户已说明 |
| 宽高比 | 横屏（16:9）还是竖屏（9:16）？ | 用户已说明 |
| 音乐描述/歌词 | 根据模式：描述想要的音乐风格，或提供歌词+风格+歌名 | 已提供 |

所有参数确认后，**才执行 Phase 1**。

---

### 第一步：提交任务（Phase 1，exec < 10 秒完成）

**先发送消息给用户**："MV 生成中，通常 3-10 分钟，每3分钟自动报告进度，请稍候。"

**提示词模式**：
```bash
python3 scripts/trustee_api.py start \
  --mode prompt \
  --aspect "16:9" \
  --project-name "我的MV" \
  --reference-image-url "https://..." \
  --prompt "轻快的流行音乐，阳光沙滩风格" \
  --vocal-gender female
```

**自定义模式**：
```bash
python3 scripts/trustee_api.py start \
  --mode custom \
  --aspect "9:16" \
  --project-name "歌词MV" \
  --reference-image "asset_xxx" \
  --lyrics "Verse 1: 春天的风..." \
  --style "pop" \
  --title "春日之歌"
```

**上传模式**：
```bash
python3 scripts/trustee_api.py start \
  --mode upload \
  --aspect "16:9" \
  --project-name "上传MV" \
  --reference-image "asset_yyy" \
  --music-asset-id "music_asset_zzz"
```

返回示例：
```json
{"code": 200, "status": "started", "data": {"project_id": "xxx", "log_file": "/path/logs/xxx.log"}}
```

**立即将 project_id 写入记忆**（`addMemory`）：
```
giggle-aimv project_id: xxx（状态：生成中，提交时间：YYYY-MM-DD HH:mm）
```

如果 start 成功（code == 200）：将 `project_id` 写入记忆后继续 Phase 2。

如果 start 失败（code != 200）：
- 响应中**有 project_id** → 告知错误，**再次执行 `start --project-id <id>`**，脚本自动重试
- 响应中**无 project_id**（create 阶段失败）→ 告知错误，询问用户是否重新提交，用户确认后重新 `start`
- **不执行后续步骤**

---

### 第二步：注册 Cron（立刻注册，在 Phase 3 之前）

使用 `cron` 工具注册轮询任务，**必须严格按照以下参数格式，不得修改任何字段名或添加额外字段**：

```json
{
  "action": "add",
  "job": {
    "name": "giggle-aimv-<project_id前8位>",
    "schedule": {
      "kind": "every",
      "everyMs": 180000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "MV任务轮询：请执行 exec python3 scripts/trustee_api.py query --project-id <完整project_id>，根据 Cron 处理逻辑处理结果。"
    },
    "sessionTarget": "main"
  }
}
```

每次 Cron 触发后执行：
```bash
python3 scripts/trustee_api.py query --project-id <project_id>
```

**Cron 处理逻辑**（根据 exit code）：

| exit code | 含义 | 处理 |
|-----------|------|------|
| 0 | 完成/支付中/进行中 | 读 JSON：already_sent→跳过取消；signed_url→发结果取消；pay_failed→发"积分不足"取消；msg 含"自动支付"→转发消息 Cron 继续；else→发步骤进度，Cron 继续 |
| 1 | 失败/积分不足 | 发错误消息，取消 Cron |

> **说明**：支付逻辑已内置于 `query` 脚本，检测到 `pay_status=="pending"` 时自动调用 pay API，**无需 agent 介入**。

**步骤进度消息格式**（从 `data.current_step` 和 `data.completed_steps` 读取）：
```
MV 生成中 — 已完成：音乐✓ 分镜✓ | 当前：镜头渲染 | 已用时 X 分钟
```

步骤名称翻译：
- `music-generate` → 音乐生成
- `storyboard` → 分镜制作
- `shot` → 镜头渲染
- `editor` → 剪辑合成

---

### 第三步：同步等待（Phase 3，乐观路径）

```bash
python3 scripts/trustee_api.py query --project-id <project_id> --poll
```

- 返回 `status: "already_sent"` → 跳过，取消 Cron
- 返回 `code: 200` + 含 `signed_url` → **立即发送结果给用户**，取消 Cron
- exec 超时 → Cron 已在运行，继续等待即可

---

### 结果消息格式

```
MV 生成完成

▶️ 在线播放：<data.signed_url>
⏱️ 时长：<data.duration>s
```

**注意**：`data.signed_url` 已将 `~` 编码为 `%7E`，飞书可正常点击。

---

### 参数提取规则

1. **reference_image 与 reference_image_url**：至少一个，用户提供 asset_id 用 `--reference-image`，提供图片链接或 base64 用 `--reference-image-url`
2. **scene_description**：默认为空，**仅当用户明确提到「场景」「画面描述」「视觉风格」等时**才填充
3. **subtitle_enabled**：默认 False，**仅当用户明确要求字幕时**用 `--subtitle`
4. **aspect**：用户提到竖屏/9:16 时用 `9:16`，否则默认 `16:9`
5. **模式判断**：用户说「用提示词/描述生成」→ `prompt`；「给歌词/歌词是」→ `custom`；「上传音乐/用我的音乐」→ `upload`

---

### 失败处理

> ⚠️ **核心原则：有 project_id 就用 `start --project-id <id>`，脚本自动判断状态并路由，绝不手动重新 `start`（会创建新项目浪费积分）**

| 场景 | 处理方式 |
|------|---------|
| 有 project_id，任意失败 | `python3 scripts/trustee_api.py start --project-id <id>`（脚本自动查状态→retry） |
| 积分不足 | "积分不足，请充值后告诉我"，充值后执行 `start --project-id <id>` |
| 超时（1小时） | "生成超时，project_id=xxx，可稍后继续查询" |
| 完全无 project_id（create 阶段失败） | 告知错误，用户确认后**重新完整执行 `start`**（带所有参数） |

**有 project_id 时统一恢复命令**：
```bash
# 脚本自动：查询状态 → 已失败则找出失败步骤并 retry → 进行中则返回状态
python3 scripts/trustee_api.py start --project-id <id>
```

**根据 start --project-id 返回的 status 决定后续动作**：

| 返回 status | 含义 | 后续动作 |
|-------------|------|---------|
| `started` | 新项目创建成功 | 写记忆 → 注册 Cron → Phase 3 |
| `retrying` | 已提交重试 | **重新注册 Cron**（原 Cron 已取消）→ 告知用户"正在重试" |
| `running` | 项目仍在进行中（如重启恢复）| **重新注册 Cron** → 告知用户"已恢复监控" |
| `completed` | 已完成 | 直接发结果给用户，无需 Cron |
| code != 200 | 出错 | 告知错误，等待用户指示 |

**判断是否有 project_id**：
- 记忆中有 → 直接用 `start --project-id <id>`
- 日志文件名中有（`logs/<project_id>_*.log`）→ 提取后用 `start --project-id <id>`
- 完全没有（`start` 在 `create` 阶段就失败）→ 才重新完整 `start`

---

### Gateway 重启后恢复

1. **记忆中有 project_id** → 执行 `start --project-id <id>`，根据返回 status 决定后续（见上表）
2. **没有** → 告知用户，询问是否重新生成

### 提交任务 API 请求示例（提示词模式）

提交任务接口 (`/api/v1/trustee_mode/mv/submit`) 的请求体示例：

```json
{
  "project_id": "c0cb1f32-bb07-4449-add5-e42ccfca1ab6",
  "music_generate_type": "prompt",
  "prompt": "一首欢快的流行乐",
  "vocal_gender": "female",
  "instrumental": false,
  "reference_image_url": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMTEhUT...（base64 图片数据）",
  "scene_description": "夕阳下海边漫步的浪漫场景，海浪轻轻拍打沙滩，天空呈现粉红色渐变",
  "aspect": "16:9",
  "subtitle_enabled": false
}
```

说明：`reference_image`（asset_id）与 `reference_image_url`（链接或 base64）二选一。

**自定义模式**：

```json
{
  "project_id": "0ea74500-9178-4693-b581-342d5e17994c",
  "music_generate_type": "custom",
  "lyrics": "Verse 1:\n站在海边看夕阳\n回忆像潮水般涌来\n\nChorus:\n就让海风吹散烦恼\n在这金色时刻里\n我们找到彼此\n",
  "style": "pop ballad",
  "title": "海边回忆",
  "reference_image": "is45gnvumgd",
  "scene_description": "黄昏时分的情侣在海边散步，背影拉长，天空橙红渐变色",
  "aspect": "9:16",
  "subtitle_enabled": false
}
```

**上传模式**：

```json
{
  "project_id": "0ea74500-9178-4693-b581-342d5e17994c",
  "music_generate_type": "upload",
  "music_asset_id": "music_asset_789",
  "reference_image": "is45gnvumgd",
  "scene_description": "城市夜景，霓虹灯闪烁，车流如织，雨后的街道反射灯光",
  "aspect": "16:9",
  "subtitle_enabled": true
}
```

### 查询进度 API 响应示例

查询进度接口 (`/api/v1/trustee_mode/mv/query`) 的响应示例（全部完成）：

```json
{
  "code": 200,
  "msg": "success",
  "uuid": "24052352-f231-495a-9581-3827c4eb0bdf",
  "data": {
    "project_id": "65cf262d-c4b1-4733-abf1-ec6a7bdb944a",
    "video_asset": {
      "asset_id": "ryco1asdmb",
      "download_url": "https://assets.giggle.pro/private/...",
      "thumbnail_url": "https://assets.giggle.pro/private/...",
      "signed_url": "https://assets.giggle.pro/private/...",
      "duration": 0
    },
    "shot_count": 0,
    "current_step": "editor",
    "completed_steps": "music-generate,storyboard,shot,editor",
    "pay_status": "paid",
    "status": "completed",
    "err_msg": "",
    "steps": [
      {
        "step": "music-generate",
        "sub_steps": [
          {
            "step": "GenerateMusic",
            "status": "completed",
            "error": "",
            "completed_at": "2026-02-17 13:35:47"
          },
          {
            "step": "GenerateMusicShot",
            "status": "completed",
            "error": "",
            "completed_at": "2026-02-17 13:36:12"
          },
          {
            "step": "CalculatePrice",
            "status": "completed",
            "error": "",
            "completed_at": "2026-02-17 13:36:15"
          }
        ],
        "retry_count": 0
      },
      {
        "step": "storyboard",
        "sub_steps": [
          { "step": "ShotStructure", "status": "completed", "completed_at": "2026-02-17 13:36:30" },
          { "step": "CharacterCreate", "status": "completed", "completed_at": "2026-02-17 13:37:00" },
          { "step": "ImageGeneration", "status": "completed", "completed_at": "2026-02-17 13:38:20" }
        ],
        "retry_count": 0
      },
      {
        "step": "shot",
        "sub_steps": [
          { "step": "OptimizePrompts", "status": "completed", "completed_at": "2026-02-17 13:38:45" },
          { "step": "VideoGeneration", "status": "completed", "completed_at": "2026-02-17 13:45:00" }
        ],
        "retry_count": 0
      },
      {
        "step": "editor",
        "sub_steps": [
          { "step": "ResourceDownload", "status": "completed", "completed_at": "2026-02-17 13:45:30" },
          { "step": "IntelligentMerge", "status": "completed", "completed_at": "2026-02-17 13:46:00" }
        ],
        "retry_count": 0
      }
    ]
  }
}
```

说明：`pay_status` 为 `pending` 时需调用支付接口；所有 `steps` 完成后 `video_asset.download_url` 有值，可下载视频。

### 支付 API 请求与响应示例

支付接口 (`/api/v1/trustee_mode/mv/pay`)：

**请求体**：
```json
{
  "project_id": "28b4f4f7-d219-4754-a78b-d9896cd16573"
}
```

**响应**：
```json
{
  "code": 200,
  "msg": "success",
  "uuid": "1440ba5f-ba1c-41f6-a92c-53337a7df1c2",
  "data": {
    "order_id": "2a93f1c1-9e4d-4d29-89d7-15deea4e3732",
    "price": 580
  }
}
```

### 重试 API 请求示例

当某步骤失败时，可引导用户调用重试接口，从指定步骤重新执行：

```json
{
  "project_id": "28b4f4f7-d219-4754-a78b-d9896cd16573",
  "current_step": "shot"
}
```

说明：`current_step` 为需要重试的步骤名（如 `music-generate`、`storyboard`、`shot`、`editor`）。

### 返回值

成功返回：
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "project_id": "...",
        "download_url": "https://...",
        "video_asset": {...},
        "status": "completed"
    }
}
```

失败返回错误信息。
