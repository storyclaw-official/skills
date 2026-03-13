---

name: giggle-generation-video
description: Supports text-to-video and image-to-video (start/end frame). Use when the user needs to generate video, create short videos, or convert text to video. Use cases: (1) Generate video from text description, (2) Use reference images as start/end frame for image-to-video, (3) Customize model, aspect ratio, duration, resolution. Triggers: generate video, text-to-video, image-to-video, AI video.
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

[简体中文](./SKILL.zh-CN.md) | English

# Giggle Video Generation

Generates AI videos via giggle.pro's Generation API. Supports text-to-video and image-to-video.

**API Key**: Load priority 1) `~/.openclaw/.env` (preferred) 2) System environment variable `GIGGLE_API_KEY`. The script will prompt if not configured.

> **No inline Python**: All commands must be executed via the `exec` tool. **Never** use `python3 << 'EOF'` or heredoc inline code.

## Supported Models

| Model | Supported Durations (s) | Default | Description |
|-------|-------------------------|---------|-------------|
| grok | 6, 10 | 6 | Strong overall capability, recommended |
| grok-fast | 6, 10 | 6 | grok fast version |
| sora2 | 4, 8, 12 | 4 | OpenAI Sora 2 |
| sora2-pro | 4, 8, 12 | 4 | Sora 2 Pro |
| sora2-fast | 10, 15 | 10 | Sora 2 Fast |
| sora2-pro-fast | 10, 15 | 10 | Sora 2 Pro Fast |
| kling25 | 5, 10 | 5 | Kling video model |
| seedance15-pro | 4, 8, 12 | 4 | Seedance Pro (with audio) |
| seedance15-pro-no-audio | 4, 8, 12 | 4 | Seedance Pro (no audio) |
| veo31 | 4, 6, 8 | 4 | Google Veo 3.1 (with audio) |
| veo31-no-audio | 4, 6, 8 | 4 | Google Veo 3.1 (no audio) |
| minimax23 | 6 | 6 | MiniMax model |
| wan25 | 5, 10 | 0 | Wanxiang model |

**Note**: `--duration` must be chosen from the model's supported durations, otherwise the API will error.

---

## Frame Reference (Image-to-Video)

For image-to-video, `--start-frame` and `--end-frame` support three mutually exclusive formats:

| Method | Format | Example |
|--------|--------|---------|
| asset_id | `asset_id:<ID>` | `asset_id:lkllv0yv81` |
| url | `url:<URL>` | `url:https://example.com/img.jpg` |
| base64 | `base64:<DATA>` | `base64:iVBORw0KGgo...` |

Each frame parameter can only use one of these methods.

---

## Execution Flow (Three-Phase Dual-Path)

Video generation typically takes 60–300 seconds. Uses "fast submit + Cron poll + sync fallback" three-phase architecture.

> **Important**: **Never** pass `GIGGLE_API_KEY` in exec's `env` parameter. API Key is read from `~/.openclaw/.env` or system environment.

---

### Phase 1: Submit Task (exec completes in ~10 seconds)

**First send a message to the user**: "Video generation in progress, usually takes 1–5 minutes. Results will be sent automatically."

```bash
# Text-to-video (default grok-fast)
python3 scripts/generation_api.py \
  --prompt "Camera slowly pushes forward, person smiling in frame" \
  --model grok-fast --duration 6 \
  --aspect-ratio 16:9 --resolution 720p \
  --no-wait --json

# Image-to-video - use asset_id as start frame
python3 scripts/generation_api.py \
  --prompt "Person slowly turns around" \
  --start-frame "asset_id:lkllv0yv81" \
  --model grok-fast --duration 6 \
  --aspect-ratio 16:9 --resolution 720p \
  --no-wait --json

# Image-to-video - use URL as start frame
python3 scripts/generation_api.py \
  --prompt "Scenery from still to motion" \
  --start-frame "url:https://example.com/img.jpg" \
  --model grok-fast --duration 6 \
  --no-wait --json

# Image-to-video - both start and end frame
python3 scripts/generation_api.py \
  --prompt "Scene transition" \
  --start-frame "asset_id:abc123" \
  --end-frame "url:https://example.com/end.jpg" \
  --model grok --duration 6 \
  --no-wait --json
```

Response example:

```json
{"status": "started", "task_id": "55bf24ca-e92a-4d9b-a172-8f585a7c5969"}
```

**Immediately store task_id in memory** (`addMemory`):

```
giggle-generation-video task_id: xxx (submitted: YYYY-MM-DD HH:mm)
```

---

### Phase 2: Register Cron (60 second interval)

Use the `cron` tool to register the polling job. **Strictly follow the parameter format**:

```json
{
  "action": "add",
  "job": {
    "name": "giggle-generation-video-<first 8 chars of task_id>",
    "schedule": {
      "kind": "every",
      "everyMs": 60000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "Video task poll: exec python3 scripts/generation_api.py --query --task-id <full task_id>, handle stdout per Cron logic. If stdout is non-JSON plain text, forward to user and remove Cron. If stdout is JSON, do not send message, keep waiting. If stdout is empty, remove Cron immediately."
    },
    "sessionTarget": "main"
  }
}
```

**Cron trigger handling** (based on exec stdout):

| stdout pattern | Action |
|----------------|--------|
| Non-empty plain text (not starting with `{`) | **Forward to user as-is**, **remove Cron** |
| stdout empty | Already pushed, **remove Cron immediately, do not send message** |
| JSON (starts with `{`, has `"status"` field) | Do not send message, do not remove Cron, keep waiting |

---

### Phase 3: Sync Wait (optimistic path, fallback when Cron hasn't fired)

**Execute this step whether or not Cron registration succeeded.**

```bash
python3 scripts/generation_api.py --query --task-id <task_id> --poll --max-wait 300
```

**Handling logic**:

- Returns plain text (video ready/failed message) → **Forward to user as-is**, remove Cron
- stdout empty → Cron already pushed, remove Cron, do not send message
- exec timeout → Cron continues polling

---

## New Request vs Query Old Task

**When the user initiates a new video generation request**, **must run Phase 1 to submit a new task**. Do not reuse old task_id from memory.

**Only when the user explicitly asks about a previous task's progress** should you query the old task_id from memory.

---

## Parameter Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--prompt` | required | Video description prompt |
| `--model` | grok | See "Supported Models" table |
| `--duration` | model default | Must choose from model's supported durations |
| `--aspect-ratio` | 16:9 | 16:9, 9:16, 1:1, 3:4, 4:3 |
| `--resolution` | 720p | 480p, 720p, 1080p |
| `--start-frame` | - | Image-to-video start frame: `asset_id:ID`, `url:URL`, or `base64:DATA` |
| `--end-frame` | - | Image-to-video end frame, same format as start |

---

Note: base64 parameter supports base64-encoded images, e.g. `"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="`. Pass the raw Base64 string directly, do not add the `data:image/xxx;base64,` prefix.

## Interaction Guide

**When the user request is vague, guide per the steps below. If the user has provided enough info, run the command directly.**

### Step 1: Model Selection (required)

Before generating, **must introduce available models** and let the user choose. Display:

> Please select a video generation model:
>
> **Recommended:**
>
> - **grok** — Strong overall, supports 6/10s (recommended)
> - **grok-fast** — grok fast, supports 6/10s
>
> **Sora series:**
>
> - **sora2** — OpenAI Sora 2, 4/8/12s
> - **sora2-pro** — Sora 2 Pro, 4/8/12s
> - **sora2-fast** — Sora 2 Fast, 10/15s
> - **sora2-pro-fast** — Sora 2 Pro Fast, 10/15s
>
> **Others:**
>
> - **kling25** — Kling, 5/10s
> - **seedance15-pro** — Seedance Pro (with audio), 4/8/12s
> - **seedance15-pro-no-audio** — Seedance Pro (no audio), 4/8/12s
> - **veo31** — Google Veo 3.1 (with audio), 4/6/8s
> - **veo31-no-audio** — Google Veo 3.1 (no audio), 4/6/8s
> - **minimax23** — MiniMax, 6s only
> - **wan25** — Wanxiang, 5/10s

Wait for explicit user choice before continuing.

### Step 2: Video Duration

For the chosen model, show supported duration options. Default to the model's default duration.

### Step 3: Generation Mode

```
Question: "Do you need reference images as start/end frame?"
Title: "Generation Mode"
Options:
- "No - text-to-video only"
- "Yes - image-to-video (set start/end frame)"
multiSelect: false
```

### Step 4: Aspect Ratio

```
Question: "What aspect ratio do you need?"
Title: "Aspect Ratio"
Options:
- "16:9 - Landscape (recommended)"
- "9:16 - Portrait (short video)"
- "1:1 - Square"
multiSelect: false
```

### Step 5: Execute and Display

Follow the execution flow: send message → Phase 1 submit → Phase 2 register Cron → Phase 3 sync wait.

When results arrive, forward exec stdout to the user as-is.

**Link return rule**: Video links in results must be **full signed URLs** (with Policy, Key-Pair-Id, Signature query params). Correct: `https://assets.giggle.pro/...?Policy=...&Key-Pair-Id=...&Signature=...`. Wrong: do not return unsigned URLs with only the base path (no query params).
