# 故障排除指南

## 目录

- [环境配置问题](#环境配置问题)
- [API 相关错误](#api-相关错误)
- [参数验证错误](#参数验证错误)
- [任务执行错误](#任务执行错误)
- [下载相关错误](#下载相关错误)
- [性能和超时](#性能和超时)

---

## 环境配置问题

### 未设置 API 密钥

```
错误: 未设置API密钥
```

**解决方案（三选一）:**

**方法 1: .env 文件（推荐）**
```bash
cp env.example .env
# 编辑 .env，将 GIGGLE_API_KEY=your-api-key-here 改为真实密钥
```

**方法 2: 环境变量**
```bash
export GIGGLE_API_KEY="your-api-key-here"
# 永久设置：echo 'export GIGGLE_API_KEY="your-key"' >> ~/.zshrc
```

**方法 3: 命令行参数**
```bash
python3 scripts/kie_nano_banana_api.py --prompt "描述" --api-key "your-key"
```

获取密钥: https://kie.ai/api-key

---

### Python 模块未找到

```
ModuleNotFoundError: No module named 'requests'
```

```bash
pip3 install requests
```

---

### 脚本执行权限错误

```
Permission denied: scripts/kie_nano_banana_api.py
```

```bash
chmod +x scripts/kie_nano_banana_api.py
```

---

## API 相关错误

### 401 Unauthorized

API 密钥无效或已过期，重新获取: https://kie.ai/api-key

确保密钥没有多余的空格或换行符：`echo $GIGGLE_API_KEY`

### 429 Too Many Requests

请求频率超限，增加轮询间隔：

```bash
python3 scripts/kie_nano_banana_api.py --prompt "描述" --poll-interval 10
```

### 网络连接错误

```
ConnectionError: Failed to connect to api.kie.ai
```

检查网络连接，如需代理：
```bash
export https_proxy=http://your-proxy:port
```

---

## 参数验证错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `prompt 长度不能超过 20000 字符` | 提示词过长 | 精简描述 |
| `最多支持 8 张参考图像` | --image-input 超限 | 减少参考图数量 |
| `invalid choice: '16:10'` | 比例值无效 | 查看有效选项：1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, auto |
| 无法访问参考图像 URL | URL 不可公开访问 | 使用可公开访问的图床 |

---

## 任务执行错误

### 任务失败（failMsg）

| failMsg | 原因 | 解决 |
|---------|------|------|
| `content unsafe` | 提示词含不安全内容 | 修改提示词 |
| `image download failed` | 无法下载参考图 | 检查图像 URL 可访问性 |
| `timeout` | 生成超时 | 降低清晰度或重试 |
| `model overload` | 模型负载过高 | 稍后重试 |

### 查询任务不存在

taskId 错误或任务已过期（超过 24 小时），重新创建任务。

---

## 下载相关错误

### PermissionError

下载目录无写权限，使用 `~/Downloads` 或有权限的路径。

### URLError: SSL CERTIFICATE_VERIFY_FAILED

```bash
pip install --upgrade certifi
```

### OSError: No space left on device

磁盘空间不足，清理磁盘或更改下载目录：
```bash
--output-dir "/Volumes/OtherDisk/downloads"
```

---

## 性能和超时

### 等待超时

```
错误: 等待超时（300秒）
```

**方法 1: 增加等待时间**
```bash
--resolution 4K --max-wait 600
```

**方法 2: 使用异步模式**
```bash
# 创建任务（不等待）
python3 scripts/kie_nano_banana_api.py --prompt "描述" --resolution 4K --no-wait

# 稍后查询
python3 scripts/kie_nano_banana_api.py --query --task-id "abc123" --download
```

**方法 3: 降低清晰度**
```bash
--resolution 2K  # 代替 4K
```

---

## 性能基准

| 清晰度 | 无参考图 | 1 张参考图 | 多张参考图 |
|--------|---------|-----------|-----------|
| 1K | 15-30秒 | 20-40秒 | 30-60秒 |
| 2K | 30-60秒 | 40-80秒 | 60-120秒 |
| 4K | 60-120秒 | 80-150秒 | 120-300秒 |

实际时间取决于 API 服务负载和网络延迟。

---

## 调试技巧

```bash
# 捕获完整输出（包括 stderr）
python3 scripts/kie_nano_banana_api.py --prompt "描述" 2>&1 | tee debug.log

# 最简测试 API 连通性（预期 15-30 秒返回 URL）
python3 scripts/kie_nano_banana_api.py --prompt "测试" --resolution 1K
```
