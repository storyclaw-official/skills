---
name: giggle-image
description: 使用 Seedream 模型（通过 giggle.pro 平台）生成 AI 图像。支持文生图、图生图和多图融合（最多 10 张）。当用户需要创建、生成图像或图片、使用即梦/seedream 模型生成图像时使用此技能。支持场景：(1) 根据文本描述生成图像，(2) 使用参考图生成图像，(3) 多图融合创意生成，(4) 自定义图像比例和生成数量。触发关键词：即梦、seedream、Seedream、seedream45。
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["GIGGLE_API_KEY"],"bins":["python3"]},"primaryEnv":"GIGGLE_API_KEY","emoji":"🖼️","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/scripts/requirements.txt"]},"version":"1.0.0","author":"姜式伙伴"}
---

# Generating Images With Seedream

使用 Seedream 模型（seedream45）通过 giggle.pro 平台生成 AI 图像。

**API 密钥**: 从环境变量 `GIGGLE_API_KEY` 或项目根目录 `.env` 文件读取。

## 执行命令

始终使用 `--json` 获取结构化输出，从 `view_urls` 提取在线查看链接展示给用户，`urls` 为下载链接备用。

```bash
# 文生图（基础）
python3 scripts/seedream_api.py \
  --prompt "描述" \
  --aspect-ratio 16:9 \
  --json

# 图生图 - URL
python3 scripts/seedream_api.py \
  --prompt "转为油画风格,保留构图" \
  --reference-images "https://example.com/photo.jpg" \
  --json

# 图生图 - 本地文件（自动 base64 编码）
python3 scripts/seedream_api.py \
  --prompt "转为油画风格,保留构图" \
  --reference-images "/path/to/photo.jpg" \
  --json

# 多图融合（2-10张，URL 和本地文件可混用）
python3 scripts/seedream_api.py \
  --prompt "融合这些图像的艺术风格" \
  --reference-images "url1" "/path/to/local.png" "url2" \
  --json

# 生成多张
python3 scripts/seedream_api.py \
  --prompt "描述" \
  --generate-count 4 \
  --json
```

**输出字段（JSON）：**

| 字段 | 类型 | 说明 |
|-----|------|------|
| `prompt` | string | 图像描述提示词 |
| `view_urls` | string[] | 在线查看链接（浏览器直接显示图像，用于展示） |
| `urls` | string[] | 原始下载链接（带 attachment 参数，用于下载） |
| `imageCount` | integer | 生成的图像数量 |

**展示方式**：脚本完成后，优先使用 `view_urls`，同时附上 `urls` 作为下载入口：

```markdown
![生成图像 #N](https://view_url)
🔗 在线查看：https://view_url
⬇️ 下载链接：https://download_url
```

如果用户明确要求保存到本地，追加 `--download` 参数重新运行，或单独运行下载命令。

---

## 参数速查

| 参数 | 默认值 | 选项 |
|-----|--------|------|
| `--aspect-ratio` | 16:9 | 16:9, 9:16, 1:1, 3:4, 4:3, 2:3, 3:2, 21:9 |
| `--generate-count` | 1 | 生成图像数量 |
| `--reference-images` | - | URL 或本地文件路径，最多 10 张（本地文件自动 base64 编码） |
| `--watermark` | false | 添加水印 |
| `--download` | false | 自动下载到 ~/Downloads |
| `--output-dir` | ~/Downloads | 自定义下载目录 |
| `--no-wait` | false | 异步模式，返回 task_id 后手动 `--query` |
| `--max-wait` | 300s | 最大等待时间 |
| `--json` | false | 结构化输出，便于脚本集成 |

---

## 交互引导流程

**当用户请求模糊（未说明比例、具体描述）时，按以下步骤引导。如用户已提供足够信息，直接执行命令，跳过相应步骤。**

**默认比例为 16:9。如果用户未明确指定图像比例，必须先询问用户确认比例后再生成。**

### 步骤 1: 图像比例（未指定时必须询问）

```
问题: "您需要什么比例的图像?"
header: "图像比例"
选项:
- "16:9 - 横屏(壁纸/封面) (推荐)"
- "9:16 - 竖屏(手机/Stories)"
- "1:1 - 正方形(社交媒体/头像)"
- "其他比例"
multiSelect: false
```

如选"其他": 3:4 (竖版) | 4:3 (横版) | 2:3 (竖版照片) | 3:2 (横版照片) | 21:9 (超宽屏)

### 步骤 2: 图像描述

询问用户描述。提示结构: `主体 + 场景 + 风格 + 细节`

好的示例：
- `"一只橘色猫咪坐在窗边,阳光洒进,水彩画风格,温馨氛围"`
- `"未来城市,赛博朋克风格,霓虹灯,夜景,高细节"`

### 步骤 3: 生成模式

```
问题: "是否需要使用参考图像?"
header: "生成模式"
选项:
- "不需要 - 纯文生图"
- "1张参考图 - 图生图(风格转换)"
- "多张参考图 - 多图融合(最多10张)"
multiSelect: false
```

如需参考图，收集可公开访问的图片 URL。

### 步骤 4: 执行生成并展示

1. 运行命令（带 `--json`），等待完成
2. 解析输出中的 `view_urls`（在线查看）和 `urls`（下载）数组
3. 对每张图像，在会话中输出：
   ```
   ![生成图像 #N](view_url)
   🔗 在线查看：view_url
   ⬇️ 下载链接：download_url
   ```
4. 无需询问是否下载，直接展示即可

### 步骤 5: 反馈迭代

```
问题: "图像已生成！您对结果满意吗?"
header: "结果评估"
选项:
- "满意，已完成"
- "需要调整提示词重新生成"
- "需要更改比例"
- "需要添加/更改参考图"
multiSelect: false
```

根据反馈返回对应步骤重新生成。

> 如用户希望保存图像到本地，可追加 `--download` 参数重新执行，或告知用户点击完整链接自行保存。

---

## 执行前检查

- [ ] `echo $GIGGLE_API_KEY` 或检查 `.env` 文件是否已配置
- [ ] 参考图（如有）URL 可公开访问，数量 ≤ 10
