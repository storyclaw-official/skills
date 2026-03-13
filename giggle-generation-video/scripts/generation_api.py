#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
giggle.pro Generation API 封装脚本
支持文生视频、图生视频（首帧/尾帧），模型：grok
API: POST /api/v1/generation/text-to-video, POST /api/v1/generation/image-to-video, GET /api/v1/generation/task/query
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class TaskStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PROCESSING = "processing"
    PENDING = "pending"


SUPPORTED_MODELS = (
    "grok", "grok-fast",
    "sora2", "sora2-pro", "sora2-fast", "sora2-pro-fast",
    "kling25",
    "seedance15-pro", "seedance15-pro-no-audio",
    "veo31", "veo31-no-audio",
    "minimax23",
    "wan25",
)

MODEL_DURATIONS = {
    "grok": [6, 10],
    "grok-fast": [6, 10],
    "sora2": [4, 8, 12],
    "sora2-pro": [4, 8, 12],
    "sora2-fast": [10, 15],
    "sora2-pro-fast": [10, 15],
    "kling25": [5, 10],
    "seedance15-pro": [4, 8, 12],
    "seedance15-pro-no-audio": [4, 8, 12],
    "veo31": [4, 6, 8],
    "veo31-no-audio": [4, 6, 8],
    "minimax23": [6],
    "wan25": [5, 10],
}

MODEL_DEFAULT_DURATION = {
    "grok": 6, "grok-fast": 6,
    "sora2": 4, "sora2-pro": 4, "sora2-fast": 10, "sora2-pro-fast": 10,
    "kling25": 5,
    "seedance15-pro": 4, "seedance15-pro-no-audio": 4,
    "veo31": 4, "veo31-no-audio": 4,
    "minimax23": 6,
    "wan25": 0,
}

SUPPORTED_ASPECT_RATIOS = ("16:9", "9:16", "1:1", "3:4", "4:3")
SUPPORTED_RESOLUTIONS = ("480p", "720p", "1080p")


# ── 防重复推送（.sent 文件标记）────────────────────────────────────────────────
def _get_log_dir() -> Path:
    log_dir = Path.home() / '.openclaw' / 'skills' / 'giggle-generation-video' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _check_sent(task_id: str) -> bool:
    return (_get_log_dir() / f"{task_id}.sent").exists()


def _mark_sent(task_id: str) -> None:
    (_get_log_dir() / f"{task_id}.sent").touch()


def _save_prompt(task_id: str, prompt: str) -> None:
    try:
        (_get_log_dir() / f"{task_id}.prompt").write_text(prompt, encoding='utf-8')
    except Exception:
        pass


def _load_prompt(task_id: str, truncate: bool = True) -> Optional[str]:
    try:
        f = _get_log_dir() / f"{task_id}.prompt"
        if f.exists():
            prompt = f.read_text(encoding='utf-8').strip()
            return prompt[:20] + "..." if truncate and len(prompt) > 20 else prompt
    except Exception:
        pass
    return None


def _increment_query_count(task_id: str) -> int:
    f = _get_log_dir() / f"{task_id}.count"
    count = int(f.read_text().strip()) + 1 if f.exists() else 1
    f.write_text(str(count))
    return count


def to_view_url(url: str) -> str:
    """将下载 URL 转换为在线查看 URL"""
    url = url.replace("&response-content-disposition=attachment", "")
    url = url.replace("?response-content-disposition=attachment&", "?")
    url = url.replace("?response-content-disposition=attachment", "")
    url = url.replace("~", "%7E")
    return url


def parse_frame_arg(frame_str: str) -> Dict[str, str]:
    """
    解析帧参数，支持三种互斥格式：
    - asset_id:xxx  -> {"asset_id": "xxx"}
    - url:https://... -> {"url": "https://..."}
    - base64:xxx -> {"base64": "xxx"}
    """
    if frame_str.startswith("asset_id:"):
        return {"asset_id": frame_str[len("asset_id:"):]}
    elif frame_str.startswith("url:"):
        return {"url": frame_str[len("url:"):]}
    elif frame_str.startswith("base64:"):
        return {"base64": frame_str[len("base64:"):]}
    else:
        raise ValueError(
            f"帧参数格式错误: {frame_str}\n"
            "支持: asset_id:<ID>, url:<URL>, base64:<DATA>"
        )


class GenerationAPI:
    """giggle.pro Video Generation API 客户端"""

    BASE_URL = "https://giggle.pro"
    TEXT_TO_VIDEO = "/api/v1/generation/text-to-video"
    IMAGE_TO_VIDEO = "/api/v1/generation/image-to-video"
    QUERY_TASK = "/api/v1/generation/task/query"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-auth": api_key,
            "Content-Type": "application/json"
        }

    def _validate_duration(self, model: str, duration: int) -> None:
        allowed = MODEL_DURATIONS.get(model, [])
        if allowed and duration not in allowed:
            raise ValueError(
                f"模型 {model} 不支持时长 {duration}秒，"
                f"支持: {', '.join(str(d) for d in allowed)}"
            )

    def text_to_video(
        self,
        prompt: str,
        model: str = "grok",
        duration: int = 6,
        aspect_ratio: str = "16:9",
        resolution: str = "720p"
    ) -> Dict[str, Any]:
        """文生视频"""
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"不支持的模型: {model}，支持: {', '.join(SUPPORTED_MODELS)}")
        self._validate_duration(model, duration)
        payload = {
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution
        }
        return self._post(self.TEXT_TO_VIDEO, payload)

    def image_to_video(
        self,
        prompt: str,
        start_frame: Optional[Dict[str, str]] = None,
        end_frame: Optional[Dict[str, str]] = None,
        model: str = "grok",
        duration: int = 6,
        aspect_ratio: str = "16:9",
        resolution: str = "720p"
    ) -> Dict[str, Any]:
        """图生视频"""
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"不支持的模型: {model}，支持: {', '.join(SUPPORTED_MODELS)}")
        self._validate_duration(model, duration)
        if not start_frame and not end_frame:
            raise ValueError("图生视频需要至少提供 start_frame 或 end_frame")
        payload = {
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution
        }
        if start_frame:
            payload["start_frame"] = start_frame
        if end_frame:
            payload["end_frame"] = end_frame
        return self._post(self.IMAGE_TO_VIDEO, payload)

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") != 200:
                raise Exception(result.get("msg", result.get("message", "未知错误")))
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")

    def query_task(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        url = f"{self.BASE_URL}{self.QUERY_TASK}"
        try:
            resp = requests.get(url, headers=self.headers, params={"task_id": task_id}, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") != 200:
                raise Exception(result.get("msg", result.get("message", "未知错误")))
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"查询失败: {str(e)}")

    def extract_video_urls(self, task_result: Dict[str, Any]) -> List[str]:
        """从任务结果中提取视频 URL"""
        return task_result.get("data", {}).get("urls", [])


def parse_args():
    parser = argparse.ArgumentParser(
        description='giggle.pro Generation API - AI 视频生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 文生视频
  python generation_api.py --prompt "相机缓缓推进" --model grok --duration 6 --no-wait --json

  # 图生视频（首帧 asset_id）
  python generation_api.py --prompt "人物转身" --start-frame "asset_id:lkllv0yv81" --no-wait --json

  # 图生视频（首帧 URL）
  python generation_api.py --prompt "风景运动" --start-frame "url:https://example.com/img.jpg" --no-wait --json

  # 查询任务
  python generation_api.py --query --task-id xxx --poll
        """
    )
    parser.add_argument('--query', action='store_true', help='查询任务')
    parser.add_argument('--poll', action='store_true', help='轮询等待完成')
    parser.add_argument('--prompt', type=str, help='视频描述')
    parser.add_argument('--api-key', type=str, help='API 密钥')
    parser.add_argument('--task-id', type=str, help='任务 ID')
    parser.add_argument('--start-frame', type=str,
                        help='首帧，格式: asset_id:<ID> 或 url:<URL> 或 base64:<DATA>')
    parser.add_argument('--end-frame', type=str,
                        help='尾帧，格式: asset_id:<ID> 或 url:<URL> 或 base64:<DATA>')
    parser.add_argument('--model', type=str, default='grok',
                        choices=list(SUPPORTED_MODELS), help='模型')
    parser.add_argument('--duration', type=int, default=None,
                        help='视频时长（秒），不指定则使用模型默认时长')
    parser.add_argument('--aspect-ratio', type=str, default='16:9',
                        choices=list(SUPPORTED_ASPECT_RATIOS))
    parser.add_argument('--resolution', type=str, default='720p',
                        choices=list(SUPPORTED_RESOLUTIONS))
    parser.add_argument('--no-wait', action='store_true', help='异步提交')
    parser.add_argument('--max-wait', type=int, default=300)
    parser.add_argument('--poll-interval', type=int, default=10)
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    return parser.parse_args()


def main():
    args = parse_args()

    if DOTENV_AVAILABLE:
        openclaw_env = Path.home() / ".openclaw" / ".env"
        if openclaw_env.exists():
            load_dotenv(openclaw_env, override=True)

    api_key = args.api_key or os.getenv("GIGGLE_API_KEY")
    if not api_key:
        openclaw_env = Path.home() / ".openclaw" / ".env"
        print("错误: 未找到 GIGGLE_API_KEY，请任选一种方式配置：", file=sys.stderr)
        print(f"  1. 在 {openclaw_env} 中添加 GIGGLE_API_KEY=your_api_key（优先读取）", file=sys.stderr)
        print("  2. 设置系统环境变量：export GIGGLE_API_KEY=your_api_key", file=sys.stderr)
        print("  API Key 可在 https://giggle.pro/ 账号设置中获取。", file=sys.stderr)
        sys.exit(1)

    client = GenerationAPI(api_key)
    task_id = None

    try:
        if args.query:
            if not args.task_id:
                print("错误: --query 需提供 --task-id", file=sys.stderr)
                sys.exit(1)

            if args.poll:
                print(f"同步轮询（最多 {args.max_wait} 秒）...", file=sys.stderr)
                start = time.time()
                while time.time() - start < args.max_wait:
                    if _check_sent(args.task_id):
                        print("已由 Cron 推送，跳过", file=sys.stderr)
                        sys.exit(0)
                    try:
                        result = client.query_task(args.task_id)
                    except Exception as e:
                        print(f"查询异常: {e}", file=sys.stderr)
                        time.sleep(args.poll_interval)
                        continue
                    data = result.get("data", {})
                    status = data.get("status", "")
                    if status == TaskStatus.COMPLETED.value:
                        break
                    elif status in ("failed", "error"):
                        break
                    print(f"状态: {status}，继续等待...", file=sys.stderr)
                    time.sleep(args.poll_interval)
                else:
                    print("同步等待超时，交给 Cron", file=sys.stderr)
                    sys.exit(0)
            else:
                count = _increment_query_count(args.task_id)
                if count > 10:
                    prompt_text = _load_prompt(args.task_id) or "视频"
                    print(f"视频生成超时\n\n关于「{prompt_text}」的创作已等待超过 5 分钟。\n\n建议重新生成，我随时待命~")
                    sys.exit(0)
                try:
                    result = client.query_task(args.task_id)
                except Exception as e:
                    print(json.dumps({"status": "network_error", "task_id": args.task_id}, ensure_ascii=False))
                    print(f"网络异常: {e}", file=sys.stderr)
                    sys.exit(0)

            data = result.get("data", {})
            status = data.get("status", "")

            if status == TaskStatus.COMPLETED.value:
                if _check_sent(args.task_id):
                    sys.exit(0)
                video_urls = client.extract_video_urls(result)
                if not video_urls:
                    prompt_text = _load_prompt(args.task_id) or "视频"
                    print(f"生成遇到了问题\n\n关于「{prompt_text}」的创作虽已完成但未返回视频。\n\n建议重新生成，我随时待命~")
                    sys.exit(0)
                _mark_sent(args.task_id)
                view_urls = [to_view_url(u) for u in video_urls]
                prompt_text = _load_prompt(args.task_id) or "视频"
                n = len(view_urls)
                lines = [f"[查看视频 {i+1}]({u})" for i, u in enumerate(view_urls)]
                print("视频已就绪！🎬\n")
                print(f"关于「{prompt_text}」的创作已完成" + (f"，共 {n} 个" if n > 1 else "") + " 🎬\n")
                print("\n".join(lines))
                print("\n⚠️ 以上链接为签名 URL（含 Policy、Key-Pair-Id、Signature），有效期有限，请及时查看或下载。")
                print("\n如需调整，随时告诉我~")
                sys.exit(0)
            elif status in ("failed", "error"):
                err_msg = data.get("err_msg", "未知错误")
                if "sensitive" in str(err_msg).lower():
                    err_msg = "输入内容可能包含敏感信息，被服务端拦截"
                prompt_text = _load_prompt(args.task_id) or "视频"
                print(f"生成遇到了问题\n\n关于「{prompt_text}」的创作未能完成：{err_msg}\n\n建议调整描述后重新尝试，我随时待命~")
                sys.exit(0)
            else:
                print(json.dumps({"status": status, "task_id": args.task_id}, ensure_ascii=False))
                sys.exit(0)

        # 生成模式
        if not args.prompt:
            print("错误: 需要 --prompt", file=sys.stderr)
            sys.exit(1)

        start_frame = parse_frame_arg(args.start_frame) if args.start_frame else None
        end_frame = parse_frame_arg(args.end_frame) if args.end_frame else None
        duration = args.duration if args.duration is not None else MODEL_DEFAULT_DURATION.get(args.model, 6)

        print("创建视频生成任务...", file=sys.stderr)
        if start_frame or end_frame:
            result = client.image_to_video(
                prompt=args.prompt,
                start_frame=start_frame,
                end_frame=end_frame,
                model=args.model,
                duration=duration,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution
            )
            print(f"模式: 图生视频, 模型: {args.model}, 时长: {duration}秒", file=sys.stderr)
        else:
            result = client.text_to_video(
                prompt=args.prompt,
                model=args.model,
                duration=duration,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution
            )
            print(f"模式: 文生视频, 模型: {args.model}, 时长: {duration}秒", file=sys.stderr)

        task_id = result.get("data", {}).get("task_id")
        print(f"✓ 任务创建成功! TaskID: {task_id}", file=sys.stderr)

        if not args.no_wait:
            print(f"等待完成（最多 {args.max_wait} 秒）...", file=sys.stderr)
            start = time.time()
            while time.time() - start < args.max_wait:
                result = client.query_task(task_id)
                data = result.get("data", {})
                st = data.get("status", "")
                if st == TaskStatus.COMPLETED.value:
                    break
                if st in ("failed", "error"):
                    raise Exception(data.get("err_msg", "生成失败"))
                time.sleep(args.poll_interval)
            else:
                raise Exception(f"等待超时 ({args.max_wait}秒)")
            video_urls = client.extract_video_urls(result)
            view_urls = [to_view_url(u) for u in video_urls]
            if args.json:
                display = "\n".join([f"[查看视频 {i+1}]({u})" for i, u in enumerate(view_urls)])
                out = {"prompt": args.prompt, "display": display, "videoCount": len(video_urls)}
                print(json.dumps(out, ensure_ascii=False, indent=2))
            else:
                print("\n" + "=" * 60)
                print("视频生成完成")
                print("=" * 60)
                print(f"提示词: {args.prompt}")
                for i, (v, d) in enumerate(zip(view_urls, video_urls), 1):
                    print(f"视频 #{i} 查看: {v}")
                    print(f"视频 #{i} 下载: {d}")
                print("=" * 60)
                print("⚠️ 以上链接为签名 URL，有效期有限，请及时查看或下载。")
        else:
            _save_prompt(task_id, args.prompt)
            print(json.dumps({"status": "started", "task_id": task_id}, ensure_ascii=False))

    except Exception as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
