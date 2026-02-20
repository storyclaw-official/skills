# 使用示例

完整的输入输出示例，展示各种使用场景。

## 目录

- [基础示例](#基础示例)
- [社交媒体场景](#社交媒体场景)
- [壁纸场景](#壁纸场景)
- [图生图场景](#图生图场景)
- [多图融合场景](#多图融合场景)
- [任务管理场景](#任务管理场景)
- [JSON 输出场景](#json-输出场景)
- [错误场景示例](#错误场景示例)
- [进阶场景](#进阶场景)

---

## 基础示例

### 示例 1: 最简单的文生图

```bash
python3 scripts/kie_nano_banana_api.py --prompt "一只可爱的猫咪"
```

输出：
```
创建图像生成任务...
✓ 任务创建成功! TaskID: abc123
等待任务完成(最多300秒)...
任务状态: waiting
任务状态: success
✓ 任务完成!

生成了 1 张图像

============================================================
图像生成完成
============================================================
提示词: 一只可爱的猫咪
生成数量: 1 张

图像 #1: https://...
============================================================
```

---

### 示例 2: 生成并下载

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "一只橘色的猫咪坐在窗边,温暖的阳光" \
  --download
```

---

## 社交媒体场景

### 示例 3: Instagram 帖子 (1:1)

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "现代简约风格的咖啡杯,木质桌面,温暖的早晨光线,商业摄影" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download
```

### 示例 4: Instagram Stories (9:16)

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "抽象艺术,渐变色彩,现代简约,充满活力" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download \
  --output-format jpg
```

---

## 壁纸场景

### 示例 5: 电脑壁纸 (16:9, 4K)

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "宁静的山谷风景,清晨的薄雾,金色的阳光穿过树林,高细节风景摄影" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download
```

### 示例 6: 手机壁纸 (9:16, 自定义目录)

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简几何图案,深蓝色渐变,科技感" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download \
  --output-dir "~/Desktop/壁纸"
```

---

## 图生图场景

### 示例 7: 风格转换 - 转为油画

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为油画风格,保留原始构图,笔触明显,色彩浓郁" \
  --image-input "https://example.com/photo.jpg" \
  --resolution 2K \
  --download
```

### 示例 8: 图像优化

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "增强色彩,专业摄影风格,高动态范围,锐利细节" \
  --image-input "https://example.com/raw_photo.jpg" \
  --resolution 4K \
  --download
```

---

## 多图融合场景

### 示例 9: 融合两张图像的风格

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合这两张图像的艺术风格,创造独特的视觉效果" \
  --image-input \
    "https://example.com/style1.jpg" \
    "https://example.com/style2.jpg" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download
```

### 示例 10: 多图创意拼贴 (最多8张)

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "将这些元素组合成和谐的场景,保持各自特点" \
  --image-input \
    "https://example.com/element1.jpg" \
    "https://example.com/element2.jpg" \
    "https://example.com/element3.jpg" \
    "https://example.com/element4.jpg" \
  --resolution 2K \
  --download
```

---

## 任务管理场景

### 示例 11: 异步模式 - 批量生成

```bash
# 提交多个任务
python3 scripts/kie_nano_banana_api.py --prompt "版本1: 蓝色系" --no-wait
python3 scripts/kie_nano_banana_api.py --prompt "版本2: 绿色系" --no-wait
python3 scripts/kie_nano_banana_api.py --prompt "版本3: 紫色系" --no-wait

# 稍后批量查询下载
python3 scripts/kie_nano_banana_api.py --query --task-id task_001 --download
python3 scripts/kie_nano_banana_api.py --query --task-id task_002 --download
python3 scripts/kie_nano_banana_api.py --query --task-id task_003 --download
```

### 示例 12: 查询任务状态

```bash
python3 scripts/kie_nano_banana_api.py --query --task-id "abc123xyz"
```

---

## JSON 输出场景

### 示例 13: JSON 格式输出（用于脚本集成）

```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "科技感logo,蓝色系" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download \
  --json
```

输出：
```json
{
  "prompt": "科技感logo,蓝色系",
  "imageUrls": ["https://..."],
  "imageCount": 1,
  "downloadedFiles": ["/Users/username/Downloads/nano_banana_20260211_160425.png"]
}
```

---

## 错误场景示例

### 示例 14: API 密钥未设置

**解决**: `export GIGGLE_API_KEY="your-key"` 或创建 `.env` 文件

### 示例 15: 提示词过长

提示词超过 20000 字符时报错，精简描述即可。

### 示例 16: 参考图数量超限

`--image-input` 最多 8 个 URL。

---

## 进阶场景

### 示例 17: 迭代改进提示词

```bash
# 第一次: 1K 快速验证
python3 scripts/kie_nano_banana_api.py --prompt "猫" --resolution 1K

# 第二次: 增加细节
python3 scripts/kie_nano_banana_api.py --prompt "一只橘色的猫咪坐在窗边" --resolution 1K

# 第三次: 满意后生成高清
python3 scripts/kie_nano_banana_api.py \
  --prompt "一只橘色的猫咪坐在窗边,温暖的阳光,水彩画风格" \
  --resolution 4K \
  --download
```

### 示例 18: 完整项目工作流

```bash
# 步骤 1: 快速原型 (1K)
python3 scripts/kie_nano_banana_api.py --prompt "极简logo,字母M" --resolution 1K

# 步骤 2: 批量生成变体 (异步)
python3 scripts/kie_nano_banana_api.py --prompt "极简logo,字母M,蓝色系" --resolution 2K --no-wait
python3 scripts/kie_nano_banana_api.py --prompt "极简logo,字母M,绿色系" --resolution 2K --no-wait

# 步骤 3: 选择最佳版本生成 4K
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简logo,字母M,蓝色系,科技感" \
  --aspect-ratio 1:1 \
  --resolution 4K \
  --download \
  --output-dir "~/Desktop/项目Logo"
```

---

## 场景速查

| 场景类型 | 推荐参数 |
|---------|---------|
| 社交媒体 | `1:1` 或 `9:16`, `2K` |
| 壁纸 | `16:9` 或 `9:16`, `4K` |
| 风格转换 | `auto`, `2K`, `--image-input` |
| 批量生成 | `--no-wait` |
| 脚本集成 | `--json` |
| 快速测试 | `--resolution 1K` |
