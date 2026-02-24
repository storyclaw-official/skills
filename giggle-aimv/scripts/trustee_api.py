#!/usr/bin/env python3
"""
MV 托管模式 API 调用脚本
支持三种音乐生成模式：提示词(prompt)、自定义(custom)、上传(upload)
"""

import argparse
import json
import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")  # 抑制 LibreSSL/urllib3 等运行时警告
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

# 从 .env 文件或环境变量读取 API Key
def _load_api_key() -> str:
    key = os.environ.get("GIGGLE_API_KEY", "")
    if not key:
        # 向上查找 .env 文件
        cur = os.path.dirname(os.path.abspath(__file__))
        for _ in range(4):
            env_path = os.path.join(cur, ".env")
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GIGGLE_API_KEY="):
                            key = line.split("=", 1)[1].strip()
                            break
                if key:
                    break
            cur = os.path.dirname(cur)
    return key

_API_KEY = _load_api_key()


def _check_requests():
    """检查并导入 requests 库"""
    try:
        import requests
        return requests
    except ImportError:
        print("错误: 需要安装 requests 库", file=sys.stderr)
        print("请运行: pip install requests", file=sys.stderr)
        sys.exit(1)


class MVTrusteeAPI:
    """MV 托管模式 API 客户端"""

    def __init__(self):
        requests = _check_requests()
        self.base_url = "https://giggle.pro"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _get_log_dir(self) -> Path:
        """获取日志目录路径"""
        log_dir = Path.home() / '.openclaw' / 'skills' / 'giggle-aimv' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    def _setup_log(self, project_id: str) -> Path:
        """创建日志文件，返回路径"""
        log_dir = self._get_log_dir()
        log_file = log_dir / f"{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file.touch()
        return log_file

    def _check_sent(self, project_id: str) -> bool:
        """检查是否已推送过结果（.sent 防重复）"""
        return (self._get_log_dir() / f"{project_id}.sent").exists()

    def _mark_sent(self, project_id: str) -> None:
        """标记已推送结果"""
        (self._get_log_dir() / f"{project_id}.sent").touch()

    def _get_query_count(self, project_id: str) -> int:
        """获取单次 query 轮询次数"""
        f = self._get_log_dir() / f"{project_id}.count"
        try:
            return int(f.read_text().strip()) if f.exists() else 0
        except Exception:
            return 0

    def _increment_query_count(self, project_id: str) -> int:
        """递增并返回单次 query 轮询次数"""
        f = self._get_log_dir() / f"{project_id}.count"
        count = self._get_query_count(project_id) + 1
        f.write_text(str(count))
        return count

    def create_project(self, name: str, aspect: str) -> Dict[str, Any]:
        """创建 MV 项目"""
        url = f"{self.base_url}/api/v1/project/create"
        data = {
            "name": name,
            "type": "mv",
            "aspect": aspect,
            "mode": "trustee"
        }
        try:
            headers = {"x-auth": _API_KEY}
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                print(f"创建项目失败: {result.get('msg', '未知错误')}")
                return result
            return result
        except Exception as e:
            print(f"请求失败: {e}")
            return {"code": -1, "msg": str(e)}

    def submit_mv_task(
        self,
        project_id: str,
        music_generate_type: str,
        aspect: str,
        reference_image: str = "",
        reference_image_url: str = "",
        scene_description: str = "",
        subtitle_enabled: bool = False,
        # prompt 模式
        prompt: str = "",
        vocal_gender: str = "auto",
        instrumental: bool = False,
        # custom 模式
        lyrics: str = "",
        style: str = "",
        title: str = "",
        # upload 模式
        music_asset_id: str = "",
    ) -> Dict[str, Any]:
        """
        提交 MV 托管任务

        Args:
            project_id: 项目 ID
            music_generate_type: prompt / custom / upload
            aspect: 16:9 或 9:16
            reference_image: 参考图 asset_id（与 reference_image_url 二选一）
            reference_image_url: 参考图下载链接（与 reference_image 二选一）
            scene_description: 场景描述，默认空
            subtitle_enabled: 字幕开关，默认 False
            prompt, vocal_gender, instrumental: 提示词模式参数
            lyrics, style, title: 自定义模式参数
            music_asset_id: 上传模式参数
        """
        url = f"{self.base_url}/api/v1/trustee_mode/mv/submit"
        data = {
            "project_id": project_id,
            "music_generate_type": music_generate_type,
            "aspect": aspect,
            "scene_description": scene_description,
            "subtitle_enabled": subtitle_enabled,
        }
        if reference_image:
            data["reference_image"] = reference_image
        elif reference_image_url:
            data["reference_image_url"] = reference_image_url

        if music_generate_type == "prompt":
            data["prompt"] = prompt
            data["vocal_gender"] = vocal_gender
            data["instrumental"] = instrumental
        elif music_generate_type == "custom":
            data["lyrics"] = lyrics
            data["style"] = style
            data["title"] = title
        elif music_generate_type == "upload":
            data["music_asset_id"] = music_asset_id

        try:
            headers = {"x-auth": _API_KEY}
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                print(f"提交任务失败: {result.get('msg', '未知错误')}")
                return result
            return result
        except Exception as e:
            print(f"请求失败: {e}")
            return {"code": -1, "msg": str(e)}

    def query_progress(self, project_id: str) -> Dict[str, Any]:
        """查询 MV 托管进度"""
        url = f"{self.base_url}/api/v1/trustee_mode/mv/query"
        params = {"project_id": project_id}
        try:
            headers = {"x-auth": _API_KEY}
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            result = response.json()
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                print(f"查询失败: {result.get('msg', '未知错误')}")
                return result
            return result
        except Exception as e:
            print(f"请求失败: {e}")
            return {"code": -1, "msg": str(e)}

    def pay(self, project_id: str) -> Dict[str, Any]:
        """MV 托管支付（模型固定，仅传 project_id）"""
        url = f"{self.base_url}/api/v1/trustee_mode/mv/pay"
        data = {"project_id": project_id}
        try:
            headers = {"x-auth": _API_KEY}
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                print(f"支付失败: {result.get('msg', '未知错误')}")
                return result
            return result
        except Exception as e:
            print(f"请求失败: {e}")
            return {"code": -1, "msg": str(e)}

    def retry(self, project_id: str, current_step: str) -> Dict[str, Any]:
        """重试失败步骤，从指定 current_step 重新执行"""
        url = f"{self.base_url}/api/v1/trustee_mode/mv/retry"
        data = {"project_id": project_id, "current_step": current_step}
        try:
            headers = {"x-auth": _API_KEY}
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                print(f"重试失败: {result.get('msg', '未知错误')}")
                return result
            return result
        except Exception as e:
            print(f"请求失败: {e}")
            return {"code": -1, "msg": str(e)}

    def create_and_submit(
        self,
        music_generate_type: str,
        aspect: str,
        project_name: str,
        reference_image: str = "",
        reference_image_url: str = "",
        scene_description: str = "",
        subtitle_enabled: bool = False,
        prompt: str = "",
        vocal_gender: str = "auto",
        instrumental: bool = False,
        lyrics: str = "",
        style: str = "",
        title: str = "",
        music_asset_id: str = "",
    ) -> Dict[str, Any]:
        """
        Phase 1：快速创建项目并提交任务（< 10秒完成）
        stdout 输出：{"status": "started", "project_id": "xxx", "log_file": "..."}
        """
        # 参数校验
        if not reference_image and not reference_image_url:
            return {"code": -1, "msg": "reference_image 或 reference_image_url 至少提供一个", "data": None}
        if music_generate_type == "prompt" and not prompt:
            return {"code": -1, "msg": "提示词模式必须提供 prompt", "data": None}
        if music_generate_type == "custom" and not (lyrics and style and title):
            return {"code": -1, "msg": "自定义模式必须提供 lyrics, style, title", "data": None}
        if music_generate_type == "upload" and not music_asset_id:
            return {"code": -1, "msg": "上传模式必须提供 music_asset_id", "data": None}

        # 步骤1：创建项目
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 创建项目...", file=sys.stderr)
        create_result = self.create_project(name=project_name, aspect=aspect)
        code = create_result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        if code != 0 and code != 200:
            return {"code": code, "msg": f"创建项目失败: {create_result.get('msg', '未知错误')}", "data": None}

        project_id = create_result.get("data", {}).get("project_id")
        if not project_id:
            return {"code": -1, "msg": "创建项目失败: 未获取到项目ID", "data": None}
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 项目创建成功，ID: {project_id}", file=sys.stderr)

        # 步骤2：提交任务
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 提交任务...", file=sys.stderr)
        submit_result = self.submit_mv_task(
            project_id=project_id,
            music_generate_type=music_generate_type,
            aspect=aspect,
            reference_image=reference_image,
            reference_image_url=reference_image_url,
            scene_description=scene_description,
            subtitle_enabled=subtitle_enabled,
            prompt=prompt,
            vocal_gender=vocal_gender,
            instrumental=instrumental,
            lyrics=lyrics,
            style=style,
            title=title,
            music_asset_id=music_asset_id,
        )
        code = submit_result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        if code != 0 and code != 200:
            return {"code": code, "msg": f"提交任务失败: {submit_result.get('msg', '未知错误')}", "data": None}
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务提交成功", file=sys.stderr)

        log_file = self._setup_log(project_id)
        return {
            "code": 200,
            "status": "started",
            "data": {
                "project_id": project_id,
                "log_file": str(log_file)
            }
        }

    def poll_until_complete(self, project_id: str, interval: int = 3) -> Dict[str, Any]:
        """
        Phase 3：轮询直到完成（乐观同步路径）
        含完整工作流：查询 → 支付 → 等待完成 → .sent 防重复
        """
        start_time = datetime.now()
        timeout = timedelta(hours=1)
        paid = False
        max_retries = 5
        retry_delay = 5
        last_logged_step = ""
        last_logged_status = ""
        completed_no_asset_count = 0

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始轮询项目 {project_id}...", file=sys.stderr)

        while True:
            if datetime.now() - start_time > timeout:
                return {"code": -1, "msg": f"轮询超时（超过1小时），project_id={project_id}", "data": {"project_id": project_id}}

            # 查询进度（带重试）
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
                    error_str = str(query_result.get("msg", ""))
                    is_net = any(x in error_str for x in ["Connection", "Remote", "timeout", "aborted", "disconnected"])
                    if not is_net:
                        return {"code": code, "msg": f"查询失败: {error_str}", "data": {"project_id": project_id}}
                    retry_count += 1
                    time.sleep(retry_delay if retry_count < max_retries else interval)
                except Exception as e:
                    error_str = str(e)
                    is_net = any(x in error_str for x in ["Connection", "Remote", "timeout", "aborted", "disconnected"])
                    if not is_net:
                        return {"code": -1, "msg": f"查询异常: {error_str}", "data": {"project_id": project_id}}
                    retry_count += 1
                    time.sleep(retry_delay if retry_count < max_retries else interval)

            if not query_success:
                continue

            data = query_result.get("data", {})
            status = data.get("status", "unknown")
            current_step = data.get("current_step", "")
            pay_status = data.get("pay_status", "")
            err_msg = data.get("err_msg", "")

            if status == "failed" or err_msg:
                return {"code": -1, "msg": f"任务失败: {err_msg or '未知错误'}", "data": {"project_id": project_id}}

            for step in data.get("steps", []):
                for sub in step.get("sub_steps", []):
                    if sub.get("status") == "failed" or sub.get("error"):
                        return {"code": -1, "msg": f"子步骤失败: {sub.get('step', '')} - {sub.get('error', '')}", "data": {"project_id": project_id}}

            # 支付（MV 只传 project_id）
            if not paid and (pay_status == "pending" or (current_step and "pay" in current_step.lower())):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{project_id}] 执行支付...", file=sys.stderr)
                pay_result = self.pay(project_id)
                code = pay_result.get("code")
                if isinstance(code, str):
                    code = int(code) if code.isdigit() else 0
                if code != 0 and code != 200:
                    return {"code": code, "msg": f"支付失败: {pay_result.get('msg', '未知错误')}", "data": {"project_id": project_id}}
                paid = True
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{project_id}] 支付成功，继续查询...", file=sys.stderr)
                continue

            # 检查完成
            video_asset = data.get("video_asset", {})
            download_url = video_asset.get("download_url") if video_asset else None
            if status == "completed":
                if video_asset and download_url:
                    # 防重复：检查 .sent 文件
                    if self._check_sent(project_id):
                        return {"code": 200, "status": "already_sent", "msg": "结果已推送，跳过重复发送", "data": {"project_id": project_id}}
                    signed_url = video_asset.get("signed_url", "").replace("~", "%7E")
                    thumbnail_url = video_asset.get("thumbnail_url", "")
                    duration = video_asset.get("duration", 0)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{project_id}] 任务完成！时长: {duration}s", file=sys.stderr)
                    self._mark_sent(project_id)
                    # CloudFront 签名中 ~ 须编码为 %7E，否则飞书等平台会截断 URL
                    safe_signed_url = signed_url.replace("~", "%7E")
                    return {
                        "code": 200,
                        "msg": "success",
                        "uuid": query_result.get("uuid", ""),
                        "data": {
                            "project_id": project_id,
                            "signed_url": safe_signed_url,
                            "download_url": download_url,
                            "thumbnail_url": thumbnail_url,
                            "duration": duration,
                            "video_asset": video_asset,
                            "status": "completed"
                        }
                    }
                else:
                    completed_no_asset_count += 1
                    if completed_no_asset_count >= 20:
                        return {"code": -1, "msg": f"任务已完成但持续无视频资源（等待超过60秒），project_id={project_id}", "data": {"project_id": project_id}}
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{project_id}] 等待视频资源 ({completed_no_asset_count}/20)...", file=sys.stderr)
            else:
                completed_no_asset_count = 0

            if status != last_logged_status or current_step != last_logged_step:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{project_id}] 状态: {status} | 步骤: {current_step} | 支付: {pay_status}", file=sys.stderr)
                last_logged_status = status
                last_logged_step = current_step

            time.sleep(interval)

    def execute_workflow(
        self,
        music_generate_type: str,
        aspect: str,
        project_name: str,
        reference_image: str = "",
        reference_image_url: str = "",
        scene_description: str = "",
        subtitle_enabled: bool = False,
        prompt: str = "",
        vocal_gender: str = "auto",
        instrumental: bool = False,
        lyrics: str = "",
        style: str = "",
        title: str = "",
        music_asset_id: str = "",
    ) -> Dict[str, Any]:
        """
        执行完整工作流：创建项目 -> 提交任务 -> 查询进度 -> 支付 -> 等待完成
        """
        start_time = datetime.now()
        timeout = timedelta(hours=1)
        query_interval = 3

        # 校验必填
        if not reference_image and not reference_image_url:
            return {"code": -1, "msg": "reference_image 或 reference_image_url 至少提供一个", "data": None}
        if music_generate_type == "prompt" and not prompt:
            return {"code": -1, "msg": "提示词模式必须提供 prompt", "data": None}
        if music_generate_type == "custom" and not (lyrics and style and title):
            return {"code": -1, "msg": "自定义模式必须提供 lyrics, style, title", "data": None}
        if music_generate_type == "upload" and not music_asset_id:
            return {"code": -1, "msg": "上传模式必须提供 music_asset_id", "data": None}

        # 步骤1：创建项目
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 步骤1: 创建项目...", file=sys.stderr)
        create_result = self.create_project(name=project_name, aspect=aspect)
        code = create_result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        if code != 0 and code != 200:
            return {"code": code, "msg": f"创建项目失败: {create_result.get('msg', '未知错误')}", "data": None}

        project_id = create_result.get("data", {}).get("project_id")
        if not project_id:
            return {"code": -1, "msg": "创建项目失败: 未获取到项目ID", "data": None}
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{project_id}] 项目创建成功", file=sys.stderr)

        # 步骤2：提交任务
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{project_id}] 步骤2: 提交任务...", file=sys.stderr)
        submit_result = self.submit_mv_task(
            project_id=project_id,
            music_generate_type=music_generate_type,
            aspect=aspect,
            reference_image=reference_image,
            reference_image_url=reference_image_url,
            scene_description=scene_description,
            subtitle_enabled=subtitle_enabled,
            prompt=prompt,
            vocal_gender=vocal_gender,
            instrumental=instrumental,
            lyrics=lyrics,
            style=style,
            title=title,
            music_asset_id=music_asset_id,
        )
        code = submit_result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        if code != 0 and code != 200:
            return {"code": code, "msg": f"提交任务失败: {submit_result.get('msg', '未知错误')}", "data": None}
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{project_id}] 任务提交成功", file=sys.stderr)

        # 步骤3：轮询进度与支付
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{project_id}] 步骤3: 查询进度...", file=sys.stderr)
        paid = False
        max_retries = 5
        retry_delay = 5
        last_logged_step = ""
        last_logged_status = ""

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
                    is_network_error = any(
                        x in error_msg for x in ["Connection", "Remote", "timeout", "aborted", "disconnected"]
                    )
                    if not is_network_error:
                        return {"code": code, "msg": f"查询失败: {error_msg}", "data": None}
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{project_id}] 网络错误，{retry_delay}秒后重试 ({retry_count}/{max_retries})", file=sys.stderr)
                        time.sleep(retry_delay)
                    else:
                        time.sleep(query_interval)
                        break
                except Exception as e:
                    error_str = str(e)
                    is_network_error = any(
                        x in error_str for x in ["Connection", "Remote", "timeout", "aborted", "disconnected"]
                    )
                    if not is_network_error:
                        return {"code": -1, "msg": f"查询异常: {error_str}", "data": None}
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(retry_delay)
                    else:
                        time.sleep(query_interval)
                        break

            if not query_success:
                continue

            data = query_result.get("data", {})
            status = data.get("status", "unknown")
            current_step = data.get("current_step", "")
            pay_status = data.get("pay_status", "")
            err_msg = data.get("err_msg", "")

            if status == "failed" or err_msg:
                return {"code": -1, "msg": f"任务失败: {err_msg or '未知错误'}", "data": None}

            steps = data.get("steps", [])
            for step in steps:
                for sub in step.get("sub_steps", []):
                    if sub.get("status") == "failed" or sub.get("error"):
                        return {"code": -1, "msg": f"子步骤失败: {sub.get('step', '')} - {sub.get('error', '')}", "data": None}

            if not paid and (pay_status == "pending" or (current_step and "pay" in current_step.lower())):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{project_id}] 执行支付...", file=sys.stderr)
                pay_result = self.pay(project_id)
                code = pay_result.get("code")
                if isinstance(code, str):
                    code = int(code) if code.isdigit() else 0
                if code != 0 and code != 200:
                    return {"code": code, "msg": f"支付失败: {pay_result.get('msg', '未知错误')}", "data": None}
                paid = True
                continue

            video_asset = data.get("video_asset", {})
            download_url = video_asset.get("download_url") if video_asset else None
            if video_asset and download_url:
                signed_url = video_asset.get("signed_url", "")
                thumbnail_url = video_asset.get("thumbnail_url", "")
                duration = video_asset.get("duration", 0)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{project_id}] 任务完成！时长: {duration}s", file=sys.stderr)
                return {
                    "code": 200,
                    "msg": "success",
                    "uuid": query_result.get("uuid", ""),
                    "data": {
                        "project_id": project_id,
                        "signed_url": signed_url,      # 在线播放链接
                        "download_url": download_url,  # 下载链接
                        "thumbnail_url": thumbnail_url,
                        "duration": duration,
                        "video_asset": video_asset,
                        "status": "completed"
                    },
                }

            # 仅在状态或步骤变化时打印，避免重复日志
            if status != last_logged_status or current_step != last_logged_step:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{project_id}] 状态: {status} | 步骤: {current_step} | 支付: {pay_status}", file=sys.stderr)
                last_logged_status = status
                last_logged_step = current_step
            time.sleep(query_interval)


def main():
    parser = argparse.ArgumentParser(description="MV 托管模式 API 调用工具", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pretty", action="store_true", help="美化 JSON")
    sub = parser.add_subparsers(dest="command")

    cp = sub.add_parser("create", help="创建项目")
    cp.add_argument("--name", required=True)
    cp.add_argument("--aspect", required=True, choices=["16:9", "9:16"])

    sp = sub.add_parser("submit", help="提交任务")
    sp.add_argument("--project-id", required=True)
    sp.add_argument("--mode", required=True, choices=["prompt", "custom", "upload"])
    sp.add_argument("--aspect", required=True, choices=["16:9", "9:16"])
    sp.add_argument("--reference-image", default="")
    sp.add_argument("--reference-image-url", default="")
    sp.add_argument("--scene-description", default="")
    sp.add_argument("--subtitle", action="store_true")
    sp.add_argument("--prompt", default="")
    sp.add_argument("--vocal-gender", default="auto")
    sp.add_argument("--instrumental", action="store_true")
    sp.add_argument("--lyrics", default="")
    sp.add_argument("--style", default="")
    sp.add_argument("--title", default="")
    sp.add_argument("--music-asset-id", default="")

    qp = sub.add_parser("query", help="查询进度")
    qp.add_argument("--project-id", required=True)
    qp.add_argument("--poll", action="store_true", help="Phase 3：轮询直到完成（含支付、.sent 防重复）")
    qp.add_argument("--interval", type=int, default=3, help="轮询间隔（秒，默认3）")

    pp = sub.add_parser("pay", help="支付")
    pp.add_argument("--project-id", required=True)

    rp = sub.add_parser("retry", help="重试失败步骤")
    rp.add_argument("--project-id", required=True)
    rp.add_argument("--current-step", required=True, help="如 music-generate, storyboard, shot, editor")

    # start 命令（Phase 1：快速创建项目并提交任务，< 10秒）
    startp = sub.add_parser("start", help="Phase 1：快速创建项目并提交任务（< 10秒）")
    startp.add_argument("--mode", required=True, choices=["prompt", "custom", "upload"])
    startp.add_argument("--aspect", required=True, choices=["16:9", "9:16"])
    startp.add_argument("--project-name", required=True)
    startp.add_argument("--reference-image", default="")
    startp.add_argument("--reference-image-url", default="")
    startp.add_argument("--scene-description", default="")
    startp.add_argument("--subtitle", action="store_true")
    startp.add_argument("--prompt", default="")
    startp.add_argument("--vocal-gender", default="auto")
    startp.add_argument("--instrumental", action="store_true")
    startp.add_argument("--lyrics", default="")
    startp.add_argument("--style", default="")
    startp.add_argument("--title", default="")
    startp.add_argument("--music-asset-id", default="")

    wp = sub.add_parser("workflow", help="完整工作流")
    wp.add_argument("--mode", required=True, choices=["prompt", "custom", "upload"])
    wp.add_argument("--aspect", required=True, choices=["16:9", "9:16"])
    wp.add_argument("--project-name", required=True)
    wp.add_argument("--reference-image", default="")
    wp.add_argument("--reference-image-url", default="")
    wp.add_argument("--scene-description", default="")
    wp.add_argument("--subtitle", action="store_true")
    wp.add_argument("--prompt", default="")
    wp.add_argument("--vocal-gender", default="auto")
    wp.add_argument("--instrumental", action="store_true")
    wp.add_argument("--lyrics", default="")
    wp.add_argument("--style", default="")
    wp.add_argument("--title", default="")
    wp.add_argument("--music-asset-id", default="")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    api = MVTrusteeAPI()

    if args.command == "create":
        r = api.create_project(name=args.name, aspect=args.aspect)
        print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))

    elif args.command == "submit":
        r = api.submit_mv_task(
            project_id=args.project_id,
            music_generate_type=args.mode,
            aspect=args.aspect,
            reference_image=args.reference_image,
            reference_image_url=args.reference_image_url,
            scene_description=args.scene_description,
            subtitle_enabled=args.subtitle,
            prompt=args.prompt,
            vocal_gender=args.vocal_gender,
            instrumental=args.instrumental,
            lyrics=args.lyrics,
            style=args.style,
            title=args.title,
            music_asset_id=args.music_asset_id,
        )
        print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))

    elif args.command == "query":
        if args.poll:
            # Phase 3：轮询直到完成（含支付、.sent 防重复）
            r = api.poll_until_complete(project_id=args.project_id, interval=args.interval)
            print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))
            code = r.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                sys.exit(1)
        else:
            # 单次查询（供 Cron 使用）
            # 超时兜底：最多轮询 15 次（约 45 分钟），超时输出纯文本触发 Cron 取消
            count = api._increment_query_count(args.project_id)
            if count > 15:
                print("⏰ MV 生成超时\n\n已等待超过 45 分钟，未能完成。\n\n💡 建议重新生成，我随时待命~")
                sys.exit(0)

            r = api.query_progress(args.project_id)
            data = (r.get("data") or {}) if r else {}
            status = data.get("status", "")
            # 自动支付：价格算出来后 pay_status 变 pending，直接付款无需 agent 介入
            pay_status = data.get("pay_status", "")
            if pay_status == "pending":
                pay_r = api.pay(args.project_id)
                pay_code = pay_r.get("code")
                if isinstance(pay_code, str):
                    pay_code = int(pay_code) if pay_code.isdigit() else 0
                if pay_code == 200:
                    price = pay_r.get("data", {}).get("price", 0)
                    print(json.dumps({"code": 200, "status": "running", "msg": f"已自动支付 {price} 积分，MV 继续生成中"}, ensure_ascii=False))
                else:
                    print(json.dumps({"code": pay_code, "status": "pay_failed", "msg": "积分不足，请充值后重试"}, ensure_ascii=False))
                    sys.exit(1)
                sys.exit(0)
            if status == "completed":
                video_asset = data.get("video_asset", {})
                if video_asset and video_asset.get("download_url"):
                    if api._check_sent(args.project_id):
                        r = {"code": 200, "status": "already_sent", "msg": "结果已推送，跳过重复发送", "data": {"project_id": args.project_id}}
                    else:
                        api._mark_sent(args.project_id)
                        # CloudFront 签名中 ~ 须编码为 %7E，否则飞书等平台会截断 URL
                        if r.get("data", {}).get("video_asset", {}).get("signed_url"):
                            r["data"]["video_asset"]["signed_url"] = r["data"]["video_asset"]["signed_url"].replace("~", "%7E")
                    print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))
                    # exit(0) 隐式：完成或已发送
                else:
                    # completed 但视频未就绪，视为进行中
                    print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))
                    sys.exit(0)
            elif status in ("failed", "error") or (r and r.get("code") == -1):
                print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))
                sys.exit(1)  # 失败
            else:
                print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))
                sys.exit(0)  # 进行中

    elif args.command == "pay":
        r = api.pay(args.project_id)
        print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))

    elif args.command == "retry":
        r = api.retry(project_id=args.project_id, current_step=args.current_step)
        print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))

    elif args.command == "start":
        r = api.create_and_submit(
            music_generate_type=args.mode,
            aspect=args.aspect,
            project_name=args.project_name,
            reference_image=args.reference_image,
            reference_image_url=args.reference_image_url,
            scene_description=args.scene_description,
            subtitle_enabled=args.subtitle,
            prompt=args.prompt,
            vocal_gender=args.vocal_gender,
            instrumental=args.instrumental,
            lyrics=args.lyrics,
            style=args.style,
            title=args.title,
            music_asset_id=args.music_asset_id,
        )
        print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))
        code = r.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        if code != 0 and code != 200:
            sys.exit(1)

    elif args.command == "workflow":
        r = api.execute_workflow(
            music_generate_type=args.mode,
            aspect=args.aspect,
            project_name=args.project_name,
            reference_image=args.reference_image,
            reference_image_url=args.reference_image_url,
            scene_description=args.scene_description,
            subtitle_enabled=args.subtitle,
            prompt=args.prompt,
            vocal_gender=args.vocal_gender,
            instrumental=args.instrumental,
            lyrics=args.lyrics,
            style=args.style,
            title=args.title,
            music_asset_id=args.music_asset_id,
        )
        print(json.dumps(r, indent=2, ensure_ascii=False) if args.pretty else json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
