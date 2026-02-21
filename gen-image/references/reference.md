# 参数参考文档

完整的命令行参数说明。

## 参数速查

| 参数 | 类型 | 默认值 | 说明 | 选项/约束 |
|-----|------|--------|------|----------|
| `--prompt` | string | **必需** | 图像描述提示词 | ≤ 20000 字符 |
| `--aspect-ratio` | string | 1:1 | 图像比例 | 见下表 |
| `--resolution` | string | 2K | 图像清晰度 | 1K, 2K, 4K |
| `--output-format` | string | png | 输出格式 | png, jpg |
| `--image-input` | string[] | [] | 参考图像 URL | ≤ 8 张，需可公开访问 |
| `--download` | flag | false | 自动下载到本地 | - |
| `--output-dir` | string | ~/Downloads | 下载目录 | - |
| `--no-wait` | flag | false | 异步模式，立即返回 taskId | - |
| `--max-wait` | integer | 300 | 最大等待时间(秒) | - |
| `--poll-interval` | integer | 5 | 轮询间隔(秒) | - |
| `--query` | flag | false | 查询已有任务 | 需配合 `--task-id` |
| `--task-id` | string | - | 要查询的任务 ID | 仅 `--query` 模式 |
| `--api-key` | string | - | API 密钥（优先级高于环境变量） | - |
| `--json` | flag | false | JSON 格式输出 | - |

---

## 图像比例详解

| 比例 | 用途 | 推荐场景 |
|-----|------|---------|
| **1:1** | 正方形 | 社交媒体头像、Instagram帖子、Logo |
| **16:9** | 横屏 | 电脑壁纸、YouTube封面 |
| **9:16** | 竖屏 | 手机壁纸、短视频、Instagram故事 |
| **4:3** | 传统屏幕 | 照片打印、演示文稿 |
| **21:9** | 超宽屏 | 电影风格、超宽显示器壁纸 |
| **2:3** | 照片竖版 | 肖像、杂志封面 |
| **3:2** | 照片横版 | 风景、相机标准比例 |
| **4:5** | Instagram竖版 | Instagram竖版帖子 |
| **5:4** | 中画幅 | 专业摄影、艺术照片 |
| **auto** | 自动 | 图生图时保持原图比例 |

---

## 清晰度详解

| 清晰度 | 生成时间 | 适用场景 |
|--------|---------|---------|
| **1K** | ~15-30秒 | 快速测试提示词效果 |
| **2K** | ~30-60秒 | 日常使用（推荐） |
| **4K** | ~60-120秒 | 打印、最终高清作品 |

**4K 多图融合**可能需要 120-300 秒，建议配合 `--no-wait` 使用。

---

## 输出格式

| 格式 | 特点 | 推荐场景 |
|-----|------|---------|
| **png** | 无损，支持透明 | 需要高质量或透明背景 |
| **jpg** | 有损，文件更小 | 照片、社交媒体分享 |

---

## 参考图像要求

- 必须是可公开访问的 HTTP(S) URL
- 支持格式：JPG, PNG, WebP
- 建议单张 < 30MB
- 最多 8 张

---

## 任务管理

### 同步模式（默认）

等待任务完成后返回结果，适合单次交互式生成。

### 异步模式（--no-wait）

立即返回 taskId，适合批量生成或长时间任务（如 4K）。

```bash
# 创建任务
python3 scripts/kie_nano_banana_api.py --prompt "描述" --resolution 4K --no-wait
# 输出: TaskID: abc123

# 稍后查询
python3 scripts/kie_nano_banana_api.py --query --task-id abc123 --download
```

### 超时建议

| 清晰度 | 推荐 --max-wait |
|--------|----------------|
| 1K | 60 秒 |
| 2K | 120 秒 |
| 4K / 多图融合 | 300-600 秒 |

---

## 下载功能

**文件命名规则:**
- 单张: `nano_banana_YYYYMMDD_HHMMSS.{format}`
- 多张: `nano_banana_YYYYMMDD_HHMMSS_1.{format}`、`..._2.{format}`

**注意:** 图像 URL 有效期有限（通常 24-72 小时），建议立即使用 `--download` 下载。

---

## API 密钥配置优先级

```
命令行 --api-key  >  环境变量 GIGGLE_API_KEY  >  .env 文件
```

**推荐方式（.env 文件）:**
```bash
cp env.example .env
# 编辑 .env，填入: GIGGLE_API_KEY=your-api-key-here
```

**临时方式（环境变量）:**
```bash
export GIGGLE_API_KEY="your-api-key-here"
```

获取密钥: https://giggle.pro/api-key

---

## 输出格式说明

### 文本格式（默认）

```
============================================================
图像生成完成
============================================================
提示词: 一只可爱的猫咪
生成数量: 1 张

图像 #1: https://...

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_143025.png
============================================================
```

### JSON 格式（--json）

```json
{
  "prompt": "一只可爱的猫咪",
  "imageUrls": ["https://..."],
  "imageCount": 1,
  "downloadedFiles": ["/Users/username/Downloads/nano_banana_20260211_143025.png"]
}
```

进度信息输出到 stderr，JSON 结果输出到 stdout，适合脚本集成：

```bash
result=$(python3 scripts/kie_nano_banana_api.py --prompt "描述" --json 2>/dev/null)
image_url=$(echo "$result" | jq -r '.imageUrls[0]')
```
