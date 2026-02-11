---
name: ad-generating-ai-music
description: 使用 Suno API（通过 kie.ai 平台）生成 AI 音乐。当用户需要创建、生成或创作音乐时使用此技能。支持场景：(1) 根据文本描述生成音乐，(2) 创作带歌词的歌曲，(3) 生成纯音乐/背景音乐，(4) 自定义音乐风格、人声性别和创意程度。触发关键词：生成音乐、创作歌曲、写歌、创建音乐、AI 作曲、音乐创作。
---

# AD Generating AI Music

使用 Suno API（通过 kie.ai 平台）生成 AI 音乐。支持从简单的文本描述到详细的自定义控制。

## 使用引导流程

**当用户请求"生成一首音乐"或类似模糊请求时，按以下流程引导：**

### 步骤 1: 询问是否已有歌词

使用 AskUserQuestion 工具询问：

```
问题: "您是否已经准备好了歌词？"
选项:
- "是，我已经有歌词了"
- "没有，想要纯音乐（无歌词）"
- "没有，让 AI 自动生成歌词"
```

### 步骤 2: 根据回答确定模式和收集信息

#### 情况 A：用户已有歌词 → **必须使用自定义模式**

**重要：自定义模式下 title、style、prompt 都是必需的！**

收集以下信息（全部必需）：
1. **歌词内容**（prompt）- 用户提供的完整歌词
2. **音乐风格**（style）- 如 "流行, 抒情" 或 "古典钢琴, 平静舒缓"
3. **歌曲标题**（title）- 歌曲名称，最多 80 字符

可选信息：
- 人声性别（--vocal-gender: male/female）
- 风格权重（--style-weight: 0-1）
- 创意程度（--weirdness-constraint: 0-1）

执行命令示例：
```bash
python3 scripts/kie_suno_api.py --custom \
  --prompt "[Verse 1]
歌词内容..." \
  --style "流行, 抒情" \
  --title "歌曲名称" \
  --vocal-gender female
```

#### 情况 B：用户想要纯音乐 → **可选简化或自定义模式**

**选项 1 - 简化模式（推荐）**：
- 只需提供音乐描述
- 命令：`--prompt "纯音乐描述" --instrumental`

**选项 2 - 自定义模式（精确控制）**：
- 必需：style（音乐风格）、title（标题）
- 自动添加：--instrumental
- 不需要：prompt

执行命令示例：
```bash
python3 scripts/kie_suno_api.py --custom \
  --style "古典钢琴, 平静舒缓" \
  --title "宁静时光" \
  --instrumental
```

#### 情况 C：让 AI 自动生成歌词 → **只能使用简化模式**

收集信息：
- 音乐描述（prompt）- 描述想要的音乐风格和主题

执行命令示例：
```bash
python3 scripts/kie_suno_api.py --prompt "一首关于友情的温暖民谣"
```

### 步骤 3: API 模式对照表

| 用户需求 | 使用模式 | 必需参数 | 命令标志 |
|---------|----------|---------|---------|
| 有歌词 | 自定义模式 | prompt, style, title | `--custom` |
| 纯音乐（精确控制） | 自定义模式 | style, title | `--custom --instrumental` |
| 纯音乐（快速） | 简化模式 | prompt | `--instrumental` |
| AI 生成歌词 | 简化模式 | prompt | 无 |

**重要提示：自定义模式下，title、style 始终是必需的；如果不是纯音乐（instrumental=False），prompt 也是必需的。**

### 步骤 4: 执行并询问保存

生成完成后，**主动询问**用户：
```
问题: "音乐已生成完成！是否将完整输出内容保存到文件？"
选项:
- "是，保存到下载文件夹"
- "不用，我只需要下载链接"
```

**如果用户选择保存，按以下步骤操作：**

1. **确定下载目录**（根据用户操作系统）：
   - **macOS/Linux**: `~/Downloads/`
   - **Windows**: `%USERPROFILE%\Downloads\` 或使用环境变量获取
   - 可通过检查环境变量或执行 `echo $HOME` / `echo %USERPROFILE%` 来确定

2. **生成文件名**：
   - 格式：`歌曲名称.txt`
   - 从输出的 `title` 字段获取歌曲名称
   - 清理文件名中的非法字符（如 `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`）
   - 如果有多首歌，为每首生成单独文件：`歌曲名称_1.txt`, `歌曲名称_2.txt`

3. **保存内容格式**：
   ```
   ============================================================
   音乐信息
   ============================================================
   音乐标题: [title]
   歌词:
   [完整歌词内容]

   下载链接: [audioUrl]
   音乐风格: [tags]

   生成时间: [当前时间]
   ============================================================
   ```

4. **使用 Write 工具保存文件**，并告知用户保存位置

**示例实现：**

```bash
# 1. 执行脚本获取输出
python3 scripts/kie_suno_api.py --prompt "描述"

# 2. 解析输出中的 title 字段
# 3. 确定下载目录（macOS: ~/Downloads/, Windows: %USERPROFILE%\Downloads\）
# 4. 使用 Write 工具保存
# 5. 告知用户：文件已保存到 [完整路径]
```

## 输出信息说明

脚本输出包含以下 4 个关键字段：
- **音乐标题**: 歌曲名称（AI 自动生成）
- **歌词**: 完整的歌词内容（保留原始格式和换行）
- **下载链接**: 音频文件 MP3 下载地址
- **音乐风格**: 音乐风格描述和标签

## Quick Start

### 1. 环境配置

**设置 API 密钥：**
```bash
export KIE_API_KEY="your-api-key-here"
```

获取 API 密钥：https://kie.ai/api-key

**验证配置：**
```bash
echo $KIE_API_KEY  # 应显示你的 API 密钥
```

### 2. 基本用法

生成音乐有两种模式：

- **简化模式** - 快速生成，只需描述
- **自定义模式** - 完全控制风格、歌词、标题等

## 音乐生成工作流

复制此检查清单并跟踪进度：

```
音乐生成进度：
- [ ] 步骤 1: 确认 API 密钥已设置
- [ ] 步骤 2: 选择生成模式（简化/自定义）
- [ ] 步骤 3: 准备提示词或歌词
- [ ] 步骤 4: 执行生成命令
- [ ] 步骤 5: 等待任务完成或记录 Task ID
- [ ] 步骤 6: 验证输出并保存音频链接
```

**决策树：**

1. **确定生成类型：**
   - 需要歌词？→ 使用自定义模式，准备歌词和风格
   - 纯音乐？→ 添加 `--instrumental` 标志
   - 快速原型？→ 使用简化模式

2. **准备参数：**
   - 简化模式：编写音乐描述（≤500 字符）
   - 自定义模式：准备风格、标题，可选歌词

3. **执行生成：**
   - 验证 KIE_API_KEY 环境变量已设置
   - 运行相应的 python3 命令
   - 选择是否等待完成（默认等待）

4. **处理结果：**
   - 成功：保存音频 URL 和元数据
   - 失败：检查错误信息，调整参数重试

## 交互式引导（重要）

**当用户请求模糊时（如"生成一首音乐"），必须按以下流程引导用户：**

### 完整引导流程示例

```
用户："生成一首音乐"

Claude：
"好的！在生成音乐之前，我需要了解一些信息。"

[使用 AskUserQuestion]
问题 1: "您是否已经准备好了歌词？"
选项:
- "是，我已经有歌词了"
- "没有，想要纯音乐（无歌词）"
- "没有，让 AI 自动生成歌词"

--- 情况 A: 用户选择"是，我已经有歌词了" ---

必须使用自定义模式（API 要求）

Claude 询问并收集信息：
1. "请提供您的歌词内容："
   用户输入完整歌词

2. "请描述音乐风格（如：流行、抒情、摇滚等）："
   用户输入：流行, 抒情

3. "请为歌曲起个标题："
   用户输入：我的歌

4. "是否需要指定人声性别？（可选）"
   选项：男声 / 女声 / 不指定

然后执行：
python3 scripts/kie_suno_api.py --custom \
  --prompt "用户的歌词" \
  --style "流行, 抒情" \
  --title "我的歌" \
  --vocal-gender female

--- 情况 B: 用户选择"没有，想要纯音乐（无歌词）" ---

Claude 询问：
"您想如何生成纯音乐？"
选项:
- "简化模式 - 我只描述想要的感觉，AI 自动处理（推荐）"
- "自定义模式 - 我想精确指定风格和标题"

如果选择简化模式：
  收集：音乐描述
  执行：python3 scripts/kie_suno_api.py --prompt "描述" --instrumental

如果选择自定义模式：
  收集：style（必需）、title（必需）
  执行：python3 scripts/kie_suno_api.py --custom \
    --style "古典钢琴" --title "标题" --instrumental

--- 情况 C: 用户选择"没有，让 AI 自动生成歌词" ---

只能使用简化模式（AI 会自动生成歌词）

Claude 询问：
"请描述您想要的音乐（AI 会根据描述自动生成歌词）："

用户输入：一首关于友情的温暖民谣

执行：python3 scripts/kie_suno_api.py --prompt "一首关于友情的温暖民谣"
```

### 生成完成后的保存引导

**在音乐生成成功后，主动询问用户是否保存输出：**

```
[使用 AskUserQuestion]
问题: "音乐已生成完成！是否将完整输出内容保存到文件？"
选项:
- "是，保存到下载文件夹"
- "不用，我只需要下载链接"
```

**如果用户选择保存：**

1. 判断操作系统和下载目录：
   ```bash
   # 在 macOS/Linux
   下载目录: ~/Downloads/

   # 在 Windows
   下载目录: %USERPROFILE%\Downloads\
   ```

2. 清理文件名（移除非法字符）：
   - 移除: `/` `\` `:` `*` `?` `"` `<` `>` `|`
   - 替换为: `-` 或 `_`

3. 为每首歌创建文件（如果生成了多首）：
   - 第一首: `歌曲名称.txt`
   - 第二首: `歌曲名称_2.txt`

4. 使用 Write 工具保存内容，格式：
   ```
   ============================================================
   音乐信息 - [歌曲名称]
   ============================================================
   音乐标题: [title]
   歌词:
   [完整歌词内容，保留所有换行]

   下载链接: [audioUrl]
   音乐风格: [tags]

   生成时间: [YYYY-MM-DD HH:MM:SS]
   ============================================================
   ```

5. 告知用户保存位置

## 简化模式

最简单的方式，仅需提供音乐描述。适合快速创作和探索。

### 基本示例

**示例 1: 流行歌曲**
```bash
python3 scripts/kie_suno_api.py --prompt "一首关于夏天的欢快流行歌"
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

**示例 2: 背景音乐**
```bash
python3 scripts/kie_suno_api.py --prompt "适合工作的舒缓背景音乐" --instrumental
```

### 排除特定风格

```bash
python3 scripts/kie_suno_api.py --prompt "现代电子音乐" --negative-tags "重金属, 说唱"
```

### 参数说明

- `--prompt`: 音乐描述（必需，最多 500 字符）
- `--instrumental`: 生成纯音乐（无歌词）
- `--negative-tags`: 排除的音乐风格
- `--model`: 模型版本（V4, V4_5, V4_5PLUS, V4_5ALL, V5），默认 V5

## 自定义模式

完全控制音乐的各个方面，适合精确创作。

**⚠️ 重要：自定义模式的必需参数**

自定义模式下，以下参数是**必需的**：
- `--style`: 音乐风格（必需）
- `--title`: 音乐标题（必需）
- `--prompt`: 歌词内容（如果不是纯音乐则必需）

**参数组合规则：**
1. **有歌词的歌曲**: 必须提供 `--style`、`--title`、`--prompt` 三个参数
2. **纯音乐**: 必须提供 `--style`、`--title`、`--instrumental`，不需要 `--prompt`

### 生成纯音乐

```bash
python3 scripts/kie_suno_api.py --custom \
  --style "古典钢琴, 平静舒缓" \
  --title "宁静时光" \
  --instrumental
```

### 创作带歌词的歌曲

```bash
python3 scripts/kie_suno_api.py --custom \
  --prompt "[Verse 1]\n歌词第一段\n[Chorus]\n副歌部分" \
  --style "流行, 抒情" \
  --title "我的歌曲" \
  --vocal-gender female
```

### 高级控制参数

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

### 参数说明

**必需参数（所有情况）：**
- `--custom`: 启用自定义模式
- `--style`: 音乐风格（V5 最多 1000 字符）- **必需**
- `--title`: 音乐标题（最多 80 字符）- **必需**

**条件必需参数：**
- `--prompt`: 歌词内容（V5 最多 5000 字符）
  - ✅ 有歌词的歌曲：**必需**
  - ❌ 纯音乐（使用 `--instrumental`）：不需要

**模式控制：**
- `--instrumental`: 生成纯音乐（无歌词）
  - 使用此参数时，不需要提供 `--prompt`

**可选参数：**
- `--vocal-gender`: 人声性别（male/female）
- `--negative-tags`: 排除的音乐风格
- `--style-weight`: 风格遵循强度（0-1，值越高越严格遵循风格）
- `--weirdness-constraint`: 创意/离散程度（0-1，值越高越有创意）
- `--audio-weight`: 音频要素权重（0-1，控制音频质量优先级）
- `--model`: 模型版本，默认 V5

**参数检查清单：**

| 场景 | `--style` | `--title` | `--prompt` | `--instrumental` |
|------|-----------|-----------|-----------|------------------|
| 有歌词的歌曲 | ✅ 必需 | ✅ 必需 | ✅ 必需 | ❌ 不要 |
| 纯音乐 | ✅ 必需 | ✅ 必需 | ❌ 不要 | ✅ 必需 |

## 任务管理

### 异步创建（不等待完成）

适合批量生成或长时间任务：

```bash
python3 scripts/kie_suno_api.py --prompt "摇滚音乐" --no-wait
```

**输出：**
```
✓ 任务创建成功! TaskID: abc123xyz
任务ID: abc123xyz
可使用以下命令查询: python scripts/kie_suno_api.py --query --task-id abc123xyz
```

### 查询任务状态

```bash
python3 scripts/kie_suno_api.py --query --task-id "abc123xyz"
```

### 调整等待参数

```bash
python3 scripts/kie_suno_api.py --prompt "描述" \
  --max-wait 600 \
  --poll-interval 15
```

- `--max-wait`: 最大等待时间（秒），默认 300
- `--poll-interval`: 轮询间隔（秒），默认 10

## 输出格式

### JSON 输出

便于程序化处理：

```bash
python3 scripts/kie_suno_api.py --prompt "音乐描述" --json
```

**输出结构：**
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

### 文本输出（默认）

默认输出格式化的文本，包含相同的 4 个字段。

## 错误处理

### API 密钥未设置

**错误信息：** "错误: 未设置API密钥"

**解决方法：**
```bash
export KIE_API_KEY="your-api-key"
# 验证
echo $KIE_API_KEY
```

### 敏感词错误

**错误信息：** 任务状态显示 `SENSITIVE_WORD_ERROR`

**解决方法：**
1. 检查 prompt 中的敏感词或不当内容
2. 修改表达方式，使用更中性的描述
3. 重新提交任务

### 字符限制错误

**错误信息：** "ValueError: 简化模式下 prompt 长度不能超过 500 字符"

**解决方法：**
- 简化模式：缩短 prompt 至 ≤500 字符
- 或切换到自定义模式（支持 ≤5000 字符）

### 任务超时

**错误信息：** "等待超时 (300秒)"

**解决方法：**
- 增加等待时间：`--max-wait 600`
- 或使用异步模式：`--no-wait`，稍后使用 `--query` 查询结果

### 任务失败

**错误信息：** 任务状态显示 `CREATE_TASK_FAILED` 或 `GENERATE_AUDIO_FAILED`

**解决方法：**
1. 查看返回的 `errorMessage` 字段获取详细错误信息
2. 根据错误信息调整参数
3. 检查网络连接和 API 配额
4. 重试任务

## 工作流程建议

### 快速原型

1. 使用简化模式快速测试想法：`--prompt "描述"`
2. 添加 `--instrumental` 或 `--negative-tags` 微调
3. 如需更多控制，切换到自定义模式

### 精确创作

1. 准备好歌词和风格描述
2. 使用自定义模式设置所有参数
3. 使用 `--json` 输出便于后续处理
4. 保存 Task ID 以便追踪和调试

### 批量生成

1. 使用 `--no-wait` 快速创建多个任务
2. 保存所有 Task ID 到文件
3. 编写脚本批量查询状态
4. 收集所有成功的音频 URL

**批量查询脚本示例：**
```bash
# 假设 Task ID 保存在 task_ids.txt
while read task_id; do
  python3 scripts/kie_suno_api.py --query --task-id "$task_id" --json
done < task_ids.txt
```

## 使用技巧

1. **简化模式优先** - 用于探索和快速迭代，找到大致方向
2. **自定义模式精调** - 确定风格后，用自定义模式精确控制
3. **JSON 输出自动化** - 使用 `--json` 便于脚本处理和数据分析
4. **V5 模型推荐** - 支持更长的 prompt（5000 字符）和 style（1000 字符）
5. **negative-tags 妙用** - 精准排除不想要的风格，如 "重金属, 快节奏鼓点"
6. **weirdness-constraint** - 值越高（接近 1.0），音乐越有创意/实验性；值越低（接近 0.0），音乐越常规
7. **任务追踪** - 保存 Task ID 便于问题排查和结果追踪

## Resources

### scripts/

- **kie_suno_api.py**: Suno API 封装脚本，支持简化和自定义两种模式生成音乐
  - 执行：`python3 scripts/kie_suno_api.py [参数]`
  - 帮助：`python3 scripts/kie_suno_api.py --help`
