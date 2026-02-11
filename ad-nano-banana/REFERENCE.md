# 参数参考文档

完整的命令行参数说明和选项。

## 参数分类

### 必需参数

| 参数 | 类型 | 说明 | 约束 |
|-----|------|------|------|
| `--prompt` | string | 图像描述提示词 | ≤ 20000 字符 |

### 图像参数

| 参数 | 类型 | 默认值 | 说明 | 选项 |
|-----|------|--------|------|------|
| `--aspect-ratio` | string | 1:1 | 图像比例 | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, auto |
| `--resolution` | string | 2K | 图像清晰度 | 1K, 2K, 4K |
| `--output-format` | string | png | 输出格式 | png, jpg |
| `--image-input` | string[] | [] | 参考图像URL | ≤ 8 张 |

### 下载参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `--download` | flag | false | 自动下载生成的图像到本地 |
| `--output-dir` | string | ~/Downloads | 下载保存目录 |

### 任务管理参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `--no-wait` | flag | false | 不等待任务完成,立即返回 |
| `--max-wait` | integer | 300 | 最大等待时间(秒) |
| `--poll-interval` | integer | 5 | 轮询间隔(秒) |

### 输出控制参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `--json` | flag | false | 以JSON格式输出 |
| `--query` | flag | false | 查询已存在的任务(需配合 --task-id) |
| `--task-id` | string | - | 要查询的任务ID(仅在 --query 模式下使用) |
| `--api-key` | string | - | API密钥(也可通过环境变量 KIE_API_KEY 设置) |

## 图像比例详解

### 常用比例

| 比例 | 用途 | 推荐场景 |
|-----|------|---------|
| **1:1** | 正方形 | 社交媒体头像、Instagram帖子、Logo |
| **16:9** | 横屏 | 电脑壁纸、YouTube封面、横屏视频 |
| **9:16** | 竖屏 | 手机壁纸、短视频、Instagram故事 |
| **4:3** | 传统屏幕 | 照片打印、演示文稿 |
| **21:9** | 超宽屏 | 电影风格、超宽显示器壁纸 |

### 特殊比例

| 比例 | 用途 | 推荐场景 |
|-----|------|---------|
| **2:3** | 照片竖版 | 肖像照片、杂志封面 |
| **3:2** | 照片横版 | 风景照片、相机标准比例 |
| **4:5** | Instagram竖版 | Instagram竖版帖子 |
| **5:4** | 中画幅相机 | 专业摄影、艺术照片 |
| **auto** | 自动 | 让AI根据内容自动选择 |

## 清晰度详解

| 清晰度 | 分辨率范围 | 适用场景 | 生成时间 | 建议 |
|--------|-----------|---------|----------|------|
| **1K** | ~1000px | 快速预览、草图 | ~15-30秒 | 测试提示词 |
| **2K** | ~2000px | 社交媒体、网页 | ~30-60秒 | 日常使用(推荐) |
| **4K** | ~4000px | 打印、专业作品 | ~60-120秒 | 最终作品 |

**选择建议:**
- 测试阶段: 使用 1K 快速验证效果
- 日常使用: 使用 2K 平衡质量和速度
- 高质量输出: 使用 4K 用于打印或专业展示

## 输出格式详解

| 格式 | 特点 | 文件大小 | 推荐场景 |
|-----|------|---------|---------|
| **png** | 无损压缩,支持透明 | 较大 | 需要透明背景、高质量要求 |
| **jpg** | 有损压缩,不支持透明 | 较小 | 照片、社交媒体分享 |

## 参考图像使用

### 数量限制

- **最少**: 0 张(文生图模式)
- **最多**: 8 张(多图融合模式)

### URL 要求

- 必须是可公开访问的 HTTP(S) URL
- 支持的格式: JPG, PNG, WebP
- 建议单个图像 < 30MB

### 使用场景

**1张参考图 (图生图)**:
- 风格转换
- 图像优化
- 背景移除
- 色彩调整

**2-8张参考图 (多图融合)**:
- 风格混合
- 元素组合
- 创意拼贴
- 概念融合

## 任务管理模式

### 同步模式 (默认)

**行为**: 等待任务完成后返回结果

**适用场景**:
- 单次生成
- 需要立即查看结果
- 交互式使用

**示例**:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "描述"
```

### 异步模式 (--no-wait)

**行为**: 立即返回 taskId,不等待完成

**适用场景**:
- 批量生成
- 长时间任务(4K图像)
- 后台执行

**示例**:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "描述" --no-wait
# 输出: TaskID: abc123

# 稍后查询
python3 scripts/kie_nano_banana_api.py --query --task-id abc123
```

### 超时控制

**默认值**:
- `--max-wait`: 300秒 (5分钟)
- `--poll-interval`: 5秒

**调整建议**:
- 1K图像: 60秒足够
- 2K图像: 120秒足够
- 4K图像: 300-600秒
- 多图融合: 300-600秒

**示例**:
```bash
# 4K图像,增加等待时间
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --resolution 4K \
  --max-wait 600
```

## 下载功能详解

### 文件命名

**单张图像**:
```
nano_banana_YYYYMMDD_HHMMSS.{format}
示例: nano_banana_20260211_143025.png
```

**多张图像**:
```
nano_banana_YYYYMMDD_HHMMSS_{N}.{format}
示例: nano_banana_20260211_143025_1.png
     nano_banana_20260211_143025_2.png
```

### 下载目录

**默认目录**:
- macOS/Linux: `~/Downloads/`
- Windows: `%USERPROFILE%\Downloads\`

**自定义目录**:
```bash
# 下载到桌面
--output-dir "~/Desktop"

# 下载到项目目录
--output-dir "./images"

# 下载到绝对路径
--output-dir "/path/to/directory"
```

### 下载特性

✅ **不依赖系统环境** - 使用 Python 内置 urllib 模块
✅ **自动创建目录** - 目录不存在时自动创建
✅ **文件冲突处理** - 同名文件自动添加序号
✅ **断点续传** - 下载失败时显示详细错误
✅ **跨平台支持** - macOS/Linux/Windows 统一体验

## 输出格式

### 文本格式 (默认)

```
============================================================
图像生成完成
============================================================
提示词: 一只可爱的猫咪
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/cat.png

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_143025.png
============================================================
```

### JSON 格式 (--json)

```json
{
  "prompt": "一只可爱的猫咪",
  "imageUrls": [
    "https://static.aiquickdraw.com/tools/example/cat.png"
  ],
  "imageCount": 1,
  "downloadedFiles": [
    "/Users/username/Downloads/nano_banana_20260211_143025.png"
  ]
}
```

## 环境变量

### KIE_API_KEY

**设置方法**:

**Bash/Zsh (macOS/Linux)**:
```bash
export KIE_API_KEY="your-api-key-here"

# 永久设置 (添加到 ~/.bashrc 或 ~/.zshrc)
echo 'export KIE_API_KEY="your-api-key-here"' >> ~/.bashrc
```

**Windows CMD**:
```cmd
set KIE_API_KEY=your-api-key-here
```

**Windows PowerShell**:
```powershell
$env:KIE_API_KEY="your-api-key-here"
```

**验证设置**:
```bash
echo $KIE_API_KEY  # Unix
echo %KIE_API_KEY%  # Windows CMD
echo $env:KIE_API_KEY  # Windows PowerShell
```

## 组合示例

### 最小命令

```bash
python3 scripts/kie_nano_banana_api.py --prompt "猫咪"
```

### 完整参数

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "详细的图像描述" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --output-format jpg \
  --image-input "https://example.com/ref.jpg" \
  --download \
  --output-dir "~/Desktop/images" \
  --max-wait 600 \
  --poll-interval 10 \
  --json
```

### 异步 + 查询

```bash
# 创建任务
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --no-wait

# 查询结果
python3 scripts/kie_nano_banana_api.py \
  --query \
  --task-id "abc123" \
  --download \
  --json
```

## 帮助信息

查看完整的命令行帮助:

```bash
python3 scripts/kie_nano_banana_api.py --help
```
