---
name: giggle-generation-image
description: 当用户希望创建、生成或绘制图像时使用此技能——包括文生图、图生图风格迁移，或融合多张参考图。触发词：生成图片、画画、创建图片、AI 艺术、做一张照片、插画、生成视觉、需要一张图、风格迁移、参考图、Seedream。
---

# 使用 Seedream 生成图像

通过 giggle.pro 的 Seedream 模型（seedream45）生成 AI 图像。支持文生图、图生图和多图融合。

**API Key**：从环境变量 `GIGGLE_API_KEY` 或项目根目录 `.env` 文件中读取。

> **禁止内联 Python**：所有命令必须通过 `exec` 工具直接执行。**切勿**使用 `python3 << 'EOF'` 或 heredoc 内联代码。内联代码会导致路径错误和方法名不匹配。

## 执行流程（三阶段双路径）

图像生成通常需要 30–60 秒。采用「快速提交 + Cron 轮询 + 同步兜底」三阶段架构，确保用户能收到结果。

> **重要**：**切勿**在 exec 的 `env` 参数中传递 `GIGGLE_API_KEY`。API Key 通过系统环境配置；脚本会自动读取。直接执行以下命令即可。

---

### 阶段 1：提交任务（exec 在 10 秒内完成）

**先向用户发送消息**：「图像生成进行中，通常需要 30–60 秒，结果将自动发送。」

```bash
# 文生图
python3 scripts/seedream_api.py \
  --prompt "描述" --aspect-ratio 16:9 \
  --no-wait --json

# 图生图 - URL
python3 scripts/seedream_api.py \
  --prompt "转换为油画风格，保持构图" \
  --reference-images "https://example.com/photo.jpg" \
  --no-wait --json

# 图生图 - 本地文件（自动 base64 编码）
python3 scripts/seedream_api.py \
  --prompt "转换为油画风格，保持构图" \
  --reference-images "/path/to/photo.jpg" \
  --no-wait --json

# 多图融合（2–10 张，URL 与本地文件可混用）
python3 scripts/seedream_api.py \
  --prompt "融合这些图片的艺术风格" \
  --reference-images "url1" "/path/to/local.png" "url2" \
  --no-wait --json

# 批量生成多张图
python3 scripts/seedream_api.py \
  --prompt "描述" \
  --generate-count 4 \
  --no-wait --json
```

响应示例：

```json
{"status": "started", "task_id": "xxx"}
```

**立即将 task_id 存入记忆**（`addMemory`）：

```
giggle-generation-image task_id: xxx (submitted: YYYY-MM-DD HH:mm)
```

---

### 阶段 2：注册 Cron（45 秒间隔）

> **禁止内联 Python**：Cron payload 中的 exec 命令必须直接调用 `python3 scripts/seedream_api.py`，**切勿**使用 heredoc 内联代码。

使用 `cron` 工具注册轮询任务。**必须严格遵循参数格式；不得修改字段名或添加额外字段**：

```json
{
  "action": "add",
  "job": {
    "name": "giggle-generation-image-<task_id 前 8 位>",
    "schedule": {
      "kind": "every",
      "everyMs": 45000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "图像任务轮询：执行 exec python3 scripts/seedream_api.py --query --task-id <完整 task_id>，按 Cron 逻辑处理 stdout。若 stdout 为非 JSON 纯文本，发送给用户并移除 Cron。若 stdout 为 JSON，不发送消息，继续等待。若 stdout 为空，立即移除 Cron。"
    },
    "sessionTarget": "main"
  }
}
```

注册后，Cron 每 45 秒向 Agent 发送一次系统事件。Agent 收到后执行查询命令。

**Cron 触发处理**（根据 exec stdout 判断；以下路径均 exit 0）：

| stdout 模式 | 动作 |
|----------------|--------|
| 非空纯文本（不以 `{` 开头） | **将 stdout 原样转发给用户**（不加前缀、不修改），**移除 Cron**（使用 `cron` 工具 `action: "remove"`） |
| stdout 为空 | 已推送，**立即移除 Cron，不发送消息** |
| JSON（以 `{` 开头，含 `"status"` 字段） | 不发送消息，不移除 Cron，等待下次轮询 |

> **关键**：stdout 中的 Markdown 链接（`[View image N](...)`）**必须原样保留**。不要提取 URL，不要改写链接格式，不要发送裸 URL。

**若 Cron 注册失败**：直接进入阶段 3。

---

### 阶段 3：同步等待（乐观路径，Cron 未触发时的兜底）

**目的**：应对已知的平台 bug（Cron 调度器可能不触发），确保用户能收到结果。

**无论 Cron 是否注册成功，都必须执行此步骤。**

> **禁止内联 Python**：必须直接执行以下命令，**切勿**使用 heredoc 内联代码。

```bash
python3 scripts/seedream_api.py --query --task-id <task_id> --poll --max-wait 180
```

**处理逻辑**：

- 返回纯文本（图像就绪/失败消息） → **原样转发给用户**，移除 Cron
- stdout 为空 → Cron 已推送，移除 Cron，不发送消息
- exec 超时 → Cron 继续轮询

> 脚本内部每 5 秒轮询一次；若 Cron 已推送（存在 `.sent` 标记），则自动退出，不会重复推送。

---

## 新请求 vs 查询旧任务（重要区分）

**当用户发起新的图像生成请求**（例如「生成一张 XX 的图」「画 XX」）时，**必须执行阶段 1 提交新任务**。不要复用记忆中的旧 task_id。每次新请求都是独立任务。

**仅当用户明确询问之前任务的进度**（例如「我上次的图好了吗？」「那张图怎么样了？」）时，才从记忆中查询旧 task_id：

1. **记忆中有 task_id** → 执行 `--query --task-id xxx`
2. **记忆中无 task_id** → 告知用户，询问是否要重新生成

---

## 结果展示格式

任务完成时脚本输出用户友好的纯文本（非 JSON）：

**成功示例**：

```
图像生成完成！✨

「美丽的校园风景」创作完成 ✨

[查看图片 1](https://assets.giggle.pro/...)

如有需要可以继续调整~
```

**失败示例**：

```
生成遇到问题

「美丽的校园风景」无法完成：输入可能包含敏感内容，已被服务端拦截

建议调整描述后重试。准备好了随时告诉我~
```

**转发规则**：

- stdout 已包含完整上下文（含用户 prompt）；**不要**在前面加文字
- **必须原样转发 stdout**；不得增删改
- 不要从方括号中提取 URL 单独展示
- 不要发送裸 URL（飞书会截断包含 `_` 的 URL）

---

## 参数速查

| 参数 | 默认值 | 选项 |
|-----------|---------|---------|
| `--aspect-ratio` | 16:9 | 16:9、9:16、1:1、3:4、4:3、2:3、3:2、21:9 |
| `--generate-count` | 1 | 图像数量；单次请求最多 4 张 |
| `--reference-images` | - | URL 或本地文件路径；最多 10 张（本地文件自动 base64 编码） |
| `--watermark` | false | 添加水印 |
| `--download` | false | 自动下载到 ~/Downloads |
| `--output-dir` | ~/Downloads | 自定义下载目录 |
| `--max-wait` | 300s | 最长等待时间（同步模式建议 180） |
| `--json` | false | 结构化输出，便于脚本集成 |

---

## 交互引导流程

**当用户请求较模糊**（未指定画幅比例或具体描述）时，按以下步骤引导。若用户已提供足够信息，可直接执行命令并跳过部分步骤。

**默认画幅比例为 16:9。若用户未指定，生成前请先确认。**

### 步骤 1：画幅比例（未指定时询问）

```
问题：「需要什么画幅比例？」
标题：「画幅比例」
选项：
- "16:9 - 横屏（壁纸/封面）（推荐）"
- "9:16 - 竖屏（手机/故事）"
- "1:1 - 方形（社交/头像）"
- "其他比例"
multiSelect: false
```

若选「其他」：3:4（竖屏） | 4:3（横屏） | 2:3（竖屏照片） | 3:2（横屏照片） | 21:9（超宽屏）

### 步骤 2：图像描述

请用户描述。Prompt 结构：`主体 + 场景 + 风格 + 细节`

好的示例：

- `「一只橘猫在窗边，阳光洒入，水彩风格，温馨氛围」`
- `「未来城市，赛博朋克风格，霓虹灯，夜景，高细节」`

### 步骤 3：生成模式

```
问题：「需要参考图片吗？」
标题：「生成模式」
选项：
- "不需要 - 仅文生图"
- "1 张参考 - 图生图（风格迁移）"
- "多张参考 - 多图融合（最多 10 张）"
multiSelect: false
```

若需要参考图，收集可公开访问的图片 URL。

### 步骤 4：执行并展示

按照「执行流程（三阶段双路径）」：发送消息 → 阶段 1 提交 → 阶段 2 注册 Cron → 阶段 3 同步等待。

结果到达后将 exec stdout 原样转发给用户。

> 若用户希望本地保存，可加 `--download` 重新执行，或告知用户点击完整链接保存。

---

## 限制说明

- 单次请求最多 10 张参考图
- 文字渲染可能不完美（建议单独叠加文字）
- 高度具体的品牌 logo 可能无法准确复现

---

## Prompt 技巧

- **具体描述** - 「木桌上的红苹果」比「一个苹果」更好
- **包含风格** - 「像素艺术风格」或「写实风格」
- **说明用途** - 「儿童绘本用」会影响输出风格
- **描述构图** - 「居中」「三分法」「特写」
- **指定颜色** - 明确色彩搭配效果更好
- **参考图 prompt** - 使用「与参考图相同风格」「保持视觉美感」「匹配色彩 palette」
- **避免** - 不要在图像中要求复杂文字（建议用叠加层实现）
