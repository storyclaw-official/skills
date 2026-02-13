---
name: ad-nano-banana
description: 使用 Nano Banana Pro 模型(通过 kie.ai 平台)生成 AI 图像。支持文生图、图生图和多图融合(最多 8 张)。当用户需要创建、生成图像或图片时使用此技能。支持场景：(1) 根据文本描述生成图像，(2) 使用参考图生成图像，(3) 多图融合创意生成，(4) 自定义图像比例和清晰度。触发关键词：生成图像、创建图片、画一张图、AI 作画、图像生成、图片创作、nano-banana。
---

# AD Nano Banana

使用 Nano Banana Pro 模型(通过 kie.ai 平台)生成 AI 图像。支持从简单的文本描述到多图融合的高级创作。

## 核心输出

脚本输出包含 3 个关键字段:

| 字段 | 类型 | 说明 |
|-----|------|------|
| **prompt** | string | 图像描述提示词 |
| **imageUrls** | string[] | 生成的图像 URL 数组 |
| **imageCount** | integer | 生成的图像数量 |

## 交互式引导流程

**当用户请求"生成一张图片"或类似模糊请求时,按以下流程引导:**

### 步骤 1: 收集图像比例

使用 AskUserQuestion 工具:

```
问题: "您需要什么比例的图像?"
header: "图像比例"
选项:
- "1:1 - 正方形(社交媒体/头像)"
- "16:9 - 横屏(壁纸/封面)"
- "9:16 - 竖屏(手机/Stories)"
- "其他比例"

multiSelect: false
```

**如果选择"其他比例",继续询问:**
```
选项: 2:3 (竖版照片) | 3:2 (横版照片) | 4:3 (传统屏幕) | 21:9 (超宽屏) | auto (自动)
```

**💡 推荐:**
- 社交媒体: 1:1 (Instagram)
- 横屏壁纸: 16:9
- 手机壁纸: 9:16
- 打印照片: 4:3 或 2:3

---

### 步骤 2: 确定清晰度

使用 AskUserQuestion 工具:

```
问题: "您需要什么清晰度?"
header: "清晰度"
选项:
- "2K (推荐) - 平衡质量和速度 (~30-60秒)"
- "4K - 最高质量,适合打印 (~60-120秒)"
- "1K - 快速预览 (~15-30秒)"

multiSelect: false
```

---

### 步骤 3: 收集图像描述

询问用户:
```
问题: "请描述您想要生成的图像内容"
```

**💡 提示词建议** (简要版):
- **主体**: 明确描述主要内容(如"一只橘色的猫")
- **场景**: 添加环境描述(如"坐在窗边")
- **风格**: 指定艺术风格(如"水彩画风格")
- **细节**: 补充氛围和光线(如"温暖的阳光,高细节")

**好的示例**:
- "一只橘色猫咪坐在窗边,阳光洒进,水彩画风格,温馨氛围"
- "未来城市,赛博朋克风格,霓虹灯,夜景,高细节"

**避免**: "猫"(太简短) | "好看的图片"(过于模糊)

📖 **完整指南**: 参考 PROMPT_GUIDE.md 获取详细的提示词最佳实践

---

### 步骤 4: 确定生成模式

使用 AskUserQuestion 工具:

```
问题: "是否需要使用参考图像?"
header: "生成模式"
选项:
- "不需要 - 纯文生图"
- "1张参考图 - 图生图(风格转换)"
- "多张参考图 - 多图融合(最多8张)"

multiSelect: false
```

#### 模式 A: 纯文生图

直接执行生成:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "用户的描述" \
  --aspect-ratio "16:9" \
  --resolution "2K" \
  --download
```

#### 模式 B: 图生图(1张参考图)

收集参考图 URL,然后执行:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为油画风格,保留构图" \
  --image-input "https://example.com/photo.jpg" \
  --aspect-ratio "16:9" \
  --resolution "2K" \
  --download
```

**💡 图生图提示词建议**:
- "转为[风格],保持主体"
- "增强色彩,专业摄影风格"
- "移除背景,保留人物"

#### 模式 C: 多图融合(2-8张)

收集多张参考图 URL,然后执行:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合这些图像的风格" \
  --image-input "url1" "url2" "url3" \
  --aspect-ratio "16:9" \
  --resolution "2K" \
  --download
```

**💡 多图融合提示词建议**:
- "融合这些图像的艺术风格"
- "结合图1的构图和图2的色彩"
- "将这些元素组合成和谐场景"

---

### 步骤 5: 执行生成

1. **运行脚本**,显示进度
2. **等待完成** (1K: 15-30秒 | 2K: 30-60秒 | 4K: 60-120秒)
3. **显示结果** (图像 URL 和下载路径)

**默认行为**: 使用 `--download` 自动下载到 `~/Downloads/`

**文件命名**: `nano_banana_YYYYMMDD_HHMMSS.png`

---

### 步骤 6: 反馈和迭代 ✨

生成完成后,**主动询问**:

```
问题: "图像已生成!您对结果满意吗?"
header: "结果评估"
选项:
- "满意,已完成"
- "需要调整提示词重新生成"
- "需要更改比例或清晰度"
- "需要添加/更改参考图"

multiSelect: false
```

#### 如果需要调整:

**调整提示词**: 返回步骤 3,根据用户反馈优化描述
- 提示用户: "可以更具体地描述想要的效果,比如调整风格、色彩、光线等"

**更改参数**: 返回步骤 1 或 2,修改比例或清晰度
- 提示用户: "可以尝试不同的比例或提升到 4K"

**调整参考图**: 返回步骤 4,更换或添加参考图
- 提示用户: "可以提供其他参考图或移除某些参考图"

**💡 迭代建议**:
- 第一次生成可以使用 1K 快速测试
- 满意后再生成 2K 或 4K 高清版本
- 每次调整一个方面(提示词、比例或参考图)

---

## 工作流检查清单 ✅

在执行生成前,确认以下要点:

- [ ] 图像比例是否符合最终用途?
- [ ] 清晰度是否满足质量要求?
- [ ] 提示词是否包含主体、场景、风格?
- [ ] 提示词长度 ≤ 20000 字符?
- [ ] 参考图(如有)数量 ≤ 8 张?
- [ ] 参考图 URL 是否可公开访问?
- [ ] API 密钥是否已设置? (`echo $KIE_API_KEY`)

---

## Quick Start

### 1. 环境配置

**推荐方式：使用 .env 文件**
```bash
# 1. 复制模板文件
cp .env.example .env

# 2. 编辑 .env 文件，填入你的 API 密钥
# KIE_API_KEY=your-api-key-here
```

**替代方式：环境变量**
```bash
export KIE_API_KEY="your-api-key-here"
```

获取密钥: https://kie.ai/api-key

验证配置:
```bash
# 如果使用 .env 文件，脚本会自动加载
# 如果使用环境变量，可以验证：
echo $KIE_API_KEY  # 应显示你的密钥
```

### 2. 最简单的使用

只需提供描述:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "一只可爱的猫咪"
```

### 3. 生成并下载

推荐用法(自动下载):
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "一只可爱的猫咪" \
  --download
```

📖 **更多示例**: 参考 EXAMPLES.md 获取 18+ 完整使用示例

---

## 生成模式

| 模式 | 使用场景 | 关键参数 |
|-----|---------|---------|
| **文生图** | 根据描述创建全新图像 | `--prompt` |
| **图生图** | 风格转换、图像优化 | `--prompt` + `--image-input` (1张) |
| **多图融合** | 创意拼贴、风格混合 | `--prompt` + `--image-input` (2-8张) |

---

## 核心参数

### 必需参数

- `--prompt`: 图像描述 (≤ 20000 字符)

### 常用参数

| 参数 | 默认值 | 选项 |
|-----|--------|------|
| `--aspect-ratio` | 1:1 | 1:1, 16:9, 9:16, 2:3, 3:2, 4:3, 21:9, auto |
| `--resolution` | 2K | 1K, 2K, 4K |
| `--output-format` | png | png, jpg |
| `--image-input` | - | 最多 8 个 URL |

### 下载参数

- `--download`: 自动下载到本地
- `--output-dir`: 指定下载目录 (默认 ~/Downloads)

### 任务管理

- `--no-wait`: 异步模式,立即返回
- `--max-wait`: 最大等待时间(秒,默认 300)
- `--query --task-id`: 查询已创建的任务

### 输出格式

- `--json`: JSON 格式输出(便于脚本集成)

📖 **完整参数说明**: 参考 REFERENCE.md

---

## 快速预设命令

### 社交媒体

```bash
# Instagram 帖子 (1:1)
python3 scripts/kie_nano_banana_api.py \
  --prompt "你的描述" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download

# Instagram Stories (9:16)
python3 scripts/kie_nano_banana_api.py \
  --prompt "你的描述" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download
```

### 壁纸

```bash
# 桌面壁纸 (16:9, 4K)
python3 scripts/kie_nano_banana_api.py \
  --prompt "你的描述" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download

# 手机壁纸 (9:16, 2K)
python3 scripts/kie_nano_banana_api.py \
  --prompt "你的描述" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download
```

📖 **更多预设**: 参考 PRESETS.md 获取完整的场景预设配置

---

## 图像下载

### 自动下载机制

使用 `--download` 参数:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --download
```

**下载特性:**
- ✅ 使用 Python 内置 urllib,不依赖系统环境
- ✅ 自动创建下载目录
- ✅ 文件命名: `nano_banana_YYYYMMDD_HHMMSS.png`
- ✅ 多图自动编号: `_1.png`, `_2.png`
- ✅ 跨平台支持 (macOS/Linux/Windows)

**⚠️ 重要**: 图像 URL 有效期有限,建议立即下载!

### 自定义下载目录

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --download \
  --output-dir "~/Desktop/images"
```

---

## 输出格式

### 文本格式 (默认)

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

### JSON 格式 (--json)

```json
{
  "prompt": "一只可爱的猫咪",
  "imageUrls": ["https://..."],
  "imageCount": 1,
  "downloadedFiles": ["/Users/username/Downloads/..."]
}
```

---

## 异步任务管理

### 创建异步任务

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --resolution 4K \
  --no-wait

# 输出: TaskID: abc123xyz
```

### 查询任务状态

```bash
python3 scripts/kie_nano_banana_api.py \
  --query \
  --task-id "abc123xyz" \
  --download
```

**适用场景:**
- 批量生成多个版本
- 4K 高清图像(生成时间较长)
- 后台执行,不阻塞其他操作

---

## 常见问题快速解决

| 问题 | 解决方案 |
|-----|---------|
| 未设置 API 密钥 | `export KIE_API_KEY="your-key"` |
| 提示词过长 | 精简描述,≤ 20000 字符 |
| 参考图数量超限 | 最多 8 张 |
| 等待超时 | 使用 `--max-wait 600` 或 `--no-wait` |
| 下载失败 | 检查网络,URL 可能已过期 |

📖 **详细故障排除**: 参考 TROUBLESHOOTING.md

---

## 使用技巧

1. **快速迭代**: 先用 1K 测试提示词,满意后生成 4K
2. **及时下载**: URL 有效期有限,使用 `--download` 立即保存
3. **批量生成**: 使用 `--no-wait` 异步模式批量提交
4. **JSON 集成**: 使用 `--json` 便于脚本自动化处理
5. **自定义目录**: 使用 `--output-dir` 按项目组织文件

---

## 帮助资源

### 文档

- **EXAMPLES.md** - 18+ 完整输入/输出示例
- **REFERENCE.md** - 完整参数说明和配置指南
- **PRESETS.md** - 常见场景快速预设
- **PROMPT_GUIDE.md** - 提示词撰写最佳实践
- **TROUBLESHOOTING.md** - 详细错误处理和常见问题

### API 信息

- **模型**: nano-banana-pro
- **平台**: Kie.ai
- **API 文档**: https://api.kie.ai/docs
- **获取密钥**: https://kie.ai/api-key

### 命令行帮助

```bash
python3 scripts/kie_nano_banana_api.py --help
```

---

## 版本信息

- **版本**: v1.2
- **更新日期**: 2026-02-11
- **变更**: 优化工作流,添加反馈循环,实施渐进式文档披露
