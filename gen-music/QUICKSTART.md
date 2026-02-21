# 快速开始指南

**版本**: v2.2
**更新日期**: 2026-02-13

---

## ⚡ 5 分钟快速开始

### 步骤 1: 获取 API 密钥

访问 https://giggle.pro/api-key 获取你的 API 密钥

---

### 步骤 2: 配置 API 密钥（推荐使用 .env 文件）

```bash
# 1. 进入项目目录
cd gen-music

# 2. 复制示例文件
cp env.example .env

# 3. 编辑 .env 文件，替换为你的 API 密钥
# 使用你喜欢的编辑器打开 .env
nano .env  # 或 vim .env 或 code .env
```

**编辑内容：**
```env
# giggle.pro API 密钥配置
GIGGLE_API_KEY=sk_xxxxxxxxxxxxx  # 替换为你的真实密钥
```

---

### 步骤 3: 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 或者只安装必需的包
pip install requests python-dotenv
```

---

### 步骤 4: 生成你的第一首音乐

```bash
# 最简单的方式
python3 scripts/kie_suno_api.py --prompt "一首关于夏天的欢快流行歌"
```

**预期输出：**
```
✓ 已加载配置文件: /path/to/.env
使用简化模式生成音乐...
✓ 任务创建成功! TaskID: abc123xyz
等待任务完成（最多300秒）...
任务状态: PENDING
任务状态: TEXT_SUCCESS
任务状态: SUCCESS
✓ 任务完成!

生成了 2 首音乐

============================================================
音乐 #1
============================================================
音乐标题: Summer Vibes
歌词:
一首关于夏天的欢快流行歌

下载链接: https://assets.giggle.pro/audio/xxx-1.mp3
音乐风格: pop, upbeat, summer
```

---

## 🎵 常用命令

### 生成带歌词的歌曲

```bash
python3 scripts/kie_suno_api.py --custom \
  --prompt "[Verse 1]
夏日的阳光洒在海边
[Chorus]
这是属于我们的夏天" \
  --style "流行, 抒情" \
  --title "夏日时光"
```

---

### 生成纯音乐（无人声）

```bash
python3 scripts/kie_suno_api.py --prompt "古典钢琴，平静舒缓" --instrumental
```

---

### 自动下载到本地

```bash
python3 scripts/kie_suno_api.py --prompt "描述" --download
```

---

### JSON 格式输出

```bash
python3 scripts/kie_suno_api.py --prompt "描述" --json
```

---

## 🔧 常见问题

### Q: 提示 "错误: 未设置API密钥"

**解决方法：**

1. 检查 .env 文件是否存在：`ls -la .env`
2. 检查 .env 文件内容：`cat .env`
3. 确认 API 密钥格式正确（没有多余空格或引号）
4. 确认已安装 python-dotenv：`pip install python-dotenv`

---

### Q: 看不到 "✓ 已加载配置文件" 提示

**可能原因：**

1. python-dotenv 未安装
   ```bash
   pip install python-dotenv
   ```

2. .env 文件不在正确位置
   - 应该在项目根目录：`gen-music/.env`
   - 或当前工作目录

---

### Q: 生成音乐太慢

**解决方法：**

1. 检查网络连接
2. 使用异步模式：
   ```bash
   python3 scripts/kie_suno_api.py --prompt "描述" --no-wait
   # 稍后查询：
   python3 scripts/kie_suno_api.py --query --task-id "abc123xyz"
   ```

---

## 📚 更多资源

- **完整文档**: [SKILL.md](SKILL.md)
- **Bug 修复说明**: [BUGFIX_DOWNLOAD.md](BUGFIX_DOWNLOAD.md)
- **.env 配置详解**: [ENV_FILE_SUPPORT.md](ENV_FILE_SUPPORT.md)
- **测试输出示例**: [TEST_OUTPUT_EXAMPLE.md](TEST_OUTPUT_EXAMPLE.md)

---

## 🎯 推荐工作流

### 工作流 1: 快速探索

```bash
# 1. 快速生成多个版本
python3 scripts/kie_suno_api.py --prompt "轻松的爵士音乐"

# 2. 听音乐，选择喜欢的风格

# 3. 精细调整
python3 scripts/kie_suno_api.py --custom \
  --style "爵士, 轻快, 钢琴" \
  --title "午后时光" \
  --instrumental
```

---

### 工作流 2: 精确创作

```bash
# 1. 准备好歌词

# 2. 使用自定义模式
python3 scripts/kie_suno_api.py --custom \
  --prompt "你的完整歌词" \
  --style "你想要的风格" \
  --title "歌曲名称" \
  --vocal-gender female

# 3. 下载到本地
# 在脚本询问时选择 "是"
```

---

## 🚀 下一步

现在你已经掌握了基础用法，可以：

1. ✅ 查看 [SKILL.md](SKILL.md) 了解所有功能
2. ✅ 尝试不同的音乐风格和参数
3. ✅ 使用 `--help` 查看所有可用参数
4. ✅ 分享你的音乐创作！

---

**祝你创作愉快！** 🎵
