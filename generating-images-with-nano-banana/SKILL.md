---
name: generating-images-with-nano-banana
description: 使用 Nano Banana Pro 模型(通过 kie.ai 平台)生成 AI 图像。支持文生图、图生图和多图融合(最多 8 张)。当用户需要创建、生成图像或图片时使用此技能。支持场景：(1) 根据文本描述生成图像，(2) 使用参考图生成图像，(3) 多图融合创意生成，(4) 自定义图像比例和清晰度。触发关键词：生成图像、创建图片、画一张图、AI 作画、图像生成、图片创作、nano-banana。
---

# Generating Images with Nano Banana

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

### 步骤 5: 执行并询问保存

生成完成后,**主动询问**用户:

```
问题: "图像已生成完成!是否将生成信息保存到文件?"
选项:
- "是,保存到下载文件夹"
- "不用,我只需要图像链接"
```

**如果用户选择保存,按以下步骤操作:**

1. **确定下载目录**(根据用户操作系统):
   - **macOS/Linux**: `~/Downloads/`
   - **Windows**: `%USERPROFILE%\Downloads\`

2. **生成文件名**:
   - 格式: `nano_banana_YYYYMMDD_HHMMSS.txt`
   - 示例: `nano_banana_20260211_143025.txt`

3. **保存内容格式**:
   ```
   ============================================================
   图像生成信息
   ============================================================
   提示词: [prompt]
   图像比例: [aspect_ratio]
   清晰度: [resolution]
   输出格式: [output_format]
   生成数量: [imageCount] 张

   图像 #1: [imageUrl1]
   图像 #2: [imageUrl2]

   生成时间: [YYYY-MM-DD HH:MM:SS]
   ============================================================
   ```

4. **使用 Write 工具保存文件**,并告知用户保存位置

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

# 社交媒体头像
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简logo设计,现代感,蓝色系" \
  --aspect-ratio 1:1 \
  --resolution 2K
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
  --resolution 2K

# 图像优化
python3 scripts/kie_nano_banana_api.py \
  --prompt "增强色彩,专业摄影风格,高细节" \
  --image-input "https://example.com/raw.jpg" \
  --resolution 4K

# 移除背景
python3 scripts/kie_nano_banana_api.py \
  --prompt "移除背景,保留主体,纯白背景" \
  --image-input "https://example.com/person.jpg"
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
  --aspect-ratio 16:9

# 组合多个元素
python3 scripts/kie_nano_banana_api.py \
  --prompt "将这些元素组合成一个和谐的场景" \
  --image-input "url1" "url2" "url3" "url4" \
  --resolution 4K

# 最多支持8张图像
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合所有图像的特点" \
  --image-input "url1" "url2" "url3" "url4" "url5" "url6" "url7" "url8"
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

### 示例 1: 社交媒体配图

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "现代简约风格的咖啡杯,温暖的早晨光线,专业摄影" \
  --aspect-ratio 1:1 \
  --resolution 2K
```

### 示例 2: 电脑壁纸

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "宁静的山水风景,日落时分,高细节,4K质量" \
  --aspect-ratio 16:9 \
  --resolution 4K
```

### 示例 3: 手机壁纸

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "抽象艺术,渐变色彩,现代简约" \
  --aspect-ratio 9:16 \
  --resolution 2K
```

### 示例 4: 图像风格转换

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为水彩画风格,柔和的色彩,艺术感" \
  --image-input "https://example.com/original.jpg" \
  --resolution 2K
```

### 示例 5: 多图创意融合

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合这些图像的艺术风格,创造独特的视觉效果" \
  --image-input "https://example.com/img1.jpg" "https://example.com/img2.jpg" "https://example.com/img3.jpg" \
  --aspect-ratio 16:9 \
  --resolution 4K
```

### 示例 6: 查询任务状态

```bash
python3 scripts/kie_nano_banana_api.py \
  --query \
  --task-id "abc123xyz"
```

### 示例 7: 异步模式(不等待完成)

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "复杂场景,需要较长生成时间" \
  --no-wait
```

### 示例 8: JSON 输出(便于程序化处理)

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

**适用场景:**
- 批量生成多张图像
- 高清晰度图像(4K)生成时间较长
- 需要同时进行其他操作

### 查询任务

使用 taskId 查询已创建任务的状态和结果。

```bash
python3 scripts/kie_nano_banana_api.py --query --task-id "abc123xyz"
```

**可能的状态:**
- `waiting`: 任务等待中或处理中
- `success`: 任务成功完成
- `fail`: 任务失败

### 调整超时参数

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --max-wait 600 \
  --poll-interval 10
```

- `--max-wait`: 最大等待时间(秒),默认300秒(5分钟)
- `--poll-interval`: 轮询间隔(秒),默认5秒

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

**JSON 输出优势:**
- 便于程序化处理
- 易于集成到工作流
- 支持批量操作

## 错误处理

### 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| "错误: 未设置API密钥" | 未配置 KIE_API_KEY | 设置环境变量: `export KIE_API_KEY="your-key"` 或使用 `--api-key` 参数 |
| "prompt 长度不能超过 20000 字符" | 提示词过长 | 精简描述,保留关键信息 |
| "最多支持 8 张参考图像" | 参考图数量超限 | 减少参考图数量至8张以内 |
| "任务失败: ..." | API 任务执行失败 | 检查 failMsg 错误信息,调整参数后重试 |
| "等待超时 (300秒)" | 任务生成时间过长 | 增加 `--max-wait` 时间或使用 `--no-wait` 异步模式 |
| "API错误: 401" | API 密钥无效 | 检查 API 密钥是否正确,访问 https://kie.ai/api-key 获取 |
| "API错误: 402" | 账户余额不足 | 充值账户或联系 kie.ai 客服 |
| "API错误: 429" | 请求频率超限 | 降低请求频率,稍后重试 |

### 错误排查步骤

1. **验证 API 密钥**
   ```bash
   echo $KIE_API_KEY  # 检查环境变量
   ```

2. **检查参数有效性**
   - prompt 长度 ≤ 20000 字符
   - image_input 数量 ≤ 8 张
   - 参数值在允许范围内

3. **查看详细错误信息**
   - 脚本会输出详细的错误信息到 stderr
   - 查询任务状态获取 failMsg 字段

4. **测试基本功能**
   ```bash
   # 最简单的测试
   python3 scripts/kie_nano_banana_api.py --prompt "测试" --json
   ```

5. **检查网络连接**
   - 确保能访问 https://api.kie.ai
   - 检查防火墙和代理设置

## 工作流程建议

### 快速原型

**目标:** 快速验证想法和概念

1. 使用默认参数(1:1, 2K)快速生成
2. 使用简短的提示词描述核心概念
3. 多次迭代,调整提示词

**示例流程:**
```bash
# 第一次尝试
python3 scripts/kie_nano_banana_api.py --prompt "猫咪"

# 增加细节
python3 scripts/kie_nano_banana_api.py --prompt "一只橘色的猫咪"

# 添加场景和风格
python3 scripts/kie_nano_banana_api.py --prompt "一只橘色的猫咪,坐在窗边,温暖的阳光,水彩画风格"
```

### 精细创作

**目标:** 生成高质量的最终作品

1. 准备详细的提示词(包含主体、场景、风格、细节)
2. 选择合适的比例(根据用途)
3. 使用 4K 清晰度
4. 如需要,使用参考图辅助

**示例流程:**
```bash
# 横屏壁纸 - 高质量
python3 scripts/kie_nano_banana_api.py \
  --prompt "宁静的山谷风景,清晨的薄雾,金色的阳光穿过树林,高细节风景摄影,专业色彩" \
  --aspect-ratio 16:9 \
  --resolution 4K

# 使用参考图优化
python3 scripts/kie_nano_banana_api.py \
  --prompt "增强色彩,专业摄影风格,高动态范围" \
  --image-input "https://example.com/original.jpg" \
  --resolution 4K
```

### 风格迁移

**目标:** 将现有图像转换为特定风格

1. 准备参考图像URL
2. 使用图生图模式
3. 清楚描述想要的风格转换
4. 保持原始比例或选择目标比例

**示例流程:**
```bash
# 转为油画风格
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为油画风格,笔触明显,色彩浓郁" \
  --image-input "https://example.com/photo.jpg" \
  --resolution 2K

# 转为卡通风格
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为日式动漫风格,保留人物特征" \
  --image-input "https://example.com/portrait.jpg" \
  --resolution 2K
```

### 创意融合

**目标:** 组合多张图像创造新的视觉效果

1. 选择2-8张参考图像
2. 使用多图融合模式
3. 描述期望的融合效果
4. 选择合适的输出比例

**示例流程:**
```bash
# 融合两种风格
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合第一张的构图和第二张的色彩风格" \
  --image-input "https://example.com/composition.jpg" "https://example.com/colors.jpg" \
  --aspect-ratio 16:9 \
  --resolution 4K

# 多元素组合
python3 scripts/kie_nano_banana_api.py \
  --prompt "将这些元素和谐地组合成一个统一的场景" \
  --image-input "url1" "url2" "url3" "url4" \
  --resolution 2K
```

### 批量生成

**目标:** 一次性生成多个图像变体

1. 使用异步模式(--no-wait)快速创建多个任务
2. 保存所有 taskId
3. 编写脚本批量查询状态
4. 收集所有成功的图像URL

**示例流程:**
```bash
# 创建多个任务
python3 scripts/kie_nano_banana_api.py --prompt "版本1描述" --no-wait > task1_id.txt
python3 scripts/kie_nano_banana_api.py --prompt "版本2描述" --no-wait > task2_id.txt
python3 scripts/kie_nano_banana_api.py --prompt "版本3描述" --no-wait > task3_id.txt

# 稍后批量查询
# (可以编写 shell 脚本自动化此过程)
```

## 快速预设

针对常见使用场景的参数预设:

### 社交媒体

```bash
# Instagram 帖子 (1:1)
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 1:1 \
  --resolution 2K

# Instagram 故事 (9:16)
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 9:16 \
  --resolution 2K
```

### 屏幕壁纸

```bash
# 电脑横屏壁纸 (16:9)
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 16:9 \
  --resolution 4K

# 手机竖屏壁纸 (9:16)
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 9:16 \
  --resolution 2K

# 超宽屏壁纸 (21:9)
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 21:9 \
  --resolution 4K
```

### 打印输出

```bash
# 照片打印 (4:3 或 3:2)
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 4:3 \
  --resolution 4K
```

### 视频封面

```bash
# YouTube 缩略图 (16:9)
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 16:9 \
  --resolution 2K
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

**缺乏细节:**
```
❌ "风景"
✓ "山谷中的小溪,清澈的水流,周围是茂密的森林,清晨的薄雾"
```

### 提示词结构建议

**基础结构:**
```
[主体] + [场景/背景] + [风格] + [细节要求]
```

**示例:**
```
主体: 一只蓝色的鸟
场景: 站在开花的树枝上
风格: 日本浮世绘风格
细节: 细腻的线条,柔和的色彩

完整提示词: "一只蓝色的鸟站在开花的树枝上,日本浮世绘风格,细腻的线条,柔和的色彩"
```

### 风格关键词参考

**艺术风格:**
- 油画风格、水彩画风格、素描风格
- 日本浮世绘、中国水墨画
- 印象派、抽象派、现代艺术

**摄影风格:**
- 专业摄影、商业摄影、肖像摄影
- 风景摄影、街拍摄影
- 黑白摄影、高动态范围(HDR)

**数字艺术:**
- 赛博朋克、蒸汽朋克、未来主义
- 像素艺术、低多边形(Low Poly)
- 3D渲染、概念艺术

**氛围描述:**
- 温暖、冷色调、柔和
- 戏剧性光线、神秘、梦幻
- 宁静、活力、忧郁

## 使用技巧

1. **从简到繁** - 先用简短提示词测试,再逐步添加细节
2. **比例选择** - 根据最终用途选择比例(1:1社交媒体,16:9横屏,9:16竖屏)
3. **清晰度策略** - 快速预览用1K,最终作品用4K
4. **参考图妙用** - 图生图模式可以精确控制风格转换
5. **多图融合创意** - 尝试融合不同风格的图像创造独特效果
6. **异步批量** - 使用--no-wait生成多个版本,再选择最佳
7. **JSON自动化** - 使用--json输出便于脚本处理和工作流集成
8. **任务追踪** - 保存taskId便于问题排查和结果追踪

## API 信息

- **模型:** nano-banana-pro
- **平台:** Kie.ai
- **API 文档:** https://api.kie.ai/docs
- **获取 API 密钥:** https://kie.ai/api-key
- **支持:** support@kie.ai

## Resources

### scripts/

- **kie_nano_banana_api.py**: Nano Banana Pro API 封装脚本,支持文生图、图生图和多图融合
  - 执行: `python3 scripts/kie_nano_banana_api.py [参数]`
  - 帮助: `python3 scripts/kie_nano_banana_api.py --help`

### 相关文档

- **TEST_OUTPUT_EXAMPLE.md**: 输出示例和保存格式
- **README.txt**: 快速参考指南

## 版本信息

- **版本:** v1.0
- **更新日期:** 2026-02-11
- **维护者:** storyclaw-skills
