# 🎬 giggle-drama - AI视频生成Skill

「姜式伙伴」AI 导演 - 智能视频创作助手

## 简介

这是一个用于生成AI视频的Claude Code / OpenClaw skill，基于Giggle.pro Trustee Mode V2 API。支持多种视频风格（3D动画、2D插画、电影写实等），可以通过简单的文字描述生成专业级短视频。

## 功能特性

- 🎨 **7种视频风格**：3D古风、2D漫剧、吉卜力、皮克斯、写实、二次元、国风水墨
- 📐 **灵活比例**：支持16:9横屏和9:16竖屏
- ⏱️ **可控时长**：auto/30/60/120/180/240/300秒
- 🔄 **全自动工作流**：创建→提交→支付→生成→**自动下载**一站式完成
- 📥 **自动下载**：视频生成后自动下载到本地 `~/Downloads/giggle-videos/` 目录
- 🔒 **安全配置**：使用.env文件管理API密钥

## 兼容性

- ✅ **Claude Code** (Anthropic官方)
- ✅ **OpenClaw** (开源替代品)
- ✅ 遵循 AgentSkills 标准格式

## 安装方法

### 在Claude Code中安装

1. 将此文件夹复制到 `~/.claude/skills/` 目录：
   ```bash
   cp -r giggle-drama ~/.claude/skills/
   ```

2. 安装Python依赖：
   ```bash
   cd ~/.claude/skills/giggle-drama
   pip3 install -r scripts/requirements.txt
   ```

3. 配置API密钥：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加你的 GIGGLE_API_KEY
   ```

### 在OpenClaw中安装

OpenClaw会自动识别skill依赖并提示安装。首次使用时：

1. OpenClaw会检测到缺少 `GIGGLE_API_KEY` 环境变量
2. 运行提示的安装命令
3. 编辑 `.env` 文件添加API密钥

或者手动安装：
```bash
cd <skill-directory>
pip3 install -r scripts/requirements.txt
cp .env.example .env
# 编辑 .env 添加 GIGGLE_API_KEY
```

## 使用方法

### 快速开始

调用skill：
```
/giggle-drama
```

然后按提示输入信息，或直接描述需求：
```
关于故乡记忆的短视频，回忆杀，16:9，写实风格，30s
```

### 参数说明

- **故事创意**（必需）：视频内容描述
- **视频比例**（必需）：16:9 或 9:16
- **项目名称**（必需）：给视频起个名字
- **视频时长**（可选）：auto/30/60/120/180/240/300秒
- **风格ID**（可选）：从7种风格中选择

### 可用风格

| ID  | 名称 | 分类 | 描述 |
|-----|------|------|------|
| 142 | 3D古风 | 3D动画 | CG渲染质感，史诗级幻想氛围 |
| 143 | 2D漫剧 | 2D插画 | 日漫国漫风格，低饱和配色 |
| 144 | 吉卜力 | 2D插画 | 治愈系手绘，温暖生活气息 |
| 145 | 皮克斯 | 3D动画 | 卡通动画，情绪表达强烈 |
| 146 | 写实风格 | 电影写实 | 真实光影，电影级镜头感 |
| 147 | 二次元 | 2D插画 | 动漫画风，色彩明亮丰富 |
| 148 | 国风水墨 | 2D插画 | 传统水墨，讲究留白意境 |

## 系统要求

- Python 3.7+
- 必需的Python包：requests, python-dotenv
- 有效的Giggle.pro API密钥
- 支持的操作系统：macOS, Linux, Windows

## 配置文件

- `.env` - 存储API密钥（不要提交到Git）
- `.env.example` - 配置模板
- `.gitignore` - Git忽略规则
- `SKILL.md` - Skill定义文件
- `CLAUDE.md` - 项目文档
- `scripts/trustee_api.py` - API客户端
- `scripts/requirements.txt` - Python依赖

## 安全提示

⚠️ **重要**：
- 永远不要将 `.env` 文件提交到Git仓库
- 不要在公开场合分享你的API密钥
- 使用 `.env.example` 作为配置模板

## 故障排除

### 错误：未找到API密钥

```bash
# 确保已创建.env文件
cp .env.example .env
# 编辑.env添加密钥
nano .env
```

### 错误：缺少Python包

```bash
pip3 install -r scripts/requirements.txt
```

### OpenClaw特定问题

如果OpenClaw无法识别环境变量：
1. 检查 `~/.openclaw/config.json` 中的环境变量配置
2. 重启OpenClaw
3. 手动设置环境变量：`export GIGGLE_API_KEY=your_key`

## 开发

### 项目结构

```
giggle-drama/
├── README.md               # 说明文档
├── SKILL.md               # Skill定义（AgentSkills标准）
├── CLAUDE.md              # Claude Code项目文档
├── .env.example           # 环境变量模板
├── .env                   # 实际配置（不提交）
├── .gitignore             # Git忽略规则
└── scripts/
    ├── requirements.txt   # Python依赖
    └── trustee_api.py     # API客户端
```

### 扩展开发

如需添加新功能：
1. 修改 `scripts/trustee_api.py` 添加API方法
2. 更新 `SKILL.md` 添加使用说明
3. 更新 `CLAUDE.md` 添加开发文档

## 许可证

请遵守Giggle.pro的服务条款和API使用限制。

## 反馈

如有问题或建议，请联系开发者。

---

**版本**: 1.0.0
**作者**: 姜式伙伴
**兼容**: Claude Code, OpenClaw
