import requests
from typing import Any, Dict, Optional

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        
    def _build_url(self, endpoint: str) -> str:
        """构建完整的API URL"""
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """发送GET请求"""
        url = self._build_url(endpoint)
        return self.session.get(url, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """发送POST请求"""
        url = self._build_url(endpoint)
        return self.session.post(url, data=data, json=json, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """发送PUT请求"""
        url = self._build_url(endpoint)
        return self.session.put(url, data=data, json=json, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        url = self._build_url(endpoint)
        return self.session.delete(url, **kwargs) 