# 故障排除指南

完整的错误处理、常见问题和解决方案。

## 目录

- [环境配置问题](#环境配置问题)
- [API 相关错误](#api-相关错误)
- [参数验证错误](#参数验证错误)
- [任务执行错误](#任务执行错误)
- [下载相关错误](#下载相关错误)
- [性能和超时问题](#性能和超时问题)
- [输出格式问题](#输出格式问题)

---

## 环境配置问题

### ❌ 错误: 未设置 API 密钥

**错误信息:**
```
错误: 未设置API密钥
请使用以下任意一种方式设置:
  1. 在项目根目录创建 .env 文件，添加: KIE_API_KEY=your-api-key
  2. 设置环境变量: export KIE_API_KEY=your-api-key
  3. 使用命令行参数: --api-key your-api-key
```

**原因:**
- 未创建 `.env` 文件或文件中未设置密钥
- 未设置 `KIE_API_KEY` 环境变量
- 未使用 `--api-key` 参数

**解决方案:**

**方法 1: 使用 .env 文件（推荐）**

```bash
# 1. 复制模板文件
cp .env.example .env

# 2. 编辑 .env 文件
# 将 KIE_API_KEY=your-api-key-here 改为你的真实密钥
# 例如: KIE_API_KEY=sk-1234567890abcdef

# 3. 验证 .env 文件位置
# 应放在 ad-nano-banana 目录下
```

**优点:**
- ✅ 密钥存储在本地文件，不会暴露在命令历史中
- ✅ 脚本自动加载，无需每次手动导出
- ✅ 适合多个项目独立配置
- ✅ `.gitignore` 会忽略 `.env`，避免泄漏到 Git 仓库

**方法 2: 设置环境变量**

Bash/Zsh (macOS/Linux):
```bash
export KIE_API_KEY="your-api-key-here"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export KIE_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

Windows CMD:
```cmd
set KIE_API_KEY=your-api-key-here
```

Windows PowerShell:
```powershell
$env:KIE_API_KEY="your-api-key-here"
```

**方法 2: 使用命令行参数**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --api-key "your-api-key-here"
```

**获取 API 密钥:**
访问 https://kie.ai/api-key 获取您的密钥

---

### ❌ Python 模块未找到

**错误信息:**
```
ModuleNotFoundError: No module named 'requests'
```

**原因:**
缺少必需的 Python 依赖

**解决方案:**
```bash
pip install requests

# 或使用 pip3
pip3 install requests
```

---

### ❌ 脚本执行权限错误

**错误信息:**
```
Permission denied: scripts/kie_nano_banana_api.py
```

**解决方案:**
```bash
chmod +x scripts/kie_nano_banana_api.py
```

---

## API 相关错误

### ❌ API 请求失败

**错误信息:**
```
HTTP 错误: 401 Unauthorized
```

**原因:**
- API 密钥无效或已过期
- API 密钥格式错误

**解决方案:**
1. 验证 API 密钥是否正确:
   ```bash
   echo $KIE_API_KEY
   ```
2. 重新获取 API 密钥: https://kie.ai/api-key
3. 确保密钥没有多余的空格或换行符

---

### ❌ API 限流错误

**错误信息:**
```
HTTP 错误: 429 Too Many Requests
```

**原因:**
请求频率超过 API 限制

**解决方案:**
1. 等待一段时间后重试
2. 使用 `--no-wait` 异步模式，避免频繁轮询
3. 增加 `--poll-interval` 间隔时间:
   ```bash
   python3 scripts/kie_nano_banana_api.py \
     --prompt "描述" \
     --poll-interval 10
   ```

---

### ❌ 网络连接错误

**错误信息:**
```
ConnectionError: Failed to connect to api.kie.ai
```

**原因:**
- 网络连接问题
- 防火墙阻止连接
- API 服务暂时不可用

**解决方案:**
1. 检查网络连接:
   ```bash
   ping api.kie.ai
   ```
2. 检查防火墙设置
3. 使用代理（如需要）:
   ```bash
   export https_proxy=http://your-proxy:port
   ```
4. 稍后重试

---

## 参数验证错误

### ❌ 提示词过长

**错误信息:**
```
错误: prompt 长度不能超过 20000 字符，当前长度: 25000
```

**原因:**
提示词超过 20000 字符限制

**解决方案:**
精简提示词，保留核心描述:

**❌ 过长的提示词:**
```
一只非常可爱的小猫咪坐在窗边，窗外是美丽的风景... (重复很多次)
```

**✅ 精简后:**
```
橘色小猫坐在窗边，阳光洒进，温馨氛围，水彩画风格
```

---

### ❌ 参考图像数量超限

**错误信息:**
```
错误: 最多支持 8 张参考图像，当前提供了 10 张
```

**原因:**
`--image-input` 参数超过 8 张图像

**解决方案:**
减少参考图像数量:
```bash
# ❌ 错误：超过 8 张
--image-input "url1" "url2" ... "url10"

# ✅ 正确：最多 8 张
--image-input "url1" "url2" "url3" "url4" "url5"
```

---

### ❌ 无效的图像 URL

**错误信息:**
```
错误: 无法访问参考图像: https://example.com/invalid.jpg
```

**原因:**
- URL 不可访问
- 图像格式不支持
- 需要认证才能访问

**解决方案:**
1. 确保 URL 可公开访问（浏览器中测试）
2. 使用支持的格式: JPG, PNG, WebP
3. 避免使用需要登录的图床
4. 推荐使用稳定的图床服务

---

### ❌ 无效的参数值

**错误信息:**
```
error: argument --aspect-ratio: invalid choice: '16:10'
```

**原因:**
参数值不在允许的选项中

**解决方案:**
查看有效选项:
```bash
# 查看帮助
python3 scripts/kie_nano_banana_api.py --help

# 有效的比例选项
1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, auto

# 有效的清晰度选项
1K, 2K, 4K

# 有效的格式选项
png, jpg
```

---

## 任务执行错误

### ❌ 任务创建失败

**错误信息:**
```
错误: 创建任务失败 - {"code": 400, "message": "Invalid parameters"}
```

**原因:**
- 提示词为空或无效
- 参数组合不合法
- API 参数格式错误

**解决方案:**
1. 确保提供了 `--prompt` 参数
2. 检查参数值是否有效
3. 尝试最简命令验证:
   ```bash
   python3 scripts/kie_nano_banana_api.py --prompt "测试"
   ```

---

### ❌ 任务失败

**错误信息:**
```
错误: 任务失败 - content unsafe
```

**原因:**
- 提示词包含不安全内容
- 参考图像包含不当内容
- 违反了 AI 使用政策

**解决方案:**
1. 修改提示词，避免敏感内容
2. 检查参考图像是否合规
3. 参考平台使用政策: https://kie.ai/terms

**常见失败原因和 failMsg:**

| failMsg | 原因 | 解决方案 |
|---------|------|---------|
| "content unsafe" | 内容不安全 | 修改提示词 |
| "image download failed" | 无法下载参考图像 | 检查图像 URL |
| "timeout" | 生成超时 | 降低清晰度或重试 |
| "model overload" | 模型负载过高 | 稍后重试 |

---

### ❌ 查询任务失败

**错误信息:**
```
错误: 查询任务失败 - 任务不存在
```

**原因:**
- taskId 错误
- 任务已过期（超过 24 小时）

**解决方案:**
1. 确认 taskId 正确无误
2. 任务创建后尽快查询
3. 重新创建任务

---

## 下载相关错误

### ❌ 下载目录不存在

**错误信息:**
```
错误: 下载目录不存在: /invalid/path
```

**原因:**
`--output-dir` 指定的目录无效

**解决方案:**

**使用默认目录（推荐）:**
```bash
# 不指定 --output-dir，自动使用 ~/Downloads
--download
```

**使用相对路径:**
```bash
--download --output-dir "./images"
```

**使用绝对路径:**
```bash
--download --output-dir "/Users/username/Pictures"
```

**注意:** 脚本会自动创建不存在的目录（如果有权限）

---

### ❌ 下载权限错误

**错误信息:**
```
PermissionError: [Errno 13] Permission denied
```

**原因:**
对下载目录没有写入权限

**解决方案:**
1. 使用有权限的目录（如 ~/Downloads）
2. 修改目录权限:
   ```bash
   chmod u+w /path/to/directory
   ```
3. 使用 sudo（不推荐）

---

### ❌ 下载文件失败

**错误信息:**
```
URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]>
```

**原因:**
- SSL 证书验证失败
- 图像 URL 已过期
- 网络连接问题

**解决方案:**
1. 生成完成后立即下载（URL 有效期有限）
2. 检查网络连接
3. 更新 Python 的 SSL 证书:
   ```bash
   pip install --upgrade certifi
   ```

---

### ❌ 磁盘空间不足

**错误信息:**
```
OSError: [Errno 28] No space left on device
```

**原因:**
下载目录所在磁盘空间不足

**解决方案:**
1. 清理磁盘空间
2. 更改下载目录到其他磁盘:
   ```bash
   --output-dir "/Volumes/OtherDisk/downloads"
   ```

---

## 性能和超时问题

### ❌ 等待超时

**错误信息:**
```
错误: 等待超时（300秒）- 任务仍在进行中
TaskID: abc123 (可使用此 ID 稍后查询)
```

**原因:**
- 生成时间超过 `--max-wait` 设置（默认 300 秒）
- 4K 图像生成时间较长
- API 服务繁忙

**解决方案:**

**方法 1: 增加等待时间**
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --resolution 4K \
  --max-wait 600  # 等待 10 分钟
```

**方法 2: 使用异步模式**
```bash
# 创建任务（不等待）
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --resolution 4K \
  --no-wait

# 输出: TaskID: abc123

# 稍后查询
python3 scripts/kie_nano_banana_api.py \
  --query \
  --task-id "abc123" \
  --download
```

**方法 3: 降低清晰度**
```bash
# 使用 2K 代替 4K（更快）
--resolution 2K
```

---

### ❌ 轮询过于频繁

**问题:**
频繁轮询导致 API 限流

**解决方案:**
增加轮询间隔:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --poll-interval 10  # 10 秒轮询一次（默认 5 秒）
```

---

## 输出格式问题

### ❌ JSON 解析错误

**错误信息:**
```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**原因:**
- 使用了 `--json` 但输出包含非 JSON 内容
- 进度信息混入 JSON 输出

**解决方案:**
脚本已正确处理，进度输出到 stderr，JSON 输出到 stdout。

如果仍有问题，重定向 stderr:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --json 2>/dev/null
```

---

### ❌ 文件名包含特殊字符

**问题:**
下载文件名在某些系统上无法识别

**解决方案:**
脚本使用时间戳命名，避免特殊字符:
```
nano_banana_20260211_143025.png
```

如果仍有问题，检查文件系统类型和字符编码。

---

## 常见问题 FAQ

### Q: 生成的图像质量不理想怎么办？

**A:** 优化策略:
1. **改进提示词**: 增加细节描述，指定风格
2. **提升清晰度**: 使用 4K 代替 2K
3. **调整比例**: 选择适合内容的比例
4. **使用参考图**: 图生图模式可以更精确控制

---

### Q: 如何加速生成？

**A:** 加速技巧:
1. **降低清晰度**: 使用 1K 或 2K
2. **使用异步模式**: `--no-wait` 避免等待
3. **避免高峰期**: 非高峰时段生成更快

---

### Q: 图像 URL 多久失效？

**A:**
- URL 有效期因平台而异，通常为 24-72 小时
- **强烈建议**: 使用 `--download` 立即下载到本地
- 不要依赖 URL 长期存储

---

### Q: 可以批量生成吗？

**A:**
使用异步模式批量提交:
```bash
# 提交多个任务
for prompt in "描述1" "描述2" "描述3"; do
  python3 scripts/kie_nano_banana_api.py \
    --prompt "$prompt" \
    --no-wait
done

# 稍后批量查询
```

---

### Q: 支持哪些图像格式？

**A:**
- **输出格式**: PNG (默认), JPG
- **参考图像**: JPG, PNG, WebP
- 使用 `--output-format` 选择

---

### Q: 如何在脚本中使用？

**A:**
使用 JSON 输出模式:
```bash
#!/bin/bash
result=$(python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  --json)

# 解析 JSON（使用 jq）
image_url=$(echo "$result" | jq -r '.imageUrls[0]')
echo "图像URL: $image_url"
```

---

## 获取帮助

### 命令行帮助

```bash
python3 scripts/kie_nano_banana_api.py --help
```

### 文档

- **SKILL.md**: 完整使用指南
- **REFERENCE.md**: 参数详细说明
- **EXAMPLES.md**: 使用示例
- **PRESETS.md**: 快速预设配置

### API 文档

- Kie 平台文档: https://api.kie.ai/docs
- 获取 API 密钥: https://kie.ai/api-key

---

## 错误报告

如果遇到未列出的错误，请提供:
1. 完整的命令
2. 错误信息
3. Python 版本 (`python3 --version`)
4. 操作系统

---

## 调试模式

### 详细输出

脚本默认输出进度信息到 stderr。

查看完整调试信息:
```bash
python3 scripts/kie_nano_banana_api.py \
  --prompt "描述" \
  2>&1 | tee debug.log
```

### 测试 API 连接

```bash
# 最简测试
python3 scripts/kie_nano_banana_api.py \
  --prompt "测试" \
  --resolution 1K

# 预期：15-30秒内返回图像 URL
```

---

## 性能基准

**预期生成时间:**

| 清晰度 | 无参考图 | 1 张参考图 | 多张参考图 |
|--------|---------|-----------|-----------|
| 1K | 15-30秒 | 20-40秒 | 30-60秒 |
| 2K | 30-60秒 | 40-80秒 | 60-120秒 |
| 4K | 60-120秒 | 80-150秒 | 120-300秒 |

**注意:** 实际时间取决于:
- API 服务负载
- 网络延迟
- 提示词复杂度
- 参考图像数量和大小
