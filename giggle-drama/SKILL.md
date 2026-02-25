---
name: giggle-drama
description: 用户在有生成视频需求、生成短视频需求、有一个创意需要生成视频、或查看可用风格时使用此skill，可以引导用户查看风格。
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🎬","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/scripts/requirements.txt","cp {baseDir}/.env.example {baseDir}/.env","echo 'Please edit .env and add your GIGGLE_API_KEY'"]},"version":"2.0.0","author":"姜式伙伴"}
---

# 托管模式V2 API Skill

此 skill 用于调用托管模式V2 API，执行视频生成工作流。

## 启动流程（必须先确认，再生成）

视频生成耗时 10-30 分钟且消耗积分，**首次生成前必须先与用户确认关键参数**。

**重试场景（用户说"重试"/"再试一次"，或子步骤失败后用户确认重新生成）：跳过故事/时长/风格确认（复用原参数），但必须提醒用户"重新生成将创建新项目并再次消耗积分（之前的费用无法恢复），是否继续？"，用户确认后执行 start。**

### 跳过确认的唯一条件

用户消息中**同时明确**了以下三项，才可跳过确认直接生成：
- 故事内容清晰（有具体情节，不只是一个词）
- 明确说了时长（如"30秒""1分钟"）
- 明确说了风格（风格名称或 ID）

否则**必须先用 AskUserQuestion 确认**，不得直接执行。

### 确认步骤（AskUserQuestion，最多一次）

用以下格式和用户确认，可同时问 2-3 个问题：

**问题 1：故事梗概确认**
> 复述你理解的故事内容，让用户确认或补充细节

**问题 2：视频时长**（选项）
- 30秒（约6个分镜，适合简短内容）
- 60秒（约12个分镜，**推荐**）
- 120秒（约24个分镜，适合完整故事）
- 自动决定

**问题 3：画面风格**（选项）
- 3D古风（国风仙侠 CG 渲染质感）
- 写实风格（电影级写实视觉）
- 二次元（标准动漫画风）
- 吉卜力（治愈系手绘插画）
- 皮克斯（3D卡通动画）
- 2D漫剧（日漫国漫融合）
- 国风水墨（传统水墨插画）
- 交给系统自动选择

用户回复后，**重复确认一遍生成参数**，然后执行 Phase 1。

## 可用视频风格

| ID  | 风格名称 | 分类 | 描述 |
|-----|---------|------|------|
| 142 | 3D古风 | 3D动画 | 3D 国风仙侠风格，偏 CG 渲染质感 |
| 143 | 2D漫剧 | 2D插画 | 融合日漫与国漫风格的二次元画风 |
| 144 | 吉卜力 | 2D插画 | 治愈系手绘插画风格，色彩柔和 |
| 145 | 皮克斯 | 3D动画 | 典型皮克斯风格的 3D 卡通动画 |
| 146 | 写实风格 | 电影写实 | 偏电影级的写实视觉风格 |
| 147 | 二次元 | 2D插画 | 标准二次元动漫画风 |
| 148 | 国风水墨 | 2D插画 | 中国传统水墨风格插画 |

**提示**：不指定风格 ID 时，系统自动选择最适合的风格。

---

## 执行流程（三阶段双路径）

视频生成通常需要 10-30 分钟。采用「同步等待 + Cron 兜底」双路径，确保用户一定收到结果。

---

### 第一步：提交任务（Phase 1，exec < 10 秒完成）

**先发送消息给用户**："视频生成中，通常 10-30 分钟，每3分钟自动报告进度，请耐心等待。"

```bash
python3 scripts/trustee_api.py start \
  --story "故事内容" \
  --aspect "16:9" \
  --project-name "项目名称" \
  --duration 30
```

> **时长参数提取规则**：
> - 用户说"30秒" / "30s" → `--duration 30`
> - 用户说"1分钟" / "60秒" → `--duration 60`
> - 用户说"2分钟" → `--duration 120`
> - 用户说"6个分镜"/"短视频" → 推断为 `--duration 30`（约5-6个镜头）
> - 用户未指定时长 → **不传此参数**（系统自动决定）
> - 可选值：`30 / 60 / 120 / 180 / 240 / 300`（秒）

返回示例：
```json
{"code": 200, "status": "started", "data": {"project_id": "xxx", "log_file": "/path/logs/xxx.log"}}
```

**立即将 project_id 写入记忆**（`addMemory`）：
```
giggle-drama project_id: xxx（状态：生成中，提交时间：YYYY-MM-DD HH:mm）
```

如果 start 失败（code != 200）：告知错误信息，询问用户是否重试，**不执行后续步骤**。

---

### 第二步：注册 Cron（立刻注册，在 Phase 3 之前）

**目的**：兜底路径，无论 Phase 3 是否成功，Cron 保证用户收到结果。

使用 `cron` 工具注册轮询任务，**必须严格按照以下参数格式，不得修改任何字段名或添加额外字段**：

```json
{
  "action": "add",
  "job": {
    "name": "giggle-drama-<project_id前8位>",
    "schedule": {
      "kind": "every",
      "everyMs": 180000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "视频任务轮询：请执行 exec python3 scripts/trustee_api.py query --project-id <完整project_id>，根据 Cron 处理逻辑处理结果。"
    },
    "sessionTarget": "main"
  }
}
```

每次 Cron 触发后执行：
```bash
python3 scripts/trustee_api.py query --project-id <project_id>
```

**Cron 处理逻辑**（根据 exit code）：

| exit code | 含义 | 处理 |
|-----------|------|------|
| 0 | 完成/支付中/进行中 | 读 JSON：already_sent→跳过取消；signed_url→发结果取消；pay_failed→发"积分不足"取消；msg 含"自动支付"→转发消息 Cron 继续；else→发步骤进度，Cron 继续 |
| 1 | 失败/积分不足 | 发错误消息，取消 Cron |

> **说明**：支付逻辑已内置于 `query` 脚本，检测到 `pay_status=="pending"` 时自动调用 pay API，**无需 agent 介入**。

**步骤进度消息格式**（从 `data.current_step` 和 `data.steps` 读取）：
```
视频渲染中 — 已完成：剧本✓ 角色✓ 分镜✓ 镜头图✓ | 已用时 X 分钟
```

步骤名称翻译：
- `script` → 剧本生成
- `character` → 角色设计
- `storyboard` → 分镜制作
- `shot` → 镜头图渲染
- `video` → 视频渲染

---

### 第三步：同步等待（Phase 3，乐观路径）

**目的**：如果视频较快完成（< LLM 超时），直接在此步骤返回结果。

```bash
python3 scripts/trustee_api.py query --project-id <project_id> --poll
```

**处理逻辑**：

- 返回 `status: "already_sent"` → 跳过（Cron 已发送），取消 Cron
- 返回 `code: 200` + 含 `signed_url` → **立即发送结果给用户**，取消 Cron
- exec 超时/失败 → Cron 已在运行，继续等待即可

---

## 结果消息格式

收到完成结果后，发送以下格式的消息：

```
视频生成完成

▶️ 在线播放：<data.signed_url>
⏱️ 时长：<data.duration>s | 分镜：<data.shot_count> 个
📁 本地：<data.local_path>（如下载失败则无此行）
```

**说明**：
- `data.signed_url` 已将 `~` 编码为 `%7E`，飞书可正常点击
- 如果 `data.download_failed == true`，则无本地路径，提示用户可直接用 `data.signed_url` 在浏览器播放

---

## 失败处理

| 场景 | 处理方式 |
|------|---------|
| `start` 失败 | 告知错误，询问用户是否重试 |
| 支付失败（msg 含"积分"） | "积分不足，请充值后告诉我重试" |
| 子步骤失败 | 告知步骤名和错误信息，提醒"重新生成将创建新项目并再次消耗积分（之前的费用无法恢复）"，询问用户是否重新生成。确认后执行 `start`（唯一重试方式，API 不支持断点续传）：`python3 scripts/trustee_api.py start --story "..." --aspect "..." --project-name "..."` |
| 超时（1小时） | "生成超时，project_id=xxx，可稍后查询" |
| 视频下载失败 | 提供 `signed_url`，"可直接在浏览器打开" |

---

## Gateway 重启后恢复

用户询问之前视频进度时：

1. **记忆中有 project_id** → 直接执行 `query --project-id xxx`，**绝不重新 start**
2. **记忆无，有日志** → `ls ~/.openclaw/skills/giggle-drama/logs/` 找最近 project_id，再 query
3. **两者都无** → 告知用户，询问是否重新生成

---

## 其他命令

**查看风格列表**：
```bash
python3 scripts/trustee_api.py styles
```

**遗留工作流（不推荐，阻塞等待）**：
```bash
python3 scripts/trustee_api.py workflow \
  --story "..." --aspect "16:9" --project-name "..."
```
