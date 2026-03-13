# Storyclaw Skills

[English](./README.md) | 简体中文

基于 [Giggle.pro](https://giggle.pro/) 的 AI 生成技能库，涵盖图像、视频、音乐、语音、剧本等。

## 使用 `npx skills add` 安装

```bash
# 从 GitHub 仓库列出所有技能
npx skills add storyclaw-official/storyclaw-skills --list --full-depth

# 从 GitHub 仓库安装指定技能
npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-image -y

# 从 GitHub 仓库安装全部
npx skills add storyclaw-official/storyclaw-skills

# 本地开发（在本仓库目录执行）
npx skills add . --list --full-depth
```

## 特色

- 🎨 **多模态 AI**：图像、视频、音乐、语音、剧本生成一站搞定。
- 🎬 **视频创作**：文生视频、图生视频、短片、短剧、MV 全流程支持。
- 📝 **故事与剧本**：姜文式叙事风格，分场大纲与对白剧本生成。
- 🔐 **本地优先**：技能在本地运行，API Key 存储在 `~/.openclaw/.env`。

## 可用技能

| 名称 | 说明 | 文档 | 安装命令 |
|------|------|------|----------|
| giggle-generation-image | 文生图与图生图。支持 Seedream、Midjourney、Nano Banana。可自定义画幅比例与分辨率。 | [SKILL.md](./skills/giggle-generation-image/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-image -y` |
| giggle-generation-video | 文生视频与图生视频（首帧/尾帧）。支持 Grok、Sora2、Veo、Kling 等。可自定义模型、时长、画幅比例。 | [SKILL.md](./skills/giggle-generation-video/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-video -y` |
| giggle-generation-drama | 根据故事生成短片、短剧或解说视频。支持剧集、解说、短片三种模式。 | [SKILL.md](./skills/giggle-generation-drama/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-drama -y` |
| giggle-generation-aimv | AI 音乐视频（MV）。根据文字描述或自定义歌词生成音乐，再结合参考图生成歌词视频。 | [SKILL.md](./skills/giggle-generation-aimv/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-aimv -y` |
| giggle-generation-music | 根据文字描述、自定义歌词或纯乐器创建 AI 音乐。支持简化、自定义、纯音乐三种模式。 | [SKILL.md](./skills/giggle-generation-music/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-music -y` |
| giggle-generation-speech | 通过 Giggle.pro 文转音，将文本合成为 AI 语音。支持多种音色、情绪与语速。 | [SKILL.md](./skills/giggle-generation-speech/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-speech -y` |
| giggle-generation-scripts | 姜文式中文剧本生成：故事梗概、人物小传、分场大纲、含对白与场面调度的分场剧本。 | [SKILL.md](./skills/giggle-generation-scripts/SKILL.md) | `npx skills add storyclaw-official/storyclaw-skills --full-depth --skill giggle-generation-scripts -y` |

## 快速验证

例如，查看可用 TTS 音色（需配置 `GIGGLE_API_KEY`）：

```bash
cd skills/giggle-generation-speech
python3 scripts/text_to_audio_api.py --list-voices
```

## Giggle API Key（必填）

前往 [Giggle.pro](https://giggle.pro/) 获取 API Key，并按以下方式配置：

```bash
# 方式一：~/.openclaw/.env（推荐）
echo "GIGGLE_API_KEY=your_api_key" >> ~/.openclaw/.env

# 方式二：系统环境变量
export GIGGLE_API_KEY=your_api_key
```

所有技能均使用该 Key 进行认证。加载优先级：1) `~/.openclaw/.env` 2) 系统环境变量。
