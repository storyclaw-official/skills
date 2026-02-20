#!/usr/bin/env python3
"""
grok-imagine 文生视频调用脚本

使用 kie.ai 的 grok-imagine/text-to-video 模型生成视频。
从 .env 文件读取 KIE_API_KEY（三级搜索：当前目录 → 技能目录 → 项目根目录）。

用法:
    python3 text_to_video.py \
        --prompt "描述文本" \
        --aspect_ratio "16:9" \
        --duration "6" \
        --resolution "720p"
"""

import argparse
import json
import os
import ssl
import sys
import time
import urllib.request
import urllib.error

try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CONTEXT = None


def get_skill_dir():
    """获取技能根目录（scripts/ 的父目录）"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env():
    """从三级路径查找并加载 .env 文件"""
    skill_dir = get_skill_dir()
    project_dir = os.path.dirname(skill_dir)

    env_paths = [
        os.path.join(os.getcwd(), ".env"),      # 当前工作目录
        os.path.join(skill_dir, ".env"),         # 技能根目录
        os.path.join(project_dir, ".env"),       # 项目根目录
    ]

    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip("\"'")
                        os.environ.setdefault(key, value)
            return

    if os.environ.get("KIE_API_KEY"):
        return
    print("错误: 未找到 .env 文件且环境变量 KIE_API_KEY 未设置", file=sys.stderr)
    print(f"请在项目根目录创建 .env 文件: cp env.example .env", file=sys.stderr)
    sys.exit(1)


def create_task(api_key: str, prompt: str, aspect_ratio: str, duration: str, resolution: str) -> str:
    """创建文生视频任务，返回 taskId"""
    url = "https://api.kie.ai/api/v1/jobs/createTask"
    payload = {
        "model": "grok-imagine/text-to-video",
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "mode": "normal",
            "duration": duration,
            "resolution": resolution,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=_SSL_CONTEXT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"错误: HTTP {e.code} - {body}", file=sys.stderr)
        sys.exit(1)

    if result.get("code") != 200:
        print(f"错误: {result.get('msg', '未知错误')}", file=sys.stderr)
        sys.exit(1)

    task_id = result["data"]["taskId"]
    return task_id


def poll_task(api_key: str, task_id: str, poll_interval: int = 10, max_wait: int = 600) -> dict:
    """轮询任务状态直到完成或超时"""
    url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    elapsed = 0
    while elapsed < max_wait:
        try:
            with urllib.request.urlopen(req, timeout=30, context=_SSL_CONTEXT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"查询出错: HTTP {e.code} - {body}", file=sys.stderr)
            sys.exit(1)

        if result.get("code") != 200:
            print(f"查询出错: {result.get('msg', '未知错误')}", file=sys.stderr)
            sys.exit(1)

        state = result["data"]["state"]

        if state == "success":
            return result["data"]
        elif state == "fail":
            fail_msg = result["data"].get("failMsg", "未知原因")
            print(f"任务失败: {fail_msg}", file=sys.stderr)
            sys.exit(1)

        print(f"  状态: {state} | 已等待 {elapsed}s ...", file=sys.stderr)
        time.sleep(poll_interval)
        elapsed += poll_interval

    print(f"错误: 任务超时（已等待 {max_wait}s）", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="grok-imagine 文生视频")
    parser.add_argument("--prompt", required=True, help="视频描述提示词")
    parser.add_argument("--aspect_ratio", default="16:9",
                        choices=["2:3", "3:2", "1:1", "9:16", "16:9"],
                        help="视频比例 (默认: 16:9)")
    parser.add_argument("--duration", default="6",
                        choices=["6", "10"],
                        help="视频时长秒数 (默认: 6)")
    parser.add_argument("--resolution", default="720p",
                        choices=["480p", "720p"],
                        help="视频清晰度 (默认: 720p)")
    args = parser.parse_args()

    load_env()
    api_key = os.environ.get("KIE_API_KEY")
    if not api_key:
        print("错误: 未设置 KIE_API_KEY", file=sys.stderr)
        sys.exit(1)

    print(f"正在创建文生视频任务...", file=sys.stderr)
    print(f"  模型: grok-imagine", file=sys.stderr)
    print(f"  比例: {args.aspect_ratio}", file=sys.stderr)
    print(f"  时长: {args.duration}s", file=sys.stderr)
    print(f"  清晰度: {args.resolution}", file=sys.stderr)

    task_id = create_task(api_key, args.prompt, args.aspect_ratio, args.duration, args.resolution)
    print(f"  任务ID: {task_id}", file=sys.stderr)
    print(f"正在等待视频生成...", file=sys.stderr)

    data = poll_task(api_key, task_id)

    result_json = json.loads(data.get("resultJson", "{}"))
    urls = result_json.get("resultUrls", [])
    cost_time = data.get("costTime")

    # 获取系统下载目录
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")

    output = {
        "success": True,
        "taskId": task_id,
        "model": "grok-imagine/text-to-video",
        "videoUrls": urls,
        "costTimeMs": cost_time,
        "downloadsDir": downloads_dir,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"生成完成!", file=sys.stderr)
    if cost_time:
        print(f"耗时: {cost_time / 1000:.1f}s", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)
    for i, url in enumerate(urls):
        print(f"\n视频 [{i + 1}] 下载链接（可复制到浏览器打开）:", file=sys.stderr)
        print(f"{url}", file=sys.stderr)
    print(f"\n默认下载目录: {downloads_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
