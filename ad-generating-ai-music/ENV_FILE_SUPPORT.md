# 支持 .env 文件配置 API 密钥

**更新日期**: 2026-02-13
**版本**: v2.1 → v2.2

---

## 📝 更新说明

新增支持从项目目录下的 `.env` 文件读取 `KIE_API_KEY`，简化配置流程。

---

## ✨ 新增功能

### 1. 自动加载 .env 文件

脚本现在会自动查找并加载 `.env` 文件，优先级顺序：

1. **当前工作目录** - `./env`
2. **项目根目录** - `/path/to/ad-generating-ai-music/.env`

**加载成功提示：**
```
✓ 已加载配置文件: /path/to/ad-generating-ai-music/.env
```

---

### 2. 配置优先级

API 密钥的读取优先级：

| 优先级 | 方式 | 说明 |
|-------|------|------|
| **1** | 命令行参数 | `--api-key "your-key"` |
| **2** | 环境变量 | `export KIE_API_KEY="your-key"` |
| **3** | .env 文件 | `KIE_API_KEY=your-key` |

**优先级规则：**
- 命令行参数 > 环境变量 > .env 文件
- 如果多个方式都设置了，使用优先级最高的

---

## 🚀 快速开始

### 步骤 1: 创建 .env 文件

```bash
# 方法 1: 复制示例文件
cp .env.example .env

# 方法 2: 手动创建
cat > .env << 'EOF'
# kie.ai API 密钥配置
KIE_API_KEY=your-api-key-here
EOF
```

---

### 步骤 2: 编辑 .env 文件

将 `your-api-key-here` 替换为你的真实 API 密钥：

```env
# kie.ai API 密钥配置
# 获取 API 密钥: https://kie.ai/api-key

KIE_API_KEY=sk_xxxxxxxxxxxxx
```

---

### 步骤 3: 安装依赖

```bash
# 安装 python-dotenv（支持 .env 文件）
pip install python-dotenv

# 或安装所有依赖
pip install -r requirements.txt
```

**注意：** 如果没有安装 `python-dotenv`，脚本会自动回退到使用环境变量。

---

### 步骤 4: 运行脚本

```bash
# 直接运行，脚本会自动加载 .env 文件
python3 scripts/kie_suno_api.py --prompt "一首关于夏天的欢快流行歌"
```

**输出示例：**
```
✓ 已加载配置文件: /path/to/ad-generating-ai-music/.env
使用简化模式生成音乐...
✓ 任务创建成功! TaskID: abc123xyz
...
```

---

## 📁 文件结构

```
ad-generating-ai-music/
├── .env                  # 你的配置文件（不会提交到 Git）
├── .env.example          # 配置文件模板
├── .gitignore            # Git 忽略文件（已配置 .env）
├── requirements.txt      # Python 依赖（新增）
├── scripts/
│   └── kie_suno_api.py   # 主脚本（已更新）
└── SKILL.md              # 使用文档（已更新）
```

---

## 🔒 安全性

### .gitignore 配置

`.env` 文件已自动添加到 `.gitignore`，**不会被提交到 Git**：

```gitignore
# 环境变量文件（包含敏感信息）
.env
```

**重要提醒：**
- ✅ 只提交 `.env.example`（不包含真实密钥）
- ❌ 永远不要提交 `.env` 文件（包含真实密钥）
- ✅ 分享代码时，只分享 `.env.example`

---

## 🛠️ 代码实现细节

### 修改的代码部分

**1. 导入 dotenv（可选依赖）**

```python
# 尝试导入 dotenv，如果不存在则忽略
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
```

**2. 自动加载 .env 文件**

```python
def main():
    # 加载 .env 文件（如果存在）
    if DOTENV_AVAILABLE:
        # 查找 .env 文件：优先当前目录，然后脚本所在目录
        env_paths = [
            Path.cwd() / ".env",  # 当前工作目录
            Path(__file__).parent.parent / ".env"  # 项目根目录
        ]

        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"✓ 已加载配置文件: {env_path}", file=sys.stderr)
                break

    # 获取API密钥（优先级：命令行 > 环境变量 > .env 文件）
    api_key = args.api_key or os.getenv("KIE_API_KEY")
```

**3. 改进的错误提示**

```python
if not api_key:
    print("错误: 未设置API密钥", file=sys.stderr)
    print("", file=sys.stderr)
    print("请使用以下任意一种方式设置:", file=sys.stderr)
    print("  1. 在项目根目录创建 .env 文件，添加: KIE_API_KEY=your-api-key", file=sys.stderr)
    print("  2. 设置环境变量: export KIE_API_KEY=your-api-key", file=sys.stderr)
    print("  3. 使用命令行参数: --api-key your-api-key", file=sys.stderr)
```

---

## 🎯 使用场景对比

### 场景 1: 本地开发（推荐使用 .env）

```bash
# 一次性配置
cp .env.example .env
# 编辑 .env 添加 API 密钥

# 以后每次运行都无需设置
python3 scripts/kie_suno_api.py --prompt "描述"
```

**优势：**
- ✅ 无需每次设置环境变量
- ✅ 配置持久化
- ✅ 方便管理多个项目

---

### 场景 2: 临时使用（使用环境变量）

```bash
# 每次使用前设置
export KIE_API_KEY="your-key"
python3 scripts/kie_suno_api.py --prompt "描述"
```

**优势：**
- ✅ 不创建文件
- ✅ 适合临时测试

---

### 场景 3: CI/CD 环境（使用环境变量）

```yaml
# GitHub Actions 示例
env:
  KIE_API_KEY: ${{ secrets.KIE_API_KEY }}

steps:
  - run: python3 scripts/kie_suno_api.py --prompt "描述"
```

**优势：**
- ✅ 使用 Secrets 管理
- ✅ 不需要 .env 文件

---

## 📊 对比表格

| 特性 | .env 文件 | 环境变量 | 命令行参数 |
|-----|-----------|----------|-----------|
| **配置持久性** | ✅ 是 | ❌ 否 | ❌ 否 |
| **安全性** | ✅ 高（不提交到 Git） | ⚠️ 中 | ❌ 低（命令历史可见） |
| **使用便捷性** | ✅ 高（一次配置） | ⚠️ 中（每次设置） | ❌ 低（每次输入） |
| **推荐场景** | 本地开发 | CI/CD, 临时使用 | 测试, 覆盖配置 |

---

## ⚠️ 常见问题

### Q1: 没有安装 python-dotenv 会怎样？

**答：** 脚本会自动回退到使用环境变量，不会报错。

```bash
# 如果没有安装 python-dotenv
python3 scripts/kie_suno_api.py --prompt "描述"
# 仍然可以工作，但需要先设置环境变量
```

---

### Q2: .env 文件放在哪里？

**答：** 两个位置都可以（优先级从高到低）：

1. **当前工作目录** - 运行脚本时所在的目录
2. **项目根目录** - `ad-generating-ai-music/.env`

**推荐：** 放在项目根目录

---

### Q3: 如何验证 .env 文件是否加载？

**答：** 运行脚本时会显示加载提示：

```
✓ 已加载配置文件: /path/to/.env
```

如果没有这行提示，说明：
- .env 文件不存在
- python-dotenv 未安装

---

### Q4: .env 文件会被提交到 Git 吗？

**答：** 不会！`.gitignore` 已配置排除 `.env` 文件：

```bash
# 验证 .env 是否被忽略
git status
# 不应该看到 .env 文件
```

---

## 🔄 迁移指南

### 从环境变量迁移到 .env 文件

**步骤 1: 获取当前 API 密钥**

```bash
# macOS/Linux
echo $KIE_API_KEY

# Windows PowerShell
echo $env:KIE_API_KEY
```

**步骤 2: 创建 .env 文件**

```bash
echo "KIE_API_KEY=$KIE_API_KEY" > .env
```

**步骤 3: 验证**

```bash
python3 scripts/kie_suno_api.py --prompt "测试"
# 应该看到: ✓ 已加载配置文件: .env
```

**步骤 4: （可选）删除环境变量**

```bash
unset KIE_API_KEY  # macOS/Linux
```

---

## 📝 更新清单

### 新增文件

- [x] `.env.example` - 配置文件模板
- [x] `.gitignore` - Git 忽略文件
- [x] `requirements.txt` - Python 依赖列表
- [x] `ENV_FILE_SUPPORT.md` - 本文档

### 修改文件

- [x] `scripts/kie_suno_api.py` - 添加 .env 支持
- [x] `SKILL.md` - 更新环境配置说明
- [x] `README.txt` - 更新快速开始

### 功能增强

- [x] 自动查找并加载 .env 文件
- [x] 改进的错误提示（列出 3 种配置方式）
- [x] 兼容性处理（python-dotenv 可选）

---

## ✅ 测试清单

- [ ] 创建 .env 文件并运行脚本
- [ ] 验证 .env 加载提示
- [ ] 验证 .gitignore 配置（.env 不应出现在 git status）
- [ ] 测试不同配置优先级
- [ ] 测试没有 python-dotenv 的情况

---

**总结**: 现在可以使用更方便、更安全的 `.env` 文件管理 API 密钥，无需每次设置环境变量！
