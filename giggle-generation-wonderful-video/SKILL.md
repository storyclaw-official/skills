---
name: giggle-generation-wonderful-video
description: 仅当用户明确提及「精彩视频」「wonderful video」或「wonderful-video」时使用此技能。此技能可生成角色驱动的 AI 视频。
version: "0.0.1"
license: MIT
metadata:
  {
    "openclaw":
      {
        "emoji": "📂",
        "requires": { "bins": ["python3"], "env": ["GIGGLE_API_KEY"] },
        "primaryEnv": "GIGGLE_API_KEY",
      },
  }
---

# 精彩视频生成技能

调用 Giggle trustee 模式 API，使用 **wonderful-video** 项目类型执行完整视频生成工作流。一次函数调用即可完成整个流程。以下情况不触发：生成视频、短视频、制作视频、generate video、create video、short video、character video 等未包含「精彩视频」或「wonderful video」或「wonderful-video」的通用视频请求。

## 首次使用前的配置（必选）

**在执行任何操作前，确认用户已配置 API Key。**

**API Key**：登录 [Giggle.pro](https://giggle.pro/) 并在账号设置中获取 API Key。

**加载优先级**：1) `~/.openclaw/.env`（优先） 2) 系统环境变量 `GIGGLE_API_KEY`

配置方式（任选其一）：
1. **~/.openclaw/.env**（推荐）：创建 `~/.openclaw/.env`，添加 `GIGGLE_API_KEY=your_api_key`
2. **系统环境变量**：`export GIGGLE_API_KEY=your_api_key`

**检查步骤**：
1. 确认用户已在 `~/.openclaw/.env` 或系统环境变量中配置 `GIGGLE_API_KEY`
2. 若未配置，**引导用户**：
   > 你好！在使用视频生成功能前，需要先配置 API Key。请前往 [Giggle.pro](https://giggle.pro/) 获取 API Key，然后任选一种方式：在 `~/.openclaw/.env` 中添加 `GIGGLE_API_KEY=your_api_key`，或在终端执行 `export GIGGLE_API_KEY=your_api_key`。
3. 等待用户配置后再继续工作流

## 项目类型

本技能默认使用 **wonderful-video** 项目类型，无需选择模式。

## 工作流函数

使用 `execute_workflow` 函数运行完整工作流。该函数**一步完成项目创建与任务提交**，并自动处理后续步骤：
1. 创建项目 + 提交任务（合并）
2. 每 3 秒轮询进度
3. 检测待支付状态并自动支付（如需要）
4. 等待任务完成（最长 1 小时）
5. 返回视频下载链接或错误信息

**重要**：只需调用一次该函数并等待返回结果。

### 函数签名

```python
execute_workflow(
    diy_story: str,                           # 故事/剧本内容（必填）
    aspect: str,                              # 视频画幅比例 16:9/9:16（必填）
    project_name: str,                        # 项目名称（必填）
    video_duration: str = "auto",             # 视频时长，默认 "auto"（可选）
    style_id: Optional[int] = None,           # 风格 ID（可选）
    character_info: Optional[List[Dict]] = None,  # 角色图片（可选）
    subtitle_enabled: Optional[bool] = None   # 是否启用字幕（可选）
)
```

### 参数说明

1. **diy_story**（必填）：故事/剧本内容
2. **aspect**（必填）：视频画幅比例，`16:9` 或 `9:16`
3. **project_name**（必填）：项目名称
4. **video_duration**（可选）：可选值 `30`、`60`、`120`、`180`、`240`、`300`；默认 `auto`
5. **style_id**（可选）：风格 ID；未指定时可省略
6. **character_info**（可选）：角色图片列表，用于定义外观。格式：`[{"name": "角色名", "url": "图片 URL"}, ...]`
7. **subtitle_enabled**（可选）：是否启用字幕，`True`/`False`

### 使用流程

1. **若用户希望查看可选风格**：
   - 调用 `get_styles()` 获取风格列表
   - 向用户展示风格（ID、名称、分类、描述）

2. **执行工作流**：
   - 调用一次 `execute_workflow()`
   - 传入故事内容、画幅比例、项目名称
   - 可选传入：时长、style_id、character_info、subtitle_enabled
   - 若用户提供了角色图片 URL，构建 `character_info` 数组并传入
   - 等待函数返回结果

### 示例

**查看风格**：
```python
api = WonderfulVideoAPI()
styles_result = api.get_styles()
# 向用户展示风格列表
```

**执行工作流**：
```python
api = WonderfulVideoAPI()
result = api.execute_workflow(
    diy_story="一个冒险故事...",
    aspect="16:9",
    project_name="我的精彩视频"
)
# result 包含下载 URL 或错误信息
```

**指定时长和风格**：
```python
api = WonderfulVideoAPI()
result = api.execute_workflow(
    diy_story="今天我们来聊...",
    aspect="9:16",
    project_name="竖屏视频",
    video_duration="60",
    style_id=142
)
```

**带角色图片**（当用户提供角色图片 URL 时）：
```python
api = WonderfulVideoAPI()
result = api.execute_workflow(
    diy_story="两个角色的故事",
    aspect="16:9",
    project_name="角色视频",
    video_duration="30",
    character_info=[
        {"name": "角色 A", "url": "https://xxx/char_a.jpg"},
        {"name": "角色 B", "url": "https://xxx/char_b.jpg"}
    ],
    subtitle_enabled=True
)
```

### 返回值

成功时：
```json
{
    "code": 200,
    "msg": "success",
    "uuid": "...",
    "data": {
        "project_id": "...",
        "download_url": "https://...",
        "video_asset": {...},
        "status": "completed"
    }
}
```

**链接返回规范**：返回给用户时，必须使用**完整签名 URL**（含 Policy、Key-Pair-Id、Signature 等查询参数）。正确示例：
```
https://assets.giggle.pro/private/.../xxx.mp4?Policy=...&Key-Pair-Id=...&Signature=...&response-content-disposition=attachment
```
错误：不要返回仅含基础路径的未签名 URL，例如 `https://assets.giggle.pro/private/.../xxx.mp4`（无查询参数）。

失败时：
```json
{
    "code": -1,
    "msg": "Error message",
    "data": null
}
```
