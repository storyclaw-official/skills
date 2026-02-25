# CHANGELOG

## [Unreleased]

---

## [3.2.0] - 2026-02-25

### 新增
- `giggle-image`：`seedream_api.py` 新增 `--poll` 参数，`--query --poll` 模式支持同步轮询等待任务完成（每 5 秒查询，默认最多 180 秒）
- `giggle-image` SKILL.md：新增 Phase 3 同步兜底路径（`--query --task-id <id> --poll`），与 Cron 双路径确保结果送达，架构升级为三阶段双路径（对齐 giggle-drama）
- `giggle-image`：新建 `scripts/requirements.txt`（`requests>=2.31.0`），统一依赖声明

### 修复
- `giggle-drama` SKILL.md：重试场景提醒改为引导用户去网页端专业模式继续制作，明确告知重试将创建新任务、之前费用不退，使用敬语"您"
- 修复 OpenClaw Cron `armTimer skipped` bug 导致 `giggle-image` 结果不推送的问题（平台 Cron 注册成功但 `nextRunAtMs` 为 null，定时器未触发）

---

## [3.1.0] - 2026-02-25

### 修复
- `giggle-drama` SKILL.md：子步骤失败处理中明确给出 `start` 命令示例，并注明"唯一重试方式，API 不支持断点续传"，防止 Agent 调用不存在的 `retry` 等子命令
- `giggle-drama` SKILL.md：重试场景（用户说"重试"或子步骤失败后确认重新生成）新增跳过确认流程的明确指令，防止 Agent 重复向用户确认费用/参数

---

## [3.0.0] - 2026-02-25

### 新增
- **全部 4 个生成类 Skill（image/music/aimv/drama）**：新增 Cron 超时兜底计数器（`.count` 文件），防止任务永不返回时 Cron 无限运行
  - `giggle-music`：超过 5 次轮询（约 10 分钟）输出超时纯文本 + exit(0)
  - `giggle-image`：超过 10 次轮询（约 5 分钟）输出超时纯文本 + exit(0)
  - `giggle-aimv`：超过 15 次轮询（约 45 分钟）输出超时纯文本 + exit(0)
  - `giggle-drama`：超过 20 次轮询（约 60 分钟）输出超时纯文本 + exit(0)
- `giggle-music`：新增 `_save_music_prompt` / `_load_music_prompt`，`--no-wait` 提交时保存 prompt，`--query` 时读取展示给用户

### 变更
- `giggle-music`：`completed` 输出改为纯文本（对齐 giggle-image 风格），格式：`🎶 音乐已就绪！\n关于「{prompt}」...共 N 首 + Markdown 链接`
- `giggle-music`：`failed` 输出改为纯文本 + exit(0)（原为 JSON + exit(1)），避免触发 exec failed
- `giggle-music` SKILL.md v3.0：Cron 处理逻辑改为纯文本判断（对齐 giggle-image），删除"结果消息格式"章节（脚本直接输出，Agent 无需格式化），删除 `--no-wait` 参数说明
- `giggle-image` SKILL.md：删除冗余章节（执行前检查、步骤5反馈迭代、参数约束重复说明）
- `giggle-aimv` SKILL.md：删除 Cron 参数约束重复说明
- `giggle-drama` SKILL.md：删除 Cron 参数约束重复说明

### 修复
- `giggle-aimv` / `giggle-drama`：单次 query 路径中 API 返回 `no task found` 时 `data` 为 `None`，`None.get()` 抛 `AttributeError` → exit(1) → 触发 `⚠️ Exec failed`；改为 `(r.get("data") or {})` 防止崩溃

---

## [2.0.0] - 2026-02-24

### 新增
- `giggle-drama`：新增 `start` 子命令（Phase 1），< 10 秒完成创建项目 + 提交任务，stdout 返回 `{"status": "started", "project_id": "...", "log_file": "..."}`
- `giggle-drama`：新增 `poll_until_complete()` 方法（Phase 3），含完整工作流（支付逻辑、下载、`.sent` 防重复、completed 无资源超时限制）
- `giggle-drama`：新增日志系统，路径 `~/.openclaw/skills/giggle-drama/logs/{project_id}_{yyyyMMdd_HHmmss}.log`
- `giggle-drama`：新增 `.sent` 防重复文件，`query --poll` 与 `query`（单次）均检查，防止 Cron 与同步路径双重推送
- `giggle-music`：新增日志系统，路径 `~/.openclaw/skills/giggle-music/logs/{task_id}_{yyyyMMdd_HHmmss}.log`
- `giggle-music`：新增 `.sent` 防重复文件（同 giggle-drama 机制）

### 变更
- `giggle-drama` SKILL.md v2.0：重写为三阶段双路径架构（Phase 1 start → Phase 2 Cron 兜底 → Phase 3 同步等待），附步骤翻译表、失败处理、Gateway 重启恢复指令
- `giggle-music` SKILL.md v2.0：重写为三阶段双路径架构，`--no-wait` stdout 输出 `{"status": "started", "task_id": "..."}`（原为 stderr）
- `giggle-music`：修复 `--query` exit code：completed → exit(0)；failed → exit(1)；processing/pending → **exit(2)**（原全部 exit(1)）
- `giggle-drama` `query --poll`：升级为调用 `poll_until_complete`，不再仅简单轮询，完整处理支付与下载
- `giggle-drama` `query`（单次）：加入 `.sent` 防重复逻辑，供 Cron 调用时防重复推送

### 修复
- `giggle-drama`：修复 `status=completed` 但 `video_asset` 为空时的无限等待问题（新增 20 轮计数器，约 60 秒后报错退出）
- `giggle-drama`：修复视频下载失败时静默无输出问题，现在返回结果中包含 `"download_failed": true`，并提示用 `signed_url` 备用

### 历史变更
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
