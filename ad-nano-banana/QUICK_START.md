# 🚀 快速开始 - .env 配置方式

## 📦 一分钟上手

```bash
# 1. 进入 skill 目录
cd ad-nano-banana

# 2. 复制配置模板
cp .env.example .env

# 3. 编辑 .env 文件（用你喜欢的编辑器）
vim .env  # 或者 nano .env

# 将这一行:
# KIE_API_KEY=your-api-key-here

# 改为你的真实密钥:
# KIE_API_KEY=sk-1234567890abcdef...

# 4. 保存并退出，然后测试
python3 scripts/kie_nano_banana_api.py --prompt "一只可爱的猫咪" --download
```

## 🔑 获取 API 密钥

访问: https://kie.ai/api-key

## ✅ 验证配置

```bash
# 脚本会显示配置加载状态
python3 scripts/kie_nano_banana_api.py --prompt "测试"

# 输出应包含:
# ✓ 已加载配置文件: /path/to/.env
```

## 🔒 安全提示

- ✅ `.env` 文件已被 Git 忽略，不会被提交
- ✅ 不要在命令行使用 `--api-key`（会留在历史记录中）
- ✅ 不要将 `.env` 文件分享给他人
- ✅ 定期更换 API 密钥

## 📋 配置优先级

如果同时存在多种配置，优先级为：

1. **命令行参数** `--api-key` (最高)
2. **环境变量** `export KIE_API_KEY=...`
3. **.env 文件** `KIE_API_KEY=...` (推荐)

## 🛠️ 可选: 安装 python-dotenv

脚本自动支持 `.env` 文件，但如果你想确保最佳兼容性：

```bash
pip3 install python-dotenv
```

**注意**: 即使不安装 `python-dotenv`，脚本仍可通过环境变量和命令行参数工作。

## 🔄 从旧方式迁移

**旧方式 (环境变量)**
```bash
export KIE_API_KEY="your-key"
python3 scripts/kie_nano_banana_api.py --prompt "测试"
```

**新方式 (.env 文件)**
```bash
# 一次配置，永久使用
echo 'KIE_API_KEY=your-key' > .env
python3 scripts/kie_nano_banana_api.py --prompt "测试"
```

## 💡 常见问题

### Q: 我的 .env 文件在哪里?

A: 应该在 `ad-nano-banana/` 目录下（与 `scripts/` 同级）

```
ad-nano-banana/
├── .env           ← 在这里
├── .env.example
├── scripts/
│   └── kie_nano_banana_api.py
└── ...
```

### Q: 脚本找不到 .env 文件?

A: 脚本会自动在以下位置查找：
1. 当前工作目录
2. 项目根目录 (scripts/ 的上级目录)

确保运行脚本时在正确的目录，或使用绝对路径。

### Q: 可以为不同项目使用不同的 API 密钥吗?

A: 可以！在每个项目目录下创建独立的 `.env` 文件即可。

## 📖 更多帮助

- 完整文档: `SKILL.md`
- 使用示例: `EXAMPLES.md`
- 故障排除: `TROUBLESHOOTING.md`
- 更新日志: `CHANGELOG.md`
