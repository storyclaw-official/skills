# 输出格式示例

## 文本格式输出（默认）

```bash
python3 scripts/kie_suno_api.py --prompt "一首欢快的流行歌曲"
```

**输出：**
```
使用简化模式生成音乐...
✓ 任务创建成功! TaskID: abc123xyz
等待任务完成（最多300秒）...
任务状态: PENDING
任务状态: TEXT_SUCCESS
任务状态: FIRST_SUCCESS
任务状态: SUCCESS
✓ 任务完成!

生成了 2 首音乐

============================================================
音乐 #1
============================================================
音乐标题: Summer Joy
歌词:
一首欢快的流行歌曲

下载链接: https://cdn.kie.ai/audio/xxx-1.mp3
音乐风格: pop, upbeat, energetic

============================================================
音乐 #2
============================================================
音乐标题: Happy Vibes
歌词:
一首欢快的流行歌曲

下载链接: https://cdn.kie.ai/audio/xxx-2.mp3
音乐风格: pop, cheerful, dance
```

---

## 自定义模式带歌词示例

```bash
python3 scripts/kie_suno_api.py --custom \
  --prompt "[Verse 1]
夏天的阳光照耀
微风轻轻吹过
[Chorus]
快乐的节奏在跳动
让我们一起歌唱" \
  --style "流行, 抒情" \
  --title "夏日时光" \
  --vocal-gender female
```

**输出：**
```
============================================================
音乐 #1
============================================================
音乐标题: 夏日时光
歌词:
[Verse 1]
夏天的阳光照耀
微风轻轻吹过
[Chorus]
快乐的节奏在跳动
让我们一起歌唱

下载链接: https://cdn.kie.ai/audio/xxx.mp3
音乐风格: pop, lyrical, female vocals, summer vibes
```

---

## 完整歌词示例

```bash
python3 scripts/kie_suno_api.py --custom \
  --prompt "[Verse 1]
（女）你说你只是路过
却记得我爱喝什么
十点半的那家角落
我们还是坐同一个位置

（男）你说最近睡得不错
其实眼圈一点都不合格
翻聊天记录像翻剧本
删了又看 以为自己洒脱

[Pre-Chorus]
（女）话到嘴边停在空气里
（男）连关心都练习成客气
（合）谁先退一步
谁就输了自己

[Chorus]
（合）关于迟到的勇气
我们都欠自己一句
那年如果多走一步靠近
是不是现在就不必演习" \
  --style "流行, 抒情, 对唱" \
  --title "关于迟到的勇气" \
  --vocal-gender female
```

**输出：**
```
============================================================
音乐 #1
============================================================
音乐标题: 关于迟到的勇气
歌词:
[Verse 1]
（女）你说你只是路过
却记得我爱喝什么
十点半的那家角落
我们还是坐同一个位置

（男）你说最近睡得不错
其实眼圈一点都不合格
翻聊天记录像翻剧本
删了又看 以为自己洒脱

[Pre-Chorus]
（女）话到嘴边停在空气里
（男）连关心都练习成客气
（合）谁先退一步
谁就输了自己

[Chorus]
（合）关于迟到的勇气
我们都欠自己一句
那年如果多走一步靠近
是不是现在就不必演习

下载链接: https://tempfile.aiquickdraw.com/r/c06db58dbe234f489f6fedf49bd80803.mp3
音乐风格: Mid-tempo Mandopop duet with male and female vocals trading lines. Clean piano and acoustic guitar in the verses, warm pad beds under the pre-chorus; chorus blooms with wide stereo drums, subtle synth arps, and stacked harmonies from both singers.
```

---

## JSON 格式输出

```bash
python3 scripts/kie_suno_api.py --prompt "一首欢快的流行歌曲" --json
```

**输出：**
```json
[
  {
    "title": "Summer Joy",
    "prompt": "一首欢快的流行歌曲",
    "audioUrl": "https://cdn.kie.ai/audio/xxx-1.mp3",
    "tags": "pop, upbeat, energetic"
  },
  {
    "title": "Happy Vibes",
    "prompt": "一首欢快的流行歌曲",
    "audioUrl": "https://cdn.kie.ai/audio/xxx-2.mp3",
    "tags": "pop, cheerful, dance"
  }
]
```

---

## 输出字段说明

| 显示名称 | JSON 字段 | 说明 | 示例 |
|---------|-----------|------|------|
| **音乐标题** | `title` | 歌曲名称（AI 自动生成） | "关于迟到的勇气" |
| **歌词** | `prompt` | 完整歌词（保留格式和换行） | "[Verse 1]\n歌词内容..." |
| **下载链接** | `audioUrl` | MP3 音频文件下载地址 | "https://cdn.kie.ai/..." |
| **音乐风格** | `tags` | 音乐风格描述和标签 | "Mid-tempo Mandopop duet..." |

---

## 格式特点

### 文本格式
- ✅ 使用分隔线和清晰的标题
- ✅ **歌词字段完整显示**，保留所有换行和格式
- ✅ 中文字段名称，更易读
- ✅ 适合人工阅读和查看

### JSON 格式
- ✅ 标准 JSON 数组格式
- ✅ 支持程序化处理
- ✅ 字段名称保持英文（API 标准）
- ✅ 适合脚本和自动化

---

## 注意事项

### 1. 歌词字段（prompt）
- **简化模式**：包含原始音乐描述
  - 示例：`"一首欢快的流行歌曲"`
- **自定义模式（有歌词）**：包含完整歌词结构
  - 示例：`"[Verse 1]\n歌词内容\n[Chorus]\n副歌"`
- **自定义模式（纯音乐）**：可能为空或包含风格描述
  - 示例：`""`

### 2. 下载链接（audioUrl）
- 直接可访问的 HTTPS 链接
- 支持浏览器播放和下载
- 有效期根据 API 平台规则（通常长期有效）

### 3. 音乐风格（tags）
- AI 自动生成的风格描述
- 可能包含：
  - 简短标签：`"pop, upbeat, energetic"`
  - 详细描述：`"Mid-tempo Mandopop duet with..."`
- 用于音乐分类、检索和推荐

### 4. 输出数量
- Suno API 通常每次生成 **2 首音乐变体**
- 每首音乐都有独立的下载链接
- JSON 格式返回数组，包含所有变体

---

## 实际使用示例

### 查看完整歌词
```bash
# 文本格式，歌词会完整显示
python3 scripts/kie_suno_api.py --custom \
  --prompt "$(cat lyrics.txt)" \
  --style "流行" \
  --title "我的歌"
```

### 批量处理（JSON）
```bash
# JSON 格式，便于脚本解析
python3 scripts/kie_suno_api.py --prompt "摇滚音乐" --json > output.json

# 提取所有下载链接
jq -r '.[].audioUrl' output.json

# 提取所有歌词
jq -r '.[].prompt' output.json
```

### 下载音频文件
```bash
# 使用 curl 下载
curl -o music.mp3 "https://cdn.kie.ai/audio/xxx.mp3"

# 使用 wget 下载
wget -O music.mp3 "https://cdn.kie.ai/audio/xxx.mp3"
```

---

## 保存完整输出到文件

### 场景说明

当生成的歌词很长时，终端输出可能不完整。可以将完整输出保存到文件便于查看和保存。

### 保存文件示例

**文件名格式**: `歌曲名称.txt`
**保存位置**: 用户的下载文件夹
- macOS/Linux: `~/Downloads/`
- Windows: `%USERPROFILE%\Downloads\`

**文件内容示例**:

```
============================================================
音乐信息 - 关于迟到的勇气
============================================================
音乐标题: 关于迟到的勇气
歌词:
[Verse 1]
（女）你说你只是路过
却记得我爱喝什么
十点半的那家角落
我们还是坐同一个位置

（男）你说最近睡得不错
其实眼圈一点都不合格
翻聊天记录像翻剧本
删了又看 以为自己洒脱

[Pre-Chorus]
（女）话到嘴边停在空气里
（男）连关心都练习成客气
（合）谁先退一步
谁就输了自己

[Chorus]
（合）关于迟到的勇气
我们都欠自己一句
那年如果多走一步靠近
是不是现在就不必演习
（女）学着说恭喜
（男）学着当朋友而已
（合）把想你的那句
藏在每一次 转身的背影里

[Verse 2]
（男）你说工作忙得刚好
就可以少一点乱想
生日那天关掉讯息
却还期待有谁会例外

（女）我说生活慢慢变好
只是笑得有点用力
逞强的人不敢停下
怕一停就会掉进回忆

[Pre-Chorus]
（男）手机亮了又暗下去
（女）你的名字还是不敢点起
（合）那一点在意
被我们装成礼仪

[Chorus]
（合）关于迟到的勇气
我们都欠自己一句
那年如果多走一步靠近
是不是现在就不必演习
（女）学着说恭喜
（男）学着当朋友而已
（合）把想你的那句
藏在每一次 转身的背影里

[Bridge]
（女）要不要 这次我先走过去
（男）要不要 这次我直接喊你
（合）就算世界 没有为我们暂停
至少承认 心还站在原地

[Chorus]
（合）关于迟到的勇气
就让它停在这里
如果明天我们还能相遇
就把那一句放在眼睛里
（女）不再只说恭喜
（男）不再只当朋友而已
（合）哪怕结局还是
路过的关系
也谢谢你 来过我的消息

下载链接: https://tempfile.aiquickdraw.com/r/c06db58dbe234f489f6fedf49bd80803.mp3
音乐风格: Mid-tempo Mandopop duet with male and female vocals trading lines. Clean piano and acoustic guitar in the verses, warm pad beds under the pre-chorus; chorus blooms with wide stereo drums, subtle synth arps, and stacked harmonies from both singers. Keep the groove gently driving, letting call-and-response phrasing shine, then strip back to piano and vocal for the bridge before a final, lifted chorus.

生成时间: 2026-02-11 16:30:45
============================================================
```

### 文件名清理规则

生成文件名时，需要移除或替换非法字符：

| 非法字符 | 替换为 |
|---------|--------|
| `/` | `-` |
| `\` | `-` |
| `:` | `-` |
| `*` | `` |
| `?` | `` |
| `"` | `'` |
| `<` | `(` |
| `>` | `)` |
| `|` | `-` |

**示例：**
- 原标题: `关于"迟到"的勇气?`
- 清理后: `关于'迟到'的勇气.txt`

### 多首歌曲的处理

如果生成了多首歌曲（通常是 2 首变体），为每首创建单独文件：

```
~/Downloads/关于迟到的勇气.txt
~/Downloads/关于迟到的勇气_2.txt
```

### 用户交互流程

**生成完成后，Claude 应主动询问：**

```
问题: "音乐已生成完成！是否将完整输出内容保存到文件？"
选项:
- "是，保存到下载文件夹"
- "不用，我只需要下载链接"
```

**如果用户选择"是"：**
1. Claude 判断用户操作系统
2. 确定下载文件夹路径
3. 清理文件名
4. 使用 Write 工具保存文件
5. 告知用户：`✅ 文件已保存到: ~/Downloads/关于迟到的勇气.txt`

### 手动保存方法

如果用户想手动保存，可以使用输出重定向：

```bash
# 保存到文件
python3 scripts/kie_suno_api.py --prompt "描述" > output.txt

# 保存 JSON 格式
python3 scripts/kie_suno_api.py --prompt "描述" --json > output.json
```
