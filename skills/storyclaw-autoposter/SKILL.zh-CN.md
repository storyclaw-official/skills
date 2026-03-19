---
name: storyclaw-autoposter
description: "通过 StoryClaw 支持 13 个社交平台的发帖、定时发布、查询、管理与数据分析。适用场景：(1) 发布或定时发送帖子（含媒体文件），(2) 查询帖子历史或查看帖子详情，(3) 查看帖子或账号数据分析（点赞、浏览、粉丝、曝光），(4) 删除帖子。触发词：帮我发帖、自动发帖、定时发帖、查看帖子、帖子数据、观看量、粉丝数、账号分析。"
version: "1.0.0"
license: MIT
author: storyclaw-official
homepage: https://storyclaw.com
repository: https://github.com/storyclaw-official/skills
requires:
  bins: [python3]
  env: [STORYCLAW_API_KEY]
  pip: [requests]
metadata:
  {
    "openclaw": {
      "emoji": "📱",
      "requires": {
        "bins": ["python3"],
        "env": ["STORYCLAW_API_KEY"],
        "pip": ["requests"]
      },
      "primaryEnv": "STORYCLAW_API_KEY",
      "installSpec": {
        "bins": ["python3"],
        "env": ["STORYCLAW_API_KEY"],
        "pip": ["requests"]
      }
    }
  }
---

# StoryClaw 自动发帖 Skill

提供完整的社交媒体帖子管理与数据分析能力，支持 13 个平台。

**支持平台：** TikTok、Instagram、Facebook、X/Twitter、YouTube、LinkedIn、Threads、Pinterest、Reddit、Bluesky、Telegram、Snapchat、Google Business Profile

**API 端点：** `POST https://aipuejhjwmabtobjrqdz.supabase.co/functions/v1/storyclaw-api`

---

## 阶段一：API Key 检查 & 账号绑定确认

### 第一步：检查 API Key

首先检查环境变量中是否已配置 `STORYCLAW_API_KEY`：

- **已配置** → 直接使用，进入第二步
- **未配置** → 告知用户：
  > "开始之前需要你的 StoryClaw API Key。请前往 **https://storyclaw.com/profile** → **StoryClaw API Key**，复制后粘贴给我。"

获取到 Key 后（来自环境变量或用户输入），调用 `get_social_status` 验证：

```json
{ "storyclaw_api_key": "<STORYCLAW_API_KEY>", "action": "get_social_status" }
```

- 401 Invalid API key → 告知用户：
  > "API Key 好像有问题，请前往 **https://storyclaw.com/profile** → **StoryClaw API Key** 重新检查并复制。"
- 成功 → 记录已连接平台，进入第二步

### 第二步：确认社交账号绑定

将 `get_social_status` 返回的已连接平台展示给用户。

如果没有任何平台已连接，或用户询问如何绑定社交账号，引导用户：
> "请前往 **https://storyclaw.com/profile** → **社交账号绑定**，按照页面提示绑定你的 TikTok、Instagram 等账号，完成后回来继续。"

至少有一个平台已连接 → 进入阶段二。

**所有操作的平台选项均基于已连接平台，不展示未绑定的平台。**

---

## 阶段三：选择功能

| 功能 | 说明 |
|------|------|
| 📝 发帖 | 立即或定时发布新帖子 |
| 🔍 查询帖子列表 | 查看某平台的历史帖子 |
| 📄 查看帖子详情 | 查看特定帖子的完整信息 |
| 📊 帖子数据分析 | 查看点赞、浏览、评论、分享等数据 |
| 👥 账号概况分析 | 查看粉丝数、关注数、曝光量等账号级数据 |
| 🗑️ 删除帖子 | 删除指定帖子 |

---

## 功能一：发帖

### 收集内容
询问用户想发什么内容，如提供草稿或想法，进入内容优化环节。

### 内容优化（如需要）
询问偏好：平台风格、语气、是否添加 hashtag、语言。优化后展示给用户确认。

### 选择发布平台
从已连接平台中让用户选择（可多选）。若无视频内容，自动移除 TikTok 选项。

### 媒体附件（可选）
`publish_post` 只接受 HTTPS URL，不接受本地文件。

**本地文件需先上传获取 S3 链接：**

```bash
curl -X POST https://aipuejhjwmabtobjrqdz.supabase.co/functions/v1/storyclaw-api \
  -F "action=upload_file" \
  -F "storyclaw_api_key=<key>" \
  -F "file=@/path/to/photo.jpg" \
  -F "folder=my-media"
```

流程：本地文件 → `upload_file` → S3 链接 → `mediaUrls` → `publish_post`

### ⚠️ 发帖前媒体限制检查（必须执行）

发帖前逐项核查目标平台限制，发现违规立即阻止：

| 检查项 | 说明 |
|--------|------|
| 文件格式 | 是否在平台支持列表中 |
| 文件大小 | 是否超过最大限制 |
| 视频时长 | 是否在最小/最大范围内 |
| 分辨率/宽高比 | 是否符合要求 |
| 媒体数量 | 是否超过每帖上限 |
| 视频 URL | 是否以已知扩展名结尾 |
| Reddit + 视频 | Reddit 不支持视频 → 阻止 |
| TikTok + PNG | TikTok 不支持 PNG → 阻止 |
| HTTPS | URL 必须以 https:// 开头 |

违规示例提示：
- "⚠️ 无法发布：TikTok 不支持 PNG 格式图片，请转换为 JPG 或 WebP 后重试。"
- "⚠️ 无法发布：X/Twitter 视频时长为 145 秒，超过最大限制 140 秒。"
- "⚠️ 无法发布：Reddit 不支持视频发布，请移除视频或取消勾选 Reddit 平台。"

文件大于 50 MB 建议使用 `scheduleDate` 定时发送。

### 各平台媒体限制速查

**TikTok**
- 图片：JPG/JPEG/WebP（不支持 PNG），最多 35 张，推荐 1080×1920
- 视频：MP4/MOV/WebM，最大 1GB，3 秒~10 分钟，360~4096px，23~60 FPS，最多 1 个

**Instagram**
- 图片：JPG/GIF/PNG，最大 8MB，宽 320~1440px，比例 4:5~1.91:1，最多 10 张，每日限 50 条
- 视频（Feed/Reels）：MP4/MOV，最大 300MB，3 秒~15 分钟，最多 1 个
- Stories 视频：最大 100MB，3~60 秒

**Facebook Pages**
- 图片：JPEG/BMP/PNG/GIF/TIFF，最大 10MB，最大 2048×2048px，最多 10 张
- 视频：最大 2GB，最多 1 个

**LinkedIn**
- 图片：JPG/GIF/PNG，最大 5MB，推荐 1200×627px，最多 9 张，每日限 150 条
- 文档：PPT/PPTX/DOC/DOCX/PDF，最大 100MB，最多 300 页
- 视频：MP4，最大 500MB，3 秒~30 分钟，比例 1:2.4~2.4:1，最多 1 个

**X / Twitter**
- 图片：JPG/PNG/GIF/WebP，最大 5MB，最多 4 张
- 视频：MP4/MOV，最大 1280×1024px，0.5~140 秒（longVideo 支持 10+ 分钟），比例 1:3~3:1，最多 4 个；避免使用 Dropbox 或 S3 签名 URL

**Bluesky**
- 图片：JPG/GIF/PNG，最大 1MB，最多 4 张
- 视频：MP4，最大 1GB，1 秒~3 分钟，比例 1:3~3:1，最多 1 个

**Pinterest**
- 图片：BMP/JPEG/PNG/TIFF/GIF/WebP，最大 20MB，推荐 1000×1500（2:3），最多 1 张
- 视频：MP4/MOV/M4V，最大 1GB，4 秒~15 分钟，最多 1 个

**Reddit**
- 图片：JPG/PNG/GIF/WebP，最大 10MB，最多 1 张
- 视频：❌ 不支持

**Snapchat**
- 图片：JPEG/PNG，最大 20MB，推荐 1080×1920
- 视频：MP4，最大 500MB，5~60 秒，推荐 540×960，9:16，最多 1 个

**Telegram**
- 图片：JPG/PNG/GIF/WebP，最大 5MB，宽高之和 ≤10,000，比例 ≤20:1，最多 1 张，文字 ≤1,024 字符
- 视频：最大 20MB，文字 ≤1,024 字符，最多 1 个

**Threads**
- 最多 20 张图片/视频混合；不支持 API 删除（需在 App 内手动删除）

**YouTube**
- 视频：MP4/MOV，最大 4GB，推荐 16:9，H.264+AAC，最多 1 个

**Google Business Profile**
- 图片：最多 1 张

**通用规则**
- 所有媒体 URL 必须以 https:// 开头
- 视频 URL 必须以已知扩展名结尾；否则加 `isVideo: true`
- 文件 > 50MB：使用 `scheduleDate` 异步处理

### 定时设置

推荐发帖时间参考：

| 平台 | 推荐时间 |
|------|----------|
| TikTok | 工作日 7-9am, 12-3pm, 7-9pm |
| Instagram | 周二至周五 9-11am, 1-3pm |
| Facebook | 周三 11am-1pm, 周四 1-3pm |
| LinkedIn | 周二至周四 8-10am, 12pm |
| X/Twitter | 周一至周五 8am, 12pm, 5pm |
| YouTube | 周五至周日 2-4pm |

### 最终确认

**调用 API 之前必须展示完整摘要并等待用户确认：**

```
📋 发帖确认单
─────────────────
内容：[最终内容]
平台：[选择的平台]
媒体：[有/无]
发布时间：[立即 / 具体时间]
─────────────────
确认发布？
```

确认后调用 `publish_post`：

```json
{
  "storyclaw_api_key": "<key>",
  "action": "publish_post",
  "post": "<内容>",
  "platforms": ["tiktok", "instagram"],
  "mediaUrls": ["<url>"],
  "scheduleDate": "<ISO8601，立即发布则省略>"
}
```

---

## 功能二：查询帖子列表

```json
{ "storyclaw_api_key": "<key>", "action": "get_posts", "platform": "<platform>" }
```

整理展示帖子内容摘要、发布时间。

---

## 功能三：查看帖子详情

若不知道 post_id，先调用 `get_posts` 展示列表让用户选择。

```json
{ "storyclaw_api_key": "<key>", "action": "get_post", "post_id": "<post_id>" }
```

---

## 功能四：帖子数据分析

**方式 A — StoryClaw Post ID：**
```json
{ "storyclaw_api_key": "<key>", "action": "get_analytics_post", "post_id": "<id>", "platforms": ["tiktok"] }
```

**方式 B — 平台原生 ID：**
```json
{ "storyclaw_api_key": "<key>", "action": "get_analytics_post_by_social_id", "social_post_id": "<id>", "platforms": ["instagram"] }
```

按平台分组展示：点赞、浏览、评论、分享、曝光、触达等数据。

---

## 功能五：账号概况分析

```json
{ "storyclaw_api_key": "<key>", "action": "get_analytics_social", "platforms": ["instagram", "tiktok"] }
```

展示粉丝数、关注数、帖子数、曝光量等账号级数据。

---

## 功能六：删除帖子

先展示帖子列表供用户选择，再二次确认后删除：

```json
{ "storyclaw_api_key": "<key>", "action": "delete_post", "post_id": "<post_id>" }
```

---

## 错误处理

| 错误 | 提示 |
|------|------|
| 401 Invalid API key | "API Key 无效，请重新从个人中心复制" |
| 400 No social profile | "社交账号尚未绑定，请先在 StoryClaw.com 个人中心完成绑定" |
| 500 Internal server error | "服务暂时不可用，请稍后重试" |

---

## 重要原则

- **绝对不在未获得用户明确确认前调用发帖或删除接口**
- API Key 脱敏显示（`sk_****...`）
- 平台选项始终基于 `get_social_status` 实际返回
- 用户随时可以返回修改任何步骤的设置
