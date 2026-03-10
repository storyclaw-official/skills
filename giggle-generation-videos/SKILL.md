---
name: generating-videos
description: 用户在有生成视频需求、生成短视频需求、有一个创意需要生成视频、或查看可用风格时使用此skill，可以引导用户查看风格。
---

# 托管模式V2 API Skill

此skill用于调用托管模式V2 API，执行完整的视频生成工作流。

## 首次使用配置（必读）

**在执行任何操作前，必须先检查用户是否已配置 API 密钥。**

**API Key 获取方式**：登录 [Giggle.pro](https://giggle.pro/) 平台，在个人中心或账户设置中获取 API 密钥。

配置方式（二选一）：
1. **项目根目录 `.env`**：复制 `env.example` 为 `.env`，填写 `GIGGLE_API_KEY=your_api_key`
2. **环境变量**：`export GIGGLE_API_KEY=your_api_key`

**检查步骤**：
1. 确认用户已在 `.env` 或环境变量中配置 `GIGGLE_API_KEY`
2. 如果未配置，**必须提示用户**：
   > 您好！在使用视频生成功能前，需要先配置 API 密钥。请先到 [Giggle.pro](https://giggle.pro/) 平台获取 API Key，然后在项目根目录创建 `.env` 文件（可参考 `env.example`），添加 `GIGGLE_API_KEY=your_api_key`，或通过环境变量设置。
3. 等待用户确认已配置后，再执行后续工作流

## 生成模式说明

视频生成支持三种模式，**开始工作流前必须提示用户选择**：

| 模式 | project_type 值 | 说明 |
|------|----------------|------|
| **短剧模式** | `director` | 适合剧情类短视频，AI 自动编排分镜和导演风格 |
| **旁白模式** | `narration` | 适合旁白解说类视频，以旁白叙述为主要驱动 |
| **短片模式** | `short-film` | 适合短片创作，兼顾剧情与电影感画面表达 |

如果用户未明确指定模式，默认使用**短剧模式**（`director`）。

## 工作流函数

主要使用 `execute_workflow` 函数执行完整工作流。该函数**一步完成**创建项目与提交任务，并自动处理后续步骤：
1. 创建项目 + 提交任务（合并为一步）
2. 循环查询进度（每3秒查询一次）
3. 自动检测待支付状态并执行支付（如果需要）
4. 等待任务完成（最多等待1小时）
5. 返回视频下载链接或错误信息

**重要**：只需调用此函数一次，等待返回结果即可。

### 函数签名

```python
execute_workflow(
    diy_story: str,                    # 故事创意内容（必需）
    aspect: str,                       # 视频宽高比 (16:9/9:16)（必需）
    project_name: str,                 # 项目名称（必需）
    video_duration: str = "auto",      # 视频时长，默认为"auto"（可选）
    style_id: Optional[int] = None,    # 风格ID（可选）
    project_type: str = "director"     # 项目类型，默认为"director"（可选）
)
```

### 参数说明

1. **diy_story**（必需）：故事创意内容
2. **aspect**（必需）：视频宽高比，可选值：`16:9` 或 `9:16`
3. **project_name**（必需）：项目名称
4. **video_duration**（可选）：视频时长，可选值：`auto`、`30`、`60`、`120`、`180`、`240`、`300`。如果用户不提及时长，默认使用 `"auto"`
5. **style_id**（可选）：风格ID。如果用户不指定风格ID，默认不传此参数
6. **project_type**（可选）：项目类型，可选值：`director`（短剧模式）、`narration`（旁白模式）或 `short-film`（剧情模式）。如果用户不指定，默认使用 `"director"`

### 使用流程

1. **提示用户选择生成模式**（必须在执行工作流前询问）：
   - **短剧模式**（`director`）：适合剧情类短视频
   - **旁白模式**（`narration`）：适合旁白解说类视频
   - **短片模式**（`short-film`）：适合短片创作，兼顾剧情与电影感
   - 如果用户不明确选择，默认使用短剧模式

2. **如果用户想查看可用风格**：
   - 调用 `get_styles()` 函数获取风格列表
   - 向用户展示所有可用风格（ID、名称、分类、描述）
   - 等待用户选择风格

3. **执行工作流**：
   - 调用 `execute_workflow()` 函数
   - 传入用户提供的故事创意、比例、项目名称
   - 根据用户选择的模式传入 `project_type`（`director`、`narration` 或 `short-film`）
   - 如果用户指定了时长，传入时长参数；否则使用默认值 `"auto"`
   - 如果用户选择了风格，传入风格ID；否则不传风格ID参数
   - **等待函数返回结果**：函数会自动处理所有步骤（创建项目、提交任务、查询进度、支付、等待完成），最终返回视频下载链接或错误信息

### 示例

**查看风格列表**：
```python
api = TrusteeModeAPI()
styles_result = api.get_styles()
# 展示风格列表给用户
```

**执行工作流（不指定时长和风格）**：
```python
api = TrusteeModeAPI()
# 调用后会阻塞等待，直到返回下载链接或错误信息
result = api.execute_workflow(
    diy_story="一个关于冒险的故事...",
    aspect="16:9",
    project_name="我的视频项目"
)
# result 包含下载链接或错误信息
```

**执行工作流（指定时长，不指定风格）**：
```python
api = TrusteeModeAPI()
# 调用后会阻塞等待，直到返回下载链接或错误信息
result = api.execute_workflow(
    diy_story="一个关于冒险的故事...",
    aspect="16:9",
    project_name="我的视频项目",
    video_duration="60"
)
# result 包含下载链接或错误信息
```

**执行工作流（指定时长和风格）**：
```python
api = TrusteeModeAPI()
# 调用后会阻塞等待，直到返回下载链接或错误信息
result = api.execute_workflow(
    diy_story="一个关于冒险的故事...",
    aspect="16:9",
    project_name="我的视频项目",
    video_duration="60",
    style_id=142
)
# result 包含下载链接或错误信息
```

**执行工作流（旁白模式）**：
```python
api = TrusteeModeAPI()
# 使用旁白模式（narration）生成视频
result = api.execute_workflow(
    diy_story="今天我们来聊一聊人工智能的发展...",
    aspect="16:9",
    project_name="旁白解说视频",
    project_type="narration"
)
# result 包含下载链接或错误信息
```

**执行工作流（短片模式）**：
```python
api = TrusteeModeAPI()
# 使用短片模式（short-film）生成视频
result = api.execute_workflow(
    diy_story="夕阳西下，老渔夫独自划船归来，身后是染红的海面……",
    aspect="16:9",
    project_name="短片示例",
    project_type="short-film"
)
# result 包含下载链接或错误信息
```

### 返回值

**注意**：函数会阻塞执行，直到任务完成（成功或失败）或超时（1小时）。调用后只需等待返回结果即可。

成功时返回包含下载链接的响应：
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

说明：`video_asset.download_url` 有值，需要返回完整的下载链接。正确返回：
```json
https://assets.giggle.pro/private/ai_director/348e4956c7bd4f763b/qzjc7gwkpf.mp4?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9hc3NldHMuZ2lnZ2xlLnByby9wcml2YXRlL2FpX2RpcmVjdG9yLzM0OGU0OTU2YzdiZDRmNzYzYi9xempjN2d3a3BmLm1wNCoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3NzMyNzM1OTkwMDB9fX1dfQ__&Key-Pair-Id=K36RVPYROCSUEJ&Signature=StUnhxVXvyK-KRDF3NAWC51nCOKYE31seHnsNr5B%7E3KM4QhtF9rZOt1GzYx-WW7Yt3r4wxtjuk%7E6KxVtbgTzCAHxjweKzLwyEoIJpeZ6xX36jmPwtk8381e4BIwwa%7EjxbO3pKkOS8ZPIs-5JirJRqOAU7bOT8tf%7EHBMZF11WgbnbkI7jmBibefh0cvjhBrhQl681YxcFozXw5PbrlPQpwGe90tOrWbhBKXjcXQGJa8SSLf2NDwZucjnTK40piDcAxJoAHCRd-q5AYhdIVMxfVY0kWndXHKYPRBwzX0iyNDcfcDhJdAnlZlBPP9l8c0F9yATKhhAFLMaJdt8Qybse4g__&response-content-disposition=attachment
```
错误返回：
```json
https://assets.giggle.pro/private/ai_director/348e4956c7bd4f763b/qzjc7gwkpf.mp4
```

失败时返回错误信息：
```json
{
    "code": -1,
    "msg": "错误信息",
    "data": null
}
```
