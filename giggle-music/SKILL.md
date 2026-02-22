---
name: giggle-music
description: 使用 giggle.pro 平台生成 AI 音乐。当用户需要创建、生成或创作音乐时使用此技能。支持根据文本描述生成音乐、创作带歌词的歌曲、生成纯音乐/背景音乐、自定义音乐风格和人声性别。触发关键词：生成音乐、创作歌曲、写歌、AI 作曲、音乐创作。
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🎶","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/requirements.txt"]},"version":"2.0.0","author":"姜式伙伴"}
---

# Giggle Music

通过 giggle.pro 平台生成 AI 音乐，支持简化模式和自定义模式。

## 环境配置

在项目根目录 `.env` 文件中配置 `GIGGLE_API_KEY`。详见 [SETUP.md](SETUP.md)。

---

## 交互式引导

### 分析用户输入

| 用户输入 | 动作 |
|---------|------|
| 包含音乐描述（如"生成一首欢快的歌"） | 直接执行简化模式 |
| 包含歌词内容 | 询问风格和标题，使用自定义模式 |
| 信息不足（如"生成音乐"） | 询问音乐类型 |

询问音乐类型（信息不足时）：

```
问题: "您想生成什么类型的音乐？"
选项: AI自动创作 / 使用我的歌词 / 纯音乐
```

---

## 执行流程（三阶段双路径）

音乐生成通常 1-3 分钟。采用「同步等待 + Cron 兜底」双路径。

---

### 第一步：提交任务（exec < 5 秒）

**先发送消息给用户**："音乐生成中，通常 1-3 分钟，稍后自动发送结果。"

#### A：简化模式
```bash
python3 scripts/giggle_music_api.py --prompt "用户描述" --no-wait
```

#### B：自定义模式
```bash
python3 scripts/giggle_music_api.py --custom \
  --prompt "歌词内容" \
  --style "流行, 抒情" \
  --title "歌曲标题" \
  --vocal-gender female \
  --no-wait
```

#### C：纯音乐
```bash
python3 scripts/giggle_music_api.py --prompt "用户描述" --instrumental --no-wait
```

返回示例：
```json
{"status": "started", "task_id": "xxx", "log_file": "/path/logs/xxx.log"}
```

**立即将 task_id 写入记忆**（`addMemory`）：
```
giggle-music task_id: xxx（状态：生成中，提交时间：YYYY-MM-DD HH:mm）
```

如果命令失败：告知错误，询问用户是否重试，**不执行后续步骤**。

---

### 第二步：注册 Cron（立刻注册，在 Phase 3 之前）

注册间隔 **3 分钟** 的 Cron，每次执行：
```bash
python3 scripts/giggle_music_api.py --query --task-id <task_id>
```

**Cron 处理逻辑**（根据 exit code 和输出）：

| exit code | 输出内容 | 处理 |
|-----------|---------|------|
| 0 | `{"status": "already_sent"}` | 跳过，取消 Cron |
| 0 | 音乐链接列表 | 发送结果给用户，取消 Cron |
| 1 | 错误信息 | 发错误消息，取消 Cron |
| 2 | `{"status": "processing/pending"}` | 发"音乐生成中，请稍候"，Cron 继续 |

---

### 第三步：同步等待（乐观路径）

**目的**：音乐任务通常 1-3 分钟，大概率在此步骤直接完成。

```bash
python3 scripts/giggle_music_api.py --query --task-id <task_id>
```

**处理逻辑**：
- exit(0) + `status: "already_sent"` → 跳过，取消 Cron
- exit(0) + 音乐链接 → **立即发送结果给用户**，取消 Cron
- exit(2)（进行中）→ Cron 已在运行，等待即可
- exit(1)（失败）→ 发送错误消息，取消 Cron

如果首次 query 返回 exit(2)，可隔 30 秒再尝试一次（音乐任务较短）。

---

## 结果消息格式

收到完成结果后，发送以下格式的消息：

```
音乐生成完成，共 N 首：

1. 🎵 music_1
   收听：<audioUrl>

2. 🎵 music_2
   收听：<audioUrl>
```

---

## 失败处理

| 场景 | 处理方式 |
|------|---------|
| `--no-wait` 命令失败 | 告知错误，询问用户是否重试 |
| exit(1) 任务失败 | "生成失败，请修改描述后重试" |
| 超时（> 10 分钟）| "生成超时，task_id=xxx，可稍后查询" |
| API 不可用 | 报错 + 保存 task_id |

---

## Gateway 重启后恢复

1. **记忆中有 task_id** → 直接执行 `--query --task-id xxx`，**绝不重新提交**
2. **记忆无，有日志** → `ls ~/.openclaw/skills/giggle-music/logs/` 找最近 task_id，再 query
3. **两者都无** → 告知用户，询问是否重新生成

---

## 参数速查

| 参数 | 说明 |
|------|------|
| `--prompt` | 音乐描述或歌词（简化模式必需） |
| `--custom` | 启用自定义模式 |
| `--style` | 音乐风格（自定义模式必需） |
| `--title` | 音乐标题（自定义模式必需） |
| `--instrumental` | 生成纯音乐 |
| `--vocal-gender` | 人声性别：male / female（仅自定义模式） |
| `--no-wait` | 提交后立即返回 task_id（Phase 1 必用） |
| `--query` | 查询任务状态（Phase 2/3 使用） |
| `--task-id` | 任务 ID（配合 --query） |
| `--json` | JSON 格式输出 |

---

## exit code 说明（--query 模式）

| code | 含义 |
|------|------|
| 0 | 完成（或 already_sent） |
| 1 | 失败 |
| 2 | 进行中（processing / pending） |
