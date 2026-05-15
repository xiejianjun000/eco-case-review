"""
消息平台网关模块 - 支持飞书、钉钉、企业微信等平台
"""
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
import httpx
import hashlib
import base64
from urllib.parse import quote


class MessageGateway:
    """消息平台网关 - 支持多平台消息发送"""
    
    def __init__(self):
        self.clients = {
            'feishu': FeishuClient(),
            'dingtalk': DingTalkClient(),
            'wecom': WeComClient()
        }
    
    async def send_message(self, platform: str, message: str, to: str = None):
        """
        发送消息到指定平台
        
        Args:
            platform: 平台名称 (feishu/dingtalk/wecom)
            message: 消息内容
            to: 接收者（可选）
        
        Returns:
            发送结果
        """
        if platform not in self.clients:
            raise ValueError(f"不支持的平台: {platform}")
        
        client = self.clients[platform]
        return await client.send_message(message, to)
    
    async def send_report(self, platform: str, report_path: str, to: str = None):
        """
        发送报告到指定平台
        
        Args:
            platform: 平台名称
            report_path: 报告文件路径
            to: 接收者
        
        Returns:
            发送结果
        """
        if platform not in self.clients:
            raise ValueError(f"不支持的平台: {platform}")
        
        client = self.clients[platform]
        return await client.send_file(report_path, to)


class FeishuClient:
    """飞书客户端"""
    
    def __init__(self):
        self.base_url = "https://open.feishu.cn/open-apis"
        self.app_id = None
        self.app_secret = None
        self.bot_token = None
        self.access_token = None
        self.token_expire_time = 0
    
    async def _get_token(self) -> str:
        """获取访问令牌"""
        now = datetime.now().timestamp()
        if self.access_token and now < self.token_expire_time:
            return self.access_token
        
        if not self.app_id or not self.app_secret:
            raise ValueError("飞书 App ID 和 App Secret 未配置")
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal/"
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            self.access_token = result['tenant_access_token']
            self.token_expire_time = now + result['expire'] - 60
        
        return self.access_token
    
    async def send_message(self, message: str, to: str = None) -> Dict[str, Any]:
        """发送文本消息"""
        try:
            token = await self._get_token()
            
            url = f"{self.base_url}/im/v1/messages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "receive_id": to or "oc_xxxxxx",
                "content": json.dumps({
                    "text": message
                }),
                "msg_type": "text"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"飞书消息发送失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_file(self, file_path: str, to: str = None) -> Dict[str, Any]:
        """发送文件"""
        try:
            # 先上传文件
            token = await self._get_token()
            
            # 上传文件
            upload_url = f"{self.base_url}/im/v1/files"
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            with open(file_path, 'rb') as f:
                files = {"file": ("report.md", f, "text/markdown")}
                async with httpx.AsyncClient() as client:
                    response = await client.post(upload_url, headers=headers, files=files)
                    response.raise_for_status()
                    file_key = response.json()['data']['file_key']
            
            # 发送文件消息
            send_url = f"{self.base_url}/im/v1/messages"
            data = {
                "receive_id": to or "oc_xxxxxx",
                "content": json.dumps({
                    "file_key": file_key
                }),
                "msg_type": "file"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(send_url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"飞书文件发送失败: {e}")
            return {"success": False, "error": str(e)}


class DingTalkClient:
    """钉钉客户端"""
    
    def __init__(self):
        self.base_url = "https://oapi.dingtalk.com"
        self.robot_token = None
        self.app_key = None
        self.app_secret = None
    
    async def send_message(self, message: str, to: str = None) -> Dict[str, Any]:
        """发送文本消息"""
        try:
            if not self.robot_token:
                raise ValueError("钉钉机器人 Token 未配置")
            
            url = f"{self.base_url}/robot/send?access_token={self.robot_token}"
            
            data = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"钉钉消息发送失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_file(self, file_path: str, to: str = None) -> Dict[str, Any]:
        """发送文件"""
        try:
            if not self.robot_token:
                raise ValueError("钉钉机器人 Token 未配置")
            
            # 钉钉机器人不支持直接发送文件，需要通过钉盘
            # 这里简化处理，发送文件路径消息
            message = f"评查报告已生成：{file_path}"
            return await self.send_message(message, to)
                
        except Exception as e:
            logger.error(f"钉钉文件发送失败: {e}")
            return {"success": False, "error": str(e)}


class WeComClient:
    """企业微信客户端"""
    
    def __init__(self):
        self.base_url = "https://qyapi.weixin.qq.com/cgi-bin"
        self.corpid = None
        self.corpsecret = None
        self.agentid = None
        self.access_token = None
        self.token_expire_time = 0
    
    async def _get_token(self) -> str:
        """获取访问令牌"""
        now = datetime.now().timestamp()
        if self.access_token and now < self.token_expire_time:
            return self.access_token
        
        if not self.corpid or not self.corpsecret:
            raise ValueError("企业微信 CorpID 和 CorpSecret 未配置")
        
        url = f"{self.base_url}/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            
            self.access_token = result['access_token']
            self.token_expire_time = now + result['expires_in'] - 60
        
        return self.access_token
    
    async def send_message(self, message: str, to: str = None) -> Dict[str, Any]:
        """发送文本消息"""
        try:
            token = await self._get_token()
            
            url = f"{self.base_url}/message/send?access_token={token}"
            
            data = {
                "touser": to or "@all",
                "agentid": self.agentid or 1000001,
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"企业微信消息发送失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_file(self, file_path: str, to: str = None) -> Dict[str, Any]:
        """发送文件"""
        try:
            token = await self._get_token()
            
            # 先上传临时素材
            upload_url = f"{self.base_url}/media/upload?access_token={token}&type=file"
            
            with open(file_path, 'rb') as f:
                files = {"media": ("report.md", f)}
                async with httpx.AsyncClient() as client:
                    response = await client.post(upload_url, files=files)
                    response.raise_for_status()
                    media_id = response.json()['media_id']
            
            # 发送文件消息
            send_url = f"{self.base_url}/message/send?access_token={token}"
            data = {
                "touser": to or "@all",
                "agentid": self.agentid or 1000001,
                "msgtype": "file",
                "file": {
                    "media_id": media_id
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(send_url, json=data)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"企业微信文件发送失败: {e}")
            return {"success": False, "error": str(e)}


# 全局实例
message_gateway = MessageGateway()
