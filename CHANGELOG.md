# CHANGELOG

## [Unreleased]

### 变更
- 统一环境变量管理：移除各技能目录的隐藏 `.env.example`，改为根目录统一 `env.example`
- 新增各技能目录可见的 `env.example`（非隐藏），供独立使用时参考
- 为 6 个缺失 metadata 的技能补充 `SKILL.md` frontmatter（`requires.env`、`user-invocable`、`emoji` 等字段）：giggle-aimv、giggle-image、giggle-music、giggle-screenplay、kie-nano-banana、kie-grok-imagine

---

## [1.0.0] - 2026-02-22

### 新增
- 新增根目录 `README.md`：技能列表、使用示例、目录结构、API 平台说明
- 新增根目录 `CLAUDE.md`：架构说明、命名规范、测试命令，供 Claude Code / AI Agent 使用
- 新增根目录 `env.example`：统一的环境变量模板

### 变更
- 统一技能目录命名前缀（按 API 平台区分）：
  - `ad-drama` → `giggle-drama`
  - `generate-mv` → `giggle-aimv`
  - `ad-generating-ai-music` → `giggle-music`
  - `generating-images-with-seedream` → `giggle-image`
  - `generating-scripts` → `giggle-screenplay`
  - `ad-nano-banana` → `kie-nano-banana`
  - `generating-videos-with-grok-imagine` → `kie-grok-imagine`
- 同步更新所有 `SKILL.md` 的 `name:` 字段与目录名一致
- 更新 `generating-videos/SKILL.md` 模型注册表
- 更新 `giggle-screenplay/agents/openai.yaml` skill 引用名

### 命名规范确立
- `giggle-*` — Giggle.pro 平台技能
- `kie-*` — kie.ai 平台技能
- `generating-*` — 路由入口（不直接调用 API）

---

## [0.x] - 历史版本

- giggle-drama（原 ad-drama）：Giggle.pro Trustee Mode V2 视频生成
- giggle-aimv（原 generate-mv）：MV 托管模式视频生成
- giggle-music（原 ad-generating-ai-music）：giggle.pro AI 音乐生成
- giggle-image（原 generating-images-with-seedream）：Seedream 模型图像生成
- giggle-screenplay（原 generating-scripts）：姜文风格中文剧本生成
- kie-nano-banana（原 ad-nano-banana）：Nano Banana Pro 图像生成
- kie-grok-imagine（原 generating-videos-with-grok-imagine）：grok-imagine 视频生成
- generating-videos：视频生成路由入口
