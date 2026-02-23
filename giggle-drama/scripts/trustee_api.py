#!/usr/bin/env python3
"""
托管模式V2 API调用脚本
支持创建项目、提交任务、查询进度和支付功能
"""

import argparse
import json
import sys
import time
import os
import warnings
warnings.filterwarnings("ignore")  # 抑制 LibreSSL/urllib3 等运行时警告
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

# 延迟导入requests，只在需要时导入
def _check_requests():
    """检查并导入requests库"""
    try:
        import requests
        return requests
    except ImportError:
        print("错误: 需要安装 requests 库", file=sys.stderr)
        print("请运行: pip install requests", file=sys.stderr)
        sys.exit(1)


class TrusteeModeAPI:
    """托管模式V2 API客户端"""
    
    def __init__(self):
        """
        初始化API客户端
        """
        requests = _check_requests()  # 延迟导入

        # 加载环境变量
        self._load_env()

        # 从环境变量读取API密钥
        self.api_key = os.getenv('GIGGLE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "未找到API密钥。请确保：\n"
                "1. 已创建 .env 文件\n"
                "2. 在 .env 文件中设置了 GIGGLE_API_KEY=your_api_key"
            )

        self.base_url = "https://giggle.pro"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def _load_env(self):
        """加载环境变量文件"""
        try:
            from dotenv import load_dotenv
            # 获取脚本所在目录的父目录（项目根目录）
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            env_file = project_root / '.env'

            if env_file.exists():
                load_dotenv(env_file)
            else:
                # 如果项目根目录没有.env，尝试从当前工作目录加载
                load_dotenv()
        except ImportError:
            print("警告: 未安装 python-dotenv 库", file=sys.stderr)
            print("请运行: pip install python-dotenv", file=sys.stderr)

    def _get_log_dir(self) -> Path:
        """获取日志目录路径"""
        log_dir = Path.home() / '.openclaw' / 'skills' / 'giggle-drama' / 'logs'
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
        sent_file = self._get_log_dir() / f"{project_id}.sent"
        return sent_file.exists()

    def _mark_sent(self, project_id: str) -> None:
        """标记已推送结果"""
        sent_file = self._get_log_dir() / f"{project_id}.sent"
        sent_file.touch()

    def create_project(self, name: str, project_type: str, aspect: str, mode: str = "trustee") -> Dict[str, Any]:
        """
        创建项目
        
        Args:
            name: 项目名称
            project_type: 项目类型 (mv/director)
            aspect: 视频宽高比 (16:9/9:16)
            mode: 项目模式 (professional/trustee)
        
        Returns:
            API响应数据
        """
        url = f"{self.base_url}/api/v1/project/create"
        data = {
            "name": name,
            "type": project_type,
            "aspect": aspect,
            "mode": mode
        }
        
        try:
            headers = {"x-auth": self.api_key}
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # 兼容不同的响应格式：code可能是字符串"200"或数字200
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
    
    def submit_task(self, project_id: str, diy_story: str, aspect: str, 
                   video_duration: str, language: str, style_id: Optional[int] = None) -> Dict[str, Any]:
        """
        提交任务
        
        Args:
            project_id: 项目ID
            diy_story: 自定义故事内容
            aspect: 视频宽高比 (16:9/9:16)
            video_duration: 视频时长 (auto/30/60/120/180/240/300)
            language: 语言 (zh/en)
            style_id: 风格ID（可选，如果不提供则不传此参数）
        
        Returns:
            API响应数据
        """
        url = f"{self.base_url}/api/v1/trustee_mode/submit-v2"
        data = {
            "project_id": project_id,
            "diy_story": diy_story,
            "aspect": aspect,
            "video_duration": video_duration,
            "language": language
        }
        
        # 只有当提供了style_id时才添加到请求中
        if style_id is not None:
            data["style_id"] = style_id
        
        try:
            headers = {"x-auth": self.api_key}
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # 兼容不同的响应格式：code可能是字符串"200"或数字200
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
        """
        查询任务进度
        
        Args:
            project_id: 项目ID
        
        Returns:
            API响应数据
        """
        url = f"{self.base_url}/api/v1/trustee_mode/query-v2"
        params = {"project_id": project_id}
        
        try:
            headers = {"x-auth": self.api_key}
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # 兼容不同的响应格式：code可能是字符串"200"或数字200
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
    
    def pay(self, project_id: str, video_first_model: str, 
           video_second_model: str, image_first_model: str) -> Dict[str, Any]:
        """
        支付
        
        Args:
            project_id: 项目ID
            video_first_model: 视频首选模型
            video_second_model: 视频备选模型
            image_first_model: 图片首选模型
        
        Returns:
            API响应数据
        """
        url = f"{self.base_url}/api/v1/trustee_mode/pay"
        data = {
            "project_id": project_id,
            "video_first_model": video_first_model,
            "video_second_model": video_second_model,
            "image_first_model": image_first_model
        }
        
        try:
            headers = {"x-auth": self.api_key}
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # 兼容不同的响应格式：code可能是字符串"200"或数字200
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
    
    def get_styles(self, page: int = 1, page_size: int = 999, language: str = "zh") -> Dict[str, Any]:
        """
        获取风格列表
        
        Args:
            page: 页码（默认1）
            page_size: 每页数量（默认999）
            language: 语言（默认zh，可选zh/en）
        
        Returns:
            API响应数据
        """
        url = f"{self.base_url}/api/v1/ai_style/list"
        params = {
            "page": page,
            "page_size": page_size,
            "language": language
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            # 兼容不同的响应格式
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            
            if code != 0 and code != 200:
                print(f"获取风格列表失败: {result.get('msg', '未知错误')}")
                return result
            
            return result
        except Exception as e:
            print(f"请求失败: {e}")
            return {"code": -1, "msg": str(e)}

    def create_and_submit(self, diy_story: str, aspect: str, project_name: str,
                         video_duration: str = "auto", style_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Phase 1：快速创建项目并提交任务（< 10秒完成）
        stdout 输出：{"status": "started", "project_id": "xxx", "log_file": "..."}
        """
        language = "zh"
        project_type = "director"

        # 步骤1：创建项目
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 创建项目...", file=sys.stderr)
        create_result = self.create_project(
            name=project_name,
            project_type=project_type,
            aspect=aspect,
            mode="trustee"
        )

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

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 项目创建成功，ID: {project_id}", file=sys.stderr)

        # 步骤2：提交任务
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 提交任务...", file=sys.stderr)
        submit_result = self.submit_task(
            project_id=project_id,
            diy_story=diy_story,
            aspect=aspect,
            video_duration=video_duration,
            language=language,
            style_id=style_id
        )

        code = submit_result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0

        if code != 0 and code != 200:
            return {
                "code": code,
                "msg": f"提交任务失败: {submit_result.get('msg', '未知错误')}",
                "data": None
            }

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务提交成功", file=sys.stderr)

        # 创建日志文件
        log_file = self._setup_log(project_id)

        return {
            "code": 200,
            "status": "started",
            "data": {
                "project_id": project_id,
                "log_file": str(log_file)
            }
        }

    def download_video(self, download_url: str, project_name: str, output_dir: Optional[str] = None) -> Optional[str]:
        """
        下载视频到本地

        Args:
            download_url: 视频下载链接
            project_name: 项目名称（用于生成文件名）
            output_dir: 输出目录（可选，默认为~/Downloads）

        Returns:
            本地文件路径，失败返回None
        """
        try:
            # 确定输出目录
            if output_dir is None:
                # 默认保存到用户的Downloads目录
                home = Path.home()
                output_dir = home / "Downloads" / "giggle-videos"
            else:
                output_dir = Path(output_dir)

            # 创建输出目录
            output_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名（使用项目名称和时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{project_name}_{timestamp}.mp4"
            # 清理文件名中的非法字符
            filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
            filepath = output_dir / filename

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始下载视频到: {filepath}", file=sys.stderr)

            # 下载视频
            response = self.session.get(download_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 下载进度: {progress:.1f}%",
                                  end='', file=sys.stderr)

            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 视频下载完成！", file=sys.stderr)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 本地路径: {filepath}", file=sys.stderr)

            return str(filepath)

        except Exception as e:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 视频下载失败: {e}", file=sys.stderr)
            return None

    def execute_workflow(self, diy_story: str, aspect: str, project_name: str,
                        video_duration: str = "auto", style_id: Optional[int] = None) -> Dict[str, Any]:
        """
        执行完整工作流：创建项目 -> 提交任务 -> 查询进度 -> 支付 -> 等待完成
        
        Args:
            diy_story: 故事创意内容
            aspect: 视频宽高比 (16:9/9:16)
            project_name: 项目名称
            video_duration: 视频时长 (auto/30/60/120/180/240/300)，默认为"auto"
            style_id: 风格ID（可选）
        
        Returns:
            包含下载链接的响应数据，或失败信息
        """
        start_time = datetime.now()
        timeout = timedelta(hours=1)  # 固定超时时间为1小时
        query_interval = 3  # 固定查询间隔为3秒
        language = "zh"  # 固定语言为中文
        project_type = "director"  # 固定项目类型为director
        
        # 步骤1：创建项目
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 步骤1: 创建项目...", file=sys.stderr)
        create_result = self.create_project(
            name=project_name,
            project_type=project_type,
            aspect=aspect,
            mode="trustee"
        )
        
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
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 项目创建成功，项目ID: {project_id}", file=sys.stderr)
        
        # 步骤2：提交任务
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 步骤2: 提交任务...", file=sys.stderr)
        submit_result = self.submit_task(
            project_id=project_id,
            diy_story=diy_story,
            aspect=aspect,
            video_duration=video_duration,
            language=language,
            style_id=style_id
        )
        
        code = submit_result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        
        if code != 0 and code != 200:
            return {
                "code": code,
                "msg": f"提交任务失败: {submit_result.get('msg', '未知错误')}",
                "data": None
            }
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务提交成功", file=sys.stderr)
        
        # 步骤3：循环查询进度
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 步骤3: 开始查询进度...", file=sys.stderr)
        
        video_first_model = "grok"
        video_second_model = "seedance15-pro"
        image_first_model = "seedream45"
        paid = False  # 标记是否已支付，避免重复支付
        max_retries = 5  # 最大重试次数
        retry_delay = 5  # 重试延迟（秒）
        last_logged_step = ""  # 上次打印的步骤，避免重复日志
        last_logged_status = ""

        while True:
            # 检查超时
            if datetime.now() - start_time > timeout:
                return {
                    "code": -1,
                    "msg": "工作流超时（超过1小时）",
                    "data": None
                }
            
            # 查询进度（带重试机制）
            query_result = None
            query_success = False
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    query_result = self.query_progress(project_id)
                    code = query_result.get("code")
                    if isinstance(code, str):
                        code = int(code) if code.isdigit() else 0
                    
                    # 如果查询成功（code为0或200），跳出重试循环
                    if code == 0 or code == 200:
                        query_success = True
                        break
                    
                    # 检查错误信息，判断是否为网络错误
                    error_msg = query_result.get("msg", "")
                    error_str = str(error_msg)
                    
                    # 判断是否为网络错误
                    is_network_error = (
                        "Connection" in error_str or 
                        "Remote" in error_str or 
                        "timeout" in error_str.lower() or
                        "aborted" in error_str.lower() or
                        "disconnected" in error_str.lower()
                    )
                    
                    # 如果是业务错误（非网络错误），直接返回
                    if not is_network_error:
                        return {
                            "code": code,
                            "msg": f"查询进度失败: {error_msg}",
                            "data": None
                        }
                    
                    # 网络错误，继续重试
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 网络错误，{retry_delay}秒后重试 ({retry_count}/{max_retries}): {error_msg}", file=sys.stderr)
                        time.sleep(retry_delay)
                    else:
                        # 达到最大重试次数，但不退出，等待后继续下一次循环
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 网络错误，已达到最大重试次数，等待{query_interval}秒后继续查询...", file=sys.stderr)
                        time.sleep(query_interval)
                        break
                        
                except Exception as e:
                    # 捕获异常，判断是否为网络错误
                    error_str = str(e)
                    is_network_error = (
                        "Connection" in error_str or 
                        "Remote" in error_str or 
                        "timeout" in error_str.lower() or
                        "aborted" in error_str.lower() or
                        "disconnected" in error_str.lower()
                    )
                    
                    if is_network_error:
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 网络异常，{retry_delay}秒后重试 ({retry_count}/{max_retries}): {error_str}", file=sys.stderr)
                            time.sleep(retry_delay)
                        else:
                            # 达到最大重试次数，但不退出，等待后继续下一次循环
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 网络异常，已达到最大重试次数，等待{query_interval}秒后继续查询...", file=sys.stderr)
                            time.sleep(query_interval)
                            break
                    else:
                        # 非网络错误，直接返回
                        return {
                            "code": -1,
                            "msg": f"查询进度失败: {error_str}",
                            "data": None
                        }
            
            # 如果查询失败（网络错误且重试后仍失败），继续下一次循环
            if not query_success:
                continue
            
            # 查询成功，继续处理
            code = query_result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            
            data = query_result.get("data", {})
            status = data.get("status", "unknown")
            current_step = data.get("current_step", "")
            pay_status = data.get("pay_status", "")
            err_msg = data.get("err_msg", "")
            
            # 检查是否有错误
            if status == "failed" or err_msg:
                return {
                    "code": -1,
                    "msg": f"任务失败: {err_msg or '未知错误'}",
                    "data": None
                }
            
            # 检查子步骤是否有失败
            steps = data.get("steps", [])
            for step in steps:
                sub_steps = step.get("sub_steps", [])
                for sub_step in sub_steps:
                    sub_status = sub_step.get("status", "")
                    sub_error = sub_step.get("error", "")
                    if sub_status == "failed" or sub_error:
                        return {
                            "code": -1,
                            "msg": f"子步骤失败: {sub_step.get('step', '未知步骤')} - {sub_error or '未知错误'}",
                            "data": None
                        }
            
            # 检查是否需要支付（只在未支付且状态为待支付时执行）
            if not paid and (pay_status == "pending" or (current_step and "pay" in current_step.lower())):
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检测到待支付状态，执行支付...", file=sys.stderr)
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
                    return {
                        "code": code,
                        "msg": f"支付失败: {pay_result.get('msg', '未知错误')}",
                        "data": None
                    }
                
                paid = True  # 标记已支付
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 支付成功，继续查询进度...", file=sys.stderr)
                # 支付后立即再次查询进度
                continue
            
            # 检查是否完成
            if status == "completed":
                video_asset = data.get("video_asset", {})
                download_url = video_asset.get("download_url") if video_asset else None
                
                if video_asset and download_url:
                    signed_url = video_asset.get("signed_url", "")
                    thumbnail_url = video_asset.get("thumbnail_url", "")
                    duration = video_asset.get("duration", 0)
                    shot_count = data.get("shot_count", 0)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务完成！时长: {duration}s | 分镜数: {shot_count}", file=sys.stderr)

                    # 自动下载视频到本地
                    local_path = self.download_video(download_url, project_name)

                    # 对 signed_url 做 URL 编码：~ → %7E
                    # 飞书发送文本消息时会在 ~ 处截断链接，导致 Signature 不完整
                    safe_signed_url = signed_url.replace("~", "%7E")

                    return {
                        "code": 200,
                        "msg": "success",
                        "uuid": query_result.get("uuid", ""),
                        "data": {
                            "project_id": project_id,
                            "signed_url": safe_signed_url,  # 在线播放链接（~ 已编码为 %7E，飞书可正常点击）
                            "download_url": download_url,
                            "thumbnail_url": thumbnail_url,
                            "duration": duration,
                            "shot_count": shot_count,
                            "local_path": local_path,
                            "video_asset": video_asset,
                            "status": status
                        }
                    }
                else:
                    # 已完成但还没有下载链接，继续等待
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务状态为完成，但尚未生成下载链接，继续等待...", file=sys.stderr)
            
            # 仅在状态或步骤发生变化时打印，避免每3秒一条重复日志
            if status != last_logged_status or current_step != last_logged_step:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 状态: {status} | 步骤: {current_step} | 支付: {pay_status}", file=sys.stderr)
                last_logged_status = status
                last_logged_step = current_step

            # 等待后继续查询
            time.sleep(query_interval)

    def poll_until_complete(self, project_id: str, interval: int = 3) -> Dict[str, Any]:
        """
        Phase 3：轮询直到完成（乐观同步路径）
        含完整工作流：查询 → 支付 → 等待完成 → .sent 防重复
        """
        start_time = datetime.now()
        timeout = timedelta(hours=1)

        video_first_model = "grok"
        video_second_model = "seedance15-pro"
        image_first_model = "seedream45"
        paid = False
        max_retries = 5
        retry_delay = 5
        last_logged_step = ""
        last_logged_status = ""
        completed_no_asset_count = 0  # 防止 completed 但无 video_asset 无限等待

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始轮询项目 {project_id}...", file=sys.stderr)

        while True:
            # 检查超时
            if datetime.now() - start_time > timeout:
                return {
                    "code": -1,
                    "msg": f"轮询超时（超过1小时），project_id={project_id}",
                    "data": {"project_id": project_id}
                }

            # 查询进度（带重试机制）
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

                    error_msg = query_result.get("msg", "")
                    error_str = str(error_msg)
                    is_network_error = any(kw in error_str for kw in
                        ["Connection", "Remote", "timeout", "aborted", "disconnected"])

                    if not is_network_error:
                        return {
                            "code": code,
                            "msg": f"查询进度失败: {error_msg}",
                            "data": {"project_id": project_id}
                        }

                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 网络错误，{retry_delay}秒后重试 ({retry_count}/{max_retries})", file=sys.stderr)
                        time.sleep(retry_delay)
                    else:
                        time.sleep(interval)
                        break

                except Exception as e:
                    error_str = str(e)
                    is_network_error = any(kw in error_str for kw in
                        ["Connection", "Remote", "timeout", "aborted", "disconnected"])

                    if is_network_error:
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 网络异常，{retry_delay}秒后重试 ({retry_count}/{max_retries})", file=sys.stderr)
                            time.sleep(retry_delay)
                        else:
                            time.sleep(interval)
                            break
                    else:
                        return {
                            "code": -1,
                            "msg": f"查询进度异常: {error_str}",
                            "data": {"project_id": project_id}
                        }

            if not query_success:
                continue

            # 解析查询结果
            data = query_result.get("data", {})
            status = data.get("status", "unknown")
            current_step = data.get("current_step", "")
            pay_status = data.get("pay_status", "")
            err_msg = data.get("err_msg", "")

            # 检查任务失败
            if status == "failed" or err_msg:
                return {
                    "code": -1,
                    "msg": f"任务失败: {err_msg or '未知错误'}",
                    "data": {"project_id": project_id}
                }

            # 检查子步骤失败
            steps = data.get("steps", [])
            for step in steps:
                sub_steps = step.get("sub_steps", [])
                for sub_step in sub_steps:
                    if sub_step.get("status") == "failed" or sub_step.get("error"):
                        return {
                            "code": -1,
                            "msg": f"子步骤失败: {sub_step.get('step', '未知')} - {sub_step.get('error', '未知错误')}",
                            "data": {"project_id": project_id}
                        }

            # 支付逻辑（迁移自 execute_workflow）
            if not paid and (pay_status == "pending" or (current_step and "pay" in current_step.lower())):
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检测到待支付状态，执行支付...", file=sys.stderr)
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
                    return {
                        "code": code,
                        "msg": f"支付失败: {pay_result.get('msg', '未知错误')}",
                        "data": {"project_id": project_id}
                    }
                paid = True
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 支付成功，继续查询...", file=sys.stderr)
                continue

            # 检查完成
            if status == "completed":
                video_asset = data.get("video_asset", {})
                download_url = video_asset.get("download_url") if video_asset else None

                if video_asset and download_url:
                    # 防重复：检查 .sent 文件
                    if self._check_sent(project_id):
                        return {
                            "code": 200,
                            "status": "already_sent",
                            "msg": "结果已推送，跳过重复发送",
                            "data": {"project_id": project_id}
                        }

                    signed_url = video_asset.get("signed_url", "")
                    thumbnail_url = video_asset.get("thumbnail_url", "")
                    duration = video_asset.get("duration", 0)
                    shot_count = data.get("shot_count", 0)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务完成！时长: {duration}s | 分镜数: {shot_count}", file=sys.stderr)

                    # 下载视频
                    local_path = None
                    download_failed = False
                    try:
                        local_path = self.download_video(download_url, project_id)
                    except Exception as e:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 视频下载失败: {e}", file=sys.stderr)
                        download_failed = True

                    # 对 signed_url 做 URL 编码：~ → %7E
                    safe_signed_url = signed_url.replace("~", "%7E")

                    # 标记已推送
                    self._mark_sent(project_id)

                    result = {
                        "code": 200,
                        "msg": "success",
                        "data": {
                            "project_id": project_id,
                            "signed_url": safe_signed_url,
                            "download_url": download_url,
                            "thumbnail_url": thumbnail_url,
                            "duration": duration,
                            "shot_count": shot_count,
                            "local_path": local_path,
                            "video_asset": video_asset,
                            "status": status
                        }
                    }
                    if download_failed:
                        result["data"]["download_failed"] = True
                    return result
                else:
                    # completed 但无 video_asset：计数器限制等待（最多约60秒）
                    completed_no_asset_count += 1
                    if completed_no_asset_count >= 20:
                        return {
                            "code": -1,
                            "msg": f"任务已完成但持续无视频资源（等待超过60秒），project_id={project_id}",
                            "data": {"project_id": project_id}
                        }
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 状态已完成，等待视频资源生成 ({completed_no_asset_count}/20)...", file=sys.stderr)
            else:
                completed_no_asset_count = 0  # 重置计数器

            # 仅在状态或步骤发生变化时打印
            if status != last_logged_status or current_step != last_logged_step:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 状态: {status} | 步骤: {current_step} | 支付: {pay_status}", file=sys.stderr)
                last_logged_status = status
                last_logged_step = current_step

            time.sleep(interval)


def print_response(result: Dict[str, Any], pretty: bool = True):
    """打印响应结果"""
    if pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="托管模式V2 API调用工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='美化JSON输出'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建项目命令
    create_parser = subparsers.add_parser('create', help='创建项目')
    create_parser.add_argument('--name', required=True, help='项目名称')
    create_parser.add_argument('--type', required=True, choices=['mv', 'director'], 
                              help='项目类型: mv 或 director')
    create_parser.add_argument('--aspect', required=True, choices=['16:9', '9:16'],
                               help='视频宽高比: 16:9 或 9:16')
    create_parser.add_argument('--mode', default='trustee', choices=['professional', 'trustee'],
                              help='项目模式 (默认: trustee)')
    
    # 提交任务命令
    submit_parser = subparsers.add_parser('submit', help='提交任务')
    submit_parser.add_argument('--project-id', required=True, help='项目ID')
    submit_parser.add_argument('--story', required=True, dest='diy_story', help='自定义故事内容')
    submit_parser.add_argument('--aspect', required=True, choices=['16:9', '9:16'],
                               help='视频宽高比: 16:9 或 9:16')
    submit_parser.add_argument('--style-id', type=int, help='风格ID（可选，建议先使用 styles 命令查询可用风格）')
    submit_parser.add_argument('--duration', required=True, dest='video_duration',
                              choices=['auto', '30', '60', '120', '180', '240', '300'],
                              help='视频时长: auto/30/60/120/180/240/300')
    submit_parser.add_argument('--language', required=True, choices=['zh', 'en'], help='语言: zh 或 en')
    
    # 查询进度命令
    query_parser = subparsers.add_parser('query', help='查询任务进度')
    query_parser.add_argument('--project-id', required=True, help='项目ID')
    query_parser.add_argument('--poll', action='store_true', help='轮询查询直到完成')
    query_parser.add_argument('--interval', type=int, default=3, help='轮询间隔（秒，默认3秒）')
    
    # 支付命令
    pay_parser = subparsers.add_parser('pay', help='支付')
    pay_parser.add_argument('--project-id', required=True, help='项目ID')
    pay_parser.add_argument('--video-first-model', required=True, help='视频首选模型')
    pay_parser.add_argument('--video-second-model', required=True, help='视频备选模型')
    pay_parser.add_argument('--image-first-model', required=True, help='图片首选模型')
    
    # 获取风格列表命令
    styles_parser = subparsers.add_parser('styles', help='获取风格列表')
    styles_parser.add_argument('--page', type=int, default=1, help='页码（默认1）')
    styles_parser.add_argument('--page-size', type=int, default=999, dest='page_size', help='每页数量（默认999）')
    styles_parser.add_argument('--language', default='zh', choices=['zh', 'en'], help='语言（默认zh，可选zh/en）')
    styles_parser.add_argument('--table', action='store_true', help='以表格形式输出')
    
    # 完整工作流命令
    workflow_parser = subparsers.add_parser('workflow', help='执行完整工作流（创建项目->提交任务->查询进度->支付->等待完成）')
    workflow_parser.add_argument('--story', required=True, dest='diy_story', help='故事创意内容')
    workflow_parser.add_argument('--aspect', required=True, choices=['16:9', '9:16'], help='视频宽高比: 16:9 或 9:16')
    workflow_parser.add_argument('--duration', default='auto', dest='video_duration',
                                choices=['auto', '30', '60', '120', '180', '240', '300'],
                                help='视频时长: auto/30/60/120/180/240/300（默认: auto）')
    workflow_parser.add_argument('--project-name', required=True, dest='project_name', help='项目名称')
    workflow_parser.add_argument('--style-id', type=int, help='风格ID（可选）')

    # start 命令（Phase 1：快速创建项目并提交任务，< 10秒）
    start_parser = subparsers.add_parser('start', help='Phase 1：快速创建项目并提交任务（< 10秒完成）')
    start_parser.add_argument('--story', required=True, dest='diy_story', help='故事创意内容')
    start_parser.add_argument('--aspect', required=True, choices=['16:9', '9:16'], help='视频宽高比: 16:9 或 9:16')
    start_parser.add_argument('--project-name', required=True, dest='project_name', help='项目名称')
    start_parser.add_argument('--duration', default='auto', dest='video_duration',
                             choices=['auto', '30', '60', '120', '180', '240', '300'],
                             help='视频时长（默认: auto）')
    start_parser.add_argument('--style-id', type=int, help='风格ID（可选）')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # 只有在实际需要调用API时才初始化客户端（会检查requests）
    api = TrusteeModeAPI()
    
    if args.command == 'create':
        result = api.create_project(
            name=args.name,
            project_type=args.type,
            aspect=args.aspect,
            mode=args.mode
        )
        print_response(result, args.pretty)
        
        # 兼容不同的响应格式：code可能是字符串"200"或数字200
        code = result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        
        if code == 0 or code == 200:
            project_id = result.get("data", {}).get("project_id")
            if project_id:
                print(f"\n项目ID: {project_id}", file=sys.stderr)
    
    elif args.command == 'submit':
        result = api.submit_task(
            project_id=args.project_id,
            diy_story=args.diy_story,
            aspect=args.aspect,
            video_duration=args.video_duration,
            language=args.language,
            style_id=args.style_id if hasattr(args, 'style_id') and args.style_id is not None else None
        )
        print_response(result, args.pretty)
        
        # 兼容不同的响应格式：code可能是字符串"200"或数字200
        code = result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        
        if code == 0 or code == 200:
            task_id = result.get("data", {}).get("task_id")
            if task_id:
                print(f"\n任务ID: {task_id}", file=sys.stderr)
    
    elif args.command == 'query':
        if args.poll:
            # Phase 3：轮询模式（乐观同步路径），含完整工作流（支付、下载、.sent 防重复）
            result = api.poll_until_complete(
                project_id=args.project_id,
                interval=args.interval
            )
            print_response(result, args.pretty)
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            if code != 0 and code != 200:
                sys.exit(1)
        else:
            # 单次查询（供 cron 使用）
            result = api.query_progress(args.project_id)
            # 单次查询也加 .sent 防重复
            data = result.get("data", {}) if result else {}
            status = data.get("status", "")
            # 自动支付：价格算出来后 pay_status 变 pending，直接付款无需 agent 介入
            pay_status = data.get("pay_status", "")
            if pay_status == "pending":
                pay_r = api.pay(
                    project_id=args.project_id,
                    video_first_model="grok",
                    video_second_model="seedance15-pro",
                    image_first_model="seedream45"
                )
                pay_code = pay_r.get("code")
                if isinstance(pay_code, str):
                    pay_code = int(pay_code) if pay_code.isdigit() else 0
                if pay_code == 200:
                    price = pay_r.get("data", {}).get("price", 0)
                    print_response({"code": 200, "status": "running", "msg": f"已自动支付 {price} 积分，视频继续生成中"}, args.pretty)
                else:
                    print_response({"code": pay_code, "status": "pay_failed", "msg": "积分不足，请充值后重试"}, args.pretty)
                    sys.exit(1)
                sys.exit(0)
            if status == "completed":
                video_asset = data.get("video_asset", {})
                if video_asset and video_asset.get("download_url"):
                    if api._check_sent(args.project_id):
                        print_response({
                            "code": 200,
                            "status": "already_sent",
                            "msg": "结果已推送，跳过重复发送",
                            "data": {"project_id": args.project_id}
                        }, args.pretty)
                    else:
                        api._mark_sent(args.project_id)
                        # CloudFront 签名中 ~ 须编码为 %7E，否则飞书等平台会截断 URL
                        if result.get("data", {}).get("video_asset", {}).get("signed_url"):
                            result["data"]["video_asset"]["signed_url"] = result["data"]["video_asset"]["signed_url"].replace("~", "%7E")
                        print_response(result, args.pretty)
                    # exit(0) 隐式：完成或已发送
                else:
                    # completed 但视频未就绪，视为进行中
                    print_response(result, args.pretty)
                    sys.exit(0)
            elif status in ("failed", "error") or (result and result.get("code") == -1):
                print_response(result, args.pretty)
                sys.exit(1)  # 失败
            else:
                print_response(result, args.pretty)
                sys.exit(0)  # 进行中
    
    elif args.command == 'pay':
        result = api.pay(
            project_id=args.project_id,
            video_first_model=args.video_first_model,
            video_second_model=args.video_second_model,
            image_first_model=args.image_first_model
        )
        print_response(result, args.pretty)
        
        # 兼容不同的响应格式：code可能是字符串"200"或数字200
        code = result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        
        if code == 0 or code == 200:
            data = result.get("data", {})
            order_id = data.get("order_id")
            price = data.get("price")
            if order_id:
                print(f"\n项目ID: {order_id}, 消耗积分: {price}", file=sys.stderr)
    
    elif args.command == 'styles':
        result = api.get_styles(page=args.page, page_size=args.page_size, language=args.language)
        
        if args.table:
            # 表格形式输出
            code = result.get("code")
            if isinstance(code, str):
                code = int(code) if code.isdigit() else 0
            
            if code == 0 or code == 200:
                data = result.get("data", {})
                styles = data.get("list", [])
                
                if styles:
                    print(f"\n{'ID':<8} {'名称':<20} {'分类':<15} {'描述':<50}", file=sys.stderr)
                    print("-" * 95, file=sys.stderr)
                    for style in styles:
                        style_id = style.get("id", "")
                        name = style.get("name", "")[:18]
                        category = style.get("category", "")[:13]
                        description = style.get("description", "")[:48]
                        print(f"{style_id:<8} {name:<20} {category:<15} {description:<50}", file=sys.stderr)
                    
                    pagination = data.get("pagination", {})
                    total = pagination.get("total", 0)
                    print(f"\n总计: {total} 个风格", file=sys.stderr)
                else:
                    print("未找到风格列表", file=sys.stderr)
            else:
                print_response(result, args.pretty)
        else:
            print_response(result, args.pretty)
    
    elif args.command == 'start':
        # Phase 1：快速创建项目并提交任务
        result = api.create_and_submit(
            diy_story=args.diy_story,
            aspect=args.aspect,
            project_name=args.project_name,
            video_duration=args.video_duration,
            style_id=args.style_id if hasattr(args, 'style_id') and args.style_id is not None else None
        )
        print_response(result, args.pretty)
        code = result.get("code")
        if isinstance(code, str):
            code = int(code) if code.isdigit() else 0
        if code != 0 and code != 200:
            sys.exit(1)

    elif args.command == 'workflow':
        result = api.execute_workflow(
            diy_story=args.diy_story,
            aspect=args.aspect,
            project_name=args.project_name,
            video_duration=args.video_duration,
            style_id=args.style_id if hasattr(args, 'style_id') and args.style_id is not None else None
        )
        print_response(result, args.pretty)


if __name__ == '__main__':
    main()
