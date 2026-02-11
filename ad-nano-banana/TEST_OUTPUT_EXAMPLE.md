# 输出示例和格式说明

本文档展示 `kie_nano_banana_api.py` 脚本的各种输出格式和实际使用示例。

## 输出字段说明

脚本输出包含 3 个核心字段:

| 字段 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| **prompt** | string | 图像描述提示词 | "一只可爱的猫咪" |
| **imageUrls** | array | 生成的图像URL数组 | ["https://static.aiquickdraw.com/..."] |
| **imageCount** | integer | 生成的图像数量 | 1 |

## 文本格式输出示例

默认输出格式,适合直接阅读和查看。

### 示例 1: 基础文生图

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py --prompt "一只坐在窗边的橘猫"
```

**输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: abc123xyz
等待任务完成(最多300秒)...
任务状态: waiting
任务状态: waiting
任务状态: success
✓ 任务完成!

生成了 1 张图像

============================================================
图像生成完成
============================================================
提示词: 一只坐在窗边的橘猫
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/1763662100739_cat.png
============================================================
```

### 示例 2: 指定比例和清晰度

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "未来主义城市,赛博朋克风格,霓虹灯,夜景" \
  --aspect-ratio 16:9 \
  --resolution 4K
```

**输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: def456uvw
等待任务完成(最多300秒)...
任务状态: waiting
任务状态: waiting
任务状态: waiting
任务状态: success
✓ 任务完成!

生成了 1 张图像

============================================================
图像生成完成
============================================================
提示词: 未来主义城市,赛博朋克风格,霓虹灯,夜景
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/cyberpunk_city_4k.png
============================================================
```

### 示例 3: 图生图(风格转换)

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为油画风格,保留原始构图" \
  --image-input "https://example.com/original_photo.jpg" \
  --resolution 2K
```

**输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: ghi789rst
等待任务完成(最多300秒)...
任务状态: waiting
任务状态: waiting
任务状态: success
✓ 任务完成!

生成了 1 张图像

============================================================
图像生成完成
============================================================
提示词: 转为油画风格,保留原始构图
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/oil_painting_style.png
============================================================
```

### 示例 4: 多图融合

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合这三张图像的风格,创造独特的艺术作品" \
  --image-input "https://example.com/img1.jpg" "https://example.com/img2.jpg" "https://example.com/img3.jpg" \
  --aspect-ratio 16:9 \
  --resolution 4K
```

**输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: jkl012mno
等待任务完成(最多300秒)...
任务状态: waiting
任务状态: waiting
任务状态: waiting
任务状态: success
✓ 任务完成!

生成了 1 张图像

============================================================
图像生成完成
============================================================
提示词: 融合这三张图像的风格,创造独特的艺术作品
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/fusion_result.png
============================================================
```

### 示例 5: 异步模式(不等待完成)

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "复杂场景,高清晰度生成" \
  --resolution 4K \
  --no-wait
```

**输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: pqr345stu
任务ID: pqr345stu
可使用以下命令查询: python scripts/kie_nano_banana_api.py --query --task-id pqr345stu
```

### 示例 6: 查询任务状态

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py --query --task-id "pqr345stu"
```

**输出(任务等待中):**
```
查询任务: pqr345stu
任务状态: waiting
任务尚未完成或失败: waiting
```

**输出(任务完成):**
```
查询任务: pqr345stu
任务状态: success

生成了 1 张图像

============================================================
图像生成完成
============================================================
提示词: 复杂场景,高清晰度生成
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/complex_scene_4k.png
============================================================
```

### 示例 7: 任务失败

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py --prompt "测试失败场景"
```

**输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: vwx678yz
等待任务完成(最多300秒)...
任务状态: waiting
任务状态: fail
✗ 错误: 任务失败: 提示词包含敏感内容
```

## JSON 格式输出示例

使用 `--json` 参数输出 JSON 格式,便于程序化处理。

### 示例 1: 基础文生图(JSON)

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "一只可爱的猫咪" \
  --json
```

**输出:**
```json
{
  "prompt": "一只可爱的猫咪",
  "imageUrls": [
    "https://static.aiquickdraw.com/tools/example/1763662100739_cat.png"
  ],
  "imageCount": 1
}
```

### 示例 2: 指定参数(JSON)

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "山水风景,日落时分" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --json
```

**输出:**
```json
{
  "prompt": "山水风景,日落时分",
  "imageUrls": [
    "https://static.aiquickdraw.com/tools/example/landscape_sunset_4k.png"
  ],
  "imageCount": 1
}
```

### 示例 3: 图生图(JSON)

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为水彩画风格" \
  --image-input "https://example.com/photo.jpg" \
  --json
```

**输出:**
```json
{
  "prompt": "转为水彩画风格",
  "imageUrls": [
    "https://static.aiquickdraw.com/tools/example/watercolor_style.png"
  ],
  "imageCount": 1
}
```

### 示例 4: 多图融合(JSON)

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合所有图像的艺术风格" \
  --image-input "url1" "url2" "url3" "url4" \
  --json
```

**输出:**
```json
{
  "prompt": "融合所有图像的艺术风格",
  "imageUrls": [
    "https://static.aiquickdraw.com/tools/example/multi_fusion.png"
  ],
  "imageCount": 1
}
```

## 保存到文件示例

当用户选择保存生成信息时,文件格式和位置。

### 保存位置

**macOS/Linux:**
```
~/Downloads/nano_banana_20260211_143025.txt
```

**Windows:**
```
%USERPROFILE%\Downloads\nano_banana_20260211_143025.txt
```

### 文件内容格式

**示例 1: 文生图保存内容**

文件名: `nano_banana_20260211_143025.txt`

```
============================================================
图像生成信息
============================================================
提示词: 一只坐在窗边的橘猫,温暖的阳光洒进来
图像比例: 1:1
清晰度: 2K
输出格式: png
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/cat_window.png

生成时间: 2026-02-11 14:30:25
============================================================
```

**示例 2: 图生图保存内容**

文件名: `nano_banana_20260211_144512.txt`

```
============================================================
图像生成信息
============================================================
提示词: 转为油画风格,笔触明显,色彩浓郁
图像比例: 16:9
清晰度: 4K
输出格式: png
参考图像: https://example.com/original_photo.jpg
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/oil_painting.png

生成时间: 2026-02-11 14:45:12
============================================================
```

**示例 3: 多图融合保存内容**

文件名: `nano_banana_20260211_151820.txt`

```
============================================================
图像生成信息
============================================================
提示词: 融合这些图像的风格,创造独特的视觉效果
图像比例: 16:9
清晰度: 4K
输出格式: png
参考图像:
  - https://example.com/img1.jpg
  - https://example.com/img2.jpg
  - https://example.com/img3.jpg
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/fusion_result.png

生成时间: 2026-02-11 15:18:20
============================================================
```

## 错误输出示例

### 错误 1: API 密钥未设置

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py --prompt "测试"
```

**输出:**
```
错误: 未设置API密钥
请通过 --api-key 参数或环境变量 KIE_API_KEY 设置
获取API密钥: https://kie.ai/api-key
```

### 错误 2: 提示词过长

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py --prompt "非常长的提示词..."
```

**输出:**
```
创建图像生成任务...
✗ 错误: prompt 长度不能超过 20000 字符
```

### 错误 3: 参考图数量超限

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "测试" \
  --image-input "url1" "url2" "url3" "url4" "url5" "url6" "url7" "url8" "url9"
```

**输出:**
```
创建图像生成任务...
✗ 错误: 最多支持 8 张参考图像
```

### 错误 4: 任务超时

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "复杂场景" \
  --max-wait 10
```

**输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: timeout123
等待任务完成(最多10秒)...
任务状态: waiting
任务状态: waiting
✗ 错误: 等待超时 (10秒)
```

### 错误 5: API 错误

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py --prompt "测试" --api-key "invalid_key"
```

**输出:**
```
创建图像生成任务...
✗ 错误: 请求失败: 401 Client Error: Unauthorized for url: https://api.kie.ai/api/v1/jobs/createTask
```

## 进度输出示例

### 同步模式进度输出

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "测试图像生成" \
  --resolution 4K
```

**完整输出流程:**
```
创建图像生成任务...                              # 步骤1: 创建任务
✓ 任务创建成功! TaskID: progress123              # 步骤2: 获取taskId
等待任务完成(最多300秒)...                        # 步骤3: 开始轮询
任务状态: waiting                                # 步骤4: 第1次查询
任务状态: waiting                                # 步骤5: 第2次查询(5秒后)
任务状态: waiting                                # 步骤6: 第3次查询(再过5秒)
任务状态: success                                # 步骤7: 任务完成
✓ 任务完成!                                      # 步骤8: 确认完成

生成了 1 张图像                                  # 步骤9: 提取结果

============================================================
图像生成完成
============================================================
提示词: 测试图像生成
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/test_4k.png
============================================================
```

### 异步模式输出

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "高清场景" \
  --resolution 4K \
  --no-wait
```

**完整输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: async456
任务ID: async456
可使用以下命令查询: python scripts/kie_nano_banana_api.py --query --task-id async456
```

## 实际使用场景示例

### 场景 1: 社交媒体配图

**需求:** 为 Instagram 帖子生成 1:1 正方形配图

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "现代简约风格的咖啡杯,木质桌面,温暖的早晨光线,商业摄影" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --json
```

**输出:**
```json
{
  "prompt": "现代简约风格的咖啡杯,木质桌面,温暖的早晨光线,商业摄影",
  "imageUrls": [
    "https://static.aiquickdraw.com/tools/example/coffee_1x1_2k.png"
  ],
  "imageCount": 1
}
```

### 场景 2: 电脑壁纸生成

**需求:** 为显示器生成 16:9 横屏 4K 壁纸

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "宁静的山谷风景,清晨的薄雾,金色的阳光穿过树林,高细节风景摄影" \
  --aspect-ratio 16:9 \
  --resolution 4K
```

**输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: wallpaper789
等待任务完成(最多300秒)...
任务状态: waiting
任务状态: waiting
任务状态: waiting
任务状态: success
✓ 任务完成!

生成了 1 张图像

============================================================
图像生成完成
============================================================
提示词: 宁静的山谷风景,清晨的薄雾,金色的阳光穿过树林,高细节风景摄影
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/landscape_16x9_4k.png
============================================================
```

### 场景 3: 照片风格转换

**需求:** 将照片转换为油画风格

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为印象派油画风格,笔触明显,色彩浓郁,艺术感" \
  --image-input "https://example.com/my_photo.jpg" \
  --resolution 2K
```

**输出:**
```
创建图像生成任务...
✓ 任务创建成功! TaskID: transform101
等待任务完成(最多300秒)...
任务状态: waiting
任务状态: waiting
任务状态: success
✓ 任务完成!

生成了 1 张图像

============================================================
图像生成完成
============================================================
提示词: 转为印象派油画风格,笔触明显,色彩浓郁,艺术感
生成数量: 1 张

图像 #1: https://static.aiquickdraw.com/tools/example/impressionist_oil.png
============================================================
```

### 场景 4: 批量生成变体

**需求:** 生成同一主题的多个变体,用于选择最佳版本

**工作流程:**

```bash
# 第1个变体 - 异步创建
python3 scripts/kie_nano_banana_api.py \
  --prompt "现代简约logo,蓝色系,科技感" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --no-wait

# 输出: ✓ 任务创建成功! TaskID: variant1

# 第2个变体 - 调整风格
python3 scripts/kie_nano_banana_api.py \
  --prompt "现代简约logo,绿色系,自然感" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --no-wait

# 输出: ✓ 任务创建成功! TaskID: variant2

# 第3个变体 - 调整色彩
python3 scripts/kie_nano_banana_api.py \
  --prompt "现代简约logo,紫色系,创新感" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --no-wait

# 输出: ✓ 任务创建成功! TaskID: variant3

# 稍后批量查询
python3 scripts/kie_nano_banana_api.py --query --task-id variant1 --json
python3 scripts/kie_nano_banana_api.py --query --task-id variant2 --json
python3 scripts/kie_nano_banana_api.py --query --task-id variant3 --json
```

## 输出字段详细说明

### prompt 字段

- **类型:** string
- **说明:** 用户提供的原始图像描述提示词
- **用途:** 记录生成请求,便于追溯和复现
- **示例:**
  ```
  "一只坐在窗边的橘猫,温暖的阳光洒进来"
  ```

### imageUrls 字段

- **类型:** array of strings
- **说明:** 生成的图像 URL 数组(通常包含1个URL)
- **URL 格式:** `https://static.aiquickdraw.com/tools/example/[filename].png`
- **有效期:** URL 长期有效,建议及时下载保存
- **用途:** 直接访问下载生成的图像
- **示例:**
  ```json
  [
    "https://static.aiquickdraw.com/tools/example/1763662100739_cat.png"
  ]
  ```

### imageCount 字段

- **类型:** integer
- **说明:** 生成的图像数量(当前 API 总是生成1张)
- **取值范围:** 通常为 1
- **用途:** 便于程序化处理和验证
- **示例:**
  ```
  1
  ```

## 性能和时间参考

不同参数组合的预估生成时间:

| 清晰度 | 无参考图 | 1张参考图 | 多张参考图(3-8张) |
|-------|---------|----------|----------------|
| 1K | 15-30秒 | 20-40秒 | 30-60秒 |
| 2K | 30-60秒 | 40-80秒 | 60-120秒 |
| 4K | 60-120秒 | 80-150秒 | 120-240秒 |

**注意:** 实际时间受多种因素影响:
- API 服务器负载
- 提示词复杂度
- 参考图像大小和数量
- 网络延迟

## 总结

本文档展示了 `kie_nano_banana_api.py` 脚本的:

✅ **文本格式输出** - 适合直接阅读和查看
✅ **JSON 格式输出** - 适合程序化处理和集成
✅ **保存文件格式** - 便于归档和管理生成记录
✅ **错误输出示例** - 帮助快速排查问题
✅ **实际使用场景** - 展示真实工作流程

这些示例涵盖了所有主要使用模式:
- 文生图(基础)
- 图生图(风格转换)
- 多图融合(创意组合)
- 异步任务管理
- 批量生成工作流

使用这些示例作为参考,可以快速上手并根据实际需求调整参数。
