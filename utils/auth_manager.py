#!/usr/bin/env python3
"""
认证管理器 - 支持邮箱登录优先
支持多种认证方式：邮箱密码登录、client_credentials
"""

import os
import yaml
import time
import json
import requests
from typing import Dict, Any, Optional
from pathlib import Path

class AuthManager:
    """认证管理器"""
    
    def __init__(self, config_path: str = "config/auth_config.yaml"):
        """初始化认证管理器"""
        self.config_path = config_path
        self.config = self._load_config()
        self.token_cache_file = self.config.get("auth", {}).get("token_cache", {}).get("cache_file", ".token_cache")
        self.cached_token = None
        self.token_expire_time = 0
        
        # 邮箱登录配置
        self.email_login_config = {
            "auth_url": "https://auth-pre-station-staging.aevatar.ai/connect/token",
            "client_id": "AevatarAuthServer",
            "apple_app_id": "com.gpt.god",
            "scope": "Aevatar offline_access",
            "email": os.getenv("TEST_EMAIL", "test@example.com"),
            "password": os.getenv("TEST_PASSWORD", "Test123456!")
        }
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"认证配置文件不存在: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"认证配置文件格式错误: {e}")
            return {}
    
    def _get_client_credentials(self) -> tuple:
        """获取客户端凭据"""
        client_id_env = self.config.get("auth", {}).get("client_id_env", "AUTH_CLIENT_ID")
        client_secret_env = self.config.get("auth", {}).get("client_secret_env", "AUTH_CLIENT_SECRET")
        
        client_id = os.getenv(client_id_env)
        client_secret = os.getenv(client_secret_env)
        
        if not client_id or not client_secret:
            raise ValueError(f"环境变量 {client_id_env} 或 {client_secret_env} 未设置")
        
        return client_id, client_secret
    
    def _load_cached_token(self) -> Optional[Dict]:
        """加载缓存的token"""
        try:
            if os.path.exists(self.token_cache_file):
                with open(self.token_cache_file, 'r') as f:
                    cached_data = json.load(f)
                    
                # 检查token是否过期
                expire_time = cached_data.get("expire_time", 0)
                if time.time() < expire_time:
                    return cached_data
                else:
                    print("缓存的Token已过期")
        except Exception as e:
            print(f"加载缓存Token失败: {e}")
        
        return None
    
    def _save_token_cache(self, token_data: Dict):
        """保存token到缓存"""
        try:
            # 计算过期时间
            expires_in = token_data.get("expires_in", 3600)
            expire_before = self.config.get("auth", {}).get("token_cache", {}).get("expire_before", 300)
            expire_time = time.time() + expires_in - expire_before
            
            cache_data = {
                "access_token": token_data.get("access_token"),
                "token_type": token_data.get("token_type"),
                "expires_in": expires_in,
                "expire_time": expire_time,
                "auth_method": token_data.get("auth_method", "unknown")
            }
            
            with open(self.token_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            print("Token缓存已保存")
        except Exception as e:
            print(f"保存Token缓存失败: {e}")
    
    def _get_token_via_email_login(self) -> Optional[Dict]:
        """通过邮箱登录获取token"""
        try:
            print("尝试邮箱登录获取Token")
            
            login_data = {
                "grant_type": "password",
                "client_id": self.email_login_config["client_id"],
                "apple_app_id": self.email_login_config["apple_app_id"],
                "scope": self.email_login_config["scope"],
                "username": self.email_login_config["email"],
                "password": self.email_login_config["password"]
            }
            
            headers = {
                'accept': 'application/json',
                'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://godgpt-ui-testnet.aelf.dev',
                'pragma': 'no-cache',
                'referer': 'https://godgpt-ui-testnet.aelf.dev/',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
            }
            
            response = requests.post(
                self.email_login_config["auth_url"],
                data=login_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                token_data["auth_method"] = "email_login"
                print("邮箱登录Token获取成功")
                return token_data
            else:
                print(f"邮箱登录失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"邮箱登录异常: {e}")
            return None
    
    def _get_token_via_client_credentials(self) -> Optional[Dict]:
        """通过客户端凭据获取token"""
        try:
            print("尝试客户端凭据获取Token")
            
            client_id, client_secret = self._get_client_credentials()
            
            token_url = self.config.get("auth", {}).get("token_url")
            if not token_url:
                raise ValueError("认证服务器URL未配置")
            
            data = {
                "grant_type": "client_credentials",
                "scope": self.config.get("auth", {}).get("scope", "Aevatar"),
                "client_id": client_id,
                "client_secret": client_secret
            }
            
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            response = requests.post(token_url, data=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                token_data["auth_method"] = "client_credentials"
                print("客户端凭据Token获取成功")
                return token_data
            else:
                print(f"客户端凭据认证失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"客户端凭据认证异常: {e}")
            return None
    
    def get_token(self) -> Optional[str]:
        """获取访问token，优先使用邮箱登录"""
        
        # 1. 尝试加载缓存的token
        cached_data = self._load_cached_token()
        if cached_data:
            self.cached_token = cached_data.get("access_token")
            self.token_expire_time = cached_data.get("expire_time", 0)
            auth_method = cached_data.get("auth_method", "unknown")
            print(f"使用缓存的Token (认证方式: {auth_method})")
            return self.cached_token
        
        # 2. 尝试邮箱登录获取token
        print("缓存中没有有效Token，尝试邮箱登录")
        token_data = self._get_token_via_email_login()
        
        # 3. 如果邮箱登录失败，尝试客户端凭据
        if not token_data:
            print("邮箱登录失败，尝试客户端凭据认证")
            token_data = self._get_token_via_client_credentials()
        
        # 4. 如果都失败了，返回None
        if not token_data:
            print("所有认证方式都失败了")
            return None
        
        # 5. 保存token到缓存
        self._save_token_cache(token_data)
        
        self.cached_token = token_data.get("access_token")
        self.token_expire_time = time.time() + token_data.get("expires_in", 3600)
        
        auth_method = token_data.get("auth_method", "unknown")
        print(f"Token获取成功 (认证方式: {auth_method})")
        return self.cached_token
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        token = self.get_token()
        if not token:
            raise ValueError("无法获取访问token")
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def refresh_token(self) -> bool:
        """刷新token"""
        try:
            # 清除缓存
            if os.path.exists(self.token_cache_file):
                os.remove(self.token_cache_file)
            
            # 重新获取token
            token = self.get_token()
            return token is not None
            
        except Exception as e:
            print(f"刷新Token失败: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """检查token是否有效"""
        if not self.cached_token:
            return False
        
        # 检查是否接近过期
        current_time = time.time()
        return current_time < self.token_expire_time

# 全局认证管理器实例
_auth_manager = None

def get_auth_manager() -> AuthManager:
    """获取全局认证管理器实例"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager 