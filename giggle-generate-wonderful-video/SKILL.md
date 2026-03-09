---
name: giggle-generate-wonderful-video
description: Generates wonderful-video type videos via Giggle API. Supports character images (character_info), subtitles, and style selection. Use when creating wonderful-video content, specifying character appearance by image URL, or viewing available styles.
---

# Wonderful Video 生成 Skill

调用 Giggle 托管模式 API，以 **wonderful-video** 项目类型执行完整的视频生成工作流。AI 只需调用一个函数即可完成全流程。

## 首次使用配置（必读）

**执行任何操作前，必须先检查用户是否已配置鉴权令牌。**

配置文件路径：`scripts/config.json`

配置格式：
```json
{"x_auth": "你的令牌"}
```

**检查步骤**：
1. 读取配置文件，检查 `x_auth` 字段是否已填写
2. 如果文件不存在或 `x_auth` 为空，**必须提示用户填写**：
   > 您好！在使用视频生成功能前，需要先配置鉴权令牌。请将您的 x-auth 令牌填写到配置文件 `scripts/config.json` 的 `x_auth` 字段中，然后再继续操作。
3. 等待用户确认已填写后，再执行后续工作流

## 项目类型说明

本 Skill 固定使用 **wonderful-video** 项目类型，无需用户选择模式。

## 工作流函数

使用 `execute_workflow` 函数执行完整工作流。该函数**一步完成**创建项目与提交任务，并自动处理后续步骤：
1. 创建项目 + 提交任务（合并为一步）
2. 循环查询进度（每3秒）
3. 自动检测待支付状态并执行支付（如需要）
4. 等待任务完成（最多1小时）
5. 返回视频下载链接或错误信息

**重要**：只需调用此函数一次，等待返回结果即可。

### 函数签名

```python
execute_workflow(
    diy_story: str,                           # 故事创意内容（必需）
    aspect: str,                              # 视频宽高比 16:9/9:16（必需）
    project_name: str,                        # 项目名称（必需）
    video_duration: str = "auto",             # 视频时长，默认 "auto"（可选）
    style_id: Optional[int] = None,           # 风格ID（可选）
    character_info: Optional[List[Dict]] = None,  # 角色图片（可选）
    subtitle_enabled: Optional[bool] = None   # 是否启用字幕（可选）
)
```

### 参数说明

1. **diy_story**（必需）：故事创意内容
2. **aspect**（必需）：视频宽高比，`16:9` 或 `9:16`
3. **project_name**（必需）：项目名称
4. **video_duration**（必需）：`30`、`60`、`120`、`180`、`240`、`300`中选择一个
5. **style_id**（可选）：风格ID，不指定则不传
6. **character_info**（可选）：角色图片列表，用于指定角色外貌。格式：`[{"name": "角色名", "url": "图片URL"}, ...]`
7. **subtitle_enabled**（可选）：是否启用字幕，`True`/`False`

### 使用流程

1. **如用户想查看可用风格**：
   - 调用 `get_styles()` 获取风格列表
   - 向用户展示风格（ID、名称、分类、描述）

2. **执行工作流**：
   - 调用 `execute_workflow()` 一次
   - 传入故事创意、比例、项目名称
   - 可选传入：时长、风格ID、角色图片（`character_info`）、是否启用字幕（`subtitle_enabled`）
   - 若用户提供角色图片 URL，构建 `character_info` 数组传入
   - 等待函数返回结果

### 示例

**查看风格**：
```python
api = WonderfulVideoAPI()
styles_result = api.get_styles()
# 展示风格列表给用户
```

**执行工作流**：
```python
api = WonderfulVideoAPI()
result = api.execute_workflow(
    diy_story="一个关于冒险的故事...",
    aspect="16:9",
    project_name="我的wonderful视频"
)
# result 包含下载链接或错误信息
```

**指定时长和风格**：
```python
api = WonderfulVideoAPI()
result = api.execute_workflow(
    diy_story="今天我们来聊一聊...",
    aspect="9:16",
    project_name="竖屏视频",
    video_duration="60",
    style_id=142
)
```

**指定角色图片**（用户提供角色图片 URL 时）：
```python
api = WonderfulVideoAPI()
result = api.execute_workflow(
    diy_story="潘金莲与西门庆",
    aspect="16:9",
    project_name="角色视频",
    video_duration="30",
    character_info=[
        {"name": "潘金莲", "url": "https://xxx/pan.jpg"},
        {"name": "西门庆", "url": "https://xxx/xi.jpg"}
    ],
    subtitle_enabled=True
)
```

### 返回值

成功：
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

失败：
```json
{
    "code": -1,
    "msg": "错误信息",
    "data": null
}
```
