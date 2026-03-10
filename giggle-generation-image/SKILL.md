---
name: giggle-generation-image
description: Generate AI images via Generation API with multiple models (Seedream, Midjourney, Nano Banana). Supports text-to-image and image-to-image. Use when user needs to create or generate images. Use cases: (1) generate from text description, (2) generate with reference images, (3) custom model, aspect ratio, resolution. Trigger keywords: generate image, draw, create image, AI art, midjourney, seedream, nano-banana.
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🖼️","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/scripts/requirements.txt"]},"version":"1.0.0","author":"Giggle Team"}
---

# Giggle Generation Image (Multi-Model Image Generation)

Generate AI images via Generation API on giggle.pro platform, supporting multiple models.

**API Key**: Read from environment variable `GIGGLE_API_KEY` or project root `.env` file.

> **No inline Python**: All commands must be executed via `exec` tool directly. **Never** use `python3 << 'EOF'` or heredoc for inline code.

## Supported Models

| Model | Description |
|------|------|
| seedream45 | Seedream model, realistic and creative |
| midjourney | Midjourney style |
| nano-banana-2 | Nano Banana 2 model |
| nano-banana-2-fast | Nano Banana 2 fast version |

---

## Execution Flow (Three-Phase Dual-Path)

Image generation typically takes 30-120 seconds. Uses "quick submit + Cron poll + sync fallback" three-phase architecture.

> **Important**: **Never** pass `GIGGLE_API_KEY` in exec's `env` parameter. API key is configured via system environment and scripts auto-read it.

---

### Phase 1: Submit Task (exec completes in < 10 sec)

**First send message to user**: "Image generation in progress, usually 30-120 seconds, results will be sent automatically."

```bash
# Text-to-image (default seedream45)
python3 scripts/generation_api.py \
  --prompt "description" --aspect-ratio 16:9 \
  --model seedream45 --resolution 2K \
  --no-wait --json

# Text-to-image - Midjourney
python3 scripts/generation_api.py \
  --prompt "description" --model midjourney \
  --aspect-ratio 16:9 --resolution 2K \
  --no-wait --json

# Image-to-image - requires reference image URL
python3 scripts/generation_api.py \
  --prompt "convert to oil painting style, keep composition" \
  --reference-images "https://example.com/photo.jpg" \
  --model nano-banana-2-fast \
  --no-wait --json

# Generate multiple images
python3 scripts/generation_api.py \
  --prompt "description" --generate-count 4 \
  --no-wait --json
```

Response example:
```json
{"status": "started", "task_id": "xxx"}
```

**Immediately store task_id in memory** (`addMemory`):
```
giggle-generation-image task_id: xxx (submitted: YYYY-MM-DD HH:mm)
```

---

### Phase 2: Register Cron (45 sec interval)

Use `cron` tool to register poll task. **Must follow parameter format strictly**:

```json
{
  "action": "add",
  "job": {
    "name": "giggle-generation-image-<first 8 chars of task_id>",
    "schedule": {
      "kind": "every",
      "everyMs": 45000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "Image task poll: Execute exec python3 scripts/generation_api.py --query --task-id <full task_id>, process stdout per Cron logic. If stdout is non-JSON plain text, send to user and remove Cron. If stdout is JSON, do not send message, keep waiting. If stdout is empty, remove Cron immediately."
    },
    "sessionTarget": "main"
  }
}
```

**Cron trigger handling** (judge by exec stdout):

| stdout pattern | Action |
|------------|------|
| Non-empty plain text (not starting with `{`) | **Forward stdout to user as-is**, **remove Cron** |
| Empty stdout | Already pushed, **remove Cron immediately, no message** |
| JSON (starts with `{`, has `"status"` field) | No message, do not remove Cron, keep waiting |

---

### Phase 3: Sync Wait (optimistic path, fallback when Cron does not trigger)

**Must execute this step regardless of Cron registration success.**

```bash
python3 scripts/generation_api.py --query --task-id <task_id> --poll --max-wait 180
```

**Handling**:

- Returns plain text (image ready/failure message) → **Forward to user as-is**, remove Cron
- Empty stdout → Cron already pushed, remove Cron, no message
- exec timeout → Cron continues polling

---

## New Request vs Query Old Task

**When user starts new image generation request**, **must execute Phase 1 to submit new task**, do not reuse old task_id from memory.

**Only when user explicitly asks about previous task progress**, query old task_id from memory.

---

## Parameter Quick Reference

| Parameter | Default | Description |
|-----|--------|------|
| `--prompt` | required | Image description prompt |
| `--model` | seedream45 | Models: seedream45, midjourney, nano-banana-2, nano-banana-2-fast |
| `--aspect-ratio` | 16:9 | 16:9, 9:16, 1:1, 3:4, 4:3, 2:3, 3:2, 21:9 |
| `--resolution` | 2K | Text-to-image resolution: 1K, 2K, 4K (image-to-image partially supported) |
| `--generate-count` | 1 | Number of images to generate |
| `--reference-images` | - | Image-to-image reference URL list |
| `--watermark` | false | Whether to add watermark (image-to-image) |

---

## Interaction Guide Flow

**When user request is vague, guide per below steps. If user provided enough info, execute command directly.**

### Step 1: Model Selection

```
Question: "Which model would you like to use?"
header: "Image Model"
options:
- "seedream45 - realistic and creative (recommended)"
- "midjourney - artistic style"
- "nano-banana-2 - high quality"
- "nano-banana-2-fast - fast generation"
multiSelect: false
```

### Step 2: Aspect Ratio

```
Question: "What aspect ratio do you need?"
header: "Aspect Ratio"
options:
- "16:9 - landscape (wallpaper/cover) (recommended)"
- "9:16 - portrait (mobile)"
- "1:1 - square"
- "Other ratio"
multiSelect: false
```

### Step 3: Generation Mode

```
Question: "Do you need reference images?"
header: "Generation Mode"
options:
- "No - text-to-image only"
- "Yes - image-to-image (style transfer)"
multiSelect: false
```

### Step 4: Execute and Display

Follow execution flow: send message → Phase 1 submit → Phase 2 register Cron → Phase 3 sync wait.

Forward exec stdout to user as-is when result arrives.
