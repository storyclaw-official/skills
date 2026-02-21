# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **ad-drama** project - a video generation tool that interfaces with the Giggle.pro Trustee Mode V2 API. It provides both a Python API client and a Claude Code skill for generating AI videos from story prompts.

## Architecture

### Core Components

- **`scripts/trustee_api.py`**: Main API client with complete workflow automation
  - `TrusteeModeAPI` class: Handles all API interactions (create project, submit task, query progress, payment)
  - `execute_workflow()`: Automated end-to-end workflow that blocks until video generation completes (up to 1 hour)
  - CLI interface with subcommands: `create`, `submit`, `query`, `pay`, `styles`, `workflow`

- **`SKILL.md`**: Claude Code skill definition for video generation
  - Skill name: `generating-videos`
  - Enables natural language video generation requests in Claude Code sessions

### API Workflow

The complete workflow is:
1. Create project → 2. Submit task → 3. Poll progress (every 3 seconds) → 4. Auto-pay when needed → 5. Wait for completion → 6. **Auto-download video** → 7. Return download URL and local path

Key features:
- Automatic retry logic for network errors (5 retries with 5s delay)
- Auto-detection and execution of payment when status is "pending"
- Progress polling with detailed logging to stderr
- **Automatic video download** to `~/Downloads/giggle-videos/` (NEW!)
- Fixed timeout: 1 hour
- Fixed query interval: 3 seconds

## Common Commands

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r scripts/requirements.txt
   ```

2. **Configure API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Giggle.pro API key
   ```

### Using the Python CLI

```bash
# Get available video styles
python scripts/trustee_api.py styles --table

# Run complete workflow (simplest approach - blocks until done)
python scripts/trustee_api.py workflow \
  --story "一个关于冒险的故事..." \
  --aspect 16:9 \
  --project-name "我的视频" \
  --duration auto \
  --style-id 142

# Manual step-by-step (for debugging)
python scripts/trustee_api.py create --name "项目名" --type director --aspect 16:9
python scripts/trustee_api.py submit --project-id <ID> --story "..." --aspect 16:9 --duration auto --language zh
python scripts/trustee_api.py query --project-id <ID> --poll --interval 3
```

### Using the Claude Code Skill

When invoked via `/generating-videos` or similar prompts, the skill will:
1. Ask for story content, aspect ratio, and optional style/duration
2. Call `execute_workflow()` which handles everything automatically
3. Return the video download URL upon completion

## Configuration

### API Authentication

**Environment Variables** (Recommended): The project now uses `.env` file for secure configuration management.

1. **Setup**: Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. **Configure**: Edit `.env` and set your API key:
   ```bash
   GIGGLE_API_KEY=your_api_key_here
   ```

3. **Security**: The `.env` file is already in `.gitignore` and will not be committed to version control.

**File Structure**:
- `.env.example` - Template file (safe to commit)
- `.env` - Your actual configuration (never commit this!)
- `.gitignore` - Ensures `.env` is not tracked by Git

**How it works**: `trustee_api.py` automatically loads the API key from `.env` using `python-dotenv`. If the key is missing, a clear error message will be displayed.

### API Parameters

- **aspect**: `16:9` or `9:16` (required)
- **video_duration**: `auto`, `30`, `60`, `120`, `180`, `240`, `300` (default: `auto`)
- **language**: `zh` or `en` (default: `zh`)
- **project_type**: `mv` or `director` (default: `director`)
- **style_id**: Optional integer (use `styles` command to list available styles)

## Important Implementation Details

### Error Handling Strategy

The workflow uses sophisticated retry logic:
- **Network errors** (Connection, Remote, timeout, aborted): Retry up to 5 times with 5s delay
- **Business errors** (invalid parameters, insufficient balance): Fail immediately
- **Progress polling**: Continues indefinitely (up to 1 hour timeout) even after failed retries

### Response Format Compatibility

API responses may have `code` as either string `"200"` or integer `200`. The code normalizes this:
```python
code = result.get("code")
if isinstance(code, str):
    code = int(code) if code.isdigit() else 0
```

### Payment Logic

Payment is triggered automatically when:
- `pay_status == "pending"`, OR
- `current_step` contains "pay" (case-insensitive)

Payment only executes once per workflow via the `paid` flag.

### Status Checks

The workflow monitors multiple failure indicators:
- Top-level: `status == "failed"` or `err_msg` present
- Sub-steps: Any sub_step with `status == "failed"` or `error` present

## Development Notes

- All progress logs go to **stderr** to keep stdout clean for JSON responses
- The `--pretty` flag formats JSON output with indentation
- The CLI uses `argparse` with subcommands for different operations
- The `execute_workflow()` function is designed to be called from both CLI and as a Python library
