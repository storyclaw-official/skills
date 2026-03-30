---
name: x2c-socialposter
description: "Social media publishing and engagement management via X2C Open API. Use when the user needs to publish posts to social media, check linked accounts, manage comments, or upload media. Use cases: (1) Publish text/media posts to TikTok, Instagram, Facebook, YouTube, LinkedIn, Twitter, etc. (2) Schedule posts for future publishing. (3) Manage comments and replies on posts. (4) Upload media files and get CDN links. (5) View post history and linked account status. Triggers: post to social media, publish post, social media, schedule post, social publish, upload media, social accounts, comment on post."
version: "0.0.1"
license: MIT
author: storyclaw-official
homepage: https://github.com/storyclaw-official/skills
repository: https://github.com/storyclaw-official/skills
requires:
  bins: [python3]
  env: [X2C_API_KEY]
  pip: [requests]
metadata:
  {
    "openclaw": {
      "emoji": "📱",
      "requires": {
        "bins": ["python3"],
        "env": ["X2C_API_KEY"],
        "pip": ["requests"]
      },
      "primaryEnv": "X2C_API_KEY",
      "installSpec": {
        "bins": ["python3"],
        "env": ["X2C_API_KEY"],
        "pip": ["requests"]
      }
    }
  }
---

[简体中文](./SKILL.zh-CN.md) | English

# X2C Social Poster

**Source**: [storyclaw-official/skills](https://github.com/storyclaw-official/skills) · Dashboard: [x2creel.ai](https://www.x2creel.ai/)

Publish posts, manage comments, and upload media to social platforms via X2C Open API. Supports 13+ platforms including TikTok, Instagram, YouTube, Facebook, LinkedIn, Twitter, and more.

---

## Installation Requirements

| Requirement | Value |
|-------------|-------|
| **Binary** | `python3` |
| **Environment** | `X2C_API_KEY` (required; obtain from [X2C Dashboard](https://www.x2creel.ai/)) |
| **Pip** | `requests` |

Set `X2C_API_KEY` before use. The script will prompt if not configured.

---

## First-Time Setup Guide

**When the user invokes this skill for the first time, follow these onboarding steps IN ORDER:**

### Step 0: Check API Key

Run the following to check if `X2C_API_KEY` is already set:

```bash
python3 scripts/x2c_social.py --action check-key
```

- If the key is set → proceed to Step 1.
- If the key is NOT set → guide the user through setup:

```
🔑 X2C API Key is not configured yet. Let's set it up:

1. Go to https://www.x2creel.ai/social-accounts
2. Create your X2C account (if you don't have one)
3. Link your social media accounts (TikTok, Instagram, etc.)
4. Go to Dashboard → Developer API Key
5. Copy your X2C Open API Key
6. Paste your API key here in the chat

Once you provide the key, I'll save it for you.
```

After the user provides the key, save it to the environment and confirm with a `social/status` check.

### Step 1: Verify Linked Accounts

Once the API key is configured, always check linked accounts first:

```bash
python3 scripts/x2c_social.py --action status
```

Display the linked platforms to the user. If no accounts are linked, guide them:

```
⚠️ No social accounts linked yet.

Please visit https://www.x2creel.ai/social-accounts to link your social media accounts, then come back and try again.
```

---

## Supported Platforms

| Platform | Key | Notes |
|----------|-----|-------|
| TikTok | `tiktok` | Video required |
| Instagram | `instagram` | Image/video supported |
| Facebook | `facebook` | Text, image, video |
| YouTube | `youtube` | Video required |
| LinkedIn | `linkedin` | Text, image, video |
| Twitter / X | `twitter` | Text, image, video |
| Threads | `threads` | Text, image |
| Pinterest | `pinterest` | Image required |
| Reddit | `reddit` | Text, image, video |
| Bluesky | `bluesky` | Text, image |
| Telegram | `telegram` | Text, image, video |
| Snapchat | `snapchat` | Image/video |
| Google My Business | `gmb` | Text, image |

---

## Commands

### 1. Check Linked Accounts

```bash
python3 scripts/x2c_social.py --action status
```

### 2. Publish Post

```bash
# Text-only post
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "Check out our latest update! 🚀"

# Post with remote media URL
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "Watch this! 🎬" \
  --media-urls "https://example.com/video.mp4"

# Post with local file (auto-uploads to S3, then publishes — one step!)
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "Watch this! 🎬" \
  --media-files "/path/to/video.mp4"

# Mix local files and remote URLs
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "Dual media post! 🎬" \
  --media-files "/path/to/local.mp4" \
  --media-urls "https://example.com/remote.jpg"

# Scheduled post with local file
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "Coming soon! ⏰" \
  --media-files "/path/to/video.mp4" \
  --schedule "2026-04-01T12:00:00Z"

# Post with link shortening
python3 scripts/x2c_social.py --action publish \
  --platforms twitter linkedin \
  --post "Read our blog: https://example.com/very-long-url" \
  --shorten-links
```

> **One-step publish**: When using `--media-files` with local file paths, the script automatically uploads each file to S3 first, then uses the returned CDN URLs to publish. You can also pass local paths directly to `--media-urls` — they are auto-detected and uploaded. No need to run upload separately.

### 3. Get Post History

```bash
# All platforms
python3 scripts/x2c_social.py --action posts

# Filter by platform
python3 scripts/x2c_social.py --action posts --platform tiktok
```

### 4. Delete Post

```bash
# Delete from specific platforms
python3 scripts/x2c_social.py --action delete-post --post-id post_abc123

# Bulk delete from all platforms
python3 scripts/x2c_social.py --action delete-post --post-id post_abc123 --bulk
```

### 5. Post Comment

```bash
python3 scripts/x2c_social.py --action comment \
  --post-id post_abc123 \
  --platforms tiktok \
  --comment "Great content! 🔥"
```

### 6. Get Comments

```bash
python3 scripts/x2c_social.py --action comments \
  --post-id post_abc123 \
  --platform tiktok
```

### 7. Reply to Comment

```bash
python3 scripts/x2c_social.py --action reply \
  --comment-id comment_xyz \
  --platforms tiktok \
  --comment "Thanks for watching!"
```

### 8. Delete Comment

```bash
python3 scripts/x2c_social.py --action delete-comment \
  --comment-id comment_xyz
```

### 9. Upload Media

```bash
python3 scripts/x2c_social.py --action upload \
  --file /path/to/video.mp4 \
  --folder my-videos
```

Returns a permanent CDN URL that can be used in `--media-urls` for publishing.

---

## Execution Flow: One-Step Publish with Local Media

When publishing with local files, the script handles everything automatically:

```
User runs publish with --media-files /path/to/video.mp4
  ↓
Script detects local file path (not http/https)
  ↓
Auto-uploads file to S3 via media/upload
  ↓
Receives CDN URL (https://v.arkfs.co/...)
  ↓
Injects CDN URL into media_urls
  ↓
Calls social/publish with the CDN URL
  ↓
Returns publish result to user
```

**Example — single command, full flow:**

```bash
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "Check this out! 🎬" \
  --media-files /path/to/video.mp4
```

The script will output upload progress, then the final publish result:

```json
{"status": "uploading", "file": "video.mp4", "message": "Uploading video.mp4 to S3..."}
{"status": "uploaded", "file": "video.mp4", "url": "https://v.arkfs.co/.../video.mp4"}
{
  "success": true,
  "data": {
    "id": "post_abc123",
    "postIds": [
      {"platform": "tiktok", "id": "7123456789", "status": "success"},
      {"platform": "instagram", "id": "17898765432", "status": "success"}
    ]
  }
}
```

### Standalone Upload (optional)

You can still upload files independently to get a CDN URL for later use:

```bash
python3 scripts/x2c_social.py --action upload --file /path/to/video.mp4 --folder my-videos
```

---

## Parameter Reference

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--action` | ✅ | Action to perform (see Commands) |
| `--post` | for publish | Post text content |
| `--platforms` | for publish | Space-separated target platforms |
| `--platform` | for filtering | Single platform filter |
| `--media-urls` | ❌ | Remote URLs or local paths (local files auto-uploaded) |
| `--media-files` | ❌ | Local file paths to auto-upload and attach |
| `--schedule` | ❌ | ISO 8601 date for scheduled posting |
| `--shorten-links` | ❌ | Shorten URLs in post text |
| `--post-id` | for post ops | Ayrshare post ID |
| `--comment-id` | for comment ops | Comment ID |
| `--comment` | for comment/reply | Comment or reply text |
| `--bulk` | ❌ | Delete from all platforms |
| `--file` | for upload | Local file path to upload |
| `--folder` | ❌ | Upload subfolder (default: `uploads`) |

---

## Interaction Guide

**When the user request is vague, guide per the steps below. If the user has provided enough info, run the command directly.**

### Step 1: Onboarding Check

Always run the First-Time Setup Guide first. Verify API key and linked accounts before any operation.

### Step 2: Determine Intent

```
What would you like to do?
Options:
  📝 Publish a post
  📊 View post history
  💬 Manage comments
  📤 Upload media
  🔗 Check linked accounts
```

### Step 3: For Publishing — Collect Info

```
Question: "Which platforms do you want to post to?"
→ Show only the user's linked platforms from status check.

Question: "What's your post content?"
→ Accept text input.

Question: "Do you want to attach any media (images/videos)?"
→ If yes, accept local file paths OR remote URLs. Local files are auto-uploaded — no extra step needed.

Question: "Schedule for later or publish now?"
→ If schedule, collect ISO 8601 datetime.
```

### Step 4: Execute and Display

Run the appropriate command and forward the result to the user. For publish actions, display the per-platform status (success/failure) clearly.

---

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Missing/invalid parameters | Check and fix parameters |
| 401 | Invalid API key | Guide user to verify/reset API key |
| 500 | Server error | Retry or inform user |

When an error occurs, display a clear message and suggest corrective action.
