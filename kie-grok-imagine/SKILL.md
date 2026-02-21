---
name: generating-videos-with-grok-imagine
description: 使用 grok-imagine 模型生成视频。支持文生视频和图生视频。当用户指定使用 grok-imagine、grok 模型生成视频时使用此技能。
---

# grok-imagine 视频生成

使用 kie.ai 提供的 grok-imagine 模型生成视频。支持文生视频 (text-to-video) 和图生视频 (image-to-video) 两种模式。

## 支持的模式

| 模式 | 说明 |
|------|------|
| text-to-video | 根据文本描述生成视频 |
| image-to-video | 根据参考图片 + 可选文本生成视频 |

## 前置条件

在技能目录下创建 `.env` 文件并配置 API Key（参考 `.env.example`）：

```
KIE_API_KEY=your_api_key_here
```

API Key 获取地址：https://kie.ai/api-key

## 工作流

### Step 1: 确认生成模式

如果调用方（总路由或用户）已明确模式，直接跳到对应分支。

否则使用 `AskUserQuestion` 询问：

**问题**: "请选择视频生成模式"
- **文生视频 (Text-to-Video)**: 通过文字描述生成视频
- **图生视频 (Image-to-Video)**: 上传参考图片生成视频

---

### 分支 A: 文生视频 (Text-to-Video)

#### 参数收集

| 参数 | 必填 | 默认值 | 可选值 | 说明 |
|------|------|--------|--------|------|
| prompt | ✅ | - | 最多 5000 字符 | 视频内容描述 |
| aspect_ratio | ❌ | 16:9 | 2:3, 3:2, 1:1, 9:16, 16:9 | 画面比例 |
| duration | ❌ | 6 | 6, 10 | 视频时长（秒） |
| resolution | ❌ | 720p | 480p, 720p | 清晰度 |

#### 参数确认

收集参数后，向用户展示参数摘要并确认：

```
即将生成视频：
- 模型: grok-imagine (文生视频)
- 提示词: [前50字]...
- 画面比例: 16:9
- 时长: 6s
- 清晰度: 720p

确认生成？
```

用户确认后执行脚本。

#### 执行脚本

```bash
python3 generating-videos-with-grok-imagine/scripts/text_to_video.py \
    --prompt "用户的提示词" \
    --aspect_ratio "16:9" \
    --duration "6" \
    --resolution "720p"
```

脚本会自动轮询任务状态（每 10 秒查询一次，最长等待 10 分钟）。

---

### 分支 B: 图生视频 (Image-to-Video)

#### 获取参考图片

要求用户提供参考图片。支持两种输入方式：
- **本地文件路径**: 如 `/path/to/image.png`（脚本会自动上传）
- **远程 URL**: 如 `https://example.com/image.png`（直接使用）

图片要求：
- 格式：PNG、JPG、WebP
- 大小：不超过 10MB

#### 参数收集

| 参数 | 必填 | 默认值 | 可选值 | 说明 |
|------|------|--------|--------|------|
| image | ✅ | - | 文件路径或 URL | 参考图片 |
| prompt | ❌ | "" | 最多 5000 字符 | 视频动作描述 |
| duration | ❌ | 6 | 6, 10 | 视频时长（秒） |
| resolution | ❌ | 720p | 480p, 720p | 清晰度 |

#### 参数确认

```
即将生成视频：
- 模型: grok-imagine (图生视频)
- 参考图片: [文件名或URL]
- 提示词: [前50字]...（如有）
- 时长: 6s
- 清晰度: 720p

确认生成？
```

#### 执行脚本

```bash
python3 generating-videos-with-grok-imagine/scripts/image_to_video.py \
    --image "/path/to/image.png" \
    --prompt "视频动作描述" \
    --duration "6" \
    --resolution "720p"
```

脚本会自动处理本地图片上传和任务轮询。

---

## 结果处理

脚本成功后会输出 JSON 到 stdout：

```json
{
  "success": true,
  "taskId": "xxx",
  "model": "grok-imagine/text-to-video",
  "videoUrls": ["https://file.aiquickdraw.com/.../video.mp4"],
  "costTimeMs": 12345,
  "downloadsDir": "/Users/xxx/Downloads"
}
```

### 展示结果

1. 展示生成耗时
2. **完整输出每个视频的下载链接**（不要截断或缩短 URL），用户可以直接复制到浏览器打开下载
3. 询问用户是否要通过命令行下载到本地

### 下载视频

默认下载到系统 **"下载"文件夹**（`~/Downloads/`）。文件名格式：`video_<taskId前8位>_<序号>.mp4`

```bash
curl -L -o ~/Downloads/video_<taskId前8位>_1.mp4 "完整视频URL"
```

如果用户指定了其他路径或文件名，按用户要求保存。

## 错误处理

| 错误码 | 说明 | 建议 |
|--------|------|------|
| 401 | 认证失败 | 检查 KIE_API_KEY 是否正确 |
| 402 | 余额不足 | 前往 kie.ai 充值 |
| 422 | 参数校验失败 | 检查参数值是否在允许范围内 |
| 429 | 请求频率限制 | 等待后重试 |
| 500 | 服务器内部错误 | 稍后重试 |
