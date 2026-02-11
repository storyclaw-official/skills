---
name: ad-nano-banana
description: 使用 Nano Banana Pro 模型(通过 kie.ai 平台)生成 AI 图像。支持文生图、图生图和多图融合(最多 8 张)。当用户需要创建、生成图像或图片时使用此技能。支持场景：(1) 根据文本描述生成图像，(2) 使用参考图生成图像，(3) 多图融合创意生成，(4) 自定义图像比例和清晰度。触发关键词：生成图像、创建图片、画一张图、AI 作画、图像生成、图片创作、nano-banana。
---

# AD Nano Banana

使用 Nano Banana Pro 模型(通过 kie.ai 平台)生成 AI 图像。支持从简单的文本描述到多图融合的高级创作。

## 使用引导流程

**当用户请求"生成一张图片"或类似模糊请求时,按以下流程引导:**

### 步骤 1: 检查图像比例

使用 AskUserQuestion 工具询问:

```
问题: "您需要什么比例的图像?"
选项:
- "1:1 正方形 (社交媒体头像、Instagram帖子)"
- "16:9 横屏 (电脑壁纸、YouTube封面)"
- "9:16 竖屏 (手机壁纸、短视频)"
- "其他比例"
```

**如果用户选择"其他比例",继续询问:**
```
问题: "请选择具体比例:"
选项:
- "2:3 (照片竖版)"
- "3:2 (照片横版)"
- "4:3 (传统屏幕)"
- "21:9 (超宽屏)"
- "auto (自动)"
```

### 步骤 2: 检查清晰度

使用 AskUserQuestion 工具询问:

```
问题: "您需要什么清晰度?"
选项:
- "2K (推荐) - 平衡质量和速度"
- "4K - 最高质量,适合打印"
- "1K - 快速预览"
```

### 步骤 3: 收集提示词

询问用户:
```
问题: "请描述您想要生成的图像内容:"
```

**提示词最佳实践提示:**
- 建议用户提供详细描述,包括:
  - 主体内容(如"一只橘色的猫")
  - 场景/背景(如"坐在窗边")
  - 风格/氛围(如"水彩画风格,温暖的光线")
  - 细节要求(如"高细节,专业摄影")

### 步骤 4: 检查是否使用参考图

使用 AskUserQuestion 工具询问:

```
问题: "是否需要使用参考图像?"
选项:
- "不需要,只根据文字描述生成"
- "是,我有1张参考图(图生图)"
- "是,我有多张参考图(多图融合,最多8张)"
```

#### 情况 A: 不需要参考图 → **文生图模式**

直接执行生成命令:

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "用户的提示词" \
  --aspect-ratio "16:9" \
  --resolution "2K"
```

#### 情况 B: 需要 1 张参考图 → **图生图模式**

收集参考图信息:
1. 询问用户提供图像URL
2. 验证URL可访问性(可选)
3. 执行生成命令:

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "用户的提示词" \
  --image-input "https://example.com/reference.jpg" \
  --aspect-ratio "16:9" \
  --resolution "2K"
```

**图生图提示词建议:**
- 描述想要的转换效果,如:
  - "转为油画风格"
  - "转为卡通风格,保留主体"
  - "移除背景,保留人物"
  - "增强色彩,专业摄影风格"

#### 情况 C: 需要多张参考图 → **多图融合模式**

收集参考图信息:
1. 询问用户需要几张参考图(最多8张)
2. 逐一收集每张图的URL
3. 执行生成命令:

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "用户的提示词" \
  --image-input "url1" "url2" "url3" \
  --aspect-ratio "16:9" \
  --resolution "2K"
```

**多图融合提示词建议:**
- 描述融合效果,如:
  - "融合这些图像的风格"
  - "结合第一张的构图和第二张的色彩"
  - "将这些元素组合成一个场景"

### 步骤 5: 执行并询问下载

生成完成后,**主动询问**用户:

```
问题: "图像已生成完成!是否需要下载图像到本地?"
选项:
- "是,下载到下载文件夹"
- "不用,我只需要查看链接"
```

**如果用户选择下载,按以下步骤操作:**

1. **确定下载目录**(根据用户操作系统):
   - **macOS/Linux**: `~/Downloads/`
   - **Windows**: `%USERPROFILE%\Downloads\` 或 `C:\Users\用户名\Downloads\`

2. **生成文件名**:
   - 格式: `nano_banana_YYYYMMDD_HHMMSS.png` (或 .jpg,根据输出格式)
   - 示例: `nano_banana_20260211_143025.png`
   - 如果有多张图像: `nano_banana_20260211_143025_1.png`, `nano_banana_20260211_143025_2.png`

3. **执行下载**:
   ```bash
   python3 scripts/kie_nano_banana_api.py \
     --download \
     --image-urls "url1" "url2" \
     --output-dir "~/Downloads"
   ```

   或直接在脚本中使用 Python 的 urllib 下载图像:
   ```python
   import urllib.request
   from pathlib import Path

   # 确定下载目录
   download_dir = Path.home() / "Downloads"

   # 下载图像
   for i, url in enumerate(image_urls, 1):
       filename = f"nano_banana_{timestamp}_{i}.png"
       filepath = download_dir / filename
       urllib.request.urlretrieve(url, filepath)
       print(f"✓ 图像已下载: {filepath}")
   ```

4. **告知用户下载结果**:
   - 显示下载的文件路径
   - 提示下载完成

**重要提示:**
- 图像URL有效期有限,建议及时下载
- 下载使用 Python 内置的 urllib 模块,不依赖系统环境
- 自动处理文件名冲突(如有同名文件则添加序号)

## 输出信息说明

脚本输出包含以下 3 个关键字段:

| 字段 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| prompt | string | 图像描述提示词 | "一只可爱的猫咪" |
| imageUrls | array | 生成的图像URL数组 | ["https://..."] |
| imageCount | integer | 生成的图像数量 | 1 |

## Quick Start

### 1. 环境配置

**设置 API 密钥:**
```bash
export KIE_API_KEY="your-api-key-here"
```

获取 API 密钥: https://kie.ai/api-key

**验证配置:**
```bash
echo $KIE_API_KEY  # 应显示你的 API 密钥
```

### 2. 基本用法

最简单的生成方式 - 只需提供描述:

```bash
python3 scripts/kie_nano_banana_api.py --prompt "一只可爱的猫咪"
```

### 3. 下载图像

生成并直接下载图像:

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "一只可爱的猫咪" \
  --download
```

## 生成模式详解

### 模式 1: 文生图(Text-to-Image)

根据文本描述生成全新图像。

**使用场景:**
- 创意概念可视化
- 艺术创作
- 内容创作(博客配图、社交媒体)

**命令示例:**
```bash
# 基础文生图
python3 scripts/kie_nano_banana_api.py \
  --prompt "一只坐在窗边的橘猫,温暖的阳光洒进来"

# 指定比例和清晰度
python3 scripts/kie_nano_banana_api.py \
  --prompt "未来主义城市,赛博朋克风格,霓虹灯,夜景" \
  --aspect-ratio 16:9 \
  --resolution 4K

# 生成并下载
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简logo设计,现代感,蓝色系" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download
```

### 模式 2: 图生图(Image-to-Image)

使用一张参考图像进行转换或风格迁移。

**使用场景:**
- 风格转换
- 图像优化
- 创意改造

**命令示例:**
```bash
# 风格转换
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为油画风格,保留原始构图" \
  --image-input "https://example.com/photo.jpg" \
  --resolution 2K \
  --download

# 图像优化
python3 scripts/kie_nano_banana_api.py \
  --prompt "增强色彩,专业摄影风格,高细节" \
  --image-input "https://example.com/raw.jpg" \
  --resolution 4K \
  --download
```

### 模式 3: 多图融合(Multi-Image Fusion)

融合多张图像(最多8张)创造新的视觉效果。

**使用场景:**
- 创意拼贴
- 风格混合
- 元素组合

**命令示例:**
```bash
# 融合两张图像的风格
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合这两张图像的风格,创造新的艺术作品" \
  --image-input "https://example.com/style1.jpg" "https://example.com/style2.jpg" \
  --aspect-ratio 16:9 \
  --download

# 组合多个元素
python3 scripts/kie_nano_banana_api.py \
  --prompt "将这些元素组合成一个和谐的场景" \
  --image-input "url1" "url2" "url3" "url4" \
  --resolution 4K \
  --download
```

## 参数说明

### 必需参数

| 参数 | 类型 | 说明 | 约束 |
|-----|------|------|------|
| --prompt | string | 图像描述提示词 | ≤ 20000 字符 |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 | 选项 |
|-----|------|--------|------|------|
| --aspect-ratio | string | 1:1 | 图像比例 | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, auto |
| --resolution | string | 2K | 图像清晰度 | 1K, 2K, 4K |
| --output-format | string | png | 输出格式 | png, jpg |
| --image-input | string[] | [] | 参考图像URL | ≤ 8 张 |

### 下载参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| --download | flag | false | 自动下载生成的图像到本地 |
| --output-dir | string | ~/Downloads | 下载保存目录 |

### 任务管理参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| --no-wait | flag | false | 不等待任务完成,立即返回 |
| --max-wait | integer | 300 | 最大等待时间(秒) |
| --poll-interval | integer | 5 | 轮询间隔(秒) |

### 输出控制参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| --json | flag | false | 以JSON格式输出 |

## 完整使用示例

### 示例 1: 社交媒体配图(生成并下载)

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "现代简约风格的咖啡杯,温暖的早晨光线,专业摄影" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download
```

### 示例 2: 电脑壁纸

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "宁静的山水风景,日落时分,高细节,4K质量" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download
```

### 示例 3: 手机壁纸

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "抽象艺术,渐变色彩,现代简约" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download
```

### 示例 4: 图像风格转换并下载

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为水彩画风格,柔和的色彩,艺术感" \
  --image-input "https://example.com/original.jpg" \
  --resolution 2K \
  --download
```

### 示例 5: 多图创意融合

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合这些图像的艺术风格,创造独特的视觉效果" \
  --image-input "https://example.com/img1.jpg" "https://example.com/img2.jpg" "https://example.com/img3.jpg" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download \
  --output-dir "~/Desktop"
```

### 示例 6: 仅获取链接(不下载)

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "测试图像生成" \
  --json
```

## 任务管理

### 同步模式(默认)

默认情况下,脚本会等待任务完成后返回结果。

```bash
python3 scripts/kie_nano_banana_api.py --prompt "描述"
```

**流程:**
1. 创建任务 → 获取 taskId
2. 轮询任务状态(每5秒查询一次)
3. 任务完成 → 返回图像URL
4. 任务失败或超时 → 显示错误信息

### 异步模式

使用 `--no-wait` 立即返回 taskId,不等待完成。

```bash
python3 scripts/kie_nano_banana_api.py --prompt "描述" --no-wait
```

**输出:**
```
✓ 任务创建成功! TaskID: abc123xyz
任务ID: abc123xyz
可使用以下命令查询: python scripts/kie_nano_banana_api.py --query --task-id abc123xyz
```

### 查询任务

使用 taskId 查询已创建任务的状态和结果。

```bash
python3 scripts/kie_nano_banana_api.py --query --task-id "abc123xyz"
```

查询完成后可以下载:
```bash
python3 scripts/kie_nano_banana_api.py --query --task-id "abc123xyz" --download
```

## 图像下载功能

### 自动下载

使用 `--download` 参数在生成完成后自动下载图像:

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --download
```

**下载流程:**
1. 生成图像并获取URL
2. 使用 Python urllib 下载图像文件
3. 保存到指定目录(默认 ~/Downloads)
4. 显示下载结果

### 自定义下载目录

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --download \
  --output-dir "~/Desktop"
```

### 文件命名规则

- 格式: `nano_banana_YYYYMMDD_HHMMSS.png`
- 多图: `nano_banana_20260211_143025_1.png`, `nano_banana_20260211_143025_2.png`
- 自动处理文件名冲突

### 下载特点

✅ **不依赖系统环境** - 使用 Python 内置的 urllib 模块
✅ **自动创建目录** - 如果下载目录不存在则自动创建
✅ **进度提示** - 显示下载进度和结果
✅ **错误处理** - 下载失败时显示详细错误信息
✅ **跨平台支持** - 支持 macOS/Linux/Windows

## 输出格式

### 文本格式(默认)

```
============================================================
图像生成完成
============================================================
提示词: 一只可爱的猫咪
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/cat.png
============================================================
```

### 带下载的输出

```
============================================================
图像生成完成
============================================================
提示词: 一只可爱的猫咪
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/cat.png

下载图像...
✓ 图像已下载: /Users/username/Downloads/nano_banana_20260211_143025.png
============================================================
```

### JSON 格式

使用 `--json` 参数输出JSON格式:

```bash
python3 scripts/kie_nano_banana_api.py --prompt "描述" --json
```

**输出:**
```json
{
  "prompt": "一只可爱的猫咪",
  "imageUrls": [
    "https://static.aiquickdraw.com/tools/example/cat.png"
  ],
  "imageCount": 1
}
```

## 错误处理

### 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| "错误: 未设置API密钥" | 未配置 KIE_API_KEY | 设置环境变量: `export KIE_API_KEY="your-key"` 或使用 `--api-key` 参数 |
| "prompt 长度不能超过 20000 字符" | 提示词过长 | 精简描述,保留关键信息 |
| "最多支持 8 张参考图像" | 参考图数量超限 | 减少参考图数量至8张以内 |
| "任务失败: ..." | API 任务执行失败 | 检查 failMsg 错误信息,调整参数后重试 |
| "等待超时 (300秒)" | 任务生成时间过长 | 增加 `--max-wait` 时间或使用 `--no-wait` 异步模式 |
| "下载失败: ..." | 图像URL无效或网络问题 | 检查网络连接,重新下载或手动下载 |

## 工作流程建议

### 快速原型

**目标:** 快速验证想法和概念

1. 使用默认参数(1:1, 2K)快速生成
2. 使用 `--download` 直接保存到本地
3. 多次迭代,调整提示词

**示例流程:**
```bash
# 第一次尝试
python3 scripts/kie_nano_banana_api.py --prompt "猫咪" --download

# 增加细节
python3 scripts/kie_nano_banana_api.py --prompt "一只橘色的猫咪" --download

# 添加场景和风格
python3 scripts/kie_nano_banana_api.py \
  --prompt "一只橘色的猫咪,坐在窗边,温暖的阳光,水彩画风格" \
  --download
```

### 精细创作

**目标:** 生成高质量的最终作品

1. 准备详细的提示词
2. 选择合适的比例和4K清晰度
3. 使用 `--download` 保存到指定目录

**示例流程:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "宁静的山谷风景,清晨的薄雾,金色的阳光穿过树林,高细节风景摄影,专业色彩" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download \
  --output-dir "~/Desktop/作品集"
```

### 批量生成

**目标:** 一次性生成多个图像变体

1. 使用异步模式快速创建多个任务
2. 保存所有 taskId
3. 批量查询并下载

**示例流程:**
```bash
# 创建多个任务
python3 scripts/kie_nano_banana_api.py --prompt "版本1描述" --no-wait
# 输出: TaskID: task1

python3 scripts/kie_nano_banana_api.py --prompt "版本2描述" --no-wait
# 输出: TaskID: task2

# 稍后批量下载
python3 scripts/kie_nano_banana_api.py --query --task-id task1 --download
python3 scripts/kie_nano_banana_api.py --query --task-id task2 --download
```

## 快速预设

针对常见使用场景的参数预设:

### 社交媒体

```bash
# Instagram 帖子 (1:1) + 自动下载
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download

# Instagram 故事 (9:16) + 自动下载
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download
```

### 屏幕壁纸

```bash
# 电脑横屏壁纸 (16:9, 4K)
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download

# 手机竖屏壁纸 (9:16, 2K)
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download
```

## 提示词最佳实践

### 好的提示词示例

**详细且具体:**
```
"一只橘色的猫咪坐在窗边,温暖的阳光从窗外洒进来,柔和的光影,水彩画风格,高细节"
```

**包含风格指导:**
```
"未来主义城市景观,赛博朋克风格,霓虹灯反射在湿润的街道上,夜景,高细节,专业摄影"
```

**明确主体和场景:**
```
"现代简约风格的咖啡杯,木质桌面,散景背景,温暖的早晨光线,商业产品摄影"
```

### 避免的提示词

**太简短:**
```
❌ "猫"
✓ "一只可爱的猫咪"
```

**过于模糊:**
```
❌ "一张很好看的图片"
✓ "宁静的山水风景,日落时分,温暖的色调"
```

## 使用技巧

1. **及时下载** - 图像URL有效期有限,生成后立即使用 `--download` 下载
2. **比例选择** - 根据最终用途选择比例(1:1社交媒体,16:9横屏,9:16竖屏)
3. **清晰度策略** - 快速预览用1K,最终作品用4K
4. **批量下载** - 使用异步模式生成多个版本,再批量下载
5. **自定义目录** - 使用 `--output-dir` 指定项目目录
6. **JSON自动化** - 使用 `--json` 输出便于脚本处理

## API 信息

- **模型:** nano-banana-pro
- **平台:** Kie.ai
- **API 文档:** https://api.kie.ai/docs
- **获取 API 密钥:** https://kie.ai/api-key
- **支持:** support@kie.ai

## Resources

### scripts/

- **kie_nano_banana_api.py**: Nano Banana Pro API 封装脚本,支持文生图、图生图、多图融合和自动下载
  - 执行: `python3 scripts/kie_nano_banana_api.py [参数]`
  - 帮助: `python3 scripts/kie_nano_banana_api.py --help`

### 相关文档

- **TEST_OUTPUT_EXAMPLE.md**: 输出示例和下载格式
- **README.txt**: 快速参考指南

## 版本信息

- **版本:** v1.1
- **更新日期:** 2026-02-11
- **维护者:** storyclaw-skills
