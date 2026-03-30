---
name: x2c-socialposter
description: "通过 X2C Open API 管理社交媒体发布和互动。适用场景：(1) 发布文本/媒体帖子到 TikTok、Instagram、Facebook、YouTube、LinkedIn、Twitter 等。(2) 定时发布帖子。(3) 管理帖子评论和回复。(4) 上传媒体文件获取 CDN 链接。(5) 查看发布历史和已绑定账号状态。触发词：发布社交媒体、发帖、社交媒体、定时发布、上传媒体、社交账号、评论帖子。"
version: "0.0.1"
license: MIT
author: storyclaw-official
homepage: https://github.com/storyclaw-official/skills
repository: https://github.com/storyclaw-official/skills
requires:
  bins: [python3]
  env: [X2C_API_KEY]
  pip: [requests]
metadata:
  {
    "openclaw": {
      "emoji": "📱",
      "requires": {
        "bins": ["python3"],
        "env": ["X2C_API_KEY"],
        "pip": ["requests"]
      },
      "primaryEnv": "X2C_API_KEY",
      "installSpec": {
        "bins": ["python3"],
        "env": ["X2C_API_KEY"],
        "pip": ["requests"]
      }
    }
  }
---

English | [简体中文](./SKILL.zh-CN.md)

# X2C Social Poster

**来源**: [storyclaw-official/skills](https://github.com/storyclaw-official/skills) · 控制台: [x2creel.ai](https://www.x2creel.ai/)

通过 X2C Open API 发布帖子、管理评论和上传媒体到社交平台。支持 13+ 个平台，包括 TikTok、Instagram、YouTube、Facebook、LinkedIn、Twitter 等。

---

## 安装要求

| 要求 | 值 |
|------|-----|
| **可执行文件** | `python3` |
| **环境变量** | `X2C_API_KEY`（必需；从 [X2C 控制台](https://www.x2creel.ai/) 获取） |
| **Pip 依赖** | `requests` |

使用前请设置 `X2C_API_KEY`。脚本会在未配置时提示。

---

## 首次使用引导

**当用户首次调用此技能时，请按以下步骤依次引导：**

### 步骤 0：检查 API Key

运行以下命令检查 `X2C_API_KEY` 是否已设置：

```bash
python3 scripts/x2c_social.py --action check-key
```

- 如果已设置 → 进入步骤 1。
- 如果未设置 → 引导用户完成配置：

```
🔑 X2C API Key 尚未配置，让我们来设置：

1. 访问 https://www.x2creel.ai/social-accounts
2. 创建 X2C 账号（如果还没有）
3. 绑定你的社交媒体账号（TikTok、Instagram 等）
4. 进入 Dashboard → Developer API Key
5. 复制你的 X2C Open API Key
6. 将 API Key 粘贴到对话框中

提供 Key 后，我会帮你保存并验证。
```

用户提供 Key 后，保存到环境变量并通过 `social/status` 确认。

### 步骤 1：验证已绑定账号

API Key 配置完成后，始终先检查已绑定的账号：

```bash
python3 scripts/x2c_social.py --action status
```

向用户展示已绑定的平台。如果没有绑定任何账号，引导用户：

```
⚠️ 尚未绑定任何社交账号。

请访问 https://www.x2creel.ai/social-accounts 绑定你的社交媒体账号，完成后再回来操作。
```

---

## 支持的平台

| 平台 | 标识 | 备注 |
|------|------|------|
| TikTok | `tiktok` | 需要视频 |
| Instagram | `instagram` | 支持图片/视频 |
| Facebook | `facebook` | 文本、图片、视频 |
| YouTube | `youtube` | 需要视频 |
| LinkedIn | `linkedin` | 文本、图片、视频 |
| Twitter / X | `twitter` | 文本、图片、视频 |
| Threads | `threads` | 文本、图片 |
| Pinterest | `pinterest` | 需要图片 |
| Reddit | `reddit` | 文本、图片、视频 |
| Bluesky | `bluesky` | 文本、图片 |
| Telegram | `telegram` | 文本、图片、视频 |
| Snapchat | `snapchat` | 图片/视频 |
| Google 商家 | `gmb` | 文本、图片 |

---

## 命令列表

### 1. 查看已绑定账号

```bash
python3 scripts/x2c_social.py --action status
```

### 2. 发布帖子

```bash
# 纯文本帖子
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "来看看我们的最新动态！🚀"

# 带远程媒体 URL 的帖子
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "看这个！🎬" \
  --media-urls "https://example.com/video.mp4"

# 带本地文件的帖子（自动上传到 S3，然后发布——一步到位！）
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "看这个！🎬" \
  --media-files "/path/to/video.mp4"

# 混合本地文件和远程 URL
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "双媒体帖子！🎬" \
  --media-files "/path/to/local.mp4" \
  --media-urls "https://example.com/remote.jpg"

# 带本地文件的定时发布
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "即将上线！⏰" \
  --media-files "/path/to/video.mp4" \
  --schedule "2026-04-01T12:00:00Z"

# 帖子中链接缩短
python3 scripts/x2c_social.py --action publish \
  --platforms twitter linkedin \
  --post "阅读我们的博客：https://example.com/very-long-url" \
  --shorten-links
```

> **一步到位发布**：使用 `--media-files` 传入本地文件路径时，脚本会自动将文件上传到 S3，然后用返回的 CDN URL 发布。也可以直接在 `--media-urls` 中传入本地路径，脚本会自动检测并上传。无需单独运行上传命令。

### 3. 查看发布历史

```bash
# 所有平台
python3 scripts/x2c_social.py --action posts

# 按平台筛选
python3 scripts/x2c_social.py --action posts --platform tiktok
```

### 4. 删除帖子

```bash
# 从特定平台删除
python3 scripts/x2c_social.py --action delete-post --post-id post_abc123

# 从所有平台批量删除
python3 scripts/x2c_social.py --action delete-post --post-id post_abc123 --bulk
```

### 5. 发表评论

```bash
python3 scripts/x2c_social.py --action comment \
  --post-id post_abc123 \
  --platforms tiktok \
  --comment "内容真棒！🔥"
```

### 6. 获取评论

```bash
python3 scripts/x2c_social.py --action comments \
  --post-id post_abc123 \
  --platform tiktok
```

### 7. 回复评论

```bash
python3 scripts/x2c_social.py --action reply \
  --comment-id comment_xyz \
  --platforms tiktok \
  --comment "感谢观看！"
```

### 8. 删除评论

```bash
python3 scripts/x2c_social.py --action delete-comment \
  --comment-id comment_xyz
```

### 9. 上传媒体

```bash
python3 scripts/x2c_social.py --action upload \
  --file /path/to/video.mp4 \
  --folder my-videos
```

返回永久 CDN URL，可用于 `--media-urls` 发布帖子。

---

## 执行流程：一步到位发布本地媒体

发布本地文件时，脚本自动处理全部流程：

```
用户运行 publish 并传入 --media-files /path/to/video.mp4
  ↓
脚本检测到本地文件路径（非 http/https）
  ↓
自动通过 media/upload 上传文件到 S3
  ↓
获取 CDN URL（https://v.arkfs.co/...）
  ↓
将 CDN URL 注入 media_urls
  ↓
调用 social/publish 发布帖子
  ↓
返回发布结果给用户
```

**示例 — 一条命令，完整流程：**

```bash
python3 scripts/x2c_social.py --action publish \
  --platforms tiktok instagram \
  --post "快来看！🎬" \
  --media-files /path/to/video.mp4
```

脚本会输出上传进度，然后是最终发布结果：

```json
{"status": "uploading", "file": "video.mp4", "message": "Uploading video.mp4 to S3..."}
{"status": "uploaded", "file": "video.mp4", "url": "https://v.arkfs.co/.../video.mp4"}
{
  "success": true,
  "data": {
    "id": "post_abc123",
    "postIds": [
      {"platform": "tiktok", "id": "7123456789", "status": "success"},
      {"platform": "instagram", "id": "17898765432", "status": "success"}
    ]
  }
}
```

### 单独上传（可选）

你仍然可以单独上传文件以获取 CDN URL 供后续使用：

```bash
python3 scripts/x2c_social.py --action upload --file /path/to/video.mp4 --folder my-videos
```

---

## 参数说明

| 参数 | 是否必需 | 描述 |
|------|----------|------|
| `--action` | ✅ | 要执行的操作（见命令列表） |
| `--post` | 发布时需要 | 帖子文本内容 |
| `--platforms` | 发布时需要 | 空格分隔的目标平台 |
| `--platform` | 筛选时使用 | 单个平台筛选 |
| `--media-urls` | ❌ | 远程 URL 或本地路径（本地文件自动上传） |
| `--media-files` | ❌ | 本地文件路径，自动上传并附加 |
| `--schedule` | ❌ | ISO 8601 格式的定时发布时间 |
| `--shorten-links` | ❌ | 缩短帖子中的链接 |
| `--post-id` | 帖子操作时 | Ayrshare 帖子 ID |
| `--comment-id` | 评论操作时 | 评论 ID |
| `--comment` | 评论/回复时 | 评论或回复文本 |
| `--bulk` | ❌ | 从所有平台删除 |
| `--file` | 上传时需要 | 本地文件路径 |
| `--folder` | ❌ | 上传子文件夹（默认：`uploads`） |

---

## 交互引导

**当用户请求模糊时，按以下步骤引导。如果用户已提供足够信息，直接执行命令。**

### 步骤 1：新手检查

始终先执行首次使用引导。在任何操作前验证 API Key 和已绑定账号。

### 步骤 2：确认意图

```
你想做什么？
选项：
  📝 发布帖子
  📊 查看发布历史
  💬 管理评论
  📤 上传媒体
  🔗 查看已绑定账号
```

### 步骤 3：发布帖子 — 收集信息

```
问题："你想发布到哪些平台？"
→ 仅显示用户已绑定的平台。

问题："帖子内容是什么？"
→ 接受文本输入。

问题："需要附带媒体（图片/视频）吗？"
→ 如果是，接受本地文件路径或远程 URL。本地文件会自动上传——无需额外步骤。

问题："立即发布还是定时发布？"
→ 如果定时，收集 ISO 8601 格式的时间。
```

### 步骤 4：执行并展示

运行相应命令并将结果展示给用户。对于发布操作，清晰展示每个平台的状态（成功/失败）。

---

## 错误处理

| 状态码 | 含义 | 处理方式 |
|--------|------|----------|
| 400 | 参数缺失或无效 | 检查并修正参数 |
| 401 | API Key 无效 | 引导用户验证/重置 API Key |
| 500 | 服务器错误 | 重试或通知用户 |

发生错误时，显示清晰的错误信息并建议纠正措施。
