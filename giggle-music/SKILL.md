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

### 模式判断（优先级由高到低）

| 用户输入特征 | 使用模式 | 说明 |
|------------|---------|------|
| 用户提供了完整**歌词文本** | 自定义模式（B） | 必须明确是歌词，不是描述 |
| 用户要求纯音乐/背景音乐 | 纯音乐模式（C） | 无人声 |
| 其他所有情况（含描述、风格、人声等） | **简化模式（A）** | 将用户描述直接作为 prompt，AI 自动创作 |

> **关键原则**：只要用户没有提供歌词，一律使用**简化模式 A**，将用户的描述原文作为 `--prompt`，**不得自行补充或改写描述内容**。例如用户说"女声，1分钟，古风爱情"，直接用 `--prompt "女声，1分钟，古风爱情"` 即可。

### 信息不足时的引导

仅当用户输入极度模糊（如只说"生成音乐"，无任何描述）时询问：

```
问题: "您想生成什么类型的音乐？"
选项: AI自动创作（描述风格） / 使用我的歌词 / 纯音乐
```

---

## 执行流程（三阶段双路径）

音乐生成通常 1-3 分钟。采用「同步等待 + Cron 兜底」双路径。

---

### 第一步：提交任务（exec < 5 秒）

**先发送消息给用户**："音乐生成中，通常 1-3 分钟，稍后自动发送结果。"

> **重要**：执行命令时**不得**在 exec 的 `env` 参数中传递 `GIGGLE_API_KEY`。API 密钥已通过系统环境变量配置，脚本会自动读取，无需显式传递。直接执行以下命令即可。

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

### 第二步：注册 Cron（立刻注册）

注册间隔 **2 分钟** 的 Cron，**必须指定 `wakeMode: "now"`**（默认 `next-heartbeat` 会导致延迟不触发），每次执行：
```bash
python3 scripts/giggle_music_api.py --query --task-id <task_id>
```

**Cron 处理逻辑**（所有正常情况 exit code = 0，读 stdout JSON 的 `status` 字段决定行为）：

| stdout `status` | 处理 |
|----------------|------|
| 空输出（stdout 为空） | 已推送过，**立即取消 Cron，绝对不发任何消息**（空输出代表无操作） |
| 音乐链接列表（非 JSON） | 发送结果给用户，**取消 Cron** |
| `processing` / `pending` | **不发任何消息**，Cron 继续等待 |

exit code = 1（失败）→ 发送错误消息，取消 Cron

> **重要**：进行中时绝不向用户发送任何消息，静默等待即可。

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
| 0 | 正常（已完成、already_sent、或进行中）—— 具体状态看 stdout JSON `status` 字段 |
| 1 | 失败 |
