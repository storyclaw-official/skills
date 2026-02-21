---
name: giggle-drama
description: 用户在有生成视频需求、生成短视频需求、有一个创意需要生成视频、或查看可用风格时使用此skill，可以引导用户查看风格。
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🎬","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/scripts/requirements.txt","cp {baseDir}/.env.example {baseDir}/.env","echo 'Please edit .env and add your GIGGLE_API_KEY'"]},"version":"1.0.0","author":"姜式伙伴"}
---

# 托管模式V2 API Skill

此skill用于调用托管模式V2 API，执行完整的视频生成工作流。

## 启动指令

**重要**：每次skill启动时，必须：
1. 使用标题："🎬 **「姜式伙伴」AI 导演 - 智能视频创作助手**"
2. 向用户展示以下"可用视频风格"列表，让用户了解可以选择的风格选项
3. 询问用户需要提供的信息（故事创意、视频比例、项目名称、时长、风格）
4. 在询问信息后，展示一个简洁的使用范例，格式如："关于故乡记忆的短视频，回忆杀，16:9，30s"

## 可用视频风格

在生成视频时，您可以选择以下任一风格（style_id）：

| ID  | 风格名称 | 分类 | 描述 |
|-----|---------|------|------|
| 142 | 3D古风 | 3D动画 | 3D 国风仙侠风格，偏 CG 渲染质感，人物与场景具有史诗级幻想氛围 |
| 143 | 2D漫剧 | 2D插画 | 融合日漫与国漫风格的二次元画风，低饱和配色，适合剧情向插画 |
| 144 | 吉卜力 | 2D插画 | 治愈系手绘插画风格，色彩柔和，情绪温暖，富有生活气息 |
| 145 | 皮克斯 | 3D动画 | 典型皮克斯风格的 3D 卡通动画，角色圆润，情绪表达强烈 |
| 146 | 写实风格 | 电影写实 | 偏电影级的写实视觉风格，强调真实光影与镜头感 |
| 147 | 二次元 | 2D插画 | 标准二次元动漫画风，线条清晰，色彩明亮，细节丰富 |
| 148 | 国风水墨 | 2D插画 | 中国传统水墨风格插画，讲究留白与意境表达 |

**提示**：如果不指定风格ID，系统将自动选择最适合您故事内容的风格。

## 工作流函数

主要使用 `execute_workflow` 函数执行完整工作流。该函数会自动执行以下步骤：
1. 创建项目
2. 提交任务
3. 循环查询进度（每3秒查询一次）
4. 自动检测待支付状态并执行支付（如果需要）
5. 等待任务完成（最多等待1小时）
6. 🎬 **自动下载视频到本地**（新功能！）
7. 返回视频下载链接和本地路径

**重要**：调用此函数后，只需等待函数返回结果即可，函数会自动处理所有中间步骤。视频会自动下载到 `~/Downloads/giggle-videos/` 目录。

### 函数签名

```python
execute_workflow(
    diy_story: str,           # 故事创意内容（必需）
    aspect: str,              # 视频宽高比 (16:9/9:16)（必需）
    project_name: str,        # 项目名称（必需）
    video_duration: str = "auto",  # 视频时长，默认为"auto"（可选）
    style_id: Optional[int] = None  # 风格ID（可选）
)
```

### 参数说明

1. **diy_story**（必需）：故事创意内容
2. **aspect**（必需）：视频宽高比，可选值：`16:9` 或 `9:16`
3. **project_name**（必需）：项目名称
4. **video_duration**（可选）：视频时长，可选值：`auto`、`30`、`60`、`120`、`180`、`240`、`300`。如果用户不提及时长，默认使用 `"auto"`
5. **style_id**（可选）：风格ID。如果用户不指定风格ID，默认不传此参数

### 使用流程

1. **如果用户想查看可用风格**：
   - 调用 `get_styles()` 函数获取风格列表
   - 向用户展示所有可用风格（ID、名称、分类、描述）
   - 等待用户选择风格

2. **执行工作流**：
   - 调用 `execute_workflow()` 函数
   - 传入用户提供的故事创意、比例、项目名称
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

### 返回值

**注意**：函数会阻塞执行，直到任务完成（成功或失败）或超时（1小时）。调用后只需等待返回结果即可。

成功时返回包含下载链接和本地路径的响应：
```json
{
    "code": 200,
    "msg": "success",
    "uuid": "...",
    "data": {
        "project_id": "...",
        "download_url": "https://...",
        "local_path": "/Users/xxx/Downloads/giggle-videos/项目名称_20260206_220000.mp4",
        "video_asset": {...},
        "status": "completed"
    }
}
```

失败时返回错误信息：
```json
{
    "code": -1,
    "msg": "错误信息",
    "data": null
}
```

## 🎯 重要：如何向用户展示结果

**当视频生成成功后，你必须向用户清晰展示视频 URL：**

```
✅ 视频生成成功！

🎬 视频链接：https://...（从 result["data"]["download_url"] 获取）
📁 本地路径：/path/to/video.mp4

您可以点击上面的链接在线观看或下载视频。
```

**关键要求：**
1. **必须提取并展示 `result["data"]["download_url"]`**
2. **使用清晰的标识（如 🎬）突出显示视频链接**
3. **告诉用户可以点击链接观看或下载**
4. **不要只展示本地路径，视频 URL 才是用户最需要的**
