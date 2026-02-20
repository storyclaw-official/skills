---
name: gen-image
description: 使用 Nano Banana Pro 模型(通过 kie.ai 平台)生成 AI 图像。支持文生图、图生图和多图融合(最多 8 张)。当用户需要创建、生成图像或图片时使用此技能。支持场景：(1) 根据文本描述生成图像，(2) 使用参考图生成图像，(3) 多图融合创意生成，(4) 自定义图像比例和清晰度。触发关键词：生成图像、创建图片、画一张图、AI 作画、图像生成、图片创作、nano-banana。
---

# AD Nano Banana

使用 Nano Banana Pro 模型（通过 kie.ai 平台）生成 AI 图像。

**API 密钥**: 从环境变量 `GIGGLE_API_KEY` 或项目根目录 `.env` 文件读取。

## 执行命令

始终使用 `--json` 获取结构化输出，从 `imageUrls` 中提取链接后在会话中内联展示图像。

```bash
# 文生图（基础）
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --json

# 图生图
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为油画风格,保留构图" \
  --image-input "https://example.com/photo.jpg" \
  --resolution 2K \
  --json

# 多图融合（最多8张）
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合这些图像的艺术风格" \
  --image-input "url1" "url2" "url3" \
  --resolution 2K \
  --json
```

**输出字段（JSON）：**

| 字段 | 类型 | 说明 |
|-----|------|------|
| `prompt` | string | 图像描述提示词 |
| `imageUrls` | string[] | 生成的图像 URL 数组 |
| `imageCount` | integer | 生成的图像数量 |

**展示方式**：脚本完成后，对每个 URL 执行：

```markdown
![生成图像](https://url-from-imageUrls)
🔗 完整链接：https://url-from-imageUrls
```

如果用户明确要求保存到本地，追加 `--download` 参数重新运行，或单独运行下载命令。

---

## 参数速查

| 参数 | 默认值 | 选项 |
|-----|--------|------|
| `--aspect-ratio` | 1:1 | 1:1, 16:9, 9:16, 2:3, 3:2, 4:3, 21:9, auto |
| `--resolution` | 2K | 1K (~15-30s), 2K (~30-60s), 4K (~60-120s) |
| `--output-format` | png | png, jpg |
| `--image-input` | - | URL 列表，最多 8 张 |
| `--download` | false | 自动下载到 ~/Downloads |
| `--output-dir` | ~/Downloads | 自定义下载目录 |
| `--no-wait` | false | 异步模式，返回 taskId 后手动 `--query` |
| `--max-wait` | 300s | 4K 建议设为 600 |
| `--json` | false | 结构化输出，便于脚本集成 |

---

## 交互引导流程

**当用户请求模糊（未说明比例、清晰度、具体描述）时，按以下步骤引导。如用户已提供足够信息，直接执行命令，跳过相应步骤。**

### 步骤 1: 图像比例

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

如选"其他": 2:3 (竖版照片) | 3:2 (横版照片) | 4:3 (传统屏幕) | 21:9 (超宽屏) | auto (自动)

### 步骤 2: 清晰度

```
问题: "您需要什么清晰度?"
header: "清晰度"
选项:
- "2K (推荐) - 平衡质量和速度 (~30-60秒)"
- "4K - 最高质量,适合打印 (~60-120秒)"
- "1K - 快速预览 (~15-30秒)"
multiSelect: false
```

### 步骤 3: 图像描述

询问用户描述。提示结构: `主体 + 场景 + 风格 + 细节`

好的示例：
- `"一只橘色猫咪坐在窗边,阳光洒进,水彩画风格,温馨氛围"`
- `"未来城市,赛博朋克风格,霓虹灯,夜景,高细节"`

> 提示词详细指南见 [references/prompt-guide.md](references/prompt-guide.md)

### 步骤 4: 生成模式

```
问题: "是否需要使用参考图像?"
header: "生成模式"
选项:
- "不需要 - 纯文生图"
- "1张参考图 - 图生图(风格转换)"
- "多张参考图 - 多图融合(最多8张)"
multiSelect: false
```

如需参考图，收集可公开访问的图片 URL。

### 步骤 5: 执行生成并展示

1. 运行命令（带 `--json`），等待完成（参考上方时间估算）
2. 解析输出中的 `imageUrls` 数组
3. 对每张图像，在会话中输出：
   ```
   ![生成图像 #N](url)
   🔗 完整链接：url
   ```
4. 无需询问是否下载，直接展示即可

### 步骤 6: 反馈迭代

```
问题: "图像已生成！您对结果满意吗?"
header: "结果评估"
选项:
- "满意，已完成"
- "需要调整提示词重新生成"
- "需要更改比例或清晰度"
- "需要添加/更改参考图"
multiSelect: false
```

根据反馈返回对应步骤重新生成。**迭代建议：先用 1K 快速验证，满意后再生成 4K。**

> 如用户希望保存图像到本地，可追加 `--download` 参数重新执行，或告知用户点击完整链接自行保存。

---

## 执行前检查

- [ ] `echo $GIGGLE_API_KEY` 或检查 `.env` 文件是否已配置
- [ ] 提示词长度 ≤ 20000 字符
- [ ] 参考图（如有）URL 可公开访问，数量 ≤ 8

---

## References

| 文件 | 何时读取 |
|-----|---------|
| [references/prompt-guide.md](references/prompt-guide.md) | 用户需要提示词撰写指导时 |
| [references/presets.md](references/presets.md) | 用户需要场景预设命令时 |
| [references/examples.md](references/examples.md) | 需要完整示例参考时 |
| [references/reference.md](references/reference.md) | 需要完整参数说明时 |
| [references/troubleshooting.md](references/troubleshooting.md) | 遇到错误需要排查时 |
