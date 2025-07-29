#!/usr/bin/env python3
"""
API客户端
支持自动认证的HTTP客户端
"""

import requests
from typing import Dict, Any, Optional

class APIClient:
    """API客户端类"""
    
    def __init__(self, base_url: str, auto_auth: bool = True):
        """初始化API客户端
        
        Args:
            base_url: API基础URL
            auto_auth: 是否自动添加认证头
        """
        self.base_url = base_url.rstrip('/')
        self.auto_auth = auto_auth
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'API-Automation-Test/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _build_url(self, endpoint: str) -> str:
        """构建完整URL"""
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def _get_headers(self, headers: Optional[Dict] = None) -> Dict:
        """获取请求头，自动添加认证"""
        request_headers = {}
        
        # 添加自定义头
        if headers:
            request_headers.update(headers)
            
        return request_headers
    
    def update_auth_headers(self, auth_headers: Dict[str, str]):
        """更新认证头"""
        self.session.headers.update(auth_headers)
    
    def get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, **kwargs):
        """发送GET请求"""
        url = self._build_url(endpoint)
        request_headers = self._get_headers(headers)
        
        return self.session.get(url, params=params, headers=request_headers, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None, 
             headers: Optional[Dict] = None, **kwargs):
        """发送POST请求"""
        url = self._build_url(endpoint)
        request_headers = self._get_headers(headers)
        
        return self.session.post(url, data=data, json=json, headers=request_headers, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None,
            headers: Optional[Dict] = None, **kwargs):
        """发送PUT请求"""
        url = self._build_url(endpoint)
        request_headers = self._get_headers(headers)
        
        return self.session.put(url, data=data, json=json, headers=request_headers, **kwargs)
    
    def delete(self, endpoint: str, headers: Optional[Dict] = None, **kwargs):
        """发送DELETE请求"""
        url = self._build_url(endpoint)
        request_headers = self._get_headers(headers)
        
        return self.session.delete(url, headers=request_headers, **kwargs)
    
    def patch(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None,
              headers: Optional[Dict] = None, **kwargs):
        """发送PATCH请求"""
        url = self._build_url(endpoint)
        request_headers = self._get_headers(headers)
        
        return self.session.patch(url, data=data, json=json, headers=request_headers, **kwargs)
    
    def request(self, method: str, endpoint: str, **kwargs):
        """发送自定义请求"""
        url = self._build_url(endpoint)
        headers = kwargs.pop('headers', {})
        request_headers = self._get_headers(headers)
        kwargs['headers'] = request_headers
        
        return self.session.request(method, url, **kwargs) 