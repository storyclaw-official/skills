#!/usr/bin/env python3
"""
grok-imagine 图生视频调用脚本

使用 kie.ai 的 grok-imagine/image-to-video 模型生成视频。
支持本地图片（自动上传）和远程图片 URL。
从技能目录的 .env 文件读取 KIE_API_KEY。

用法:
    python3 image_to_video.py \
        --image "/path/to/image.png" \
        --prompt "描述视频动作" \
        --duration "6" \
        --resolution "720p"

    python3 image_to_video.py \
        --image "https://example.com/image.png" \
        --prompt "描述视频动作" \
        --duration "10" \
        --resolution "480p"
"""

import argparse
import base64
import json
import mimetypes
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
    """从技能目录中查找并加载 .env 文件"""
    skill_dir = get_skill_dir()
    env_path = os.path.join(skill_dir, ".env")
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
    print(f"请在技能目录创建 .env 文件: {env_path}", file=sys.stderr)
    sys.exit(1)


def is_url(path: str) -> bool:
    """判断是否为 URL"""
    return path.startswith("http://") or path.startswith("https://")


def upload_image(api_key: str, image_path: str) -> str:
    """将本地图片通过 Base64 上传到 kie 平台，返回下载 URL"""
    image_path = os.path.expanduser(image_path)
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}", file=sys.stderr)
        sys.exit(1)

    file_size = os.path.getsize(image_path)
    if file_size > 10 * 1024 * 1024:
        print(f"错误: 图片文件超过 10MB 限制 ({file_size / 1024 / 1024:.1f}MB)", file=sys.stderr)
        sys.exit(1)

    with open(image_path, "rb") as f:
        raw = f.read()
    b64_data = base64.b64encode(raw).decode("utf-8")

    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type:
        b64_data = f"data:{mime_type};base64,{b64_data}"

    file_name = os.path.basename(image_path)

    url = "https://kieai.redpandaai.co/api/file-base64-upload"
    payload = {
        "base64Data": b64_data,
        "uploadPath": "image-to-video/uploads",
        "fileName": file_name,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://kie.ai",
            "Referer": "https://kie.ai/",
        },
        method="POST",
    )

    print(f"  正在上传图片: {file_name} ({file_size / 1024:.0f}KB)...", file=sys.stderr)

    try:
        with urllib.request.urlopen(req, timeout=60, context=_SSL_CONTEXT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"上传失败: HTTP {e.code} - {body}", file=sys.stderr)
        sys.exit(1)

    if not result.get("success") or result.get("code") != 200:
        print(f"上传失败: {result.get('msg', '未知错误')}", file=sys.stderr)
        sys.exit(1)

    download_url = result["data"]["downloadUrl"]
    print(f"  上传成功: {download_url}", file=sys.stderr)
    return download_url


def create_task(api_key: str, image_url: str, prompt: str, duration: str, resolution: str) -> str:
    """创建图生视频任务，返回 taskId"""
    url = "https://api.kie.ai/api/v1/jobs/createTask"
    payload = {
        "model": "grok-imagine/image-to-video",
        "input": {
            "image_urls": [image_url],
            "prompt": prompt,
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
    parser = argparse.ArgumentParser(description="grok-imagine 图生视频")
    parser.add_argument("--image", required=True,
                        help="参考图片路径（本地文件路径或 URL）")
    parser.add_argument("--prompt", default="",
                        help="视频动作描述提示词（可选）")
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

    if is_url(args.image):
        image_url = args.image
        print(f"使用远程图片: {image_url}", file=sys.stderr)
    else:
        print(f"检测到本地图片，需先上传...", file=sys.stderr)
        image_url = upload_image(api_key, args.image)

    print(f"正在创建图生视频任务...", file=sys.stderr)
    print(f"  模型: grok-imagine", file=sys.stderr)
    print(f"  时长: {args.duration}s", file=sys.stderr)
    print(f"  清晰度: {args.resolution}", file=sys.stderr)
    if args.prompt:
        print(f"  提示词: {args.prompt[:50]}...", file=sys.stderr)

    task_id = create_task(api_key, image_url, args.prompt, args.duration, args.resolution)
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
        "model": "grok-imagine/image-to-video",
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
