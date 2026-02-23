---
title: OpenClaw Skills 开发最佳实践
slug: skills-dev-guide
summary: 基于生产环境排查总结的 Skills 开发规范，涵盖环境配置、exec 使用、用户体验和故障排查。
---

# OpenClaw Skills 开发最佳实践

> 基于生产环境排查总结，记录开发 OpenClaw Skills 时的常见问题和规范要求。

---

## 1. 环境配置规范

### API Key 标准存放位置

**本地开发**：统一放在仓库根目录 `.env`（即 `storyclaw-skills/.env`），不在各 skill 子目录单独存放。

```bash
# storyclaw-skills/.env
GIGGLE_API_KEY=your_giggle_api_key
KIE_API_KEY=your_kie_api_key
```

**OpenClaw 部署**：统一放在 `~/.openclaw/skills/.env`。gateway-wrapper.sh 启动时会 `source` 此文件，所有 exec 子进程自动继承，无需在 SKILL.md 中显式传递。

### dotenv 搜索路径规范

脚本位于 `skills/<skill-name>/scripts/`，**必须包含上三级目录**的搜索路径：

```python
from pathlib import Path
from dotenv import load_dotenv

env_paths = [
    Path.cwd() / ".env",
    Path(__file__).parent.parent / ".env",        # skill_name/.env（可能不存在）
    Path(__file__).parent.parent.parent / ".env",  # skills/.env ← 标准位置
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break
```

**常见错误**：只写到 `parent.parent` 会停在 skill 子目录，找不到 `skills/.env`，导致报"未设置 API 密钥"。

---

## 2. exec 使用规范

### 禁止在 exec env 传递占位符

SKILL.md 的 exec 命令**严禁**加 `"env": {"KEY": "${KEY}"}` 这类参数。

**原因**：OpenClaw gateway 的 exec 工具不对 env 值做 `${VAR}` 变量替换，字面量 `${GIGGLE_API_KEY}` 会直接作为 API key 传给服务端，导致"invalid api key"认证失败。

```markdown
❌ 错误写法（会导致认证失败）
exec python3 scripts/api.py --prompt "..."
env:
  GIGGLE_API_KEY: ${GIGGLE_API_KEY}

✅ 正确写法（API key 已在系统 env 中，直接执行）
exec python3 scripts/api.py --prompt "..."
```

### SKILL.md 执行命令章节标准提示

每个 SKILL.md 的执行命令章节**必须**包含以下说明：

```markdown
> **重要**：执行命令时**不得**在 exec 的 `env` 参数中传递 API 密钥。
> 密钥已通过系统环境变量配置，脚本自动读取，无需显式传递。直接执行以下命令即可。
```

---

## 3. 用户体验规范

### 耗时任务：先发消息再执行

OpenClaw exec 工具约 10 秒后转后台，用户在等待期间看不到任何输出。**所有需要等待的任务**（图像/音乐/视频生成）在调用 exec 之前必须先发一条消息：

| 任务类型 | 先发消息示例 |
|---------|------------|
| 图像生成 | `图像生成中，请稍候...` |
| 音乐生成 | `音乐生成中，通常 1-3 分钟，稍后自动发送结果。` |
| 视频生成 | `视频生成中，通常 10-30 分钟，每 3 分钟自动报告进度。` |

在 SKILL.md 中的写法：

```markdown
### 步骤 N: 执行生成

1. **先发送消息给用户**："图像生成中，请稍候..."
2. 运行命令（带 `--json`），等待完成
3. 解析输出并展示结果
```

### 长耗时任务：三阶段双路径

对于超过 1 分钟的任务（视频、MV 等），使用「同步等待 + Cron 兜底」双路径：

```
Phase 1：提交任务（< 10 秒）
  → 先发消息告知用户
  → 执行 start 命令，获取 task_id / project_id
  → 将 id 写入 Agent 记忆

Phase 2：注册 Cron（每 3 分钟）
  → 定期查询状态，进行中时发进度消息
  → 完成时发结果 + 取消 Cron

Phase 3：同步等待（乐观路径）
  → 执行 query --poll，短任务可在此步骤直接完成
  → 完成时检查 .sent 文件防重复发送
```

### 防重复推送

Cron 和同步等待可能同时完成，使用 `.sent` 文件防止重复推送：

```python
sent_file = log_dir / f"{task_id}.sent"

if not sent_file.exists():
    # 发送结果给用户
    sent_file.touch()
else:
    print(json.dumps({"status": "already_sent"}))
```

---

## 4. SKILL.md 编写规范

### 必需字段

```yaml
---
name: skill-name
description: 技能描述，包含触发关键词
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["API_KEY"],"bins":["python3"]},"primaryEnv":"API_KEY","emoji":"🎯","os":["darwin","linux","win32"],"install":["pip3 install -r {baseDir}/scripts/requirements.txt"]},"version":"1.0.0","author":"作者"}
---
```

### 执行命令章节模板

```markdown
## 执行命令

> **重要**：执行命令时**不得**在 exec 的 `env` 参数中传递 API 密钥。
> 密钥已通过系统环境变量配置，脚本自动读取，无需显式传递。直接执行以下命令即可。

\```bash
python3 scripts/api.py --param "值" --json
\```
```

### 交互流程模板（耗时任务）

```markdown
### 步骤 N: 执行生成并展示

1. **先发送消息给用户**："XXX 生成中，请稍候..."
2. 运行命令，等待完成
3. 解析输出并展示结果
```

---

## 5. 故障排查

### 认证失败（invalid api key）

**现象**：API 返回"invalid api key"或认证错误。

**排查顺序**：

```bash
# 1. 确认 key 在 gateway 进程可见
launchctl getenv GIGGLE_API_KEY

# 2. 确认 .env 文件存在且路径正确
ls -la ~/.openclaw/skills/.env
cat ~/.openclaw/skills/.env

# 3. 确认脚本能自动加载（进入 skill 目录模拟 exec 环境）
cd ~/.openclaw/skills/<skill-name>
python3 scripts/<script>.py --help   # 不出现"未设置API密钥"即成功

# 4. 检查 SKILL.md 中是否有 ${VAR} 占位符
grep -r '\${' ~/.openclaw/skills/<skill-name>/SKILL.md
```

**常见原因**：

| 原因 | 症状 | 修复方式 |
|------|------|---------|
| exec env 传了 `${VAR}` 字面量 | API 收到 `${GIGGLE_API_KEY}` 字符串 | 删除 SKILL.md exec 中的 env 参数 |
| dotenv 搜索路径不完整 | 脚本启动时报"未设置 API 密钥" | 补充 `parent.parent.parent` 路径 |
| gateway 启动时未 source .env | launchctl getenv 无返回值 | 运行 `bash ~/.openclaw/skills/apply-env.sh` |

### 用户看不到生成进度

**原因**：SKILL.md 没有"先发消息"指令，exec 阻塞期间用户无任何反馈。

**修复**：在执行步骤中加入"先发送消息给用户"指令（见第 3 节）。

### Gateway 重启后任务丢失

**规范**：所有长耗时任务的 task_id / project_id 必须在提交后立即写入 Agent 记忆：

```
addMemory: "giggle-music task_id: xxx（状态：生成中，提交时间：YYYY-MM-DD HH:mm）"
```

恢复逻辑：
1. 记忆中有 id → 直接 query，**绝不重新提交**
2. 记忆无，查日志 → `ls ~/.openclaw/skills/<skill>/logs/`
3. 两者都无 → 告知用户，询问是否重新生成

---

## 6. 变更记录

| 日期 | 问题 | 根因 | 修复方案 |
|------|------|------|---------|
| 2026-02-23 | giggle-music / giggle-image 认证失败 | dotenv 搜索路径只到 `parent.parent`，未找到 `skills/.env` | 补充 `parent.parent.parent` 路径 |
| 2026-02-23 | Kimi 模型自动补充 exec env 导致认证失败 | gateway exec 不做 `${VAR}` 变量替换，字面量直传 API | SKILL.md 加禁止说明，删除 env 参数 |
| 2026-02-23 | giggle-image 生成期间无任何用户反馈 | SKILL.md 缺少"先发消息"指令 | 步骤 4 加入先发消息指令 |
| 2026-02-23 | giggle-image 生成完成但结果不返回用户 | exec 10 秒转后台，同步等待结果丢失；`--no-wait` task_id 输出到 stderr；`--query` 进行中与失败同为 exit(1) | 改为三阶段双路径；`--no-wait` 改 stdout JSON；`--query` 新增 exit(2) 表示进行中 |
| 2026-02-23 | giggle-drama / giggle-aimv 单次 query 无 exit code 区分 | `trustee_api.py query`（无 `--poll`）所有情况均 exit(0)，Cron 无法区分完成/失败/进行中 | 补充 exit code：完成→exit(0)，失败→exit(1)，进行中→exit(2)；SKILL.md cron 处理表改为 exit code 风格 |
