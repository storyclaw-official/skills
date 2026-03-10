---
name: giggle-generation-music
description: Generate AI music via Generation API. Two modes: (1) Prompt mode - generate from description, (2) Custom mode - generate song from lyrics. Use when user needs to create, generate or compose music. Trigger keywords: generate music, compose song, write song, AI compose, music creation.
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🎶","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/scripts/requirements.txt"]},"version":"1.0.0","author":"Giggle Team"}
---

# Giggle Generation Music

Generate AI music via Generation API on giggle.pro platform. Supports prompt mode and custom mode.

**API Key**: Read from environment variable `GIGGLE_API_KEY` or project root `.env` file.

> **No inline Python**: All commands must be executed via `exec` tool directly.

---

## Two Generation Modes

| Mode | Description | Parameters |
|------|------|------|
| **Prompt mode** | Generate from description | prompt, vocal_gender, instrumental |
| **Custom mode** | Generate from lyrics | lyrics, style, title, vocal_gender, instrumental |

### Mode Selection Rules

| User input | Use mode |
|------------|---------|
| User provided full **lyrics text** | Custom mode |
| User requests instrumental/background music | instrumental=true |
| Other (description, style, etc.) | Prompt mode |

> **Key rule**: If user did not provide lyrics, always use **prompt mode**, use user description verbatim as `--prompt`, do not supplement or rewrite.

---

## Execution Flow (Three-Phase Dual-Path)

Music generation typically takes 1-3 minutes. Uses "quick submit + Cron poll + sync fallback" three-phase architecture.

> **Important**: **Never** pass `GIGGLE_API_KEY` in exec's `env` parameter.

---

### Phase 1: Submit Task (exec completes in < 10 sec)

**First send message to user**: "Music generation in progress, usually 1-3 minutes, results will be sent automatically."

#### Prompt mode (generate from description)
```bash
python3 scripts/generation_music_api.py \
  --prompt "Upbeat pop music, summer beach vibes" \
  --vocal-gender female \
  --no-wait
```

#### Custom mode (generate from lyrics)
```bash
python3 scripts/generation_music_api.py --custom \
  --lyrics "Verse 1:\nSunshine through the window\nA new day begins\n\nChorus:\nLet's sing together\nEmbrace the good times" \
  --style "pop" \
  --title "Good Times" \
  --vocal-gender male \
  --no-wait
```

#### Instrumental
```bash
python3 scripts/generation_music_api.py \
  --prompt "Gentle piano piece, café atmosphere" \
  --instrumental \
  --no-wait
```

Response example:
```json
{"status": "started", "task_id": "xxx"}
```

**Immediately store task_id in memory**:
```
giggle-generation-music task_id: xxx (submitted: YYYY-MM-DD HH:mm)
```

---

### Phase 2: Register Cron (2 min interval)

Use `cron` tool to register poll task:

```json
{
  "action": "add",
  "job": {
    "name": "giggle-generation-music-<first 8 chars of task_id>",
    "schedule": {
      "kind": "every",
      "everyMs": 120000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "Music task poll: Execute exec python3 scripts/generation_music_api.py --query --task-id <full task_id>, process stdout per Cron logic. If stdout is non-JSON plain text, send to user and remove Cron. If stdout is JSON, do not send message, keep waiting. If stdout is empty, remove Cron immediately."
    },
    "sessionTarget": "main"
  }
}
```

**Cron trigger handling**:

| stdout pattern | Action |
|------------|------|
| Non-empty plain text (not starting with `{`) | **Forward stdout to user as-is**, **remove Cron** |
| Empty stdout | Already pushed, **remove Cron immediately, no message** |
| JSON (starts with `{`, has `"status"` field) | No message, do not remove Cron, keep waiting |

---

### Phase 3: Sync Wait (optimistic path, fallback when Cron does not trigger)

**Must execute this step regardless of Cron registration success.**

```bash
python3 scripts/generation_music_api.py --query --task-id <task_id> --poll --max-wait 300
```

---

## New Request vs Query Old Task

**When user starts new music generation request**, **must execute Phase 1 to submit new task**.

**Only when user explicitly asks about previous task progress**, query old task_id from memory.

---

## Parameter Quick Reference

| Parameter | Description |
|------|------|
| `--prompt` | Music description (prompt mode) or lyrics (custom mode) |
| `--custom` | Enable custom mode (requires lyrics + style + title) |
| `--lyrics` | Lyrics content (required for custom mode) |
| `--style` | Music style, e.g. pop, rock (required for custom mode) |
| `--title` | Song title (required for custom mode) |
| `--vocal-gender` | Vocal gender: male / female |
| `--instrumental` | Generate instrumental (no vocals) |

---

## Interaction Guide Flow

**When user input is very vague (e.g. only "generate music")**:

```
Question: "What type of music would you like to generate?"
header: "Generation Mode"
options:
- "From description - I describe style/mood, AI composes"
- "From lyrics - I have lyrics, need AI to compose music"
- "Instrumental - background music/no vocals"
multiSelect: false
```

For lyrics mode, collect: lyrics, style, title, vocal gender.

For description mode, collect: music description, vocal gender (optional).
