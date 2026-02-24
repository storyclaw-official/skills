---
name: giggle-image
description: 使用 Seedream 模型（通过 giggle.pro 平台）生成 AI 图像。支持文生图、图生图和多图融合（最多 10 张）。当用户需要创建、生成图像或图片时使用此技能。支持场景：(1) 根据文本描述生成图像，(2) 使用参考图生成图像，(3) 多图融合创意生成，(4) 自定义图像比例和生成数量。触发关键词：生图、画图、画一张、画一幅、绘图、绘制、生成图片、生成图像、生成一张图、图片生成、图像生成、帮我画、给我画、帮我生成图、我要一张图、AI绘图、AI作图、AI画图、生成壁纸、生成封面、生成插图、生成海报、即梦、seedream、Seedream、seedream45。
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🖼️","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/scripts/requirements.txt"]},"version":"1.0.0","author":"姜式伙伴"}
---

# Generating Images With Seedream (v5 - 2026-02-24)

使用 Seedream 模型（seedream45）通过 giggle.pro 平台生成 AI 图像。

**API 密钥**: 从环境变量 `GIGGLE_API_KEY` 或项目根目录 `.env` 文件读取。

## 执行流程（Phase 1 提交 + Phase 2 Cron）

图像生成通常需要 30-60 秒。采用「快速提交 + Cron 轮询」双阶段架构。

> **重要**：执行命令时**不得**在 exec 的 `env` 参数中传递 `GIGGLE_API_KEY`。API 密钥已通过系统环境变量配置，脚本会自动读取，无需显式传递。直接执行以下命令即可。

---

### Phase 1：提交任务（exec < 10 秒完成）

**先发送消息给用户**："图像生成中，通常 30-60 秒，稍后自动发送结果。"

```bash
# 文生图
python3 scripts/seedream_api.py \
  --prompt "描述" --aspect-ratio 16:9 \
  --no-wait --json

# 图生图 - URL
python3 scripts/seedream_api.py \
  --prompt "转为油画风格,保留构图" \
  --reference-images "https://example.com/photo.jpg" \
  --no-wait --json

# 图生图 - 本地文件（自动 base64 编码）
python3 scripts/seedream_api.py \
  --prompt "转为油画风格,保留构图" \
  --reference-images "/path/to/photo.jpg" \
  --no-wait --json

# 多图融合（2-10张，URL 和本地文件可混用）
python3 scripts/seedream_api.py \
  --prompt "融合这些图像的艺术风格" \
  --reference-images "url1" "/path/to/local.png" "url2" \
  --no-wait --json

# 生成多张
python3 scripts/seedream_api.py \
  --prompt "描述" \
  --generate-count 4 \
  --no-wait --json
```

返回示例：
```json
{"status": "started", "task_id": "xxx"}
```

**立即将 task_id 写入记忆**（`addMemory`）：
```
giggle-image task_id: xxx（提交时间：YYYY-MM-DD HH:mm）
```

---

### Phase 2：注册 Cron（45 秒间隔）

使用 `cron` 工具注册轮询任务。**必须严格按照以下参数格式，不得修改任何字段名或添加额外字段**：

```json
{
  "action": "add",
  "job": {
    "name": "giggle-image-<task_id前8位>",
    "schedule": {
      "kind": "every",
      "everyMs": 45000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "图片任务轮询：请执行 exec python3 scripts/seedream_api.py --query --task-id <完整task_id>，根据 Cron 处理逻辑处理 stdout 输出。如果 stdout 是非 JSON 纯文本，将其发送给用户并取消此 Cron。如果 stdout 是 JSON，不发消息继续等待。如果 stdout 为空，直接取消此 Cron。"
    },
    "sessionTarget": "main"
  }
}
```

注册成功后，Cron 每 45 秒向 Agent 发送一条系统事件。Agent 收到后执行查询命令。

**Cron 触发后的处理逻辑**（根据 exec 的 stdout 内容判断，所有路径均 exit 0）：

| stdout 特征 | 处理 |
|------------|------|
| 非空纯文本（不以 `{` 开头） | **将 stdout 原封不动发送给用户**（禁止添加任何前缀或修改），**取消 Cron**（使用 `cron` 工具 `action: "remove"`） |
| 空 stdout | 已推送过，**立即取消 Cron，不发消息** |
| JSON（以 `{` 开头，含 `"status"` 字段） | 不发消息，不取消 Cron，继续等待下次轮询 |

> **极其重要**：stdout 中的 Markdown 链接（`[查看图片 N](...)`）**必须原封不动保留**，禁止提取 URL、禁止改写链接格式、禁止发送裸 URL。

**如果 Cron 注册失败**：等待 60 秒后手动执行一次查询命令 `python3 scripts/seedream_api.py --query --task-id <task_id>`，根据上述处理逻辑处理结果。

---

## 新请求 vs 查询旧任务（重要区分）

**用户发起新的图片生成请求时**（如"帮我生成一张XX图片"、"画一张XX"），**必须执行 Phase 1 提交新任务**，不得复用记忆中的旧 task_id。每次新的生成请求都是全新的任务。

**仅当用户明确询问之前任务的进度时**（如"我上次的图片好了吗"、"之前那张图怎么样了"），才查询记忆中的旧 task_id：
1. **记忆中有 task_id** → 执行 `--query --task-id xxx`
2. **记忆无** → 告知用户，询问是否重新生成

---

## 结果展示格式

脚本在任务完成时输出用户友好的纯文本消息（非 JSON）：

**成功示例**：
```
🎨 图片已就绪！

关于「美丽的校园风景」的创作已完成 ✨

👉 [查看图片 1](https://assets.giggle.pro/...)

如需调整，随时告诉我~
```

**失败示例**：
```
😔 生成遇到了问题

关于「美丽的校园风景」的创作未能完成：输入内容可能包含敏感信息，被服务端拦截

💡 建议调整描述后重新尝试，我随时待命~
```

**转发规则**：
- stdout 已包含完整的上下文描述（含用户的提示词），**禁止**在前面添加任何文字
- **必须原封不动转发 stdout**，不添加、不删除、不改写
- 禁止提取括号中的 URL 单独展示
- 禁止发送裸 URL（飞书会截断含 `_` 的 URL）

---

## 参数速查

| 参数 | 默认值 | 选项 |
|-----|--------|------|
| `--aspect-ratio` | 16:9 | 16:9, 9:16, 1:1, 3:4, 4:3, 2:3, 3:2, 21:9 |
| `--generate-count` | 1 | 生成图像数量 |
| `--reference-images` | - | URL 或本地文件路径，最多 10 张（本地文件自动 base64 编码） |
| `--watermark` | false | 添加水印 |
| `--download` | false | 自动下载到 ~/Downloads |
| `--output-dir` | ~/Downloads | 自定义下载目录 |
| `--max-wait` | 300s | 最大等待时间（同步模式建议用 180） |
| `--json` | false | 结构化输出，便于脚本集成 |

---

## 交互引导流程

**当用户请求模糊（未说明比例、具体描述）时，按以下步骤引导。如用户已提供足够信息，直接执行命令，跳过相应步骤。**

**默认比例为 16:9。如果用户未明确指定图像比例，必须先询问用户确认比例后再生成。**

### 步骤 1: 图像比例（未指定时必须询问）

```
问题: "您需要什么比例的图像?"
header: "图像比例"
选项:
- "16:9 - 横屏(壁纸/封面) (推荐)"
- "9:16 - 竖屏(手机/Stories)"
- "1:1 - 正方形(社交媒体/头像)"
- "其他比例"
multiSelect: false
```

如选"其他": 3:4 (竖版) | 4:3 (横版) | 2:3 (竖版照片) | 3:2 (横版照片) | 21:9 (超宽屏)

### 步骤 2: 图像描述

询问用户描述。提示结构: `主体 + 场景 + 风格 + 细节`

好的示例：
- `"一只橘色猫咪坐在窗边,阳光洒进,水彩画风格,温馨氛围"`
- `"未来城市,赛博朋克风格,霓虹灯,夜景,高细节"`

### 步骤 3: 生成模式

```
问题: "是否需要使用参考图像?"
header: "生成模式"
选项:
- "不需要 - 纯文生图"
- "1张参考图 - 图生图(风格转换)"
- "多张参考图 - 多图融合(最多10张)"
multiSelect: false
```

如需参考图，收集可公开访问的图片 URL。

### 步骤 4: 执行生成并展示

按照「执行流程（Phase 1 提交 + Phase 2 Cron）」章节执行：先发消息 → Phase 1 提交 → 注册 Cron → Cron 轮询发结果。

收到结果后将 exec 返回的 stdout 原封不动发给用户。

> 如用户希望保存图像到本地，可追加 `--download` 参数重新执行，或告知用户点击完整链接自行保存。
