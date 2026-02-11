# 快速预设配置

常见使用场景的预设参数组合，开箱即用。

## 社交媒体预设

### Instagram 帖子 (1:1)

**适用场景:** Instagram 主页帖子、头像、Logo

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "你的描述" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download
```

**特点:**
- ✅ 正方形，适合 Instagram feed
- ✅ 2K 清晰度，快速生成（30-60秒）
- ✅ 自动下载到本地

---

### Instagram Stories (9:16)

**适用场景:** Instagram 故事、手机壁纸、竖屏短视频

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "你的描述" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download
```

**特点:**
- ✅ 竖屏，全屏显示
- ✅ 适合手机查看

---

### YouTube 封面 (16:9)

**适用场景:** YouTube 视频封面、演示文稿、横屏壁纸

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "你的描述" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download
```

**特点:**
- ✅ 横屏标准比例
- ✅ 4K 高清晰度
- ✅ 适合大屏显示

---

## 壁纸预设

### 桌面壁纸 (16:9 / 21:9)

**标准宽屏:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "风景/抽象描述" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download
```

**超宽屏:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "风景/抽象描述" \
  --aspect-ratio 21:9 \
  --resolution 4K \
  --download
```

**特点:**
- ✅ 4K 超高清
- ✅ 适合作为桌面背景

---

### 手机壁纸 (9:16)

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "简约/风景描述" \
  --aspect-ratio 9:16 \
  --resolution 2K \
  --download
```

**特点:**
- ✅ 竖屏全覆盖
- ✅ 2K 平衡质量和文件大小

---

## 打印预设

### 照片打印 (4:3)

**适用场景:** 传统相框、照片冲印

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "肖像/风景描述" \
  --aspect-ratio 4:3 \
  --resolution 4K \
  --output-format jpg \
  --download
```

**特点:**
- ✅ 4K 高清，适合打印
- ✅ JPG 格式，文件更小

---

### 艺术作品 (2:3 / 3:2)

**竖版 (肖像):**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "肖像/人物描述" \
  --aspect-ratio 2:3 \
  --resolution 4K \
  --download
```

**横版 (风景):**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "风景/场景描述" \
  --aspect-ratio 3:2 \
  --resolution 4K \
  --download
```

**特点:**
- ✅ 相机标准比例
- ✅ 适合专业打印

---

## 快速测试预设

### 提示词测试 (1K)

**适用场景:** 快速验证提示词效果

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "测试描述" \
  --resolution 1K
```

**特点:**
- ✅ 15-30秒快速生成
- ✅ 不下载，仅查看 URL
- ✅ 适合迭代调整提示词

---

### 草图预览 (1K + 不等待)

**适用场景:** 批量测试多个提示词

**命令:**
```bash
# 创建任务
python3 scripts/kie_nano_banana_api.py \
  --prompt "测试描述" \
  --resolution 1K \
  --no-wait

# 稍后查询（使用返回的 taskId）
python3 scripts/kie_nano_banana_api.py \
  --query \
  --task-id "your-task-id"
```

**特点:**
- ✅ 立即返回，不阻塞
- ✅ 适合批量提交

---

## 图生图预设

### 风格转换

**适用场景:** 将照片转为特定艺术风格

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "转为油画/水彩/赛博朋克风格，保持主体不变" \
  --image-input "https://example.com/photo.jpg" \
  --aspect-ratio auto \
  --resolution 2K \
  --download
```

**特点:**
- ✅ 使用 auto 自动匹配原图比例
- ✅ 清晰的风格转换描述

---

### 图像优化

**适用场景:** 提升图像质量、修复细节

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "提升图像清晰度和细节，增强色彩饱和度" \
  --image-input "https://example.com/low-res.jpg" \
  --resolution 4K \
  --download
```

**特点:**
- ✅ 升级到 4K 清晰度
- ✅ AI 增强细节

---

## 多图融合预设

### 风格混合

**适用场景:** 融合多个艺术风格

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "融合这些图像的艺术风格，创造独特的视觉效果" \
  --image-input "url1" "url2" "url3" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --download
```

**特点:**
- ✅ 最多支持 8 张图像
- ✅ 创意拼贴

---

## 工作流预设

### 完整创作流程

**第一步：快速测试提示词**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "你的初始描述" \
  --resolution 1K
```

**第二步：调整后生成 2K 版本**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "优化后的描述" \
  --aspect-ratio 16:9 \
  --resolution 2K \
  --download
```

**第三步：最终 4K 高清版本**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "最终确定的描述" \
  --aspect-ratio 16:9 \
  --resolution 4K \
  --download
```

---

## JSON 输出预设

### 脚本集成

**适用场景:** 在脚本或程序中使用

**命令:**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --aspect-ratio 1:1 \
  --resolution 2K \
  --json
```

**输出示例:**
```json
{
  "prompt": "描述",
  "imageUrls": ["https://..."],
  "imageCount": 1
}
```

**特点:**
- ✅ 易于解析
- ✅ 适合自动化流程

---

## 自定义预设模板

根据你的需求创建自己的预设：

```bash
# 社交媒体预设
--aspect-ratio 1:1 --resolution 2K --download

# 高质量输出预设
--aspect-ratio 16:9 --resolution 4K --download --output-format jpg

# 快速测试预设
--resolution 1K

# 异步批量预设
--resolution 2K --no-wait

# 脚本集成预设
--resolution 2K --json --download
```

---

## 选择建议

| 使用场景 | 推荐预设 | 理由 |
|---------|---------|------|
| 社交媒体分享 | 1:1 或 9:16, 2K | 快速生成，适合在线分享 |
| 桌面壁纸 | 16:9 或 21:9, 4K | 高清晰度，大屏显示 |
| 打印作品 | 4:3 或 2:3, 4K | 传统比例，高质量 |
| 快速测试 | 1:1, 1K | 快速验证效果 |
| 风格转换 | auto, 2K | 保持原图比例 |
| 创意融合 | 1:1, 2K | 平衡质量和速度 |

---

## 快速参考卡

**复制到终端中的命令模板：**

```bash
# 替换 "你的描述" 和参数即可使用

# 社交媒体
python3 scripts/kie_nano_banana_api.py --prompt "你的描述" --aspect-ratio 1:1 --resolution 2K --download

# 壁纸
python3 scripts/kie_nano_banana_api.py --prompt "你的描述" --aspect-ratio 16:9 --resolution 4K --download

# 快速测试
python3 scripts/kie_nano_banana_api.py --prompt "你的描述" --resolution 1K

# 图生图
python3 scripts/kie_nano_banana_api.py --prompt "你的描述" --image-input "图片URL" --resolution 2K --download
```
