#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kie平台 Nano Banana Pro API 封装脚本
支持文生图、图生图和多图融合(最多8张)
支持自动下载图像到本地
使用方法: python kie_nano_banana_api.py --prompt "图像描述" [其他参数]
"""

import os
import sys
import time
import json
import argparse
import requests
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class AspectRatio(str, Enum):
    """图像比例枚举"""
    RATIO_1_1 = "1:1"
    RATIO_2_3 = "2:3"
    RATIO_3_2 = "3:2"
    RATIO_3_4 = "3:4"
    RATIO_4_3 = "4:3"
    RATIO_4_5 = "4:5"
    RATIO_5_4 = "5:4"
    RATIO_9_16 = "9:16"
    RATIO_16_9 = "16:9"
    RATIO_21_9 = "21:9"
    AUTO = "auto"


class Resolution(str, Enum):
    """图像清晰度枚举"""
    K1 = "1K"
    K2 = "2K"
    K4 = "4K"


class OutputFormat(str, Enum):
    """输出格式枚举"""
    PNG = "png"
    JPG = "jpg"


class TaskState(str, Enum):
    """任务状态枚举"""
    WAITING = "waiting"
    SUCCESS = "success"
    FAIL = "fail"


class KieNanoBananaAPI:
    """Kie 平台 Nano Banana Pro API 客户端"""

    BASE_URL = "https://api.kie.ai"
    CREATE_TASK_ENDPOINT = "/api/v1/jobs/createTask"
    QUERY_TASK_ENDPOINT = "/api/v1/jobs/recordInfo"
    MODEL_NAME = "nano-banana-pro"

    def __init__(self, api_key: str):
        """
        初始化 API 客户端

        Args:
            api_key: kie平台的API密钥
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def create_task(
        self,
        prompt: str,
        aspect_ratio: AspectRatio = AspectRatio.RATIO_1_1,
        resolution: Resolution = Resolution.K2,
        output_format: OutputFormat = OutputFormat.PNG,
        image_input: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        创建图像生成任务

        Args:
            prompt: 图像描述提示词,最多20000字符
            aspect_ratio: 图像比例,默认1:1
            resolution: 图像清晰度,默认2K
            output_format: 输出格式,默认png
            image_input: 参考图像URL列表,最多8张

        Returns:
            包含 taskId 的响应字典
        """
        # 验证参数
        if len(prompt) > 20000:
            raise ValueError("prompt 长度不能超过 20000 字符")

        if image_input and len(image_input) > 8:
            raise ValueError("最多支持 8 张参考图像")

        # 构建请求体
        payload = {
            "model": self.MODEL_NAME,
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio.value,
                "resolution": resolution.value,
                "output_format": output_format.value,
                "image_input": image_input or []
            }
        }

        url = f"{self.BASE_URL}{self.CREATE_TASK_ENDPOINT}"

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 200:
                raise Exception(f"API错误: {result.get('msg', '未知错误')}")

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
        params = {"taskId": task_id}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 200:
                raise Exception(f"API错误: {result.get('msg', '未知错误')}")

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
            max_wait_time: 最大等待时间(秒),默认300秒
            poll_interval: 轮询间隔(秒),默认5秒

        Returns:
            完成后的任务详情
        """
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            result = self.query_task(task_id)
            data = result.get("data", {})
            state = data.get("state")

            print(f"任务状态: {state}", file=sys.stderr)

            if state == TaskState.SUCCESS.value:
                print("✓ 任务完成!", file=sys.stderr)
                return result
            elif state == TaskState.FAIL.value:
                fail_msg = data.get("failMsg", "未知错误")
                raise Exception(f"任务失败: {fail_msg}")

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
        result_json_str = data.get("resultJson", "{}")

        try:
            result_json = json.loads(result_json_str)
            return result_json.get("resultUrls", [])
        except json.JSONDecodeError:
            return []


def download_images(image_urls: List[str], output_dir: str, output_format: str = "png") -> List[str]:
    """
    下载图像到本地

    Args:
        image_urls: 图像URL列表
        output_dir: 输出目录
        output_format: 输出格式(png/jpg)

    Returns:
        下载的文件路径列表
    """
    # 确定下载目录
    download_path = Path(output_dir).expanduser()
    download_path.mkdir(parents=True, exist_ok=True)

    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 下载所有图像
    downloaded_files = []
    for i, url in enumerate(image_urls, 1):
        try:
            # 生成文件名
            if len(image_urls) == 1:
                filename = f"nano_banana_{timestamp}.{output_format}"
            else:
                filename = f"nano_banana_{timestamp}_{i}.{output_format}"

            filepath = download_path / filename

            # 下载图像
            print(f"下载图像 {i}/{len(image_urls)}...", file=sys.stderr)
            urllib.request.urlretrieve(url, filepath)
            downloaded_files.append(str(filepath))
            print(f"✓ 图像已下载: {filepath}", file=sys.stderr)

        except Exception as e:
            print(f"✗ 下载失败 (图像 {i}): {e}", file=sys.stderr)

    return downloaded_files


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='kie平台 Nano Banana Pro API - AI图像生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 文生图 - 根据描述生成图像
  python kie_nano_banana_api.py --prompt "一只可爱的猫咪"

  # 生成并下载图像
  python kie_nano_banana_api.py --prompt "一只可爱的猫咪" --download

  # 图生图 - 使用参考图像
  python kie_nano_banana_api.py --prompt "转为油画风格" --image-input "https://example.com/photo.jpg"

  # 多图融合 - 融合多张图像
  python kie_nano_banana_api.py --prompt "融合这些图像的风格" --image-input "url1" "url2" "url3"

  # 指定比例、清晰度并下载
  python kie_nano_banana_api.py --prompt "未来城市" --aspect-ratio 16:9 --resolution 4K --download

  # 查询已存在的任务
  python kie_nano_banana_api.py --query --task-id "your_task_id"

  # 查询并下载
  python kie_nano_banana_api.py --query --task-id "your_task_id" --download

环境变量:
  KIE_API_KEY    kie平台的API密钥(必需)
        """
    )

    # 操作模式
    parser.add_argument('--query', action='store_true',
                       help='查询已存在的任务(需配合 --task-id)')

    # 基本参数
    parser.add_argument('--prompt', type=str,
                       help='图像描述提示词(最多20000字符)')
    parser.add_argument('--api-key', type=str,
                       help='API密钥(也可通过环境变量 KIE_API_KEY 设置)')
    parser.add_argument('--task-id', type=str,
                       help='要查询的任务ID(仅在 --query 模式下使用)')

    # 图像参数
    parser.add_argument('--aspect-ratio', type=str, default='1:1',
                       choices=['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9', 'auto'],
                       help='图像比例(默认: 1:1)')
    parser.add_argument('--resolution', type=str, default='2K',
                       choices=['1K', '2K', '4K'],
                       help='图像清晰度(默认: 2K)')
    parser.add_argument('--output-format', type=str, default='png',
                       choices=['png', 'jpg'],
                       help='输出格式(默认: png)')
    parser.add_argument('--image-input', type=str, nargs='+',
                       help='参考图像URL(支持多个,最多8张)')

    # 下载参数
    parser.add_argument('--download', action='store_true',
                       help='自动下载生成的图像到本地')
    parser.add_argument('--output-dir', type=str, default='~/Downloads',
                       help='下载保存目录(默认: ~/Downloads)')

    # 任务管理参数
    parser.add_argument('--no-wait', action='store_true',
                       help='不等待任务完成,创建后立即返回')
    parser.add_argument('--max-wait', type=int, default=300,
                       help='最大等待时间(秒),默认300秒')
    parser.add_argument('--poll-interval', type=int, default=5,
                       help='轮询间隔(秒),默认5秒')

    # 输出参数
    parser.add_argument('--json', action='store_true',
                       help='以JSON格式输出结果')

    return parser.parse_args()


def print_output(image_urls: List[str], prompt: str, output_json: bool = False, downloaded_files: Optional[List[str]] = None):
    """
    输出结果

    Args:
        image_urls: 图像URL列表
        prompt: 原始提示词
        output_json: 是否以JSON格式输出
        downloaded_files: 下载的文件路径列表
    """
    if output_json:
        # JSON格式输出
        output_data = {
            "prompt": prompt,
            "imageUrls": image_urls,
            "imageCount": len(image_urls)
        }
        if downloaded_files:
            output_data["downloadedFiles"] = downloaded_files
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出(美化版)
        print()
        print("=" * 60)
        print("图像生成完成")
        print("=" * 60)
        print(f"提示词: {prompt}")
        print(f"生成数量: {len(image_urls)} 张")
        print()
        for i, url in enumerate(image_urls, 1):
            print(f"图像 #{i}: {url}")

        if downloaded_files:
            print()
            print("下载文件:")
            for i, filepath in enumerate(downloaded_files, 1):
                print(f"文件 #{i}: {filepath}")

        print("=" * 60)


def main():
    """主函数"""
    args = parse_args()

    # 获取API密钥
    api_key = args.api_key or os.getenv("KIE_API_KEY")
    if not api_key:
        print("错误: 未设置API密钥", file=sys.stderr)
        print("请通过 --api-key 参数或环境变量 KIE_API_KEY 设置", file=sys.stderr)
        print("获取API密钥: https://kie.ai/api-key", file=sys.stderr)
        sys.exit(1)

    # 初始化客户端
    client = KieNanoBananaAPI(api_key)

    try:
        # 查询模式
        if args.query:
            if not args.task_id:
                print("错误: 查询模式需要提供 --task-id 参数", file=sys.stderr)
                sys.exit(1)

            print(f"查询任务: {args.task_id}", file=sys.stderr)
            result = client.query_task(args.task_id)
            data = result.get("data", {})
            state = data.get("state")

            print(f"任务状态: {state}", file=sys.stderr)

            if state == TaskState.SUCCESS.value:
                image_urls = client.extract_image_urls(result)
                # 从任务参数中提取原始 prompt
                param_str = data.get("param", "{}")
                try:
                    param = json.loads(param_str)
                    prompt = param.get("input", {}).get("prompt", "")
                    output_format = param.get("input", {}).get("output_format", "png")
                except json.JSONDecodeError:
                    prompt = ""
                    output_format = "png"

                print(f"\n生成了 {len(image_urls)} 张图像\n", file=sys.stderr)

                # 下载图像
                downloaded_files = None
                if args.download and image_urls:
                    print("\n下载图像...", file=sys.stderr)
                    downloaded_files = download_images(image_urls, args.output_dir, output_format)

                print_output(image_urls, prompt, args.json, downloaded_files)
            else:
                print(f"任务尚未完成或失败: {state}", file=sys.stderr)
                if data.get("failMsg"):
                    print(f"错误信息: {data.get('failMsg')}", file=sys.stderr)
                sys.exit(1)

        # 生成模式
        else:
            if not args.prompt:
                print("错误: 生成模式需要提供 --prompt 参数", file=sys.stderr)
                sys.exit(1)

            print("创建图像生成任务...", file=sys.stderr)

            # 构建参数
            aspect_ratio = AspectRatio(args.aspect_ratio)
            resolution = Resolution(args.resolution)
            output_format = OutputFormat(args.output_format)

            result = client.create_task(
                prompt=args.prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                output_format=output_format,
                image_input=args.image_input
            )

            task_id = result.get("data", {}).get("taskId")
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

                # 下载图像
                downloaded_files = None
                if args.download and image_urls:
                    print("\n下载图像...", file=sys.stderr)
                    downloaded_files = download_images(image_urls, args.output_dir, args.output_format)

                print_output(image_urls, args.prompt, args.json, downloaded_files)
            else:
                print(f"任务ID: {task_id}", file=sys.stderr)
                print(f"可使用以下命令查询: python {sys.argv[0]} --query --task-id {task_id}", file=sys.stderr)

    except Exception as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
