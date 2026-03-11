---
name: giggle-generation-aimv
description: Use this skill whenever the user wants to create an AI music video (MV) — including generating music from a text prompt, using custom lyrics, or uploading existing audio. Calls Giggle.pro MV trustee API to run the full end-to-end workflow. Trigger on: generate MV, music video, make a video for this song, lyrics video, create MV, AI music video, music + video, video from lyrics, upload music to video. Requires a reference image (style base) and supports subtitles, aspect ratio (16:9 / 9:16), and three music modes (prompt / custom lyrics / upload).
---

# MV Trustee Mode API Skill

Calls the MV trustee mode API to run the full MV generation workflow. **Project creation and task submission are merged into a single step inside the script** — call `execute_workflow` once; never split create and submit.

## First-Time Setup (Required)

**Before any operation, verify that the user has configured the API key.**

**API Key**: Log in to [Giggle.pro](https://giggle.pro/) and obtain the API key from your account settings.

Configuration (choose one):
1. **Project root `.env`**: Copy `env.example` to `.env` and set `GIGGLE_API_KEY=your_api_key`
2. **Environment variable**: `export GIGGLE_API_KEY=your_api_key`

**Check steps**:
1. Confirm the user has configured `GIGGLE_API_KEY` in `.env` or environment variables
2. If not configured, **prompt the user**:
   > Hi! Before using the MV generation feature, you need to configure your API key. Please go to [Giggle.pro](https://giggle.pro/) to obtain an API Key, then create a `.env` file in the project root (see `env.example`), add `GIGGLE_API_KEY=your_api_key`, or set it via environment variable.
3. Wait for user confirmation before proceeding with the workflow

## Three Music Generation Modes

| Mode | music_generate_type | Required params | Description |
|------|---------------------|-----------------|-------------|
| **Prompt mode** | `prompt` | prompt, vocal_gender | Describe the music in text |
| **Custom mode** | `custom` | lyrics, style, title | Provide lyrics, style, and title |
| **Upload mode** | `upload` | music_asset_id | Use an existing uploaded music asset |

### Shared Parameters (Required for All Modes)

- **reference_image** or **reference_image_url**: Reference image — provide at least one (asset_id or download URL). This field also accepts base64-encoded images, e.g. `"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="`
- **aspect**: Aspect ratio, `16:9` or `9:16`
- **scene_description**: Visual scene description, **empty by default** — set only when the user explicitly mentions a scene (max 200 chars)
- **subtitle_enabled**: Enable subtitles, **default false**

### Mode-Specific Parameters

**Prompt mode**:
- `prompt`: Music description (required)
- `vocal_gender`: Vocal gender — `male` / `female` / `auto` (optional, default `auto`)
- `instrumental`: Instrumental only (optional, default false)

**Custom mode**:
- `lyrics`: Lyrics content (required)
- `style`: Music style (required)
- `title`: Song title (required)

**Upload mode**:
- `music_asset_id`: Existing music asset ID (required)

## Workflow Function

Use `execute_workflow` to run the full workflow — **call once and wait**. Internally handles: create project + submit task (combined) → poll progress (every 3 sec) → detect and pay if pending → wait for completion (max 1 hour).

**Important**:
- Never call `create_project` and `submit_mv_task` separately — always use `execute_workflow` or `create_and_submit`
- After calling, just wait for the function to return; all intermediate steps are handled automatically

### Function Signature

```python
execute_workflow(
    music_generate_type: str,      # Mode: prompt / custom / upload
    aspect: str,                   # Aspect ratio: 16:9 or 9:16
    project_name: str,             # Project name
    reference_image: str = "",     # Reference image asset_id (mutually exclusive with reference_image_url)
    reference_image_url: str = "", # Reference image URL or base64 (mutually exclusive with reference_image)
    scene_description: str = "",   # Scene description, empty by default
    subtitle_enabled: bool = False,# Subtitles on/off, default False
    # Prompt mode
    prompt: str = "",
    vocal_gender: str = "auto",
    instrumental: bool = False,
    # Custom mode
    lyrics: str = "",
    style: str = "",
    title: str = "",
    # Upload mode
    music_asset_id: str = "",
)
```

### Parameter Extraction Rules

1. **reference_image vs reference_image_url**: At least one is required. Use `reference_image` for asset_id, `reference_image_url` for image link or base64.
2. **scene_description**: Empty by default — fill only when user explicitly mentions "scene", "visual description", or "visual style".
3. **subtitle_enabled**: Default False — set True only when user explicitly requests subtitles.
4. **aspect**: Use `9:16` when user mentions portrait/vertical/9:16; otherwise default to `16:9`.
5. **Mode selection**: "describe the music / use a prompt" → prompt; "here are the lyrics / lyrics are" → custom; "upload music / use my audio" → upload.

### Examples

**Prompt mode**:
```python
api = MVTrusteeAPI()
result = api.execute_workflow(
    music_generate_type="prompt",
    aspect="16:9",
    project_name="My MV",
    reference_image_url="https://example.com/ref.jpg",
    prompt="Upbeat pop music, sunny beach vibes",
    vocal_gender="female"
)
```

**Custom mode (user provides lyrics)**:
```python
result = api.execute_workflow(
    music_generate_type="custom",
    aspect="9:16",
    project_name="Lyrics MV",
    reference_image="asset_xxx",
    lyrics="Verse 1: Spring wind blows...",
    style="pop",
    title="Spring Song"
)
```

**Upload mode**:
```python
result = api.execute_workflow(
    music_generate_type="upload",
    aspect="16:9",
    project_name="Uploaded Music MV",
    reference_image="asset_yyy",
    music_asset_id="music_asset_zzz"
)
```

**With scene description** (when user explicitly describes a scene):
```python
result = api.execute_workflow(
    music_generate_type="prompt",
    aspect="16:9",
    project_name="Scene MV",
    reference_image_url="https://...",
    prompt="Electronic dance music",
    scene_description="City night scene, neon lights flashing, traffic flowing"
)
```

### Submit Task API Request Examples (Prompt Mode)

Submit endpoint (`/api/v1/trustee_mode/mv/submit`) request body:

```json
{
  "project_id": "c0cb1f32-bb07-4449-add5-e42ccfca1ab6",
  "music_generate_type": "prompt",
  "prompt": "A cheerful pop song",
  "vocal_gender": "female",
  "instrumental": false,
  "reference_image_url": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMTEhUT...(base64 image data)",
  "scene_description": "A romantic beach walk at sunset, waves gently lapping the shore, pink sky gradient",
  "aspect": "16:9",
  "subtitle_enabled": false
}
```

Note: `reference_image` (asset_id) and `reference_image_url` (link or base64) are mutually exclusive.

**Custom mode**:

```json
{
  "project_id": "0ea74500-9178-4693-b581-342d5e17994c",
  "music_generate_type": "custom",
  "lyrics": "Verse 1:\nStanding by the sea watching the sunset\nMemories rush in like waves\n\nChorus:\nLet the sea breeze blow away all worries\nIn this golden moment\nWe found each other\n",
  "style": "pop ballad",
  "title": "Seaside Memories",
  "reference_image": "is45gnvumgd",
  "scene_description": "A couple walking on the beach at dusk, long shadows, orange-red sky gradient",
  "aspect": "9:16",
  "subtitle_enabled": false
}
```

**Upload mode**:

```json
{
  "project_id": "0ea74500-9178-4693-b581-342d5e17994c",
  "music_generate_type": "upload",
  "music_asset_id": "music_asset_789",
  "reference_image": "is45gnvumgd",
  "scene_description": "City night scene, neon lights, dense traffic, rain-soaked streets reflecting light",
  "aspect": "16:9",
  "subtitle_enabled": true
}
```

### Query Progress API Response Example

Query endpoint (`/api/v1/trustee_mode/mv/query`) response (all steps completed):

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

Note: When `pay_status` is `pending`, call the payment endpoint. Once all `steps` are completed, `video_asset.download_url` is populated — return the full signed URL. Correct return:
```json
https://assets.giggle.pro/private/ai_director/348e4956c7bd4f763b/qzjc7gwkpf.mp4?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9hc3NldHMuZ2lnZ2xlLnByby9wcml2YXRlL2FpX2RpcmVjdG9yLzM0OGU0OTU2YzdiZDRmNzYzYi9xempjN2d3a3BmLm1wNCoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3NzMyNzM1OTkwMDB9fX1dfQ__&Key-Pair-Id=K36RVPYROCSUEJ&Signature=StUnhxVXvyK-KRDF3NAWC51nCOKYE31seHnsNr5B%7E3KM4QhtF9rZOt1GzYx-WW7Yt3r4wxtjuk%7E6KxVtbgTzCAHxjweKzLwyEoIJpeZ6xX36jmPwtk8381e4BIwwa%7EjxbO3pKkOS8ZPIs-5JirJRqOAU7bOT8tf%7EHBMZF11WgbnbkI7jmBibefh0cvjhBrhQl681YxcFozXw5PbrlPQpwGe90tOrWbhBKXjcXQGJa8SSLf2NDwZucjnTK40piDcAxJoAHCRd-q5AYhdIVMxfVY0kWndXHKYPRBwzX0iyNDcfcDhJdAnlZlBPP9l8c0F9yATKhhAFLMaJdt8Qybse4g__&response-content-disposition=attachment
```
Wrong (unsigned URL only):
```json
https://assets.giggle.pro/private/ai_director/348e4956c7bd4f763b/qzjc7gwkpf.mp4
```

### Payment API Request and Response

Payment endpoint (`/api/v1/trustee_mode/mv/pay`):

**Request body**:
```json
{
  "project_id": "28b4f4f7-d219-4754-a78b-d9896cd16573"
}
```

**Response**:
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

### Retry API Request Example

When a step fails, guide the user to call the retry endpoint to resume from that step:

```json
{
  "project_id": "28b4f4f7-d219-4754-a78b-d9896cd16573",
  "current_step": "shot"
}
```

Note: `current_step` is the step name to retry (e.g. `music-generate`, `storyboard`, `shot`, `editor`).

### create_and_submit (Optional)

To only create the project and submit the task without waiting for completion, use `create_and_submit`. **Never** call `create_project` and `submit_mv_task` separately:

```python
api = MVTrusteeAPI()
r = api.create_and_submit(
    project_name="My MV",
    music_generate_type="prompt",
    aspect="16:9",
    reference_image_url="https://...",
    prompt="Upbeat pop music"
)
# Returns project_id for manual query/pay later
```

### Return Value

Success:
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

Failure returns an error message.
