---
name: giggle-generation-videos
description: Use this skill whenever the user wants to generate a video, create a short film, or explore available video styles. Generates AI videos via Giggle.pro trustee mode V2. Trigger on: generate video, create video, make a short film, AI video, video from story, shoot a video, I have a story idea, short drama, narration video, cinematic video, what video styles are available. Supports three modes — drama (director), narration, and short-film — with configurable aspect ratio (16:9/9:16), duration, and style selection.
---

# Video Generation (Trustee Mode V2)

Calls the Giggle.pro Trustee Mode V2 API to run the full video generation workflow from project creation to final video.

## First-Time Setup (Required)

Before any operation, confirm the user has configured the API key so the workflow does not fail mid-way due to auth.

- **API Key**: Log in to [Giggle.pro](https://giggle.pro/) and obtain the API key from your account settings.
- **Configuration (choose one)**:
  1. **Project root `.env`**: Copy `env.example` to `.env` and set `GIGGLE_API_KEY=your_api_key`
  2. **Environment variable**: `export GIGGLE_API_KEY=your_api_key`

**Check steps**:

1. Confirm the user has configured `GIGGLE_API_KEY` in `.env` or environment variables.
2. If not configured, **prompt the user**:
   > Hi! Before using the video generation feature, you need to configure your API key. Please go to [Giggle.pro](https://giggle.pro/) to obtain an API Key, then create a `.env` file in the project root (see `env.example`), add `GIGGLE_API_KEY=your_api_key`, or set it via environment variable.
3. Wait for user confirmation before proceeding with the workflow.

## Generation Modes

Three modes are supported. **Ask the user to choose a mode before starting the workflow**; if not specified, default to **drama mode** (`director`).

| Mode | project_type | Description |
|------|-------------|-------------|
| **Drama** | `director` | Short drama with AI-directed storyboard and cinematography |
| **Narration** | `narration` | Narration-driven video with voiceover as the primary driver |
| **Short-film** | `short-film` | Cinematic short film balancing story and visual expression |

## Main Workflow: execute_workflow

Use `execute_workflow` to run the full workflow in one go: create project + submit task + poll + auto-pay (if needed) + wait for completion. Call it once and wait for it to return.

1. Create project and submit task (combined)
2. Poll progress every 3 seconds
3. Detect pending payment and pay automatically if needed
4. Wait for completion (max 1 hour)
5. Return the video download link or error message

### Function Signature

```python
execute_workflow(
    diy_story: str,                    # Story/script content (required)
    aspect: str,                       # Aspect ratio: 16:9 or 9:16 (required)
    project_name: str,                 # Project name (required)
    video_duration: str = "auto",       # Duration, default "auto" (optional)
    style_id: Optional[int] = None,    # Style ID (optional)
    project_type: str = "director"     # Mode, default "director" (optional)
)
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| diy_story | Yes | Story or script content |
| aspect | Yes | Aspect ratio: `16:9` or `9:16` |
| project_name | Yes | Project name |
| video_duration | No | One of `auto`, `30`, `60`, `120`, `180`, `240`, `300`; default `"auto"` |
| style_id | No | Style ID; omit if not specified |
| project_type | No | `director` / `narration` / `short-film`; default `"director"` |

### Usage Flow

1. **Ask the user to choose a generation mode** (drama / narration / short-film). Default to drama if not specified.
2. **If the user wants to pick a style**: Call `get_styles()` to fetch the list, show ID, name, category, description; wait for the user to choose before continuing.
3. **Run the workflow**:
   - Call `execute_workflow()` with story content, aspect ratio, and project name.
   - Set `project_type` from the user’s mode; pass `video_duration` if specified (otherwise default `"auto"`); pass `style_id` if a style was chosen.
   - **Call once and wait for return** — the function handles create, submit, poll, pay, and completion, then returns the download link or error.

### Examples

**View style list**:

```python
api = TrusteeModeAPI()
styles_result = api.get_styles()
# Show style list to user
```

**Basic workflow (no duration or style)**:

```python
api = TrusteeModeAPI()
result = api.execute_workflow(
    diy_story="An adventure story...",
    aspect="16:9",
    project_name="My Video Project"
)
# result contains download URL or error message
```

**With duration, no style**:

```python
result = api.execute_workflow(
    diy_story="An adventure story...",
    aspect="16:9",
    project_name="My Video Project",
    video_duration="60"
)
```

**With duration and style**:

```python
result = api.execute_workflow(
    diy_story="An adventure story...",
    aspect="16:9",
    project_name="My Video Project",
    video_duration="60",
    style_id=142
)
```

**Narration mode**:

```python
result = api.execute_workflow(
    diy_story="Today let's talk about the development of AI...",
    aspect="16:9",
    project_name="Narration Video",
    project_type="narration"
)
```

**Short-film mode**:

```python
result = api.execute_workflow(
    diy_story="As the sun sets, an old fisherman rows home alone, the sea glowing red behind him...",
    aspect="16:9",
    project_name="Short Film",
    project_type="short-film"
)
```

## Return Value

The function blocks until the task completes (success or failure) or times out (1 hour). Wait for it to return.

**Success** (contains download link):

```json
{
    "code": 200,
    "msg": "success",
    "uuid": "...",
    "data": {
        "project_id": "...",
        "video_asset": {...},
        "status": "completed"
    }
}
```

Return the **full signed URL** to the user (`data.video_asset.download_url`), e.g.:

```
https://assets.giggle.pro/private/ai_director/348e4956c7bd4f763b/qzjc7gwkpf.mp4?Policy=...&Key-Pair-Id=...&Signature=...&response-content-disposition=attachment
```

Do not return the unsigned URL without query params, e.g.:

```
https://assets.giggle.pro/private/ai_director/348e4956c7bd4f763b/qzjc7gwkpf.mp4
```

**Failure**:

```json
{
    "code": -1,
    "msg": "Error message",
    "data": null
}
```
