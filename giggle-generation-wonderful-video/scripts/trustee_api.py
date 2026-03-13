#!/usr/bin/env python3
"""
Wonderful Video API 调用脚本
创建项目与提交任务合并为一步，仅暴露 execute_workflow 和 get_styles 供 AI 调用
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

PROJECT_TYPE = "wonderful-video"  # 固定项目类型


def _check_requests():
    """检查并导入 requests 库"""
    try:
        import requests
        return requests
    except ImportError:
        print("错误: 需要安装 requests 库", file=sys.stderr)
        print("请运行: pip install requests", file=sys.stderr)
        sys.exit(1)


class WonderfulVideoAPI:
    """Wonderful Video API 客户端，创建项目与提交任务合并为一步"""

    def __init__(self):
        requests = _check_requests()
        self._load_env()
        self.api_key = os.getenv("GIGGLE_API_KEY")
        if not self.api_key:
            openclaw_env = Path.home() / ".openclaw" / ".env"
            raise ValueError(
                "未找到 GIGGLE_API_KEY，请任选一种方式配置：\n"
                f"1. 在 {openclaw_env} 中添加 GIGGLE_API_KEY=your_api_key（优先读取）\n"
                "2. 设置系统环境变量：export GIGGLE_API_KEY=your_api_key\n"
                "API Key 可在 [Giggle.pro](https://giggle.pro/) 账号设置中获取。"
            )
        self.base_url = "https://giggle.pro"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'x-auth': self.api_key
        })

    def _load_env(self):
        """加载环境变量，优先级：1) ~/.openclaw/.env  2) 系统环境变量 GIGGLE_API_KEY"""
        try:
            from dotenv import load_dotenv
            openclaw_env = Path.home() / ".openclaw" / ".env"
            if openclaw_env.exists():
                load_dotenv(openclaw_env, override=True)
        except ImportError:
            pass

    def _create_and_submit(self, project_name: str, diy_story: str, aspect: str,
                           video_duration: str, language: str,
                           style_id: Optional[int] = None,
                           character_info: Optional[List[Dict[str, str]]] = None,
                           subtitle_enabled: Optional[bool] = None) -> Dict[str, Any]:
        """
        创建项目并提交任务（合并为一步，仅供内部调用）
        character_info: [{"name": "角色名", "url": "图片URL"}, ...]
        返回 project_id 或错误信息
        """
        url_create = f"{self.base_url}/api/v1/project/create"
        data_create = {
            "name": project_name,
            "type": PROJECT_TYPE,
            "aspect": aspect,
            "mode": "trustee"
        }

        try:
            response = self.session.post(url_create, json=data_create)
            response.raise_for_status()
            create_result = response.json()

            code = create_result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0

            if code != 0 and code != 200:
                return {
                    "code": code,
                    "msg": f"创建项目失败: {create_result.get('msg', '未知错误')}",
                    "data": None
                }

            project_id = create_result.get("data", {}).get("project_id")
            if not project_id:
                return {
                    "code": -1,
                    "msg": "创建项目失败: 未获取到项目ID",
                    "data": None
                }

            url_submit = f"{self.base_url}/api/v1/trustee_mode/submit-v2"
            data_submit = {
                "project_id": project_id,
                "diy_story": diy_story,
                "aspect": aspect,
                "video_duration": video_duration,
                "language": language
            }
            if style_id is not None:
                data_submit["style_id"] = style_id
            if character_info is not None and len(character_info) > 0:
                data_submit["character_info"] = character_info
            if subtitle_enabled is not None:
                data_submit["subtitle_enabled"] = subtitle_enabled

            response = self.session.post(url_submit, json=data_submit)
            response.raise_for_status()
            submit_result = response.json()

            code = submit_result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0

            if code != 0 and code != 200:
                return {
                    "code": code,
                    "msg": f"提交任务失败: {submit_result.get('msg', '未知错误')}",
                    "data": None
                }

            return {"code": 200, "msg": "success", "data": {"project_id": project_id}}
        except Exception as e:
            return {"code": -1, "msg": str(e), "data": None}

    def query_progress(self, project_id: str) -> Dict[str, Any]:
        """查询任务进度"""
        url = f"{self.base_url}/api/v1/trustee_mode/query-v2"
        params = {"project_id": project_id}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                print(f"查询失败: {result.get('msg', '未知错误')}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"请求失败: {e}", file=sys.stderr)
            return {"code": -1, "msg": str(e)}

    def pay(self, project_id: str, video_first_model: str,
            video_second_model: str, image_first_model: str) -> Dict[str, Any]:
        """支付"""
        url = f"{self.base_url}/api/v1/trustee_mode/pay"
        data = {
            "project_id": project_id,
            "video_first_model": video_first_model,
            "video_second_model": video_second_model,
            "image_first_model": image_first_model
        }
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                print(f"支付失败: {result.get('msg', '未知错误')}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"请求失败: {e}", file=sys.stderr)
            return {"code": -1, "msg": str(e)}

    def get_styles(self, page: int = 1, page_size: int = 999, language: str = "zh") -> Dict[str, Any]:
        """获取风格列表"""
        url = f"{self.base_url}/api/v1/ai_style/list"
        params = {"page": page, "page_size": page_size, "language": language}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                print(f"获取风格列表失败: {result.get('msg', '未知错误')}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"请求失败: {e}", file=sys.stderr)
            return {"code": -1, "msg": str(e)}

    def execute_workflow(self, diy_story: str, aspect: str, project_name: str,
                        video_duration: str = "auto", style_id: Optional[int] = None,
                        character_info: Optional[List[Dict[str, str]]] = None,
                        subtitle_enabled: Optional[bool] = None) -> Dict[str, Any]:
        """
        执行完整工作流（一步完成：创建项目+提交任务 -> 查询进度 -> 支付 -> 等待完成）
        AI 只需调用此函数一次。
        character_info: 角色图片，[{"name": "角色名", "url": "图片URL"}, ...]
        """
        start_time = datetime.now()
        timeout = timedelta(hours=1)
        query_interval = 3
        language = "zh"
        video_first_model = "seedance15-pro"
        video_second_model = "seedance15-pro"
        image_first_model = "seedream45"
        paid = False
        max_retries = 5
        retry_delay = 5

        # 步骤1：创建项目并提交任务（合并为一步）
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 步骤1: 创建项目并提交任务...", file=sys.stderr)
        create_submit_result = self._create_and_submit(
            project_name=project_name,
            diy_story=diy_story,
            aspect=aspect,
            video_duration=video_duration,
            language=language,
            style_id=style_id,
            character_info=character_info,
            subtitle_enabled=subtitle_enabled
        )

        code = create_submit_result.get("code")
        if code != 200:
            return {
                "code": code if code else -1,
                "msg": create_submit_result.get("msg", "创建或提交失败"),
                "data": None
            }

        project_id = create_submit_result.get("data", {}).get("project_id")
        if not project_id:
            return {"code": -1, "msg": "未获取到项目ID", "data": None}

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 项目创建并任务提交成功，项目ID: {project_id}", file=sys.stderr)

        # 步骤2：循环查询进度
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 步骤2: 开始查询进度...", file=sys.stderr)

        while True:
            if datetime.now() - start_time > timeout:
                return {"code": -1, "msg": "工作流超时（超过1小时）", "data": None}

            query_result = None
            query_success = False
            retry_count = 0

            while retry_count < max_retries:
                try:
                    query_result = self.query_progress(project_id)
                    code = query_result.get("code")
                    if isinstance(code, str):
                        code = int(code) if code.isdigit() else 0

                    if code == 0 or code == 200:
                        query_success = True
                        break

                    error_msg = str(query_result.get("msg", ""))
                    is_network_error = (
                        "Connection" in error_msg or "Remote" in error_msg or
                        "timeout" in error_msg.lower() or "aborted" in error_msg.lower() or
                        "disconnected" in error_msg.lower()
                    )

                    if not is_network_error:
                        return {
                            "code": code,
                            "msg": f"查询进度失败: {query_result.get('msg')}",
                            "data": None
                        }

                    retry_count += 1
                    wait = retry_delay if retry_count < max_retries else query_interval
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 网络错误，{wait}秒后重试 ({retry_count}/{max_retries})", file=sys.stderr)
                    time.sleep(wait)
                except Exception as e:
                    error_str = str(e)
                    is_network_error = (
                        "Connection" in error_str or "Remote" in error_str or
                        "timeout" in error_str.lower() or "aborted" in error_str.lower() or
                        "disconnected" in error_str.lower()
                    )
                    if is_network_error:
                        retry_count += 1
                        wait = retry_delay if retry_count < max_retries else query_interval
                        time.sleep(wait)
                    else:
                        return {"code": -1, "msg": f"查询失败: {error_str}", "data": None}

            if not query_success:
                continue

            data = query_result.get("data", {})
            status = data.get("status", "unknown")
            current_step = data.get("current_step", "")
            pay_status = data.get("pay_status", "")
            err_msg = data.get("err_msg", "")

            if status == "failed" or err_msg:
                return {"code": -1, "msg": f"任务失败: {err_msg or '未知错误'}", "data": None}

            for step in data.get("steps", []):
                for sub_step in step.get("sub_steps", []):
                    if sub_step.get("status") == "failed" or sub_step.get("error"):
                        return {
                            "code": -1,
                            "msg": f"子步骤失败: {sub_step.get('step', '未知')} - {sub_step.get('error', '')}",
                            "data": None
                        }

            if not paid and (pay_status == "pending" or (current_step and "pay" in current_step.lower())):
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检测到待支付，执行支付...", file=sys.stderr)
                pay_result = self.pay(
                    project_id=project_id,
                    video_first_model=video_first_model,
                    video_second_model=video_second_model,
                    image_first_model=image_first_model
                )
                code = pay_result.get("code")
                if isinstance(code, str):
                    code = int(code) if code.isdigit() else 0
                if code != 0 and code != 200:
                    return {"code": code, "msg": f"支付失败: {pay_result.get('msg')}", "data": None}
                paid = True
                continue

            if status == "completed":
                video_asset = data.get("video_asset", {})
                download_url = video_asset.get("download_url") if video_asset else None
                if video_asset and download_url:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务完成！下载链接: {download_url}", file=sys.stderr)
                    return {
                        "code": 200,
                        "msg": "success",
                        "uuid": query_result.get("uuid", ""),
                        "data": {
                            "project_id": project_id,
                            "download_url": download_url,
                            "video_asset": video_asset,
                            "status": status
                        }
                    }

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 状态: {status}, 步骤: {current_step}", file=sys.stderr)
            time.sleep(query_interval)


def _parse_bool(val):
    """解析布尔参数"""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    return str(val).lower() in ('true', '1', 'yes')


def print_response(result: Dict[str, Any], pretty: bool = True):
    """打印响应结果"""
    if pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Wonderful Video API 工作流工具")
    parser.add_argument('--pretty', action='store_true', help='美化JSON输出')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    workflow_parser = subparsers.add_parser('workflow', help='执行完整工作流')
    workflow_parser.add_argument('--story', required=True, dest='diy_story', help='故事创意')
    workflow_parser.add_argument('--aspect', required=True, choices=['16:9', '9:16'], help='宽高比')
    workflow_parser.add_argument('--project-name', required=True, dest='project_name', help='项目名称')
    workflow_parser.add_argument('--duration', default='auto', dest='video_duration',
                                choices=['auto', '30', '60', '120', '180', '240', '300'])
    workflow_parser.add_argument('--style-id', type=int, help='风格ID')
    workflow_parser.add_argument('--character-info', dest='character_info',
                                help='角色图片 JSON，格式: [{"name":"角色名","url":"图片URL"}]')
    workflow_parser.add_argument('--subtitle-enabled', dest='subtitle_enabled', nargs='?',
                                type=lambda x: _parse_bool(x) if x else True, const=True,
                                default=None, metavar='true|false',
                                help='是否启用字幕')

    styles_parser = subparsers.add_parser('styles', help='获取风格列表')
    styles_parser.add_argument('--page', type=int, default=1)
    styles_parser.add_argument('--page-size', type=int, default=999, dest='page_size')
    styles_parser.add_argument('--language', default='zh', choices=['zh', 'en'])

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    api = WonderfulVideoAPI()

    if args.command == 'workflow':
        character_info = None
        if getattr(args, 'character_info', None):
            try:
                character_info = json.loads(args.character_info)
            except json.JSONDecodeError:
                print("错误: character-info 必须是有效的 JSON 数组", file=sys.stderr)
                sys.exit(1)
        result = api.execute_workflow(
            diy_story=args.diy_story,
            aspect=args.aspect,
            project_name=args.project_name,
            video_duration=args.video_duration,
            style_id=getattr(args, 'style_id', None),
            character_info=character_info,
            subtitle_enabled=getattr(args, 'subtitle_enabled', None)
        )
        print_response(result, args.pretty)
    elif args.command == 'styles':
        result = api.get_styles(
            page=args.page,
            page_size=args.page_size,
            language=args.language
        )
        print_response(result, args.pretty)


if __name__ == '__main__':
    main()
