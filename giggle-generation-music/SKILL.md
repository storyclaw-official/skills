---
name: giggle-music
description: Generate AI music via giggle.pro. Use when user needs to create, generate or compose music. Supports generating from text description, composing songs with lyrics, instrumental/background music, custom style and vocal gender. Trigger keywords: generate music, compose song, write song, AI compose, music creation.
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🎶","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/requirements.txt"]},"version":"3.0.0","author":"姜式伙伴"}
---

# Giggle Music

Generate AI music via giggle.pro platform. Supports simplified mode and custom mode.

## Environment Setup

Configure `GIGGLE_API_KEY` in project root `.env` file. See [SETUP.md](SETUP.md).

---

## Interactive Guide

### Mode Selection (priority high to low)

| User input | Mode | Notes |
|------------|------|-------|
| User provided full **lyrics text** | Custom mode (B) | Must be lyrics, not description |
| User requests instrumental/background music | Instrumental mode (C) | No vocals |
| All other cases (description, style, vocals, etc.) | **Simplified mode (A)** | Use user description as prompt verbatim, AI composes |

> **Key rule**: If user did not provide lyrics, always use **simplified mode A**. Use user description verbatim as `--prompt`; **do not supplement or rewrite**. E.g. user says "female vocal, 1 min, ancient style love", use `--prompt "female vocal, 1 min, ancient style love"` directly.

### Guide When Info Is Insufficient

Only when user input is very vague (e.g. just "generate music" with no description), ask:

```
Question: "What type of music would you like to generate?"
Options: AI composes (describe style) / Use my lyrics / Instrumental
```

---

## Execution Flow (Phase 1 Submit + Phase 2 Cron)

Music generation typically takes 1-3 minutes. Uses "quick submit + Cron poll" two-phase architecture.

> **Important**: **Never** pass `GIGGLE_API_KEY` in exec's `env` parameter. API key is configured via system environment; scripts auto-read it. Execute the commands below directly.

---

### Phase 1: Submit Task (exec completes in < 10 sec)

**First send message to user**: "Music generation in progress, usually 1-3 minutes, results will be sent automatically."

#### A: Simplified Mode
```bash
python3 scripts/giggle_music_api.py --prompt "user description" --no-wait
```

#### B: Custom Mode
```bash
python3 scripts/giggle_music_api.py --custom \
  --prompt "lyrics content" \
  --style "pop, ballad" \
  --title "Song Title" \
  --vocal-gender female \
  --no-wait
```

#### C: Instrumental
```bash
python3 scripts/giggle_music_api.py --prompt "user description" --instrumental --no-wait
```

Response example:
```json
{"status": "started", "task_id": "xxx", "log_file": "/path/to/log"}
```

**Immediately store task_id in memory** (`addMemory`):
```
giggle-music task_id: xxx (submitted: YYYY-MM-DD HH:mm)
```

---

### Phase 2: Register Cron (2 min interval, wakeMode: "now")

Use `cron` tool to register poll task. **Must follow parameter format strictly; do not modify field names or add extra fields**:

```json
{
  "action": "add",
  "job": {
    "name": "giggle-music-<first 8 chars of task_id>",
    "schedule": {
      "kind": "every",
      "everyMs": 120000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "Music task poll: Execute exec python3 scripts/giggle_music_api.py --query --task-id <full task_id>, process stdout per Cron logic. If stdout is non-JSON plain text, send to user and remove Cron. If stdout is JSON, do not send message, keep waiting. If stdout is empty, remove Cron immediately."
    },
    "sessionTarget": "main"
  }
}
```

Run on each Cron trigger:
```bash
python3 scripts/giggle_music_api.py --query --task-id <task_id>
```

**Cron trigger handling** (judge by exec stdout; all paths exit 0):

| stdout pattern | Action |
|----------------|--------|
| Non-empty plain text (not starting with `{`) | **Forward stdout to user as-is** (do not add prefix or modify), **remove Cron** |
| Empty stdout | Already pushed, **remove Cron immediately, no message** |
| JSON (starts with `{`, has `"status"` field) | No message, do not remove Cron, wait for next poll |

---

## Recovery After Gateway Restart

When user asks about previous music progress:

1. **task_id in memory** → Run `--query --task-id xxx` directly, **never re-submit**
2. **No task_id in memory** → Inform user, ask if they want to regenerate

---

## Parameter Quick Reference

| Parameter | Description |
|-----------|-------------|
| `--prompt` | Music description or lyrics (required for simplified mode) |
| `--custom` | Enable custom mode |
| `--style` | Music style (required for custom mode) |
| `--title` | Song title (required for custom mode) |
| `--instrumental` | Generate instrumental |
| `--vocal-gender` | Vocal gender: male / female (custom mode only) |
| `--query` | Query task status (Cron poll and manual check) |
| `--task-id` | Task ID (used with --query) |
