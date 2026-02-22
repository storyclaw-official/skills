---
name: giggle-drama
description: 用户在有生成视频需求、生成短视频需求、有一个创意需要生成视频、或查看可用风格时使用此skill，可以引导用户查看风格。
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🎬","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/scripts/requirements.txt","cp {baseDir}/.env.example {baseDir}/.env","echo 'Please edit .env and add your GIGGLE_API_KEY'"]},"version":"2.0.0","author":"姜式伙伴"}
---

# 托管模式V2 API Skill

此 skill 用于调用托管模式V2 API，执行视频生成工作流。

## 启动指令

**重要**：
- 如果用户已提供足够信息（故事、比例），直接执行视频生成，不展示引导文字
- 只有当用户明确询问"有哪些风格"或信息不足时，才展示风格列表或询问补充信息
- 不要输出欢迎标题或固定开场白

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
  --project-name "项目名称"
```

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

注册间隔 **3 分钟** 的 Cron，每次执行：
```bash
python3 scripts/trustee_api.py query --project-id <project_id>
```

**Cron 处理逻辑**（根据返回结果）：

| 返回状态 | 处理 |
|---------|------|
| `status: "already_sent"` | 跳过，取消 Cron |
| `code: 200` + 含 `signed_url` | 发送结果给用户，取消 Cron |
| `status: "failed"` / `code: -1` 且含 `err_msg` | 发错误消息给用户，取消 Cron |
| 其他（进行中） | 发步骤进度，Cron 继续 |

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
| 子步骤失败 | "XX步骤失败，是否重新生成？" |
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
