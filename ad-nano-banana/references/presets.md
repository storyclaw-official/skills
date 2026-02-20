# 快速预设配置

常见使用场景的预设参数组合，开箱即用。

## 社交媒体预设

| 场景 | 命令参数 |
|------|---------|
| Instagram 帖子 (1:1) | `--aspect-ratio 1:1 --resolution 2K --download` |
| Instagram Stories (9:16) | `--aspect-ratio 9:16 --resolution 2K --download` |
| YouTube 封面 (16:9) | `--aspect-ratio 16:9 --resolution 4K --download` |

## 壁纸预设

| 场景 | 命令参数 |
|------|---------|
| 桌面壁纸 (标准) | `--aspect-ratio 16:9 --resolution 4K --download` |
| 桌面壁纸 (超宽屏) | `--aspect-ratio 21:9 --resolution 4K --download` |
| 手机壁纸 | `--aspect-ratio 9:16 --resolution 2K --download` |

## 打印预设

| 场景 | 命令参数 |
|------|---------|
| 照片打印 | `--aspect-ratio 4:3 --resolution 4K --output-format jpg --download` |
| 竖版肖像 | `--aspect-ratio 2:3 --resolution 4K --download` |
| 横版风景 | `--aspect-ratio 3:2 --resolution 4K --download` |

## 工作流预设

| 场景 | 命令参数 |
|------|---------|
| 快速测试提示词 | `--resolution 1K` |
| 日常使用 | `--resolution 2K --download` |
| 最终高清输出 | `--resolution 4K --download` |
| 脚本集成 | `--resolution 2K --json` |
| 批量异步生成 | `--resolution 2K --no-wait` |

## 图生图预设

| 场景 | 命令参数 |
|------|---------|
| 风格转换 | `--aspect-ratio auto --resolution 2K --image-input "url" --download` |
| 图像优化 | `--resolution 4K --image-input "url" --download` |
| 多图融合 | `--aspect-ratio 1:1 --resolution 2K --image-input "url1" "url2" --download` |

## 快速参考模板

```bash
# 社交媒体
python3 scripts/kie_nano_banana_api.py --prompt "描述" --aspect-ratio 1:1 --resolution 2K --download

# 壁纸
python3 scripts/kie_nano_banana_api.py --prompt "描述" --aspect-ratio 16:9 --resolution 4K --download

# 快速测试
python3 scripts/kie_nano_banana_api.py --prompt "描述" --resolution 1K

# 图生图
python3 scripts/kie_nano_banana_api.py --prompt "描述" --image-input "图片URL" --resolution 2K --download
```

## 场景选择建议

| 用途 | 推荐预设 | 理由 |
|-----|---------|------|
| 社交媒体分享 | 1:1 或 9:16, 2K | 快速生成，适合在线分享 |
| 桌面壁纸 | 16:9, 4K | 高清晰度，大屏显示 |
| 打印作品 | 4:3, 4K, jpg | 传统比例，高质量 |
| 快速测试 | 1K | 15-30秒验证效果 |
| 风格转换 | auto | 保持原图比例 |
