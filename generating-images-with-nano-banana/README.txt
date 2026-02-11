# generating-images-with-nano-banana 技能

使用 Nano Banana Pro 模型生成 AI 图像(通过 kie.ai 平台)

## 安装

```bash
claude skills install generating-images-with-nano-banana.skill
```

## 输出字段

✅ **prompt**      - 图像描述提示词
✅ **imageUrls**   - 生成的图像 URL 数组
✅ **imageCount**  - 生成的图像数量

## 快速开始

### 1. 设置 API 密钥
```bash
export KIE_API_KEY="your-api-key"
```

获取 API 密钥: https://kie.ai/api-key

### 2. 基础用法

文生图:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "一只可爱的猫咪"
```

图生图:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为油画风格" \
  --image-input "https://example.com/photo.jpg"
```

多图融合:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合这些图像的风格" \
  --image-input "url1" "url2" "url3"
```

JSON 输出:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "测试" --json
```

## 生成模式

| 模式 | 使用场景 | 命令示例 |
|-----|---------|---------|
| 文生图 | 根据文字生成 | `--prompt "描述"` |
| 图生图 | 风格转换 | `--prompt "描述" --image-input "url"` |
| 多图融合 | 组合多张图 | `--prompt "描述" --image-input "url1" "url2"` |

## 参数说明

**必需参数:**
- `--prompt`: 图像描述(≤20000字符)

**可选参数:**
- `--aspect-ratio`: 图像比例(默认1:1)
  - 选项: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, auto
- `--resolution`: 清晰度(默认2K)
  - 选项: 1K, 2K, 4K
- `--output-format`: 输出格式(默认png)
  - 选项: png, jpg
- `--image-input`: 参考图像URL(最多8张)

**任务管理:**
- `--no-wait`: 不等待完成,立即返回
- `--max-wait`: 最大等待时间(秒,默认300)
- `--poll-interval`: 轮询间隔(秒,默认5)

**输出:**
- `--json`: JSON格式输出
- `--query --task-id`: 查询任务状态

## 常用预设

社交媒体(1:1):
```bash
--aspect-ratio 1:1 --resolution 2K
```

横屏壁纸(16:9):
```bash
--aspect-ratio 16:9 --resolution 4K
```

竖屏壁纸(9:16):
```bash
--aspect-ratio 9:16 --resolution 2K
```

## 文档

- **SKILL.md** - 完整使用文档和交互式引导
- **TEST_OUTPUT_EXAMPLE.md** - 输出格式和示例
- **scripts/kie_nano_banana_api.py** - Python API 客户端

## API 信息

- 模型: nano-banana-pro
- 平台: Kie.ai
- 文档: https://api.kie.ai/docs
- 获取密钥: https://kie.ai/api-key

## 快速测试

```bash
export KIE_API_KEY="your-api-key"
python3 scripts/kie_nano_banana_api.py --prompt "测试图像" --json
```

## 版本

- 版本: v1.0
- 日期: 2026-02-11
