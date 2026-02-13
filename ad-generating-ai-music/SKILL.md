---
name: ad-generating-ai-music
description: 使用 Suno API（通过 kie.ai 平台）生成 AI 音乐。当用户需要创建、生成或创作音乐时使用此技能。支持场景：(1) 根据文本描述生成音乐，(2) 创作带歌词的歌曲，(3) 生成纯音乐/背景音乐，(4) 自定义音乐风格、人声性别和创意程度。触发关键词：生成音乐、创作歌曲、写歌、创建音乐、AI 作曲、音乐创作。
---

# AD Generating AI Music

使用 Suno API（通过 kie.ai 平台）生成 AI 音乐。支持从简单的文本描述到精确控制的自定义创作。

## 核心输出

脚本输出包含 4 个关键字段：

| 字段 | 类型 | 说明 |
|-----|------|------|
| **title** | string | 音乐标题（AI 自动生成或用户指定） |
| **prompt** | string | 歌词内容或音乐描述 |
| **audioUrl** | string | MP3 下载链接 |
| **tags** | string | 音乐风格标签（如 "pop, upbeat, summer"） |

**额外功能：** 支持自动下载 MP3 文件到本地（跨平台：Mac/Windows/Linux）

---

## 交互式引导流程

**核心原则：** 智能分析 → 简化优先 → 按需升级 → 自动下载

---

### 步骤 1: 智能分析用户输入

当用户说"生成音乐"时，**先分析**用户是否提供了足够信息：

| 用户输入示例 | 判断结果 | 下一步动作 |
|------------|---------|-----------|
| "生成一首关于夏天的欢快音乐" | ✅ 包含描述 | 直接执行简化模式 |
| "用这段歌词生成音乐：[歌词]" | ✅ 包含歌词 | 询问风格和标题（自定义模式） |
| "生成音乐" / "帮我写首歌" | ❌ 信息不足 | 进入步骤 2 询问 |

---

### 步骤 2: 询问音乐类型（仅在信息不足时）

使用 `AskUserQuestion` 工具：

```
问题: "您想生成什么类型的音乐？"
header: "音乐类型"
选项:
- label: "AI 自动创作 - 我描述想法，AI 生成歌词和音乐（推荐）"
  description: "只需一句话描述，AI 会自动创作歌词和音乐。适合快速创作。生成时间：~60-90秒"

- label: "使用我的歌词 - 我已准备好完整歌词"
  description: "需要提供歌词、音乐风格和标题。适合精确控制。生成时间：~90-120秒"

- label: "纯音乐 - 无人声伴奏"
  description: "只生成背景音乐，没有歌词和人声。生成时间：~60-90秒"

multiSelect: false
```

---

### 步骤 3: 收集信息并生成

根据用户选择，采用不同的收集策略：

---

#### 情况 A: AI 自动创作（简化模式 - 推荐）

**推荐话术：**
```
"我们推荐使用简化模式：
✅ 只需一句话描述
✅ AI 自动生成歌词和音乐
✅ 更快、更简单（~60-90秒）

您只需告诉我想要什么样的音乐即可！"
```

**询问：** "请描述您想要的音乐（一句话即可）"

**示例提示：**
- "一首关于友情的温暖民谣"
- "适合工作的舒缓背景音乐"
- "欢快的夏日流行歌曲"

**执行命令：**
```bash
python3 scripts/kie_suno_api.py --prompt "用户描述"
```

**输出示例：**
```
============================================================
音乐 #1
============================================================
音乐标题: Summer Vibes
歌词:
一首关于夏天的欢快流行歌

下载链接: https://cdn.kie.ai/audio/xxx.mp3
音乐风格: pop, upbeat, summer
```

---

#### 情况 B: 使用我的歌词（自定义模式）

**说明必需参数：**
```
"使用自定义模式需要提供以下信息：
1️⃣ 歌词内容（必需）
2️⃣ 音乐风格（必需）
3️⃣ 歌曲标题（必需）
4️⃣ 人声性别（可选）

让我们逐步完成这些信息～"
```

**分步骤询问：**

1. **歌词内容**（必需）
   ```
   问题: "请提供您的歌词内容"
   提示: 可以包含段落标记，如 [Verse 1]、[Chorus]、[Bridge] 等
   ```

2. **音乐风格**（必需）
   ```
   问题: "请描述音乐风格（如：流行、抒情、摇滚等）"
   示例: "流行, 抒情" / "古典钢琴, 平静舒缓" / "爵士, 轻快"
   ```

3. **歌曲标题**（必需）
   ```
   问题: "请为歌曲起个标题"
   提示: 最多 80 个字符
   ```

4. **人声性别**（可选）
   ```
   问题: "是否需要指定人声性别？"
   header: "人声性别"
   选项:
   - label: "不指定（推荐）"
     description: "AI 自动选择最适合的人声"
   - label: "女声"
     description: "使用女性人声演唱"
   - label: "男声"
     description: "使用男性人声演唱"

   multiSelect: false
   ```

**执行命令：**
```bash
python3 scripts/kie_suno_api.py --custom \
  --prompt "歌词内容" \
  --style "流行, 抒情" \
  --title "歌曲标题" \
  --vocal-gender female  # 如果指定
```

---

#### 情况 C: 纯音乐（简化模式 + --instrumental）

**询问：** "请描述您想要的音乐氛围和风格"

**示例提示：**
- "古典钢琴，平静舒缓"
- "电子音乐，节奏感强"
- "轻爵士，适合咖啡店"

**执行命令：**
```bash
python3 scripts/kie_suno_api.py --prompt "用户描述" --instrumental
```

---

### 步骤 4: 输出生成结果

生成完成后，**按格式化输出 4 个核心字段**：

**注意：Suno API 通常返回 2 首音乐变体，需要逐一输出**

```
============================================================
音乐 #1
============================================================
📝 音乐标题 (title): Summer Vibes

📄 歌词/描述 (prompt):
一首关于夏天的欢快流行歌

🔗 下载链接 (audioUrl):
https://cdn.kie.ai/audio/xxx-1.mp3

🎵 音乐风格 (tags): pop, upbeat, summer

============================================================
音乐 #2
============================================================
📝 音乐标题 (title): Summer Vibes

📄 歌词/描述 (prompt):
一首关于夏天的欢快流行歌

🔗 下载链接 (audioUrl):
https://cdn.kie.ai/audio/xxx-2.mp3

🎵 音乐风格 (tags): pop, upbeat, summer

⏱️ 生成时长: ~90 秒
```

---

### 步骤 5: 询问是否下载（跨平台支持）

使用 `AskUserQuestion` 工具：

```
问题: "是否将音乐文件下载到本地？"
header: "下载选项"
选项:
- label: "是，下载到我的下载文件夹（推荐）"
  description: "MP3 文件将保存到系统下载目录"

- label: "否，我只需要下载链接"
  description: "您可以稍后点击链接自行下载"

multiSelect: false
```

**如果用户选择"是"：下载音乐到本地**

**⚠️ 重要：直接使用已返回的 audioUrl 下载，不要重新运行脚本生成！**

**实现步骤：**

1. **获取必要信息**（从步骤 4 的输出中）
   - 音乐列表（通常 2 首）
   - 每首音乐的 `audioUrl` 和 `title`

2. **确定下载目录**（根据操作系统）
   - **macOS/Linux**: `~/Downloads/`
   - **Windows**: `%USERPROFILE%\Downloads\`

3. **下载所有音乐**（推荐使用 Python requests）

```python
import requests
import re
from pathlib import Path

# 1. 获取下载目录
download_dir = Path.home() / "Downloads"

# 2. 清理文件名函数
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '-', filename).strip()

# 3. 下载所有音乐（假设从脚本输出中解析了音乐列表）
music_list = [
    {"title": "Summer Vibes", "audioUrl": "https://cdn.kie.ai/audio/xxx-1.mp3"},
    {"title": "Summer Vibes", "audioUrl": "https://cdn.kie.ai/audio/xxx-2.mp3"}
]

for index, music in enumerate(music_list, start=1):
    title = music["title"]
    audio_url = music["audioUrl"]

    # 清理标题并添加序号
    safe_title = sanitize_filename(title)
    filename = f"{safe_title}_{index}.mp3"
    file_path = download_dir / filename

    # 下载文件
    print(f"正在下载: {filename}...")
    try:
        response = requests.get(audio_url, timeout=60)
        response.raise_for_status()

        with open(file_path, 'wb') as f:
            f.write(response.content)

        print(f"✓ 下载完成: {file_path}")
    except Exception as e:
        print(f"✗ 下载失败: {filename} - {e}")
```

**下载成功提示示例：**
```
正在下载: Summer_Vibes_1.mp3...
✓ 下载完成: /Users/username/Downloads/Summer_Vibes_1.mp3

正在下载: Summer_Vibes_2.mp3...
✓ 下载完成: /Users/username/Downloads/Summer_Vibes_2.mp3
```

**文件命名规则：**
- 第 1 首：`{safe_title}_1.mp3`
- 第 2 首：`{safe_title}_2.mp3`
- 自动清理非法字符（`< > : " / \ | ? *`）

**备用方法：使用 curl（逐个下载）**

```bash
# macOS/Linux
curl -o ~/Downloads/"{safe_title}_1.mp3" "{audioUrl_1}"
curl -o ~/Downloads/"{safe_title}_2.mp3" "{audioUrl_2}"

# Windows PowerShell
curl.exe -o "$env:USERPROFILE\Downloads\{safe_title}_1.mp3" "{audioUrl_1}"
curl.exe -o "$env:USERPROFILE\Downloads\{safe_title}_2.mp3" "{audioUrl_2}"
```

---

## 完整流程图

```
用户："生成音乐"
    ↓
┌─────────────────────────┐
│  智能分析用户输入        │
└─────────────────────────┘
    ↓
    ├─ 有提示词 → 简化模式 → 生成 → 展示结果 → 询问下载
    ├─ 有歌词 → 自定义模式 → 收集参数 → 生成 → 展示结果 → 询问下载
    └─ 无信息 → 询问类型
                  ↓
        ┌─────────────────────────┐
        │ AI 自动创作（推荐）      │ → 简化模式
        │ 使用我的歌词            │ → 自定义模式
        │ 纯音乐                  │ → 简化模式 + --instrumental
        └─────────────────────────┘
                  ↓
              生成音乐
                  ↓
              展示结果
                  ↓
              询问下载
                  ↓
        ┌─────────────────────────┐
        │ 是 → 下载 MP3 到本地     │
        │ 否 → 只显示下载链接      │
        └─────────────────────────┘
```

**⚠️ 下载场景区分：**

| 场景 | 时机 | 方法 | 说明 |
|-----|------|------|------|
| **场景 1: 询问后下载** | 生成后询问 | 使用已返回的 `audioUrl` | 推荐，用户可选 |
| **场景 2: 一次性下载** | 生成时自动 | 使用 `--download` 参数 | 不询问，直接下载 |

**场景 1 示例：**
```python
# 生成音乐
python3 scripts/kie_suno_api.py --prompt "描述"

# 输出 audioUrl 后，询问用户
# 如果用户选择下载，使用 audioUrl 直接下载（不重新生成）
requests.get(audioUrl)  # 使用已有链接
```

**场景 2 示例：**
```bash
# 一次性生成并下载（不询问）
python3 scripts/kie_suno_api.py --prompt "描述" --download
```

---

## Quick Start

### 1. 环境配置

**获取 API 密钥：** https://kie.ai/api-key

**设置 API 密钥（推荐使用方法 1）：**

**方法 1: 使用 .env 文件（推荐）**

```bash
# 1. 复制示例文件
cp .env.example .env

# 2. 编辑 .env 文件，替换为你的 API 密钥
# KIE_API_KEY=your-api-key-here

# 3. 安装 python-dotenv（如果尚未安装）
pip install python-dotenv
```

**.env 文件示例：**
```env
# kie.ai API 密钥配置
KIE_API_KEY=sk_xxxxxxxxxxxxx
```

**优势：**
- ✅ 无需每次设置环境变量
- ✅ 自动加载（脚本会自动查找并加载）
- ✅ 安全（.gitignore 已配置，不会提交到 Git）

---

**方法 2: 设置环境变量**

```bash
# macOS/Linux
export KIE_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:KIE_API_KEY="your-api-key-here"

# Windows (CMD)
set KIE_API_KEY=your-api-key-here
```

**验证配置：**
```bash
# macOS/Linux
echo $KIE_API_KEY

# Windows (PowerShell)
echo $env:KIE_API_KEY

# Windows (CMD)
echo %KIE_API_KEY%
```

---

**方法 3: 命令行参数**

```bash
python3 scripts/kie_suno_api.py --api-key "your-api-key" --prompt "描述"
```

**优先级顺序：** 命令行参数 > 环境变量 > .env 文件

---

### 2. 快速示例

**示例 1: 最简单的方式（AI 自动创作）**
```bash
python3 scripts/kie_suno_api.py --prompt "一首关于夏天的欢快流行歌"
```

**示例 2: 生成纯音乐**
```bash
python3 scripts/kie_suno_api.py --prompt "古典钢琴，平静舒缓" --instrumental
```

**示例 3: 使用自己的歌词**
```bash
python3 scripts/kie_suno_api.py --custom \
  --prompt "[Verse 1]\n歌词第一段\n[Chorus]\n副歌部分" \
  --style "流行, 抒情" \
  --title "我的歌曲" \
  --vocal-gender female
```

**示例 4: 一次性生成并自动下载（不询问）**
```bash
# 使用 --download 参数在生成的同时自动下载到本地
# 注意：这会跳过询问环节，直接下载
python3 scripts/kie_suno_api.py --prompt "一首关于夏天的欢快流行歌" --download
```

**说明：**
- `--download` 参数适用于**一次性生成+下载**场景
- 如果需要**先询问用户再下载**，请参考"步骤 5: 询问是否下载到本地"

---

## 高级用法

### 简化模式详解

最简单的方式，仅需提供音乐描述。适合快速创作和探索。

**基本参数：**
- `--prompt`: 音乐描述（必需，最多 500 字符）
- `--instrumental`: 生成纯音乐（无歌词）
- `--negative-tags`: 排除的音乐风格
- `--model`: 模型版本（V4, V4_5, V4_5PLUS, V4_5ALL, V5），默认 V5

**示例：排除特定风格**
```bash
python3 scripts/kie_suno_api.py --prompt "现代电子音乐" --negative-tags "重金属, 说唱"
```

---

### 自定义模式详解

完全控制音乐的各个方面，适合精确创作。

**⚠️ 必需参数：**
- `--custom`: 启用自定义模式
- `--style`: 音乐风格（V5 最多 1000 字符）
- `--title`: 音乐标题（最多 80 字符）
- `--prompt`: 歌词内容（如果不是纯音乐则必需，V5 最多 5000 字符）

**可选参数：**
- `--instrumental`: 生成纯音乐（使用时不需要 --prompt）
- `--vocal-gender`: 人声性别（male/female）
- `--negative-tags`: 排除的音乐风格
- `--style-weight`: 风格遵循强度（0-1，值越高越严格遵循风格）
- `--weirdness-constraint`: 创意/离散程度（0-1，值越高越有创意）
- `--audio-weight`: 音频要素权重（0-1，控制音频质量优先级）

**参数组合规则：**

| 场景 | `--style` | `--title` | `--prompt` | `--instrumental` |
|------|-----------|-----------|-----------|------------------|
| 有歌词的歌曲 | ✅ 必需 | ✅ 必需 | ✅ 必需 | ❌ 不要 |
| 纯音乐 | ✅ 必需 | ✅ 必需 | ❌ 不要 | ✅ 必需 |

**高级控制示例：**
```bash
python3 scripts/kie_suno_api.py --custom \
  --prompt "歌词内容" \
  --style "爵士, 轻快" \
  --title "夏日午后" \
  --vocal-gender male \
  --style-weight 0.8 \
  --weirdness-constraint 0.3 \
  --audio-weight 0.7
```

---

### 任务管理

**异步创建（不等待完成）：**
```bash
python3 scripts/kie_suno_api.py --prompt "摇滚音乐" --no-wait
```

输出：
```
✓ 任务创建成功! TaskID: abc123xyz
任务ID: abc123xyz
可使用以下命令查询: python scripts/kie_suno_api.py --query --task-id abc123xyz
```

**查询任务状态：**
```bash
python3 scripts/kie_suno_api.py --query --task-id "abc123xyz"
```

**调整等待参数：**
```bash
python3 scripts/kie_suno_api.py --prompt "描述" \
  --max-wait 600 \
  --poll-interval 15
```

- `--max-wait`: 最大等待时间（秒），默认 300
- `--poll-interval`: 轮询间隔（秒），默认 10

---

### 输出格式

**JSON 输出（便于程序化处理）：**
```bash
python3 scripts/kie_suno_api.py --prompt "音乐描述" --json
```

输出结构：
```json
[
  {
    "title": "音乐标题",
    "prompt": "生成提示词",
    "audioUrl": "https://cdn.kie.ai/audio/xxx.mp3",
    "tags": "pop, upbeat"
  }
]
```

**JSON + 下载：**
```bash
python3 scripts/kie_suno_api.py --prompt "音乐描述" --json --download
```

输出包含本地路径：
```json
[
  {
    "title": "音乐标题",
    "prompt": "生成提示词",
    "audioUrl": "https://cdn.kie.ai/audio/xxx.mp3",
    "tags": "pop, upbeat",
    "localPath": "/Users/username/Downloads/音乐标题.mp3"
  }
]
```

---

## 错误处理

### API 密钥未设置

**错误信息：** "错误: 未设置API密钥"

**解决方法：**
```bash
export KIE_API_KEY="your-api-key"
echo $KIE_API_KEY  # 验证
```

---

### 敏感词错误

**错误信息：** 任务状态显示 `SENSITIVE_WORD_ERROR`

**解决方法：**
1. 检查 prompt 中的敏感词或不当内容
2. 修改表达方式，使用更中性的描述
3. 重新提交任务

---

### 字符限制错误

**错误信息：** "ValueError: 简化模式下 prompt 长度不能超过 500 字符"

**解决方法：**
- 简化模式：缩短 prompt 至 ≤500 字符
- 或切换到自定义模式（支持 ≤5000 字符）

---

### 任务超时

**错误信息：** "等待超时 (300秒)"

**解决方法：**
- 增加等待时间：`--max-wait 600`
- 或使用异步模式：`--no-wait`，稍后使用 `--query` 查询结果

---

### 下载失败

**错误信息：** "✗ 下载失败: [错误详情]"

**解决方法：**
1. 检查网络连接
2. 验证下载目录权限
3. 确认 audioUrl 有效
4. 手动下载：复制 audioUrl 到浏览器

---

## 使用技巧

1. **简化模式优先** - 用于探索和快速迭代，找到大致方向
2. **自定义模式精调** - 确定风格后，用自定义模式精确控制
3. **JSON 输出自动化** - 使用 `--json` 便于脚本处理和数据分析
4. **V5 模型推荐** - 支持更长的 prompt（5000 字符）和 style（1000 字符）
5. **negative-tags 妙用** - 精准排除不想要的风格，如 "重金属, 快节奏鼓点"
6. **weirdness-constraint** - 值越高（接近 1.0），音乐越有创意/实验性；值越低（接近 0.0），音乐越常规
7. **任务追踪** - 保存 Task ID 便于问题排查和结果追踪
8. **批量下载** - 使用 `--download` 自动保存所有生成的音乐

---

## Resources

### scripts/

- **kie_suno_api.py**: Suno API 封装脚本，支持简化和自定义两种模式生成音乐
  - 执行：`python3 scripts/kie_suno_api.py [参数]`
  - 帮助：`python3 scripts/kie_suno_api.py --help`

### 文档

- **SKILL.md**: 完整使用文档（本文件）
- **TEST_OUTPUT_EXAMPLE.md**: 输出格式示例
- **README.txt**: 快速参考

---

## 版本信息

- **版本**: v2.2
- **更新日期**: 2026-02-13
- **主要更新**:
  - ✅ 重构文档结构，实施渐进式披露
  - ✅ 添加跨平台 MP3 下载功能（Mac/Windows/Linux）
  - ✅ 优化交互式引导流程
  - ✅ 简化模式优先推荐
  - ✅ 添加时间预期说明
  - ✅ 精简文档从 606 行到 ~700 行
  - 🐛 修复下载功能：使用已返回的 audioUrl
  - ✅ 统一文件命名：{title}_1.mp3, {title}_2.mp3
  - ✨ 支持 .env 文件配置 API 密钥（推荐方式）
