---
name: giggle-music
description: 使用 giggle.pro 平台生成 AI 音乐。当用户需要创建、生成或创作音乐时使用此技能。支持根据文本描述生成音乐、创作带歌词的歌曲、生成纯音乐/背景音乐、自定义音乐风格和人声性别。触发关键词：生成音乐、创作歌曲、写歌、AI 作曲、音乐创作。
---

# Giggle Music

通过 giggle.pro 平台生成 AI 音乐，支持简化模式和自定义模式。

## 环境配置

在项目根目录 `.env` 文件中配置 `GIGGLE_API_KEY`。详见 [SETUP.md](SETUP.md)。

## 交互式引导流程

### 步骤 1: 分析用户输入

| 用户输入 | 动作 |
|---------|------|
| 包含音乐描述（如"生成一首欢快的歌"） | 直接执行简化模式 |
| 包含歌词内容 | 询问风格和标题，使用自定义模式 |
| 信息不足（如"生成音乐"） | 进入步骤 2 |

### 步骤 2: 询问音乐类型（仅信息不足时）

使用 `AskUserQuestion`：

```
问题: "您想生成什么类型的音乐？"
header: "音乐类型"
选项:
- label: "AI 自动创作（推荐）"
  description: "只需一句话描述，AI 自动创作歌词和音乐。~60-90秒"
- label: "使用我的歌词"
  description: "提供歌词、风格和标题，精确控制。~90-120秒"
- label: "纯音乐"
  description: "只生成背景音乐，无人声。~60-90秒"
multiSelect: false
```

### 步骤 3: 收集信息并生成

#### A: AI 自动创作（简化模式）

询问用户音乐描述后执行。如需指定男声/女声，直接在 prompt 中描述（如"一首欢快的女声流行歌"）。

```bash
python3 scripts/giggle_music_api.py --prompt "用户描述"
```

#### B: 使用歌词（自定义模式）

依次收集：歌词内容（必需）、音乐风格（必需）、歌曲标题（必需）、人声性别（可选，用 `AskUserQuestion` 提供 male/female 选项）。

```bash
python3 scripts/giggle_music_api.py --custom \
  --prompt "歌词内容" \
  --style "流行, 抒情" \
  --title "歌曲标题" \
  --vocal-gender female
```

#### C: 纯音乐

```bash
python3 scripts/giggle_music_api.py --prompt "用户描述" --instrumental
```

### 步骤 4: 输出结果

脚本输出 JSON 到 stdout（进度信息输出到 stderr）。使用 `--json` 获取结构化输出：

```bash
python3 scripts/giggle_music_api.py --prompt "描述" --json
```

```json
[
  {"title": "music_1", "audioUrl": "https://..."},
  {"title": "music_2", "audioUrl": "https://..."}
]
```

将每首音乐的 `audioUrl` 下载链接展示给用户即可。

### 异步模式

不等待完成，后续手动查询：

```bash
# 提交任务
python3 scripts/giggle_music_api.py --prompt "描述" --no-wait

# 查询结果
python3 scripts/giggle_music_api.py --query --task-id "任务ID"
```

## 参数速查

详细参数说明见 [REFERENCE.md](REFERENCE.md)。

| 参数 | 说明 |
|------|------|
| `--prompt` | 音乐描述或歌词（简化模式必需） |
| `--custom` | 启用自定义模式 |
| `--style` | 音乐风格（自定义模式必需） |
| `--title` | 音乐标题（自定义模式必需） |
| `--instrumental` | 生成纯音乐 |
| `--vocal-gender` | 人声性别：male / female（仅自定义模式，简化模式在 prompt 中描述） |
| `--no-wait` | 提交后立即返回 |
| `--query` | 查询任务状态 |
| `--task-id` | 任务 ID（配合 --query） |
| `--json` | JSON 格式输出 |

## 错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| "未设置API密钥" | .env 文件缺失或未配置 | 见 [SETUP.md](SETUP.md) |
| 任务状态 `failed` | prompt 内容不当 | 修改描述后重试 |
| "等待超时" | 生成时间过长 | 用 `--no-wait` 异步模式 |

## Resources

- **scripts/giggle_music_api.py**: 执行 `python3 scripts/giggle_music_api.py --help`
- **[SETUP.md](SETUP.md)**: 环境配置指南
- **[REFERENCE.md](REFERENCE.md)**: 完整参数和输出格式说明
