"""
测试辅助工具类
==================
提供公共的测试方法、认证管理、请求头优化等功能
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os

@dataclass
class TestConfig:
    """测试配置类"""
    base_url: str = "https://station-developer-staging.aevatar.ai/godgpt-client/api"
    auth_url: str = "https://auth-pre-station-staging.aevatar.ai/connect/token"
    test_email: str = os.getenv("TEST_EMAIL", "test@example.com")
    test_password: str = os.getenv("TEST_PASSWORD", "Test123456!")
    origin: str = "https://godgpt-ui-testnet.aelf.dev"
    referer: str = "https://godgpt-ui-testnet.aelf.dev/"

class TestHelper:
    """测试辅助工具类"""
    
    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.access_token = None
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    
    def get_auth_token(self) -> Optional[str]:
        """获取认证token"""
        if self.access_token:
            return self.access_token
            
        login_data = {
            "grant_type": "password",
            "client_id": "AevatarAuthServer",
            "apple_app_id": "com.gpt.god",
            "scope": "Aevatar offline_access",
            "username": self.config.test_email,
            "password": self.config.test_password
        }
        
        headers = self.get_auth_headers()
        
        try:
            response = requests.post(
                self.config.auth_url,
                data=login_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                self.access_token = response_data["access_token"]
                print(f"✅ 成功获取认证token: {self.access_token[:20]}...")
                return self.access_token
            else:
                print(f"❌ 获取认证token失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"获取认证token异常: {e}")
            return None
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证请求头"""
        return {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': self.config.origin,
            'pragma': 'no-cache',
            'referer': self.config.referer,
            'user-agent': self.user_agent
        }
    
    def get_api_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """获取API请求头 - 优化版本，移除不必要的浏览器相关headers"""
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': self.config.origin,
            'pragma': 'no-cache',
            'referer': self.config.referer,
            'user-agent': self.user_agent
        }
        
        if include_auth and self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        return headers
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    params: Dict = None, headers: Dict = None, 
                    timeout: int = 30) -> requests.Response:
        """统一的请求方法"""
        url = f"{self.config.base_url}{endpoint}"
        
        if headers is None:
            headers = self.get_api_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
            
        except Exception as e:
            print(f"请求异常: {e}")
            raise
    
    def create_session(self, title: str = "Test Session", session_type: str = "chat") -> Optional[str]:
        """创建会话"""
        session_data = {
            "title": title,
            "type": session_type
        }
        
        response = self.make_request('POST', '/godgpt/create-session', data=session_data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data["code"] == "20000":
                # 处理不同的响应数据格式
                if isinstance(response_data["data"], dict):
                    return response_data["data"]["sessionId"]
                elif isinstance(response_data["data"], str):
                    return response_data["data"]
                else:
                    print(f"意外的会话数据格式: {response_data['data']}")
                    return None
            else:
                print(f"创建会话失败: {response_data}")
                return None
        else:
            print(f"创建会话请求失败: {response.status_code}")
            return None
    
    def create_guest_session(self, device_id: str = "test_device") -> Optional[Dict]:
        """创建访客会话"""
        guest_data = {
            "deviceId": device_id,
            "userAgent": "Mozilla/5.0 (Test Browser)"
        }
        
        response = self.make_request('POST', '/godgpt/guest/create-session', data=guest_data)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data["code"] == "20000":
                return response_data["data"]
            else:
                print(f"创建访客会话失败: {response_data}")
                return None
        else:
            print(f"创建访客会话请求失败: {response.status_code}")
            return None
    
    def validate_response(self, response: requests.Response, expected_status: int = 200) -> bool:
        """验证响应状态"""
        if response.status_code != expected_status:
            print(f"响应状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}")
            return False
        return True
    
    def validate_json_response(self, response: requests.Response, required_fields: List[str] = None) -> Dict:
        """验证JSON响应格式"""
        try:
            response_data = response.json()
            
            if required_fields:
                for field in required_fields:
                    if field not in response_data:
                        print(f"响应缺少必要字段: {field}")
                        return None
            
            return response_data
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
    
    def wait_for_condition(self, condition_func, timeout: int = 30, interval: float = 1.0) -> bool:
        """等待条件满足"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False
    
    def generate_test_data(self, data_type: str, **kwargs) -> Dict:
        """生成测试数据"""
        if data_type == "email":
            timestamp = int(time.time())
            return {"emailAddress": f"test_{timestamp}@example.com"}
        elif data_type == "session":
            return {
                "title": f"Test Session {int(time.time())}",
                "type": "chat"
            }
        elif data_type == "chat":
            return {
                "message": f"Test message {int(time.time())}",
                "sessionId": kwargs.get("sessionId", "test_session"),
                "stream": False
            }
        elif data_type == "voice":
            return {
                "audioData": "base64_encoded_audio_data",
                "sessionId": kwargs.get("sessionId", "test_session"),
                "format": "wav"
            }
        else:
            return {}
    
    def cleanup_test_data(self, session_ids: List[str] = None):
        """清理测试数据"""
        if session_ids:
            for session_id in session_ids:
                try:
                    self.make_request('DELETE', f'/godgpt/chat/{session_id}')
                    print(f"🧹 清理会话: {session_id}")
                except Exception as e:
                    print(f"清理会话失败 {session_id}: {e}")

# 全局测试助手实例
test_helper = TestHelper() 