# 使用示例

完整的输入输出示例,展示各种使用场景。

## 基础示例

### 示例 1: 最简单的文生图

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "一只可爱的猫咪"
```

**输出**:
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

图像 #1: https://static.aiquickdraw.com/tools/example/cat.png
============================================================
```

**结果**: 生成了符合描述的猫咪图像,使用默认参数(1:1, 2K, png)

---

### 示例 2: 生成并下载

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "一只橘色的猫咪坐在窗边,温暖的阳光" \
  --download
```

**输出**:
```
创建图像生成任务...
✓ 任务创建成功! TaskID: def456
等待任务完成(最多300秒)...
任务状态: success
✓ 任务完成!

生成了 1 张图像

下载图像...
下载图像 1/1...
✓ 图像已下载: /Users/username/Downloads/nano_banana_20260211_143025.png

============================================================
图像生成完成
============================================================
提示词: 一只橘色的猫咪坐在窗边,温暖的阳光
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/orange_cat.png

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_143025.png
============================================================
```

**结果**: 图像已生成并自动下载到本地

---

## 社交媒体场景

### 示例 3: Instagram 帖子 (1:1)

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "现代简约风格的咖啡杯,木质桌面,温暖的早晨光线,商业摄影" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download
```

**输出**:
```
============================================================
图像生成完成
============================================================
提示词: 现代简约风格的咖啡杯,木质桌面,温暖的早晨光线,商业摄影
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/coffee_1x1.png

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_144512.png
============================================================
```

**结果**: 生成了适合 Instagram 1:1 比例的咖啡杯图像

---

### 示例 4: Instagram 故事 (9:16)

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "抽象艺术,渐变色彩,现代简约,充满活力" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download \
  --output-format jpg
```

**输出**:
```
============================================================
图像生成完成
============================================================
提示词: 抽象艺术,渐变色彩,现代简约,充满活力
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/abstract_9x16.jpg

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_145820.jpg
============================================================
```

**结果**: 生成了竖屏比例的抽象艺术图像,JPG 格式

---

## 壁纸场景

### 示例 5: 电脑壁纸 (16:9, 4K)

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "宁静的山谷风景,清晨的薄雾,金色的阳光穿过树林,高细节风景摄影,专业色彩" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download
```

**输出**:
```
创建图像生成任务...
✓ 任务创建成功! TaskID: ghi789
等待任务完成(最多300秒)...
任务状态: waiting
任务状态: waiting
任务状态: waiting
任务状态: success
✓ 任务完成!

生成了 1 张图像

下载图像...
下载图像 1/1...
✓ 图像已下载: /Users/username/Downloads/nano_banana_20260211_150132.png

============================================================
图像生成完成
============================================================
提示词: 宁静的山谷风景,清晨的薄雾,金色的阳光穿过树林,高细节风景摄影,专业色彩
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/landscape_4k.png

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_150132.png
============================================================
```

**结果**: 生成了 4K 高清横屏壁纸

---

### 示例 6: 手机壁纸 (9:16, 2K)

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简几何图案,深蓝色渐变,科技感,现代设计" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download \
  --output-dir "~/Desktop/壁纸"
```

**输出**:
```
============================================================
图像生成完成
============================================================
提示词: 极简几何图案,深蓝色渐变,科技感,现代设计
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/geometric_mobile.png

下载文件:
文件 #1: /Users/username/Desktop/壁纸/nano_banana_20260211_151045.png
============================================================
```

**结果**: 图像下载到自定义目录(桌面/壁纸文件夹)

---

## 图生图场景

### 示例 7: 风格转换 - 转为油画

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为油画风格,保留原始构图,笔触明显,色彩浓郁,艺术感" \
  --image-input "https://example.com/original_photo.jpg" \
  --resolution 2K \
  --download
```

**输出**:
```
============================================================
图像生成完成
============================================================
提示词: 转为油画风格,保留原始构图,笔触明显,色彩浓郁,艺术感
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/oil_painting.png

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_152018.png
============================================================
```

**结果**: 原照片已转换为油画风格

---

### 示例 8: 图像优化 - 专业摄影

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "增强色彩,专业摄影风格,高动态范围,锐利细节" \
  --image-input "https://example.com/raw_photo.jpg" \
  --resolution 4K \
  --download
```

**输出**:
```
============================================================
图像生成完成
============================================================
提示词: 增强色彩,专业摄影风格,高动态范围,锐利细节
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/enhanced_photo.png

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_153142.png
============================================================
```

**结果**: 图像质量得到专业级优化

---

## 多图融合场景

### 示例 9: 融合两张图像的风格

**输入**:
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

**输出**:
```
============================================================
图像生成完成
============================================================
提示词: 融合这两张图像的艺术风格,创造独特的视觉效果
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/fusion_2images.png

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_154230.png
============================================================
```

**结果**: 成功融合两种风格,创造出新的艺术效果

---

### 示例 10: 多图创意拼贴 (最多8张)

**输入**:
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

**输出**:
```
============================================================
图像生成完成
============================================================
提示词: 将这些元素组合成和谐的场景,保持各自特点
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/multi_fusion.png

下载文件:
文件 #1: /Users/username/Downloads/nano_banana_20260211_155318.png
============================================================
```

**结果**: 4 张图像成功组合成统一的视觉作品

---

## 任务管理场景

### 示例 11: 异步模式 - 批量生成

**输入 (创建多个任务)**:
```bash
# 任务 1
python3 scripts/kie_nano_banana_api.py \
  --prompt "版本1: 蓝色系,现代感" \
  --no-wait

# 任务 2
python3 scripts/kie_nano_banana_api.py \
  --prompt "版本2: 绿色系,自然感" \
  --no-wait

# 任务 3
python3 scripts/kie_nano_banana_api.py \
  --prompt "版本3: 紫色系,创新感" \
  --no-wait
```

**输出**:
```
# 任务 1 输出
✓ 任务创建成功! TaskID: task_001
任务ID: task_001
可使用以下命令查询: python scripts/kie_nano_banana_api.py --query --task-id task_001

# 任务 2 输出
✓ 任务创建成功! TaskID: task_002
...

# 任务 3 输出
✓ 任务创建成功! TaskID: task_003
...
```

**输入 (批量查询)**:
```bash
python3 scripts/kie_nano_banana_api.py --query --task-id task_001 --download
python3 scripts/kie_nano_banana_api.py --query --task-id task_002 --download
python3 scripts/kie_nano_banana_api.py --query --task-id task_003 --download
```

**结果**: 3 个版本的图像并行生成,然后批量下载

---

### 示例 12: 查询任务状态

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --query \
  --task-id "abc123xyz"
```

**输出 (任务进行中)**:
```
查询任务: abc123xyz
任务状态: waiting
任务尚未完成或失败: waiting
```

**输出 (任务完成)**:
```
查询任务: abc123xyz
任务状态: success

生成了 1 张图像

============================================================
图像生成完成
============================================================
提示词: 原始提示词
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/result.png
============================================================
```

---

## JSON 输出场景

### 示例 13: JSON 格式输出

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "科技感logo,蓝色系" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download \
  --json
```

**输出**:
```json
{
  "prompt": "科技感logo,蓝色系",
  "imageUrls": [
    "https://static.aiquickdraw.com/tools/example/tech_logo.png"
  ],
  "imageCount": 1,
  "downloadedFiles": [
    "/Users/username/Downloads/nano_banana_20260211_160425.png"
  ]
}
```

**结果**: 结构化数据输出,便于程序处理

---

## 错误场景示例

### 示例 14: API 密钥未设置

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "测试"
```

**输出**:
```
错误: 未设置API密钥
请通过 --api-key 参数或环境变量 KIE_API_KEY 设置
获取API密钥: https://kie.ai/api-key
```

**解决**: 设置环境变量 `export KIE_API_KEY="your-key"`

---

### 示例 15: 提示词过长

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "[超过20000字符的文本]"
```

**输出**:
```
创建图像生成任务...
✗ 错误: prompt 长度不能超过 20000 字符
```

**解决**: 精简提示词内容

---

### 示例 16: 参考图数量超限

**输入**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合" \
  --image-input url1 url2 url3 url4 url5 url6 url7 url8 url9
```

**输出**:
```
创建图像生成任务...
✗ 错误: 最多支持 8 张参考图像
```

**解决**: 减少参考图数量至 8 张以内

---

## 进阶场景

### 示例 17: 迭代改进提示词

**第一次尝试**:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "猫" --download
```
结果: 生成的猫过于通用

**第二次改进**:
```bash
python3 scripts/kie_nano_banana_api.py --prompt "一只橘色的猫" --download
```
结果: 更具体,但缺少场景

**第三次优化**:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "一只橘色的猫咪坐在窗边,温暖的阳光,水彩画风格" \
  --download
```
结果: 完美! 符合所有期望

---

### 示例 18: 完整工作流程

**需求**: 为项目创建 Logo,需要多个版本对比

**步骤 1: 快速原型**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简logo,字母M,现代感" \
  --aspect-ratio 1:1 \
  --resolution 1K
```

**步骤 2: 批量生成变体**
```bash
# 蓝色版本
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简logo,字母M,蓝色系,科技感" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --no-wait

# 绿色版本
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简logo,字母M,绿色系,环保感" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --no-wait

# 紫色版本
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简logo,字母M,紫色系,创新感" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --no-wait
```

**步骤 3: 选择最佳版本生成 4K**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "极简logo,字母M,蓝色系,科技感" \
  --aspect-ratio 1:1 \
  --resolution 4K \
  --download \
  --output-dir "~/Desktop/项目Logo"
```

**结果**: 系统化的设计流程,获得高质量 Logo

---

## 场景总结

| 场景类型 | 推荐参数 | 示例编号 |
|---------|---------|---------|
| 社交媒体 | 1:1 或 9:16, 2K | 3, 4 |
| 壁纸 | 16:9 或 9:16, 4K | 5, 6 |
| 风格转换 | 原比例, 2K | 7, 8 |
| 创意融合 | 16:9, 4K | 9, 10 |
| 批量生成 | --no-wait | 11 |
| 程序化 | --json | 13 |
| 迭代优化 | 逐步增加细节 | 17 |

使用这些示例作为起点,根据实际需求调整参数!
