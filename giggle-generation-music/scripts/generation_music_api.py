#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
giggle.pro Generation API - 音乐生成
支持两种模式：提示词模式（根据描述）、自定义模式（根据歌词）
API: POST /api/v1/generation/generate-music, GET /api/v1/generation/task/query
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

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class TaskStatus:
    COMPLETED = "completed"
    FAILED = "failed"
    PROCESSING = "processing"
    PENDING = "pending"


# ── 防重复推送 ────────────────────────────────────────────────────────
def _get_log_dir() -> Path:
    log_dir = Path.home() / '.openclaw' / 'skills' / 'giggle-generation-music' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _check_sent(task_id: str) -> bool:
    return (_get_log_dir() / f"{task_id}.sent").exists()


def _mark_sent(task_id: str) -> None:
    (_get_log_dir() / f"{task_id}.sent").touch()


def _save_prompt(task_id: str, text: str) -> None:
    try:
        (_get_log_dir() / f"{task_id}.prompt").write_text(text, encoding='utf-8')
    except Exception:
        pass


def _load_prompt(task_id: str) -> Optional[str]:
    try:
        f = _get_log_dir() / f"{task_id}.prompt"
        if f.exists():
            p = f.read_text(encoding='utf-8').strip()
            return p[:20] + "..." if len(p) > 20 else p
    except Exception:
        pass
    return None


def _increment_query_count(task_id: str) -> int:
    f = _get_log_dir() / f"{task_id}.count"
    count = int(f.read_text().strip()) + 1 if f.exists() else 1
    f.write_text(str(count))
    return count


def to_view_url(url: str) -> str:
    """将下载 URL 转为在线收听 URL"""
    url = url.replace("&response-content-disposition=attachment", "")
    url = url.replace("?response-content-disposition=attachment&", "?")
    url = url.replace("?response-content-disposition=attachment", "")
    return url.replace("~", "%7E")


class GenerationMusicAPI:
    """giggle.pro Generation Music API 客户端"""

    BASE_URL = "https://giggle.pro"
    GENERATE = "/api/v1/generation/generate-music"
    QUERY = "/api/v1/generation/task/query"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"x-auth": api_key, "Content-Type": "application/json"}

    def prompt_generate(
        self,
        prompt: str,
        vocal_gender: Optional[str] = None,
        instrumental: bool = False
    ) -> Dict[str, Any]:
        """提示词模式：根据描述生成"""
        payload = {"prompt": prompt, "instrumental": instrumental}
        if vocal_gender:
            payload["vocal_gender"] = vocal_gender
        return self._post(self.GENERATE, payload)

    def custom_generate(
        self,
        lyrics: str,
        style: str,
        title: str,
        vocal_gender: Optional[str] = None,
        instrumental: bool = False
    ) -> Dict[str, Any]:
        """自定义模式：根据歌词生成"""
        payload = {
            "lyrics": lyrics,
            "style": style,
            "title": title,
            "instrumental": instrumental
        }
        if vocal_gender:
            payload["vocal_gender"] = vocal_gender
        return self._post(self.GENERATE, payload)

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
        url = f"{self.BASE_URL}{self.QUERY}"
        try:
            resp = requests.get(url, headers=self.headers, params={"task_id": task_id}, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") != 200:
                raise Exception(result.get("msg", result.get("message", "未知错误")))
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"查询失败: {str(e)}")

    def extract_audio_urls(self, task_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """从任务结果提取音频 URL"""
        urls = task_result.get("data", {}).get("urls", [])
        return [
            {"title": f"music_{i}", "audioUrl": to_view_url(u)}
            for i, u in enumerate(urls, 1)
        ]


def parse_args():
    parser = argparse.ArgumentParser(
        description='giggle.pro Generation Music API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 提示词模式
  python generation_music_api.py --prompt "轻松活泼的流行音乐" --vocal-gender female --no-wait

  # 自定义模式（歌词）
  python generation_music_api.py --custom --lyrics "歌词内容" --style pop --title "美好时光" --no-wait

  # 查询
  python generation_music_api.py --query --task-id xxx --poll
        """
    )
    parser.add_argument('--query', action='store_true', help='查询任务')
    parser.add_argument('--poll', action='store_true', help='轮询等待完成')
    parser.add_argument('--prompt', type=str, help='音乐描述（提示词模式）')
    parser.add_argument('--custom', action='store_true', help='自定义模式')
    parser.add_argument('--lyrics', type=str, help='歌词内容（自定义模式）')
    parser.add_argument('--style', type=str, help='音乐风格，如 pop')
    parser.add_argument('--title', type=str, help='歌曲标题')
    parser.add_argument('--vocal-gender', type=str, choices=['male', 'female'])
    parser.add_argument('--instrumental', action='store_true', help='纯音乐')
    parser.add_argument('--api-key', type=str)
    parser.add_argument('--task-id', type=str)
    parser.add_argument('--no-wait', action='store_true')
    parser.add_argument('--max-wait', type=int, default=300)
    parser.add_argument('--poll-interval', type=int, default=10)
    parser.add_argument('--json', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()

    if DOTENV_AVAILABLE:
        for p in [Path.cwd() / ".env", Path(__file__).parent.parent / ".env",
                  Path(__file__).parent.parent.parent / ".env"]:
            if p.exists():
                load_dotenv(p)
                break

    api_key = args.api_key or os.getenv("GIGGLE_API_KEY")
    if not api_key:
        print("错误: 未设置 GIGGLE_API_KEY", file=sys.stderr)
        print("  1. 项目根目录 .env 添加 GIGGLE_API_KEY=xxx", file=sys.stderr)
        print("  2. export GIGGLE_API_KEY=xxx", file=sys.stderr)
        sys.exit(1)

    client = GenerationMusicAPI(api_key)
    task_id = None
    submitted_at = None
    prompt_text = ""  # 用于 query 时展示

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
                    if status == TaskStatus.COMPLETED:
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
                if count > 5:
                    pt = _load_prompt(args.task_id) or "音乐"
                    print(f"⏰ 音乐生成超时\n\n关于「{pt}」的创作已等待超过 10 分钟，未能完成。\n\n💡 建议重新生成，我随时待命~")
                    sys.exit(0)
                try:
                    result = client.query_task(args.task_id)
                except Exception as e:
                    print(json.dumps({"status": "network_error", "task_id": args.task_id}, ensure_ascii=False))
                    print(f"网络异常: {e}", file=sys.stderr)
                    sys.exit(0)

            data = result.get("data", {})
            status = data.get("status", "")

            if status == TaskStatus.COMPLETED:
                if _check_sent(args.task_id):
                    sys.exit(0)
                audio_list = client.extract_audio_urls(result)
                if not audio_list:
                    pt = _load_prompt(args.task_id) or "音乐"
                    print(f"😔 音乐生成遇到了问题\n\n关于「{pt}」的创作虽已完成但未返回音频。\n\n💡 建议重新生成~")
                    sys.exit(0)
                _mark_sent(args.task_id)
                pt = _load_prompt(args.task_id) or "音乐"
                n = len(audio_list)
                lines = [f"🎵 [{a['title']}]({a['audioUrl']})" for a in audio_list]
                print(f"🎶 音乐已就绪！\n\n关于「{pt}」的创作已完成，共 {n} 首 ✨\n")
                print("\n".join(lines))
                print("\n如需调整，随时告诉我~")
                sys.exit(0)
            elif status in ("failed", "error"):
                err = data.get("err_msg", "未知错误")
                pt = _load_prompt(args.task_id) or "音乐"
                print(f"😔 音乐生成遇到了问题\n\n关于「{pt}」的创作未能完成：{err}\n\n💡 建议调整后重新尝试，我随时待命~")
                sys.exit(0)
            else:
                print(json.dumps({"status": status, "task_id": args.task_id}, ensure_ascii=False))
                sys.exit(0)

        # 生成模式
        if args.custom:
            if not args.lyrics or not args.style or not args.title:
                print("错误: 自定义模式需 --lyrics --style --title", file=sys.stderr)
                sys.exit(1)
            if not args.instrumental and not args.lyrics.strip():
                print("错误: 非纯音乐模式需提供歌词", file=sys.stderr)
                sys.exit(1)
            print("自定义模式生成音乐...", file=sys.stderr)
            result = client.custom_generate(
                lyrics=args.lyrics,
                style=args.style,
                title=args.title,
                vocal_gender=args.vocal_gender,
                instrumental=args.instrumental
            )
            prompt_text = args.title or args.lyrics[:30]
        else:
            if not args.prompt:
                print("错误: 提示词模式需 --prompt", file=sys.stderr)
                sys.exit(1)
            print("提示词模式生成音乐...", file=sys.stderr)
            result = client.prompt_generate(
                prompt=args.prompt,
                vocal_gender=args.vocal_gender,
                instrumental=args.instrumental
            )
            prompt_text = args.prompt

        task_id = result.get("data", {}).get("task_id")
        submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"✓ 任务创建成功! TaskID: {task_id}", file=sys.stderr)

        if not args.no_wait:
            print(f"等待完成（最多 {args.max_wait} 秒）...", file=sys.stderr)
            start = time.time()
            while time.time() - start < args.max_wait:
                result = client.query_task(task_id)
                data = result.get("data", {})
                st = data.get("status", "")
                if st == TaskStatus.COMPLETED:
                    break
                if st in ("failed", "error"):
                    raise Exception(data.get("err_msg", "生成失败"))
                time.sleep(args.poll_interval)
            else:
                raise Exception(f"等待超时 ({args.max_wait}秒)")
            audio_list = client.extract_audio_urls(result)
            if args.json:
                print(json.dumps([{"title": a["title"], "audioUrl": a["audioUrl"]} for a in audio_list],
                               ensure_ascii=False, indent=2))
            else:
                print("\n" + "=" * 60)
                print("音乐生成完成")
                print("=" * 60)
                for i, a in enumerate(audio_list, 1):
                    print(f"音乐 #{i}: {a['title']}\n收听: {a['audioUrl']}")
                print("=" * 60)
        else:
            _save_prompt(task_id, prompt_text)
            print(json.dumps({"status": "started", "task_id": task_id}, ensure_ascii=False))

    except Exception as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
