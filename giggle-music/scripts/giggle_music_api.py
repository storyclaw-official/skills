#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
giggle.pro 平台 AI 音乐生成 API 封装脚本
支持简化模式和自定义模式生成音乐
使用方法：python giggle_music_api.py --prompt "音乐描述" [其他参数]
"""

import os
import sys
import time
import json
import argparse
import warnings
warnings.filterwarnings("ignore")  # 抑制 LibreSSL/urllib3 等运行时警告
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

# 尝试导入 dotenv，如果不存在则忽略
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class VocalGender(str, Enum):
    """人声性别枚举"""
    MALE = "male"
    FEMALE = "female"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    COMPLETED = "completed"
    FAILED = "failed"
    PROCESSING = "processing"
    PENDING = "pending"


class GiggleMusicAPI:
    """giggle.pro 平台 AI 音乐生成 API 封装类"""

    BASE_URL = "https://giggle.pro"
    GENERATE_ENDPOINT = "/api/v1/generation/generate-music"
    QUERY_ENDPOINT = "/api/v1/generation/task/query"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-auth": api_key,
            "Content-Type": "application/json"
        }

    def simple_generate(self, prompt: str, instrumental: bool = False) -> Dict[str, Any]:
        """简化模式生成音乐，只需 prompt"""
        payload = {
            "prompt": prompt,
            "instrumental": instrumental
        }
        return self._make_request(payload)

    def custom_generate(
        self,
        prompt: str,
        style: str,
        title: str,
        instrumental: bool = False,
        vocal_gender: Optional[VocalGender] = None
    ) -> Dict[str, Any]:
        """自定义模式生成音乐，支持歌词、风格、标题、人声性别"""
        payload = {
            "style": style,
            "title": title,
            "instrumental": instrumental
        }

        if not instrumental:
            payload["lyrics"] = prompt

        if vocal_gender:
            payload["vocal_gender"] = vocal_gender.value

        return self._make_request(payload)

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """发送生成音乐请求"""
        url = f"{self.BASE_URL}{self.GENERATE_ENDPOINT}"

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 200:
                raise Exception(f"API错误: {result.get('msg', result.get('message', '未知错误'))}")

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")

    def query_task(self, task_id: str) -> Dict[str, Any]:
        """查询任务详情"""
        url = f"{self.BASE_URL}{self.QUERY_ENDPOINT}"
        params = {"task_id": task_id}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 200:
                raise Exception(f"API错误: {result.get('msg', result.get('message', '未知错误'))}")

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"查询失败: {str(e)}")

    def wait_for_completion(
        self,
        task_id: str,
        max_wait_time: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """轮询等待任务完成"""
        start_time = time.time()
        last_logged_status = ""

        while time.time() - start_time < max_wait_time:
            result = self.query_task(task_id)
            data = result.get("data", {})
            status = data.get("status")

            # 仅在状态变化时打印，避免重复日志
            if status != last_logged_status:
                print(f"任务状态: {status}", file=sys.stderr)
                last_logged_status = status

            if status == TaskStatus.COMPLETED.value:
                print("✓ 任务完成!", file=sys.stderr)
                return result
            elif status == TaskStatus.FAILED.value:
                error_msg = data.get("err_msg", "未知错误")
                raise Exception(f"任务失败: {error_msg}")

            time.sleep(poll_interval)

        raise Exception(f"等待超时 ({max_wait_time}秒)")

    def extract_audio_urls(self, task_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """从任务结果中提取音频 URL 列表"""
        data = task_result.get("data", {})
        urls = data.get("urls", [])

        audio_list = []
        for i, url in enumerate(urls, 1):
            # 去掉 response-content-disposition=attachment，生成在线收听链接
            view_url = url.replace("&response-content-disposition=attachment", "")
            audio_list.append({
                "title": f"music_{i}",
                "audioUrl": view_url,    # 在线收听链接（浏览器直接播放）
                "downloadUrl": url,      # 下载链接（带 attachment 参数）
            })

        return audio_list


def _get_music_log_dir() -> Path:
    """获取 giggle-music 日志目录"""
    log_dir = Path.home() / '.openclaw' / 'skills' / 'giggle-music' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _setup_music_log(task_id: str) -> Path:
    """创建任务日志文件，返回路径"""
    from datetime import datetime as _dt
    log_dir = _get_music_log_dir()
    log_file = log_dir / f"{task_id}_{_dt.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file.touch()
    return log_file


def _check_music_sent(task_id: str) -> bool:
    """检查是否已推送过结果（.sent 防重复）"""
    sent_file = _get_music_log_dir() / f"{task_id}.sent"
    return sent_file.exists()


def _mark_music_sent(task_id: str) -> None:
    """标记已推送结果"""
    sent_file = _get_music_log_dir() / f"{task_id}.sent"
    sent_file.touch()


def load_api_key() -> str:
    """从 .env 文件加载 API 密钥"""
    if DOTENV_AVAILABLE:
        env_paths = [
            Path.cwd() / ".env",
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",  # ~/.openclaw/skills/.env
        ]

        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break

    api_key = os.getenv("GIGGLE_API_KEY")
    if not api_key:
        print("错误: 未设置API密钥", file=sys.stderr)
        print("请在项目根目录创建 .env 文件，添加: GIGGLE_API_KEY=your-api-key", file=sys.stderr)
        if not DOTENV_AVAILABLE:
            print("提示: 请先安装 python-dotenv: pip install python-dotenv", file=sys.stderr)
        sys.exit(1)

    return api_key


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='giggle.pro 平台 AI 音乐生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python giggle_music_api.py --prompt "一首欢快的流行歌曲"
  python giggle_music_api.py --custom --prompt "歌词" --style "流行" --title "我的歌" --vocal-gender female
  python giggle_music_api.py --query --task-id "your_task_id"
        """
    )

    # 操作模式
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('--query', action='store_true',
                           help='查询已存在的任务（需配合 --task-id）')
    mode_group.add_argument('--custom', action='store_true',
                           help='使用自定义模式（详细控制）')

    # 基本参数
    parser.add_argument('--prompt', type=str, help='音乐提示词/歌词内容')
    parser.add_argument('--task-id', type=str, help='任务ID（仅 --query 模式）')

    # 自定义模式参数
    parser.add_argument('--style', type=str, help='音乐风格（自定义模式必需）')
    parser.add_argument('--title', type=str, help='音乐标题（自定义模式必需）')

    # 通用可选参数
    parser.add_argument('--instrumental', action='store_true', help='生成纯音乐（无歌词）')
    parser.add_argument('--vocal-gender', type=str, choices=['male', 'female'],
                       help='人声性别偏好（仅自定义模式）')

    # 轮询参数
    parser.add_argument('--no-wait', action='store_true', help='不等待任务完成')
    parser.add_argument('--max-wait', type=int, default=300, help='最大等待秒数（默认300）')
    parser.add_argument('--poll-interval', type=int, default=10, help='轮询间隔秒数（默认10）')

    # 输出参数
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    return parser.parse_args()


def print_output(audio_list: List[Dict[str, Any]], output_json: bool = False):
    """输出结果到 stdout"""
    output_data = [{"title": a.get("title", ""), "audioUrl": a.get("audioUrl", "")} for a in audio_list]

    if output_json:
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        for i, item in enumerate(output_data, 1):
            print(f"\n{'=' * 60}")
            print(f"音乐 #{i}")
            print(f"{'=' * 60}")
            print(f"音乐标题: {item['title']}")
            print(f"下载链接: {item['audioUrl']}")


def main():
    """主函数"""
    args = parse_args()
    api_key = load_api_key()
    client = GiggleMusicAPI(api_key)

    try:
        # 查询模式
        if args.query:
            if not args.task_id:
                print("错误: 查询模式需要提供 --task-id 参数", file=sys.stderr)
                sys.exit(1)

            result = client.query_task(args.task_id)
            data = result.get("data", {})
            status = data.get("status")

            if status == TaskStatus.COMPLETED.value:
                # 防重复：检查 .sent 文件
                if _check_music_sent(args.task_id):
                    print(json.dumps({"status": "already_sent", "task_id": args.task_id}, ensure_ascii=False))
                    sys.exit(0)
                audio_list = client.extract_audio_urls(result)
                print(f"\n生成了 {len(audio_list)} 首音乐\n", file=sys.stderr)
                # 标记已推送
                _mark_music_sent(args.task_id)
                print_output(audio_list, args.json)
                sys.exit(0)
            elif status == TaskStatus.FAILED.value:
                # stdout 输出供 agent 读取；exit(1) 通知 cron 停止
                print(json.dumps({"status": "failed", "err_msg": data.get("err_msg", "未知错误"), "task_id": args.task_id}, ensure_ascii=False))
                sys.exit(1)
            else:
                # processing / pending → exit(2)，cron 继续；不输出 stderr 避免触发 exec failed
                print(json.dumps({"status": status, "task_id": args.task_id}, ensure_ascii=False))
                sys.exit(2)

        # 自定义模式
        elif args.custom:
            if not args.style or not args.title:
                print("错误: 自定义模式需要提供 --style 和 --title 参数", file=sys.stderr)
                sys.exit(1)

            prompt = args.prompt or ""
            if not args.instrumental and not prompt:
                print("错误: 非纯音乐模式需要提供 --prompt 参数", file=sys.stderr)
                sys.exit(1)

            print("使用自定义模式生成音乐...", file=sys.stderr)

            kwargs = {
                "prompt": prompt,
                "style": args.style,
                "title": args.title,
                "instrumental": args.instrumental
            }

            if args.vocal_gender:
                kwargs["vocal_gender"] = VocalGender.MALE if args.vocal_gender == 'male' else VocalGender.FEMALE

            result = client.custom_generate(**kwargs)
            task_id = result.get("data", {}).get("task_id")
            print(f"✓ 任务创建成功! TaskID: {task_id}", file=sys.stderr)

            if not args.no_wait:
                print(f"等待任务完成（最多{args.max_wait}秒）...", file=sys.stderr)
                final_result = client.wait_for_completion(
                    task_id=task_id,
                    max_wait_time=args.max_wait,
                    poll_interval=args.poll_interval
                )
                audio_list = client.extract_audio_urls(final_result)
                print(f"\n生成了 {len(audio_list)} 首音乐\n", file=sys.stderr)
                print_output(audio_list, args.json)
            else:
                # 输出到 stdout，exec 可读取 task_id
                log_file = _setup_music_log(task_id)
                print(json.dumps({"status": "started", "task_id": task_id, "log_file": str(log_file)}, ensure_ascii=False))

        # 简化模式（默认）
        else:
            if not args.prompt:
                print("错误: 简化模式需要提供 --prompt 参数", file=sys.stderr)
                sys.exit(1)

            print("使用简化模式生成音乐...", file=sys.stderr)

            result = client.simple_generate(
                prompt=args.prompt,
                instrumental=args.instrumental
            )

            task_id = result.get("data", {}).get("task_id")
            print(f"✓ 任务创建成功! TaskID: {task_id}", file=sys.stderr)

            if not args.no_wait:
                print(f"等待任务完成（最多{args.max_wait}秒）...", file=sys.stderr)
                final_result = client.wait_for_completion(
                    task_id=task_id,
                    max_wait_time=args.max_wait,
                    poll_interval=args.poll_interval
                )
                audio_list = client.extract_audio_urls(final_result)
                print(f"\n生成了 {len(audio_list)} 首音乐\n", file=sys.stderr)
                print_output(audio_list, args.json)
            else:
                # 输出到 stdout，exec 可读取 task_id
                log_file = _setup_music_log(task_id)
                print(json.dumps({"status": "started", "task_id": task_id, "log_file": str(log_file)}, ensure_ascii=False))

    except Exception as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
