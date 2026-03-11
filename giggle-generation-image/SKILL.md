---
name: giggle-generation-image
description: Use this skill whenever the user wants to create, generate, or draw images — including text-to-image, image-to-image style transfer, or blending multiple reference images. Generates AI images via Seedream (giggle.pro). Trigger on: generate image, draw, create picture, AI art, make a photo, illustrate, create visual, need an image, style transfer, reference image, Seedream. Supports 1–10 reference images, custom aspect ratio (16:9, 9:16, 1:1, etc.), and batch generation (up to 4 per request).
---

# Generating Images With Seedream

Generate AI images with Seedream model (seedream45) via giggle.pro. Supports text-to-image, image-to-image, and multi-image fusion.

**API Key**: Read from environment variable `GIGGLE_API_KEY` or project root `.env` file.

> **No inline Python**: All commands must be executed via `exec` tool directly. **Never** use `python3 << 'EOF'` or heredoc for inline code. Inline code causes path errors and method name mismatches.

## Execution Flow (Three-Phase Dual-Path)

Image generation typically takes 30-60 seconds. Uses "quick submit + Cron poll + sync fallback" three-phase architecture to ensure users receive results.

> **Important**: **Never** pass `GIGGLE_API_KEY` in exec's `env` parameter. API key is configured via system environment; scripts auto-read it. Execute the commands below directly.

---

### Phase 1: Submit Task (exec completes in < 10 sec)

**First send message to user**: "Image generation in progress, usually 30-60 seconds, results will be sent automatically."

```bash
# Text-to-image
python3 scripts/seedream_api.py \
  --prompt "description" --aspect-ratio 16:9 \
  --no-wait --json

# Image-to-image - URL
python3 scripts/seedream_api.py \
  --prompt "convert to oil painting style, keep composition" \
  --reference-images "https://example.com/photo.jpg" \
  --no-wait --json

# Image-to-image - local file (auto base64 encoded)
python3 scripts/seedream_api.py \
  --prompt "convert to oil painting style, keep composition" \
  --reference-images "/path/to/photo.jpg" \
  --no-wait --json

# Multi-image fusion (2-10 images, URL and local files can be mixed)
python3 scripts/seedream_api.py \
  --prompt "blend the artistic style of these images" \
  --reference-images "url1" "/path/to/local.png" "url2" \
  --no-wait --json

# Generate multiple images
python3 scripts/seedream_api.py \
  --prompt "description" \
  --generate-count 4 \
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

> **No inline Python**: Cron payload exec command must directly call `python3 scripts/seedream_api.py`, **never** use heredoc inline code.

Use `cron` tool to register poll task. **Must follow parameter format strictly; do not modify field names or add extra fields**:

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
      "text": "Image task poll: Execute exec python3 scripts/seedream_api.py --query --task-id <full task_id>, process stdout per Cron logic. If stdout is non-JSON plain text, send to user and remove Cron. If stdout is JSON, do not send message, keep waiting. If stdout is empty, remove Cron immediately."
    },
    "sessionTarget": "main"
  }
}
```

After registration, Cron sends a system event to Agent every 45 seconds. Agent runs the query command when received.

**Cron trigger handling** (judge by exec stdout; all paths exit 0):

| stdout pattern | Action |
|----------------|--------|
| Non-empty plain text (not starting with `{`) | **Forward stdout to user as-is** (do not add prefix or modify), **remove Cron** (use `cron` tool `action: "remove"`) |
| Empty stdout | Already pushed, **remove Cron immediately, no message** |
| JSON (starts with `{`, has `"status"` field) | No message, do not remove Cron, wait for next poll |

> **Critical**: Markdown links (`[View image N](...)`) in stdout **must be preserved as-is**. Do not extract URLs, do not rewrite link format, do not send bare URLs.

**If Cron registration fails**: Proceed directly to Phase 3.

---

### Phase 3: Sync Wait (optimistic path, fallback when Cron does not trigger)

**Purpose**: Mitigate known platform bug where Cron scheduler may not fire; ensure user receives result.

**Must execute this step regardless of Cron registration success.**

> **No inline Python**: Must directly execute the command below, **never** use heredoc inline code.

```bash
python3 scripts/seedream_api.py --query --task-id <task_id> --poll --max-wait 180
```

**Handling**:

- Returns plain text (image ready/failure message) → **Forward to user as-is**, remove Cron
- Empty stdout → Cron already pushed, remove Cron, no message
- exec timeout → Cron continues polling

> Script polls every 5 seconds internally; exits automatically without duplicate push if Cron already pushed (`.sent` marker exists).

---

## New Request vs Query Old Task (Important Distinction)

**When user starts new image generation request** (e.g. "generate an image of XX", "draw XX"), **must execute Phase 1 to submit new task**. Do not reuse old task_id from memory. Each new request is a fresh task.

**Only when user explicitly asks about previous task progress** (e.g. "is my last image ready?", "how's that image?") should you query old task_id from memory:

1. **task_id in memory** → Execute `--query --task-id xxx`
2. **No task_id in memory** → Inform user, ask if they want to regenerate

---

## Result Display Format

Script outputs user-friendly plain text (non-JSON) when task completes:

**Success example**:

```
Image ready! ✨

Creation for "Beautiful campus scenery" is complete ✨

[View image 1](https://assets.giggle.pro/...)

Feel free to ask for adjustments~
```

**Failure example**:

```
Generation encountered a problem

Creation for "Beautiful campus scenery" could not be completed: input may contain sensitive content, blocked by server

Suggest adjusting the description and trying again. Ready when you are~
```

**Forwarding rules**:

- stdout already contains full context (including user prompt); **do not** add text in front
- **Must forward stdout as-is**; no additions, deletions, or rewrites
- Do not extract URLs from brackets to show separately
- Do not send bare URLs (Feishu truncates URLs containing `_`)

---

## Parameter Quick Reference

| Parameter | Default | Options |
|-----------|---------|---------|
| `--aspect-ratio` | 16:9 | 16:9, 9:16, 1:1, 3:4, 4:3, 2:3, 3:2, 21:9 |
| `--generate-count` | 1 | Number of images; max 4 per request |
| `--reference-images` | - | URL or local file path; max 10 (local files auto base64 encoded) |
| `--watermark` | false | Add watermark |
| `--download` | false | Auto download to ~/Downloads |
| `--output-dir` | ~/Downloads | Custom download directory |
| `--max-wait` | 300s | Max wait time (suggest 180 for sync mode) |
| `--json` | false | Structured output for script integration |

---

## Interaction Guide Flow

**When user request is vague** (no aspect ratio or specific description), guide per steps below. If user provided enough info, execute command directly and skip steps.

**Default aspect ratio is 16:9. If user did not specify, ask for confirmation before generating.**

### Step 1: Aspect Ratio (ask when not specified)

```
Question: "What aspect ratio do you need?"
header: "Aspect Ratio"
options:
- "16:9 - landscape (wallpaper/cover) (recommended)"
- "9:16 - portrait (mobile/Stories)"
- "1:1 - square (social/avatar)"
- "Other ratio"
multiSelect: false
```

If "Other": 3:4 (portrait) | 4:3 (landscape) | 2:3 (portrait photo) | 3:2 (landscape photo) | 21:9 (ultrawide)

### Step 2: Image Description

Ask for user description. Prompt structure: `subject + scene + style + details`

Good examples:

- `"An orange cat by the window, sunlight streaming in, watercolor style, cozy mood"`
- `"Future city, cyberpunk style, neon lights, night scene, high detail"`

### Step 3: Generation Mode

```
Question: "Do you need reference images?"
header: "Generation Mode"
options:
- "No - text-to-image only"
- "1 reference - image-to-image (style transfer)"
- "Multiple references - multi-image fusion (max 10)"
multiSelect: false
```

If reference images needed, collect publicly accessible image URLs.

### Step 4: Execute and Display

Follow "Execution Flow (Three-Phase Dual-Path)": send message → Phase 1 submit → Phase 2 register Cron → Phase 3 sync wait.

Forward exec stdout to user as-is when result arrives.

> If user wants to save locally, add `--download` and re-run, or tell user to click the full link to save.

---

## Limitations

- Max 10 reference images per request
- Text rendering may not be perfect (prefer overlaying text separately)
- Highly specific brand logos may not be reproduced accurately

---

## Prompt Tips

- **Be specific** - "A red apple on a wooden table" vs "an apple"
- **Include style** - "in the style of pixel art" or "photorealistic"
- **Mention purpose** - "for a children's book" affects the output style
- **Describe composition** - "centered", "rule of thirds", "close-up"
- **Specify colors** - Explicit color palettes yield better results
- **Reference prompts** - Use "same style as reference", "keep the visual aesthetic", "match the color palette"
- **Avoid** - Don't ask for complex text in images (use overlays instead)
