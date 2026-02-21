# storyclaw-skills

Claude Code / OpenClaw Agent 技能集合，提供 AI 创意内容生成能力，包括视频、图像、音乐和剧本生成。

## 技能列表

| 技能 | 功能 | 平台 | API 密钥 |
|------|------|------|---------|
| [giggle-drama](#giggle-drama) | AI 短视频生成（7 种风格） | Giggle.pro | GIGGLE_API_KEY |
| [giggle-aimv](#giggle-aimv) | AI 音乐视频（MV）生成 | Giggle.pro | GIGGLE_API_KEY |
| [giggle-music](#giggle-music) | AI 音乐生成 | Giggle.pro | GIGGLE_API_KEY |
| [giggle-image](#giggle-image) | AI 图像生成（Seedream 模型） | Giggle.pro | GIGGLE_API_KEY |
| [kie-nano-banana](#kie-nano-banana) | AI 图像生成（Nano Banana Pro） | kie.ai | KIE_API_KEY |
| [generating-videos](#generating-videos) | 视频生成路由入口 | — | — |
| [kie-grok-imagine](#kie-grok-imagine) | AI 视频生成（grok-imagine） | kie.ai | KIE_API_KEY |
| [giggle-screenplay](#giggle-screenplay) | 姜文风格中文剧本生成 | — | 无 |

## 快速开始

### 环境配置

所有技能共用根目录一个 `.env`，无需为每个技能单独配置：

```bash
# 复制根目录模板
cp env.example .env

# 编辑 .env 填入 API 密钥
GIGGLE_API_KEY=your_giggle_api_key   # giggle-* 技能
KIE_API_KEY=your_kie_api_key         # kie-* 技能
```

> **独立使用单个技能**：参考该技能目录下的 `env.example`（各平台的独立参考模板）。
>
> **OpenClaw 部署**：在 `~/.openclaw/openclaw.json` 配置一次，运行时自动注入，无需 `.env` 文件。

### 安装依赖

各技能使用独立的 `requirements.txt`，按需安装：

```bash
pip install requests python-dotenv
```

---

## 技能详情

### giggle-drama

使用 Giggle.pro 托管模式 V2 API 生成 AI 短视频。

**支持风格**: 3D古风、2D漫剧、吉卜力、皮克斯、写实、二次元、国风水墨

**支持比例**: 16:9（横屏）、9:16（竖屏）

**时长选项**: auto / 30 / 60 / 120 / 180 / 240 / 300 秒

```bash
python3 giggle-drama/scripts/trustee_api.py --prompt "描述" --style "写实" --aspect "16:9"
```

生成视频自动下载至 `~/Downloads/giggle-videos/`。

---

### giggle-aimv

根据音乐和参考图生成 MV（音乐视频）。

**三种音乐模式**:

- **prompt 模式** — 文字描述生成音乐
- **custom 模式** — 提供歌词、风格、歌名
- **upload 模式** — 使用已上传的音乐资产

```bash
# prompt 模式
python3 giggle-aimv/scripts/trustee_api.py \
  --mode prompt \
  --prompt "轻快的流行音乐" \
  --reference-image ./cover.jpg

# custom 模式
python3 giggle-aimv/scripts/trustee_api.py \
  --mode custom \
  --lyrics "歌词内容" \
  --style "流行" \
  --title "歌曲名称" \
  --reference-image ./cover.jpg
```

---

### giggle-music

通过 Giggle.pro 平台生成 AI 音乐，支持三种模式。

```bash
# 简化模式（AI 自动创作）
python3 giggle-music/scripts/giggle_music_api.py --prompt "轻松的爵士乐"

# 自定义模式（提供歌词）
python3 giggle-music/scripts/giggle_music_api.py \
  --custom \
  --prompt "歌词内容" \
  --style "流行" \
  --title "歌曲名" \
  --vocal-gender female

# 纯音乐模式
python3 giggle-music/scripts/giggle_music_api.py \
  --prompt "背景音乐描述" \
  --instrumental
```

输出格式：JSON 数组，包含 `title` 和 `audioUrl`。

---

### giggle-image

使用 Seedream 模型（Giggle.pro 平台）生成图像，支持文生图、图生图和多图融合。

```bash
# 文生图
python3 giggle-image/scripts/seedream_api.py \
  --prompt "赛博朋克城市夜景" \
  --aspect-ratio 16:9

# 图生图（参考图 URL）
python3 giggle-image/scripts/seedream_api.py \
  --prompt "同风格的场景" \
  --reference-images https://example.com/image.jpg \
  --aspect-ratio 1:1

# 下载到本地
python3 giggle-image/scripts/seedream_api.py \
  --prompt "描述" \
  --download
```

**支持比例**: 16:9 / 9:16 / 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 21:9

**参考图**: 最多 10 张，支持 URL 或本地文件路径

---

### kie-nano-banana

使用 Nano Banana Pro 模型（kie.ai 平台）生成图像。

```bash
# 文生图
python3 kie-nano-banana/scripts/kie_nano_banana_api.py \
  --prompt "描述内容" \
  --aspect-ratio 16:9 \
  --resolution 2K

# 图生图
python3 kie-nano-banana/scripts/kie_nano_banana_api.py \
  --prompt "风格转换" \
  --image-input https://example.com/ref.jpg \
  --resolution 2K

# 多图融合（最多 8 张）
python3 kie-nano-banana/scripts/kie_nano_banana_api.py \
  --prompt "融合描述" \
  --image-input url1 url2 url3
```

**支持比例**: 1:1 / 16:9 / 9:16 / 2:3 / 3:2 / 4:3 / 21:9 / auto

**分辨率**: 1K / 2K / 4K

---

### generating-videos

视频生成的统一路由入口，根据用户需求自动选择合适的模型。

当前注册模型：

| 模型 | 技能目录 | 支持模式 |
|------|---------|--------|
| grok-imagine | kie-grok-imagine | 文生视频、图生视频 |

直接触发对话由 Agent 引导选择模式和模型。

---

### kie-grok-imagine

使用 grok-imagine 模型（kie.ai 平台）生成视频。

```bash
# 文生视频
python3 kie-grok-imagine/scripts/text_to_video.py \
  --prompt "城市日落延时摄影" \
  --aspect-ratio 16:9 \
  --duration 10 \
  --resolution 720p

# 图生视频
python3 kie-grok-imagine/scripts/image_to_video.py \
  --image ./scene.jpg \
  --prompt "镜头缓慢推进" \
  --duration 6
```

**支持时长**: 6 秒 / 10 秒

**支持分辨率**: 480p / 720p

**支持比例**: 2:3 / 3:2 / 1:1 / 9:16 / 16:9

---

### giggle-screenplay

基于姜文电影风格生成中文剧本，纯 LLM 技能，无需外部 API。

**核心风格**: 高密度冲突 + 黑色幽默 + 话里有话的对白 + 叙事反转

**输出模式**:
- **快速版** — 故事梗概 + 人物小传
- **标准版** — 梗概 + 人物小传 + 分场大纲 + 3+ 场完整剧本
- **长篇版** — 梗概 + 人物小传 + 分场大纲 + 6-10 场剧本

直接对话描述题材、核心矛盾、人物关系即可生成。

---

## 命名规范

- `giggle-*` — Giggle.pro 工作流技能（AI 导演）
- `kie-*` — kie.ai 平台技能
- `generating-*` — 路由入口

---

## 目录结构

```
storyclaw-skills/
├── .env                          # API 密钥配置（不提交 git）
├── env.example                   # 环境变量模板
├── giggle-drama/                 # AI 视频生成
├── giggle-aimv/                  # AI MV 生成
├── giggle-music/                 # AI 音乐生成
├── giggle-image/                 # AI 图像生成（Seedream）
├── kie-nano-banana/              # AI 图像生成（Nano Banana）
├── generating-videos/            # 视频生成路由
├── kie-grok-imagine/             # AI 视频生成（grok-imagine）
└── giggle-screenplay/            # AI 剧本生成
```

每个技能目录包含：
- `SKILL.md` — Skill 定义和使用指南（含 `requires.env` 声明）
- `env.example` — 独立部署时的环境变量参考（有 API Key 要求的技能）
- `scripts/` — Python API 客户端脚本
- `references/` — 提示词指南、示例、故障排除（部分技能）

---

## API 平台

| 平台 | 网址 | 使用技能 |
|------|------|---------|
| Giggle.pro | giggle.pro | giggle-drama、giggle-aimv、giggle-music、giggle-image |
| kie.ai | kie.ai | kie-nano-banana、kie-grok-imagine |
