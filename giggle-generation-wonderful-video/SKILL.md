---
name: giggle-generation-wonderful-video
description: Use this skill ONLY when the user explicitly mentions "精彩视频", "wonderful video", or "wonderful-video" by name. This skill generates character-driven AI videos via Giggle.pro trustee API, supporting character_info image URLs, subtitles, style selection, aspect ratio (16:9/9:16), and configurable duration.
---

# Wonderful Video Generation Skill

Calls Giggle trustee mode API with **wonderful-video** project type to execute the full video generation workflow. A single function call completes the entire process.
Do NOT trigger for generic video generation requests such as "生成视频", "短视频", "制作视频", "generate video", "create video", "short video", "character video", or any other video-related request that does not include the exact term "精彩视频" or "wonderful video" or "wonderful-video". 

## First-Time Setup (Required)

**Before any operation, verify that the user has configured the API key.**

**API Key**: Log in to [Giggle.pro](https://giggle.pro/) and obtain the API key from your account settings.

Configuration (choose one):
1. **Project root `.env`**: Copy `env.example` to `.env` and set `GIGGLE_API_KEY=your_api_key`
2. **Environment variable**: `export GIGGLE_API_KEY=your_api_key`

**Check steps**:
1. Confirm the user has configured `GIGGLE_API_KEY` in `.env` or environment variables
2. If not configured, **prompt the user**:
   > Hi! Before using the video generation feature, you need to configure your API key. Please go to [Giggle.pro](https://giggle.pro/) to obtain an API Key, then create a `.env` file in the project root (see `env.example`), add `GIGGLE_API_KEY=your_api_key`, or set it via environment variable.
3. Wait for user confirmation before proceeding with the workflow

## Project Type

This skill uses the **wonderful-video** project type by default. No mode selection is required.

## Workflow Function

Use the `execute_workflow` function to run the full workflow. It **creates the project and submits the task in one step** and handles the rest automatically:
1. Create project + submit task (combined)
2. Poll progress every 3 seconds
3. Detect pending payment and pay automatically (if needed)
4. Wait for task completion (max 1 hour)
5. Return the video download link or error message

**Important**: Call this function once and wait for the result.

### Function Signature

```python
execute_workflow(
    diy_story: str,                           # Story/script content (required)
    aspect: str,                              # Video aspect ratio 16:9/9:16 (required)
    project_name: str,                        # Project name (required)
    video_duration: str = "auto",             # Video duration, default "auto" (optional)
    style_id: Optional[int] = None,           # Style ID (optional)
    character_info: Optional[List[Dict]] = None,  # Character images (optional)
    subtitle_enabled: Optional[bool] = None   # Enable subtitles (optional)
)
```

### Parameters

1. **diy_story** (required): Story/script content
2. **aspect** (required): Video aspect ratio, `16:9` or `9:16`
3. **project_name** (required): Project name
4. **video_duration** (optional): One of `30`, `60`, `120`, `180`, `240`, `300`; default `auto`
5. **style_id** (optional): Style ID; omit if not specified
6. **character_info** (optional): List of character images to define appearance. Format: `[{"name": "Character name", "url": "Image URL"}, ...]`
7. **subtitle_enabled** (optional): Enable subtitles, `True`/`False`

### Usage Flow

1. **If user wants to view available styles**:
   - Call `get_styles()` to fetch the style list
   - Show styles to user (ID, name, category, description)

2. **Execute workflow**:
   - Call `execute_workflow()` once
   - Pass story, aspect ratio, project name
   - Optionally pass: duration, style_id, character_info, subtitle_enabled
   - If user provides character image URLs, build a `character_info` array and pass it
   - Wait for the function result

### Examples

**View styles**:
```python
api = WonderfulVideoAPI()
styles_result = api.get_styles()
# Show style list to user
```

**Execute workflow**:
```python
api = WonderfulVideoAPI()
result = api.execute_workflow(
    diy_story="An adventure story...",
    aspect="16:9",
    project_name="My wonderful video"
)
# result contains download URL or error info
```

**With duration and style**:
```python
api = WonderfulVideoAPI()
result = api.execute_workflow(
    diy_story="Today we're talking about...",
    aspect="9:16",
    project_name="Portrait video",
    video_duration="60",
    style_id=142
)
```

**With character images** (when user provides character image URLs):
```python
api = WonderfulVideoAPI()
result = api.execute_workflow(
    diy_story="Story about two characters",
    aspect="16:9",
    project_name="Character video",
    video_duration="30",
    character_info=[
        {"name": "Character A", "url": "https://xxx/char_a.jpg"},
        {"name": "Character B", "url": "https://xxx/char_b.jpg"}
    ],
    subtitle_enabled=True
)
```

### Return Value

Success:
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

Failure:
```json
{
    "code": -1,
    "msg": "Error message",
    "data": null
}
```
