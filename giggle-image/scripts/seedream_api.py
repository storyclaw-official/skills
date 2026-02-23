#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
giggle.pro 平台 Seedream (seedream45) API 封装脚本
支持文生图、图生图和多图融合(最多10张)
使用方法: python seedream_api.py --prompt "图像描述" [其他参数]
"""

import os
import sys
import time
import json
import base64
import argparse
import warnings
warnings.filterwarnings("ignore")  # 抑制 LibreSSL/urllib3 等运行时警告
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

# 尝试导入 dotenv，如果不存在则忽略
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class AspectRatio(str, Enum):
    """图像比例枚举"""
    RATIO_1_1 = "1:1"
    RATIO_3_4 = "3:4"
    RATIO_4_3 = "4:3"
    RATIO_16_9 = "16:9"
    RATIO_9_16 = "9:16"
    RATIO_2_3 = "2:3"
    RATIO_3_2 = "3:2"
    RATIO_21_9 = "21:9"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    COMPLETED = "completed"
    FAILED = "failed"
    PROCESSING = "processing"
    PENDING = "pending"


SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def resolve_image_ref(image_ref: str) -> Dict[str, str]:
    """
    解析图像引用，自动判断是 URL 还是本地文件路径

    - URL (http/https 开头) → {"url": "..."}
    - 本地文件路径 → {"base64": "<纯base64字符串>"}

    Args:
        image_ref: 图像 URL 或本地文件路径

    Returns:
        {"url": "..."} 或 {"base64": "<纯base64字符串>"}
    """
    # URL 判断
    if image_ref.startswith("http://") or image_ref.startswith("https://"):
        return {"url": image_ref}

    # 本地文件路径
    file_path = Path(image_ref).expanduser().resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"图像文件不存在: {file_path}")

    if file_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(f"不支持的图像格式: {file_path.suffix} (支持: {', '.join(SUPPORTED_IMAGE_EXTENSIONS)})")

    # 读取并编码为纯 base64 字符串
    with open(file_path, "rb") as f:
        image_data = f.read()

    b64_str = base64.b64encode(image_data).decode("utf-8")

    print(f"✓ 已编码本地图像: {file_path.name} ({len(image_data) / 1024:.1f} KB)", file=sys.stderr)

    return {"base64": b64_str}


class SeedreamAPI:
    """giggle.pro 平台 Seedream API 客户端"""

    BASE_URL = "https://giggle.pro"
    TEXT_TO_IMAGE_ENDPOINT = "/api/v1/generation/text-to-image"
    IMAGE_TO_IMAGE_ENDPOINT = "/api/v1/generation/image-to-image"
    QUERY_TASK_ENDPOINT = "/api/v1/generation/task/query"
    MODEL_NAME = "seedream45"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-auth": api_key,
            "Content-Type": "application/json"
        }

    def generate(
        self,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        generate_count: int = 1,
        aspect_ratio: AspectRatio = AspectRatio.RATIO_16_9,
        watermark: bool = False
    ) -> Dict[str, Any]:
        """
        提交图像生成任务

        Args:
            prompt: 图像描述提示词
            reference_images: 参考图像URL或本地文件路径列表(1张=图生图, 2-10张=多图融合)
            generate_count: 生成数量，默认1
            aspect_ratio: 图像比例，默认16:9
            watermark: 是否添加水印，默认false

        Returns:
            包含 task_id 的响应字典
        """
        if reference_images and len(reference_images) > 10:
            raise ValueError("最多支持 10 张参考图像")

        # 构建请求体
        payload = {
            "prompt": prompt,
            "generate_count": generate_count,
            "model": self.MODEL_NAME,
            "aspect_ratio": aspect_ratio.value,
            "watermark": watermark
        }

        # 根据是否有参考图选择端点
        if reference_images and len(reference_images) > 0:
            # 自动判断每个引用是 URL 还是本地文件，分别处理
            resolved = [resolve_image_ref(ref) for ref in reference_images]
            payload["reference_images"] = resolved
            endpoint = self.IMAGE_TO_IMAGE_ENDPOINT
            mode = f"图生图({len(reference_images)}张参考图)" if len(reference_images) == 1 else f"多图融合({len(reference_images)}张)"
        else:
            endpoint = self.TEXT_TO_IMAGE_ENDPOINT
            mode = "文生图"

        print(f"模式: {mode}", file=sys.stderr)

        url = f"{self.BASE_URL}{endpoint}"

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
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务详情字典
        """
        url = f"{self.BASE_URL}{self.QUERY_TASK_ENDPOINT}"
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
        """
        轮询等待任务完成

        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间(秒)，默认300秒
            poll_interval: 轮询间隔(秒)，默认5秒

        Returns:
            完成后的任务详情
        """
        start_time = time.time()
        last_logged_status = ""

        while time.time() - start_time < max_wait_time:
            result = self.query_task(task_id)
            data = result.get("data", {})
            status = data.get("status", "")

            # 仅在状态变化时打印，避免重复日志
            if status != last_logged_status:
                print(f"任务状态: {status}", file=sys.stderr)
                last_logged_status = status

            if status == TaskStatus.COMPLETED.value:
                print("✓ 任务完成!", file=sys.stderr)
                return result
            elif status == TaskStatus.FAILED.value:
                err_msg = data.get("err_msg", "未知错误")
                raise Exception(f"任务失败: {err_msg}")

            time.sleep(poll_interval)

        raise Exception(f"等待超时 ({max_wait_time}秒)")

    def extract_image_urls(self, task_result: Dict[str, Any]) -> List[str]:
        """
        从任务结果中提取图像URL

        Args:
            task_result: query_task 或 wait_for_completion 返回的结果

        Returns:
            图像URL列表
        """
        data = task_result.get("data", {})
        return data.get("urls", [])


def to_view_url(url: str) -> str:
    """将下载 URL 转换为在线查看 URL（去掉 response-content-disposition=attachment 参数）"""
    # 去掉 &response-content-disposition=attachment（参数在中间或末尾均兼容）
    url = url.replace("&response-content-disposition=attachment", "")
    url = url.replace("?response-content-disposition=attachment&", "?")
    url = url.replace("?response-content-disposition=attachment", "")
    return url


def download_images(image_urls: List[str], output_dir: str) -> List[str]:
    """
    下载图像到本地

    Args:
        image_urls: 图像URL列表
        output_dir: 输出目录

    Returns:
        下载的文件路径列表
    """
    download_path = Path(output_dir).expanduser()
    download_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    downloaded_files = []
    for i, url in enumerate(image_urls, 1):
        try:
            # 从 URL 推断扩展名，默认 png
            ext = "png"
            if ".jpg" in url or ".jpeg" in url:
                ext = "jpg"
            elif ".webp" in url:
                ext = "webp"

            if len(image_urls) == 1:
                filename = f"seedream_{timestamp}.{ext}"
            else:
                filename = f"seedream_{timestamp}_{i}.{ext}"

            filepath = download_path / filename

            print(f"下载图像 {i}/{len(image_urls)}...", file=sys.stderr)
            download_headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": url
            }
            response = requests.get(url, headers=download_headers, timeout=60)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(response.content)
            downloaded_files.append(str(filepath))
            print(f"✓ 图像已下载: {filepath}", file=sys.stderr)

        except Exception as e:
            print(f"✗ 下载失败 (图像 {i}): {e}", file=sys.stderr)

    return downloaded_files


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='giggle.pro Seedream API - AI图像生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 文生图
  python seedream_api.py --prompt "一只可爱的猫咪在阳光下"

  # 指定比例
  python seedream_api.py --prompt "未来城市夜景" --aspect-ratio 16:9 --json

  # 图生图（URL）
  python seedream_api.py --prompt "转为油画风格" --reference-images "https://example.com/photo.jpg" --json

  # 图生图（本地文件，自动 base64 编码）
  python seedream_api.py --prompt "转为油画风格" --reference-images "/path/to/photo.jpg" --json

  # 多图融合（URL 和本地文件可混用）
  python seedream_api.py --prompt "融合风格" --reference-images "url1" "/path/to/local.png" "url2" --json

  # 生成并下载
  python seedream_api.py --prompt "描述" --download

  # 查询任务
  python seedream_api.py --query --task-id "your_task_id"

配置方式:
  1. .env 文件: 在项目根目录创建 .env 文件，添加 GIGGLE_API_KEY=your-key
  2. 环境变量: export GIGGLE_API_KEY=your-key
  3. 命令行参数: --api-key your-key
        """
    )

    # 操作模式
    parser.add_argument('--query', action='store_true',
                       help='查询已存在的任务(需配合 --task-id)')

    # 基本参数
    parser.add_argument('--prompt', type=str,
                       help='图像描述提示词')
    parser.add_argument('--api-key', type=str,
                       help='API密钥(也可通过环境变量 GIGGLE_API_KEY 设置)')
    parser.add_argument('--task-id', type=str,
                       help='要查询的任务ID(仅在 --query 模式下使用)')

    # 图像参数
    parser.add_argument('--reference-images', type=str, nargs='+',
                       help='参考图像URL或本地文件路径(支持多个，最多10张，本地文件自动base64编码)')
    parser.add_argument('--generate-count', type=int, default=1,
                       help='生成数量(默认: 1)')
    parser.add_argument('--aspect-ratio', type=str, default='16:9',
                       choices=['1:1', '3:4', '4:3', '16:9', '9:16', '2:3', '3:2', '21:9'],
                       help='图像比例(默认: 16:9)')
    parser.add_argument('--watermark', action='store_true',
                       help='添加水印')

    # 下载参数
    parser.add_argument('--download', action='store_true',
                       help='自动下载生成的图像到本地')
    parser.add_argument('--output-dir', type=str, default='~/Downloads',
                       help='下载保存目录(默认: ~/Downloads)')

    # 任务管理参数
    parser.add_argument('--no-wait', action='store_true',
                       help='不等待任务完成，创建后立即返回')
    parser.add_argument('--max-wait', type=int, default=300,
                       help='最大等待时间(秒)，默认300秒')
    parser.add_argument('--poll-interval', type=int, default=5,
                       help='轮询间隔(秒)，默认5秒')

    # 输出参数
    parser.add_argument('--json', action='store_true',
                       help='以JSON格式输出结果')

    return parser.parse_args()


def print_output(image_urls: List[str], prompt: str, output_json: bool = False, downloaded_files: Optional[List[str]] = None):
    """
    输出结果

    Args:
        image_urls: 图像URL列表（原始下载URL）
        prompt: 原始提示词
        output_json: 是否以JSON格式输出
        downloaded_files: 下载的文件路径列表
    """
    view_urls = [to_view_url(u) for u in image_urls]

    if output_json:
        output_data = {
            "prompt": prompt,
            "urls": image_urls,        # 原始下载 URL（带 response-content-disposition=attachment）
            "view_urls": view_urls,    # 在线查看 URL（浏览器直接显示图像）
            "imageCount": len(image_urls)
        }
        if downloaded_files:
            output_data["downloadedFiles"] = downloaded_files
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        print()
        print("=" * 60)
        print("图像生成完成")
        print("=" * 60)
        print(f"提示词: {prompt}")
        print(f"生成数量: {len(image_urls)} 张")
        print()
        for i, (view_url, dl_url) in enumerate(zip(view_urls, image_urls), 1):
            print(f"图像 #{i} 在线查看: {view_url}")
            print(f"图像 #{i} 下载链接: {dl_url}")

        if downloaded_files:
            print()
            print("下载文件:")
            for i, filepath in enumerate(downloaded_files, 1):
                print(f"文件 #{i}: {filepath}")

        print("=" * 60)


def main():
    """主函数"""
    args = parse_args()

    # 加载 .env 文件（如果存在）
    if DOTENV_AVAILABLE:
        env_paths = [
            Path.cwd() / ".env",
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",  # ~/.openclaw/skills/.env
        ]

        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"✓ 已加载配置文件: {env_path}", file=sys.stderr)
                break

    # 获取API密钥（优先级：命令行 > 环境变量 > .env 文件）
    api_key = args.api_key or os.getenv("GIGGLE_API_KEY")
    if not api_key:
        print("错误: 未设置API密钥", file=sys.stderr)
        print("", file=sys.stderr)
        print("请使用以下任意一种方式设置:", file=sys.stderr)
        print("  1. 在项目根目录创建 .env 文件，添加: GIGGLE_API_KEY=your-api-key", file=sys.stderr)
        print("  2. 设置环境变量: export GIGGLE_API_KEY=your-api-key", file=sys.stderr)
        print("  3. 使用命令行参数: --api-key your-api-key", file=sys.stderr)
        sys.exit(1)

    # 初始化客户端
    client = SeedreamAPI(api_key)

    try:
        # 查询模式
        if args.query:
            if not args.task_id:
                print("错误: 查询模式需要提供 --task-id 参数", file=sys.stderr)
                sys.exit(1)

            print(f"查询任务: {args.task_id}", file=sys.stderr)
            result = client.query_task(args.task_id)
            data = result.get("data", {})
            status = data.get("status", "")

            print(f"任务状态: {status}", file=sys.stderr)

            if status == TaskStatus.COMPLETED.value:
                image_urls = client.extract_image_urls(result)
                prompt = args.prompt or ""

                print(f"\n生成了 {len(image_urls)} 张图像\n", file=sys.stderr)

                downloaded_files = None
                if args.download and image_urls:
                    print("\n下载图像...", file=sys.stderr)
                    downloaded_files = download_images(image_urls, args.output_dir)

                print_output(image_urls, prompt, args.json, downloaded_files)
                # exit(0) 表示完成
            elif status in ("failed", "error"):
                # exit(1) 表示失败
                err_msg = data.get("err_msg", "未知错误")
                print(f"任务失败: {err_msg}", file=sys.stderr)
                if args.json:
                    print(json.dumps({"status": "failed", "error": err_msg}, ensure_ascii=False))
                sys.exit(1)
            else:
                # exit(2) 表示进行中（processing/pending），cron 继续等待
                print(f"任务进行中: {status}", file=sys.stderr)
                if args.json:
                    print(json.dumps({"status": status}, ensure_ascii=False))
                sys.exit(2)

        # 生成模式
        else:
            if not args.prompt:
                print("错误: 生成模式需要提供 --prompt 参数", file=sys.stderr)
                sys.exit(1)

            print("创建图像生成任务...", file=sys.stderr)

            aspect_ratio = AspectRatio(args.aspect_ratio)

            result = client.generate(
                prompt=args.prompt,
                reference_images=args.reference_images,
                generate_count=args.generate_count,
                aspect_ratio=aspect_ratio,
                watermark=args.watermark
            )

            task_id = result.get("data", {}).get("task_id")
            print(f"✓ 任务创建成功! TaskID: {task_id}", file=sys.stderr)

            # 等待完成
            if not args.no_wait:
                print(f"等待任务完成(最多{args.max_wait}秒)...", file=sys.stderr)
                final_result = client.wait_for_completion(
                    task_id=task_id,
                    max_wait_time=args.max_wait,
                    poll_interval=args.poll_interval
                )
                image_urls = client.extract_image_urls(final_result)
                print(f"\n生成了 {len(image_urls)} 张图像\n", file=sys.stderr)

                downloaded_files = None
                if args.download and image_urls:
                    print("\n下载图像...", file=sys.stderr)
                    downloaded_files = download_images(image_urls, args.output_dir)

                print_output(image_urls, args.prompt, args.json, downloaded_files)
            else:
                # --no-wait 模式：输出 task_id 到 stdout，exec 可捕获
                print(json.dumps({"status": "started", "task_id": task_id}, ensure_ascii=False))

    except Exception as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
