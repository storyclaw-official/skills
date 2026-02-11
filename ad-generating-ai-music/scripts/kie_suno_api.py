#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kie平台 Suno API 封装脚本
支持简化模式和自定义模式生成音乐
使用方法：python kie_suno_api.py --prompt "音乐描述" [其他参数]
"""

import os
import sys
import time
import json
import argparse
import requests
from typing import Optional, Dict, Any, List
from enum import Enum


class SunoModel(str, Enum):
    """Suno 模型版本枚举"""
    V4 = "V4"
    V4_5 = "V4_5"
    V4_5PLUS = "V4_5PLUS"
    V4_5ALL = "V4_5ALL"
    V5 = "V5"


class VocalGender(str, Enum):
    """人声性别枚举"""
    MALE = "m"
    FEMALE = "f"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "PENDING"
    TEXT_SUCCESS = "TEXT_SUCCESS"
    FIRST_SUCCESS = "FIRST_SUCCESS"
    SUCCESS = "SUCCESS"
    CREATE_TASK_FAILED = "CREATE_TASK_FAILED"
    GENERATE_AUDIO_FAILED = "GENERATE_AUDIO_FAILED"
    CALLBACK_EXCEPTION = "CALLBACK_EXCEPTION"
    SENSITIVE_WORD_ERROR = "SENSITIVE_WORD_ERROR"


class KieSunoAPI:
    """kie平台 Suno API 封装类"""

    BASE_URL = "https://api.kie.ai"
    GENERATE_ENDPOINT = "/api/v1/generate"
    QUERY_ENDPOINT = "/api/v1/generate/record-info"

    def __init__(self, api_key: str):
        """
        初始化 KieSunoAPI

        Args:
            api_key: kie平台的API密钥
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def simple_generate(
        self,
        prompt: str,
        callback_url: str = "https://example.com/callback",
        model: SunoModel = SunoModel.V5,
        instrumental: bool = False,
        negative_tags: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        简化模式生成音乐 (只需要 prompt)

        Args:
            prompt: 音乐提示词，最多500字符
            callback_url: 回调URL
            model: 模型版本，默认V5
            instrumental: 是否生成纯音乐（无歌词）
            negative_tags: 排除的音乐风格，如 "重金属, 快节奏鼓点"

        Returns:
            包含 taskId 的响应字典
        """
        if len(prompt) > 500:
            raise ValueError("简化模式下 prompt 长度不能超过 500 字符")

        payload = {
            "prompt": prompt,
            "customMode": False,
            "instrumental": instrumental,
            "model": model.value,
            "callBackUrl": callback_url
        }

        if negative_tags:
            payload["negativeTags"] = negative_tags

        return self._make_request(payload)

    def custom_generate(
        self,
        prompt: str,
        style: str,
        title: str,
        callback_url: str = "https://example.com/callback",
        model: SunoModel = SunoModel.V5,
        instrumental: bool = False,
        vocal_gender: Optional[VocalGender] = None,
        negative_tags: Optional[str] = None,
        style_weight: Optional[float] = None,
        weirdness_constraint: Optional[float] = None,
        audio_weight: Optional[float] = None,
        persona_id: Optional[str] = None,
        persona_model: str = "style_persona"
    ) -> Dict[str, Any]:
        """
        自定义模式生成音乐 (详细控制)

        Args:
            prompt: 音乐提示词/歌词 (当 instrumental=False 时作为歌词使用)
                    V5模型最多5000字符
            style: 音乐风格，V5模型最多1000字符
                   例如: "Classical", "Jazz", "Rock", "Pop"
            title: 音乐标题，最多80字符
            callback_url: 回调URL
            model: 模型版本，默认V5
            instrumental: 是否生成纯音乐
                         True: 不需要 prompt，只需 style 和 title
                         False: 需要 prompt 作为歌词
            vocal_gender: 人声性别偏好 (仅在 customMode=True 时生效)
            negative_tags: 排除的音乐风格
            style_weight: 风格遵循强度 (0-1)
            weirdness_constraint: 创意/离散程度 (0-1)
            audio_weight: 音频要素权重 (0-1)
            persona_id: 人格ID
            persona_model: Persona模型类型，默认 "style_persona"

        Returns:
            包含 taskId 的响应字典
        """
        # 验证字符限制
        if model == SunoModel.V4:
            if len(prompt) > 3000:
                raise ValueError("V4模型下 prompt 长度不能超过 3000 字符")
            if len(style) > 200:
                raise ValueError("V4模型下 style 长度不能超过 200 字符")
        else:  # V4_5, V4_5PLUS, V4_5ALL, V5
            if len(prompt) > 5000:
                raise ValueError(f"{model.value}模型下 prompt 长度不能超过 5000 字符")
            if len(style) > 1000:
                raise ValueError(f"{model.value}模型下 style 长度不能超过 1000 字符")

        if len(title) > 80:
            raise ValueError("title 长度不能超过 80 字符")

        # 构建请求体
        payload = {
            "customMode": True,
            "instrumental": instrumental,
            "model": model.value,
            "style": style,
            "title": title,
            "callBackUrl": callback_url
        }

        # 纯音乐模式不需要 prompt，有歌词模式需要 prompt 作为歌词
        if not instrumental:
            payload["prompt"] = prompt

        # 添加可选参数
        if vocal_gender:
            payload["vocalGender"] = vocal_gender.value

        if negative_tags:
            payload["negativeTags"] = negative_tags

        if style_weight is not None:
            if not 0 <= style_weight <= 1:
                raise ValueError("style_weight 必须在 0-1 之间")
            payload["styleWeight"] = round(style_weight, 2)

        if weirdness_constraint is not None:
            if not 0 <= weirdness_constraint <= 1:
                raise ValueError("weirdness_constraint 必须在 0-1 之间")
            payload["weirdnessConstraint"] = round(weirdness_constraint, 2)

        if audio_weight is not None:
            if not 0 <= audio_weight <= 1:
                raise ValueError("audio_weight 必须在 0-1 之间")
            payload["audioWeight"] = round(audio_weight, 2)

        if persona_id:
            payload["personaId"] = persona_id
            payload["personaModel"] = persona_model

        return self._make_request(payload)

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送生成音乐请求

        Args:
            payload: 请求体

        Returns:
            响应字典
        """
        url = f"{self.BASE_URL}{self.GENERATE_ENDPOINT}"

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
        查询任务详情

        Args:
            task_id: 任务ID

        Returns:
            任务详情字典
        """
        url = f"{self.BASE_URL}{self.QUERY_ENDPOINT}"
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
            max_wait_time: 最大等待时间（秒），默认300秒
            poll_interval: 轮询间隔（秒），默认5秒

        Returns:
            完成后的任务详情
        """
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            result = self.query_task(task_id)
            data = result.get("data", {})
            status = data.get("status")

            print(f"任务状态: {status}")

            if status == TaskStatus.SUCCESS.value:
                print("✓ 任务完成!")
                return result
            elif status in [
                TaskStatus.CREATE_TASK_FAILED.value,
                TaskStatus.GENERATE_AUDIO_FAILED.value,
                TaskStatus.CALLBACK_EXCEPTION.value,
                TaskStatus.SENSITIVE_WORD_ERROR.value
            ]:
                error_msg = data.get("errorMessage", "未知错误")
                raise Exception(f"任务失败: {status} - {error_msg}")

            time.sleep(poll_interval)

        raise Exception(f"等待超时 ({max_wait_time}秒)")

    def extract_audio_urls(self, task_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        从任务结果中提取音频URL

        Args:
            task_result: query_task 或 wait_for_completion 返回的结果

        Returns:
            音频信息列表，每项包含 id, audioUrl, title, duration 等
        """
        data = task_result.get("data", {})
        response = data.get("response", {})
        suno_data = response.get("sunoData", [])

        audio_list = []
        for item in suno_data:
            audio_info = {
                "id": item.get("id"),
                "audioUrl": item.get("audioUrl"),
                "streamAudioUrl": item.get("streamAudioUrl"),
                "imageUrl": item.get("imageUrl"),
                "title": item.get("title"),
                "tags": item.get("tags"),
                "duration": item.get("duration"),
                "prompt": item.get("prompt")
            }
            audio_list.append(audio_info)

        return audio_list


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='kie平台 Suno API - AI音乐生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 简化模式 - 快速生成音乐
  python kie_suno_api.py --prompt "一首欢快的流行歌曲"

  # 生成纯音乐（无歌词）
  python kie_suno_api.py --custom --style "古典钢琴" --title "宁静时光" --instrumental

  # 自定义歌词 + 女声
  python kie_suno_api.py --custom --prompt "[Verse]歌词内容" --style "流行" --title "我的歌" --vocal-gender female

  # 查询已存在的任务
  python kie_suno_api.py --query --task-id "your_task_id"

环境变量:
  KIE_API_KEY    kie平台的API密钥（必需）
        """
    )

    # 操作模式
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('--query', action='store_true',
                           help='查询已存在的任务（需配合 --task-id）')
    mode_group.add_argument('--custom', action='store_true',
                           help='使用自定义模式（详细控制）')

    # 基本参数
    parser.add_argument('--prompt', type=str,
                       help='音乐提示词/歌词内容')
    parser.add_argument('--api-key', type=str,
                       help='API密钥（也可通过环境变量 KIE_API_KEY 设置）')
    parser.add_argument('--task-id', type=str,
                       help='要查询的任务ID（仅在 --query 模式下使用）')

    # 自定义模式参数
    parser.add_argument('--style', type=str,
                       help='音乐风格（自定义模式必需），如："古典钢琴, 平静舒缓"')
    parser.add_argument('--title', type=str,
                       help='音乐标题（自定义模式必需）')

    # 通用可选参数
    parser.add_argument('--instrumental', action='store_true',
                       help='生成纯音乐（无歌词）')
    parser.add_argument('--model', type=str, default='V5',
                       choices=['V4', 'V4_5', 'V4_5PLUS', 'V4_5ALL', 'V5'],
                       help='模型版本（默认: V5）')
    parser.add_argument('--vocal-gender', type=str, choices=['male', 'female'],
                       help='人声性别偏好（仅自定义模式）')
    parser.add_argument('--negative-tags', type=str,
                       help='排除的音乐风格，如："重金属, 说唱"')

    # 高级参数
    parser.add_argument('--style-weight', type=float,
                       help='风格遵循强度 (0-1)')
    parser.add_argument('--weirdness-constraint', type=float,
                       help='创意/离散程度 (0-1)')
    parser.add_argument('--audio-weight', type=float,
                       help='音频要素权重 (0-1)')
    parser.add_argument('--persona-id', type=str,
                       help='人格ID')

    # 轮询参数
    parser.add_argument('--no-wait', action='store_true',
                       help='不等待任务完成，创建后立即返回')
    parser.add_argument('--max-wait', type=int, default=300,
                       help='最大等待时间（秒），默认300秒')
    parser.add_argument('--poll-interval', type=int, default=10,
                       help='轮询间隔（秒），默认10秒')

    # 输出参数
    parser.add_argument('--callback-url', type=str, default='https://example.com/callback',
                       help='回调URL（默认: https://example.com/callback）')
    parser.add_argument('--json', action='store_true',
                       help='以JSON格式输出结果')

    return parser.parse_args()


def print_output(audio_list: List[Dict[str, Any]], output_json: bool = False):
    """
    输出结果（只输出指定的4个字段）

    Args:
        audio_list: 音频信息列表
        output_json: 是否以JSON格式输出
    """
    # 只保留需要的4个字段
    output_data = []
    for audio in audio_list:
        output_data.append({
            "title": audio.get("title", ""),
            "prompt": audio.get("prompt", ""),
            "audioUrl": audio.get("audioUrl", ""),
            "tags": audio.get("tags", "")
        })

    if output_json:
        # JSON格式输出
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出（美化版）
        for i, item in enumerate(output_data, 1):
            print(f"\n{'=' * 60}")
            print(f"音乐 #{i}")
            print(f"{'=' * 60}")
            print(f"音乐标题: {item['title']}")
            print(f"歌词: ")
            print(f"{item['prompt']}")
            print()  # 空行
            print(f"下载链接: {item['audioUrl']}")
            print(f"音乐风格: {item['tags']}")


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
    client = KieSunoAPI(api_key)

    try:
        # 查询模式
        if args.query:
            if not args.task_id:
                print("错误: 查询模式需要提供 --task-id 参数", file=sys.stderr)
                sys.exit(1)

            print(f"查询任务: {args.task_id}", file=sys.stderr)
            result = client.query_task(args.task_id)
            data = result.get("data", {})
            status = data.get("status")

            print(f"任务状态: {status}", file=sys.stderr)

            if status == TaskStatus.SUCCESS.value:
                audio_list = client.extract_audio_urls(result)
                print(f"\n生成了 {len(audio_list)} 首音乐\n", file=sys.stderr)
                print_output(audio_list, args.json)
            else:
                print(f"任务尚未完成或失败: {status}", file=sys.stderr)
                if data.get("errorMessage"):
                    print(f"错误信息: {data.get('errorMessage')}", file=sys.stderr)
                sys.exit(1)

        # 自定义模式
        elif args.custom:
            if not args.style or not args.title:
                print("错误: 自定义模式需要提供 --style 和 --title 参数", file=sys.stderr)
                sys.exit(1)

            # 如果是纯音乐，prompt 可以为空
            prompt = args.prompt or ""
            if not args.instrumental and not prompt:
                print("错误: 非纯音乐模式需要提供 --prompt 参数", file=sys.stderr)
                sys.exit(1)

            print("使用自定义模式生成音乐...", file=sys.stderr)

            # 构建参数
            kwargs = {
                "prompt": prompt,
                "style": args.style,
                "title": args.title,
                "callback_url": args.callback_url,
                "model": SunoModel[args.model],
                "instrumental": args.instrumental
            }

            if args.vocal_gender:
                kwargs["vocal_gender"] = VocalGender.MALE if args.vocal_gender == 'male' else VocalGender.FEMALE
            if args.negative_tags:
                kwargs["negative_tags"] = args.negative_tags
            if args.style_weight is not None:
                kwargs["style_weight"] = args.style_weight
            if args.weirdness_constraint is not None:
                kwargs["weirdness_constraint"] = args.weirdness_constraint
            if args.audio_weight is not None:
                kwargs["audio_weight"] = args.audio_weight
            if args.persona_id:
                kwargs["persona_id"] = args.persona_id

            result = client.custom_generate(**kwargs)
            task_id = result.get("data", {}).get("taskId")
            print(f"✓ 任务创建成功! TaskID: {task_id}", file=sys.stderr)

            # 等待完成
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
                print(f"任务ID: {task_id}", file=sys.stderr)
                print(f"可使用以下命令查询: python {sys.argv[0]} --query --task-id {task_id}", file=sys.stderr)

        # 简化模式（默认）
        else:
            if not args.prompt:
                print("错误: 简化模式需要提供 --prompt 参数", file=sys.stderr)
                sys.exit(1)

            print("使用简化模式生成音乐...", file=sys.stderr)

            result = client.simple_generate(
                prompt=args.prompt,
                callback_url=args.callback_url,
                model=SunoModel[args.model],
                instrumental=args.instrumental,
                negative_tags=args.negative_tags
            )

            task_id = result.get("data", {}).get("taskId")
            print(f"✓ 任务创建成功! TaskID: {task_id}", file=sys.stderr)

            # 等待完成
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
                print(f"任务ID: {task_id}", file=sys.stderr)
                print(f"可使用以下命令查询: python {sys.argv[0]} --query --task-id {task_id}", file=sys.stderr)

    except Exception as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
