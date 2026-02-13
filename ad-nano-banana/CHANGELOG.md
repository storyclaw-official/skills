# 更新日志

## v1.2 - 2026-02-13

### ✨ 新功能

- **支持 .env 文件配置**：现在可以通过 `.env` 文件管理 API 密钥，提升安全性和便利性

### 🔧 改进

- **多种配置方式**：支持三种 API 密钥配置方式（优先级从高到低）：
  1. 命令行参数 `--api-key`
  2. 环境变量 `KIE_API_KEY`
  3. `.env` 文件中的 `KIE_API_KEY`

- **自动加载配置**：脚本启动时自动查找并加载 `.env` 文件（查找路径：当前目录 → 项目根目录）

- **优化错误提示**：未设置 API 密钥时，显示三种配置方式的详细说明

### 📄 文件变更

- **新增**: `.env.example` - 配置模板文件
- **修改**: `scripts/kie_nano_banana_api.py` - 添加 dotenv 支持
- **修改**: `README.txt` - 更新配置说明
- **修改**: `SKILL.md` - 更新环境配置部分
- **修改**: `TROUBLESHOOTING.md` - 添加 .env 相关故障排除
- **修改**: `.gitignore` - 添加 .env 忽略规则

### 🔒 安全改进

- `.env` 文件已加入 `.gitignore`，防止敏感信息泄漏到 Git 仓库
- 推荐使用 `.env` 文件存储密钥，避免命令历史泄漏

### 📖 使用示例

**快速开始**

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑 .env 文件，填入你的 API 密钥
# KIE_API_KEY=your-real-api-key

# 3. 直接运行脚本（自动加载 .env）
python3 scripts/kie_nano_banana_api.py --prompt "测试图像" --download
```

**配置优先级示例**

```bash
# .env 文件中的密钥（最低优先级）
# KIE_API_KEY=key-from-env-file

# 环境变量会覆盖 .env 文件
export KIE_API_KEY=key-from-environment

# 命令行参数优先级最高
python3 scripts/kie_nano_banana_api.py --api-key key-from-cli --prompt "测试"
```

### ⚙️ 技术细节

- 使用 `python-dotenv` 库加载 `.env` 文件
- 如果 `python-dotenv` 未安装，脚本仍可正常运行（降级到环境变量/命令行参数）
- `.env` 文件查找优先级：当前工作目录 → 项目根目录（`scripts/` 的上级目录）

### 🔄 向后兼容

- ✅ 完全兼容旧版使用方式（环境变量和命令行参数）
- ✅ 不需要强制安装 `python-dotenv`（可选依赖）
- ✅ 现有脚本和工作流无需修改

---

## v1.1 - 2026-02-11

- 优化工作流，添加反馈循环
- 实施渐进式文档披露
- 改进用户交互引导
