---
name: giggle-aimv
description: 用户在有生成 MV、生成音乐视频、根据歌词/提示词/上传音乐生成视频等需求时使用。支持三种音乐生成模式（提示词、自定义、上传），调用 MV 托管 API 完成完整工作流。
---

# MV 托管模式 API Skill

此 skill 用于调用 MV 托管模式 API，执行完整的 MV 生成工作流。**创建项目与提交任务已在脚本内合并为一步**，AI 只需调用 `execute_workflow` 一次，切勿分开调用创建和提交。

## 首次使用配置（必读）

**执行任何操作前，必须先检查用户是否已配置 API 密钥。**

**API Key 获取方式**：登录 [Giggle.pro](https://giggle.pro/) 平台，在个人中心或账户设置中获取 API 密钥。

配置方式（二选一）：
1. **项目根目录 `.env`**：复制 `env.example` 为 `.env`，填写 `GIGGLE_API_KEY=your_api_key`
2. **环境变量**：`export GIGGLE_API_KEY=your_api_key`

**检查步骤**：
1. 确认用户已在 `.env` 或环境变量中配置 `GIGGLE_API_KEY`
2. 如果未配置，**必须提示用户**：
   > 您好！在使用 MV 生成功能前，需要先配置 API 密钥。请先到 [Giggle.pro](https://giggle.pro/) 平台获取 API Key，然后在项目根目录创建 `.env` 文件（可参考 `env.example`），添加 `GIGGLE_API_KEY=your_api_key`，或通过环境变量设置。
3. 等待用户确认已配置后，再执行后续工作流

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

## 工作流函数

使用 `execute_workflow` 执行完整工作流，**只需调用一次**。函数内部自动完成：创建项目+提交任务（合并一步）→ 轮询进度（每 3 秒）→ 检测待支付并支付 → 等待完成（最多 1 小时）。

**重要**：
- 禁止分开调用 `create_project` 和 `submit_mv_task`，必须使用 `execute_workflow` 或 `create_and_submit`
- 调用后只需等待函数返回，中间步骤自动处理

### 函数签名

```python
execute_workflow(
    music_generate_type: str,      # 模式：prompt / custom / upload
    aspect: str,                   # 宽高比 16:9 或 9:16
    project_name: str,             # 项目名称
    reference_image: str = "",      # 参考图 asset_id（与 reference_image_url 二选一）
    reference_image_url: str = "", # 参考图下载链接（与 reference_image 二选一），此字段同时支持base64编码的图片，示例："iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    scene_description: str = "",    # 场景描述，默认空
    subtitle_enabled: bool = False,# 字幕开关，默认 False
    # 提示词模式
    prompt: str = "",
    vocal_gender: str = "auto",
    instrumental: bool = False,
    # 自定义模式
    lyrics: str = "",
    style: str = "",
    title: str = "",
    # 上传模式
    music_asset_id: str = "",
)
```

### 参数提取规则

1. **reference_image 与 reference_image_url**：至少一个，用户提供 asset_id 用 reference_image，提供图片链接用 reference_image_url
2. **scene_description**：默认为空，**仅当用户明确提到「场景」「画面描述」「视觉风格」等时**才填充
3. **subtitle_enabled**：默认为 False，**仅当用户明确要求字幕时**设为 True
4. **aspect**：用户提到竖屏/9:16 时用 `9:16`，否则默认 `16:9`
5. **模式判断**：用户说「用提示词/描述生成」→ prompt；「给歌词/歌词是」→ custom；「上传音乐/用我的音乐」→ upload

### 示例

**提示词模式**：
```python
api = MVTrusteeAPI()
result = api.execute_workflow(
    music_generate_type="prompt",
    aspect="16:9",
    project_name="我的 MV",
    reference_image_url="https://example.com/ref.jpg",
    prompt="轻快的流行音乐，阳光沙滩风格",
    vocal_gender="female"
)
```

**自定义模式（用户提供歌词）**：
```python
result = api.execute_workflow(
    music_generate_type="custom",
    aspect="9:16",
    project_name="歌词 MV",
    reference_image="asset_xxx",
    lyrics="Verse 1: 春天的风...",
    style="pop",
    title="春日之歌"
)
```

**上传模式**：
```python
result = api.execute_workflow(
    music_generate_type="upload",
    aspect="16:9",
    project_name="上传音乐 MV",
    reference_image="asset_yyy",
    music_asset_id="music_asset_zzz"
)
```

**用户提到场景描述时**：
```python
result = api.execute_workflow(
    music_generate_type="prompt",
    aspect="16:9",
    project_name="场景 MV",
    reference_image_url="https://...",
    prompt="电子舞曲",
    scene_description="城市夜景，霓虹灯闪烁，车流穿梭"  # 用户明确描述场景时设置
)
```

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

### create_and_submit（可选）

如需仅「创建项目+提交任务」而不等待完成，使用 `create_and_submit`，**不要**分别调用 `create_project` 和 `submit_mv_task`：

```python
api = MVTrusteeAPI()
r = api.create_and_submit(
    project_name="我的 MV",
    music_generate_type="prompt",
    aspect="16:9",
    reference_image_url="https://...",
    prompt="轻快流行乐"
)
# 返回 project_id，可后续手动 query/pay
```

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
