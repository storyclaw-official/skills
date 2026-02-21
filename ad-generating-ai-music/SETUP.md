# 环境配置

## 1. 配置 API 密钥

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入 giggle.pro API 密钥：

```env
GIGGLE_API_KEY=your-api-key-here
```

## 2. 安装依赖

```bash
pip install requests python-dotenv
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

## 3. 验证

```bash
python3 scripts/giggle_music_api.py --prompt "测试" --no-wait
```

看到 `✓ 任务创建成功!` 即配置成功。

## 注意事项

- `.env` 文件已在 `.gitignore` 中，不会被提交
- 脚本会依次查找：当前目录 `.env` → 项目根目录 `.env`
- 如果 python-dotenv 未安装，脚本会跳过 .env 加载并提示错误
