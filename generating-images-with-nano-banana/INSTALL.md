# 安装说明

## 快速安装

### 方式 1: 使用 .skill 文件(推荐)

```bash
claude skills install generating-images-with-nano-banana.skill
```

### 方式 2: 使用 .zip 文件

```bash
# 下载 generating-images-with-nano-banana.zip
# 重命名为 .skill
mv generating-images-with-nano-banana.zip generating-images-with-nano-banana.skill

# 安装
claude skills install generating-images-with-nano-banana.skill
```

## 环境配置

### 1. 安装依赖

此技能需要 Python 3 和 requests 库:

```bash
pip3 install requests
```

### 2. 设置 API 密钥

```bash
export KIE_API_KEY="your-api-key-here"
```

**获取 API 密钥:**
访问 https://kie.ai/api-key 注册并获取您的 API 密钥。

### 3. 验证安装

```bash
# 检查技能是否已安装
claude skills list | grep generating-images-with-nano-banana

# 测试脚本
cd ~/.claude/skills/generating-images-with-nano-banana
python3 scripts/kie_nano_banana_api.py --help
```

## 快速开始

### 基础用法

```bash
python3 scripts/kie_nano_banana_api.py --prompt "一只可爱的猫咪"
```

### 在 Claude 中使用

直接在 Claude 对话中说:

```
"生成一张图片"
"帮我创建一张图像"
"画一只猫"
```

Claude 会自动使用此技能并引导您完成生成过程。

## 触发关键词

当您在 Claude 对话中使用以下关键词时,此技能会被触发:

- 生成图像
- 创建图片
- 画一张图
- AI 作画
- 图像生成
- 图片创作
- nano-banana

## 支持的功能

✅ **文生图** - 根据文字描述生成图像
✅ **图生图** - 使用参考图进行风格转换
✅ **多图融合** - 融合多张图像(最多8张)
✅ **自定义比例** - 支持 11 种图像比例
✅ **多种清晰度** - 1K/2K/4K 可选
✅ **交互式引导** - 完整的用户引导流程
✅ **任务管理** - 支持同步和异步模式
✅ **JSON 输出** - 便于程序化处理

## 常见问题

### Q: 安装后无法使用?

A: 检查以下几点:
1. API 密钥是否正确设置
2. Python 3 是否已安装
3. requests 库是否已安装

```bash
echo $KIE_API_KEY  # 检查 API 密钥
python3 --version  # 检查 Python 版本
pip3 show requests  # 检查 requests 库
```

### Q: 如何更新技能?

A: 重新安装即可:

```bash
claude skills install generating-images-with-nano-banana.skill
```

### Q: 如何卸载技能?

A: 使用 Claude CLI:

```bash
claude skills uninstall generating-images-with-nano-banana
```

或手动删除技能目录:

```bash
rm -rf ~/.claude/skills/generating-images-with-nano-banana
```

## 获取帮助

- **完整文档:** 查看 SKILL.md
- **输出示例:** 查看 TEST_OUTPUT_EXAMPLE.md
- **快速参考:** 查看 README.txt
- **技术支持:** 访问 https://kie.ai/support

## 版本信息

- **当前版本:** v1.0
- **发布日期:** 2026-02-11
- **支持的模型:** nano-banana-pro
