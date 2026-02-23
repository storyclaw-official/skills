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

### 长耗时任务：二阶段双路径

对于超过 30 秒的任务（图像/音乐/视频等），使用「提交任务 + Cron 兜底」：

```
Phase 1：提交任务（< 5 秒，--no-wait 模式）
  → 先发消息告知用户（"XXX 生成中，请稍候..."）
  → 执行 --no-wait 命令，从 stdout JSON 读取 task_id
  → 将 task_id 写入 Agent 记忆（addMemory）

Phase 2：注册 Cron（立刻注册，wakeMode: "now"）
  → 轮询间隔：图像 45 秒 / 音乐 2 分钟 / 视频 3 分钟
  → 读 stdout JSON status 字段决定行为（见下表）
```

**Cron 处理表（基于 stdout JSON status 字段）：**

| stdout 内容 | 处理 |
|------------|------|
| 空输出（stdout 为空） | 已推送过，**立即取消 Cron，绝对不发任何消息** |
| status = 完成相关 | 解析结果，发送给用户，**取消 Cron** |
| status = `processing` / `pending` / `running` | **不发任何消息**，Cron 继续等待 |

exit code = 1（失败）→ 发送错误消息，取消 Cron

> **重要**：Phase 3 乐观路径（提交后立即 query）已废弃。原因：任务刚提交时始终处于进行中状态，立刻查询只会触发"仍在生成中"消息，造成"一次性输出"体验问题。依赖 Cron 即可。

### Cron 注册规范

注册 Cron 时**必须**指定 `wakeMode: "now"`：

```
wakeMode: "now"            ✅  立即在下一轮次触发
wakeMode: "next-heartbeat" ❌  默认值，可能延迟 7+ 分钟才触发
```

**原因**：`next-heartbeat` 依赖系统心跳周期，在心跳间隔较长时，Cron 注册后长时间不触发，用户迟迟收不到结果。

### 防重复推送：空输出方案

使用 `.sent` 文件防止重复推送。**已推送时必须空输出（不得输出任何 JSON）**，确保 agent 静默：

```python
sent_file = log_dir / f"{task_id}.sent"

if sent_file.exists():
    sys.exit(0)  # 空输出 exit(0)，agent 无内容可报告，Cron 静默取消

# 标记已推送（先打标记，再输出结果）
sent_file.touch()
print_output(...)  # 发送结果给用户
sys.exit(0)
```

> **不要**输出 `{"status": "already_sent"}` — LLM agent 会"帮忙"将此状态汇报给用户，产生多余消息。

### exec 脚本 stderr 规范

**`--query` 模式下禁止任何 stderr 输出。**

OpenClaw 行为：非零 exit code + 任何输出（stderr 或 stdout）→ 在 IM 中显示 "exec failed: <输出内容>"。

```python
# ❌ 错误：--query 路径中有 stderr 信息行
print(f"✓ 已加载配置文件: {env_path}", file=sys.stderr)  # 会成为 exec failed 内容
print(f"查询任务: {task_id}", file=sys.stderr)

# ✅ 正确：--query 路径零 stderr 输出
# 所有诊断信息只在 --no-wait / 生成路径输出，不在 --query 路径
```

### exit code 规范（--query 模式）

**统一 exit(0) 表示无错误，exit(1) 表示失败，不使用其他 exit code。**

| 情况 | exit code | stdout | 说明 |
|------|-----------|--------|------|
| 完成（首次） | 0 | 结果内容 | Agent 解析并发送给用户 |
| 完成（已推送） | 0 | 空 | Agent 无内容可报告，静默取消 Cron |
| 进行中 | 0 | `{"status": "processing/pending/running", ...}` | Agent 读 status 字段，不发消息，Cron 继续 |
| 失败 | 1 | `{"status": "failed", "err_msg": "..."}` | Agent 发送错误消息，取消 Cron |

> **废弃**：exit(2) 表示进行中的方案已废弃。exit(2) 是非零 exit code，会触发 "exec failed" 显示。所有非失败情况一律 exit(0)，通过 stdout JSON status 字段区分行为。

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
| 2026-02-23 | exec failed: LibreSSL/urllib3 NotOpenSSLWarning | macOS Python 3.9 使用 LibreSSL，urllib3 v2 向 stderr 输出 `NotOpenSSLWarning`；非零 exit code 触发 exec failed 展示 | 所有脚本在 `import requests` 前加 `warnings.filterwarnings("ignore")` |
| 2026-02-23 | exec failed: ✓ 已加载配置文件 | warning 修复后，`load_api_key()` 的调试 stderr 成为新的 exec failed 内容 | 删除 `--query` 路径中所有 stderr 信息行 |
| 2026-02-23 | exec failed: `{"status": "running", ...}` | exit(2) 是非零 exit code，openclaw 把 stdout 也当 exec failed 内容展示 | exit(2) 改 exit(0)；通过 stdout JSON status 字段区分进行中/完成 |
| 2026-02-23 | 一次性输出：提交后立即出现"仍在生成中"消息 | SKILL.md Phase 3 乐观路径立刻 query，任务刚开始必然返回进行中 | 废弃 Phase 3 乐观路径，仅保留 Phase 1 提交 + Phase 2 Cron |
| 2026-02-23 | giggle-image 结果重复发送 3-4 次 | 缺少 `.sent` 防重复机制，每次 Cron 触发都重新推送 | 补充 `_check_image_sent` / `_mark_image_sent` 函数 |
| 2026-02-23 | already_sent 状态仍产生消息通知用户 | 输出 `{"status": "already_sent"}` JSON，agent 自动将此状态汇报给用户 | 改为空输出 exit(0)，agent 无内容可报告 |
| 2026-02-23 | Cron 注册后 7 分钟未触发 | 默认 `wakeMode: next-heartbeat` 依赖心跳周期，可能长时间不触发 | SKILL.md 统一指定 `wakeMode: "now"` |
