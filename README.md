# Storyclaw Skills

English | [简体中文](./README.zh-CN.md)

Central repository for AI generation skills powered by [Giggle.pro](https://giggle.pro/), including image, video, music, speech, scripts, and more.

## Install with `npx skills add`

```bash
# List skills from GitHub repository
npx skills add storyclaw-official/storyclaw-skills --list --full-depth

# Install a specific skill from GitHub repository
npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-image -y

# Install from GitHub repository
npx skills add storyclaw-official/storyclaw-skills

# Local development (run in this repo directory)
npx skills add . --list --full-depth
```

## Highlights

- 🎨 **Multi-modal AI**: Image, video, music, speech, and script generation in one place.
- 🎬 **Video production**: Text-to-video, image-to-video, short films, drama, and MV workflows.
- 📝 **Story & script**: Jiang Wen–style screenplay generation with scene outlines and dialogue.
- 🔐 **Local-first**: Skills run on your machine; API key stored in `~/.openclaw/.env`.

## Available skills

| Name | Description | Documentation | Run command |
|------|-------------|---------------|-------------|
| giggle-generation-image | Text-to-image and image-to-image. Supports Seedream, Midjourney, Nano Banana. Customize aspect ratio and resolution. | [SKILL.md](./skills/giggle-generation-image/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-image -y` |
| giggle-generation-video | Text-to-video and image-to-video (start/end frame). Supports Grok, Sora2, Veo, Kling, etc. Customize model, duration, aspect ratio. | [SKILL.md](./skills/giggle-generation-video/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-video -y` |
| giggle-generation-drama | Generate short films, drama, or narration videos from story. Supports episode, narration, and short-film modes. | [SKILL.md](./skills/giggle-generation-drama/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-drama -y` |
| giggle-generation-aimv | AI music videos (MV). Generate music from text prompts or custom lyrics, then create lyric videos with reference images. | [SKILL.md](./skills/giggle-generation-aimv/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-aimv -y` |
| giggle-generation-music | Create AI music from text description, custom lyrics, or instrumental. Supports simplified, custom, and instrumental modes. | [SKILL.md](./skills/giggle-generation-music/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-music -y` |
| giggle-generation-speech | Text-to-speech via Giggle.pro. Multiple voices, emotions, and speaking rates. | [SKILL.md](./skills/giggle-generation-speech/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-speech -y` |
| giggle-generation-scripts | Jiang Wen–style Chinese screenplay generation: synopsis, character bios, scene outlines, scene scripts with dialogue and staging. | [SKILL.md](./skills/giggle-generation-scripts/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-scripts -y` |

## Quick verify

For example, list available TTS voices (requires `GIGGLE_API_KEY`):

```bash
cd skills/giggle-generation-speech
python3 scripts/text_to_audio_api.py --list-voices
```

## Giggle API Key (required)

Get your API key from [Giggle.pro](https://giggle.pro/) and configure:

```bash
# Option 1: ~/.openclaw/.env (recommended)
echo "GIGGLE_API_KEY=your_api_key" >> ~/.openclaw/.env

# Option 2: System environment variable
export GIGGLE_API_KEY=your_api_key
```

All skills use this key for authentication. Load priority: 1) `~/.openclaw/.env` 2) system environment.
