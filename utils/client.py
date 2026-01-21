"""
API 客户端封装
==============

提供统一的 HTTP 请求接口，包含：
- 自动重试机制
- 异常处理
- 超时控制
- 请求/响应日志

使用示例：
    from utils.client import APIClient
    
    client = APIClient(base_url='http://api.example.com', timeout=30)
    response = client.get('/api/users')
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class APIClient:
    """
    API 客户端封装类
    
    提供统一的 HTTP 请求接口，支持：
    - 自动重试（针对临时性错误）
    - 超时控制
    - 异常处理
    - 请求/响应日志
    """
    
    def __init__(
        self, 
        base_url: str, 
        timeout: int = 30, 
        max_retries: int = 3,
        backoff_factor: float = 1.0
    ):
        """
        初始化 API 客户端
        
        Args:
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            backoff_factor: 重试退避因子
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的 HTTP 状态码
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            raise_on_status=False  # 不直接抛出异常，由调用方处理
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 记录最后一次请求和响应（用于调试）
        self.last_request: Optional[requests.PreparedRequest] = None
        self.last_response: Optional[requests.Response] = None
        
        logger.info(f"APIClient initialized: base_url={base_url}, timeout={timeout}, max_retries={max_retries}")
    
    def _build_url(self, endpoint: str) -> str:
        """
        构建完整的 API URL
        
        Args:
            endpoint: API 端点路径
        
        Returns:
            完整的 URL
        """
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def _log_request(self, method: str, url: str, **kwargs) -> None:
        """记录请求信息"""
        logger.debug(f"Request: {method} {url}")
        if 'json' in kwargs:
            logger.debug(f"Request Body: {kwargs['json']}")
        if 'params' in kwargs:
            logger.debug(f"Request Params: {kwargs['params']}")
    
    def _log_response(self, response: requests.Response) -> None:
        """记录响应信息"""
        logger.debug(f"Response: {response.status_code} {response.reason}")
        try:
            # 只记录前500个字符，避免日志过长
            response_text = response.text[:500]
            logger.debug(f"Response Body: {response_text}")
        except Exception:
            pass
    
    def _handle_response(self, response: requests.Response, raise_on_error: bool = True) -> requests.Response:
        """
        统一处理响应
        
        Args:
            response: 响应对象
            raise_on_error: 是否在错误时抛出异常
        
        Returns:
            响应对象
        
        Raises:
            requests.HTTPError: 当 raise_on_error=True 且响应状态码表示错误时
        """
        self.last_response = response
        self._log_response(response)
        
        if raise_on_error:
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(
                    f"HTTP Error: {response.status_code} - {response.reason}\n"
                    f"URL: {response.url}\n"
                    f"Response: {response.text[:500]}"
                )
                raise
        
        return response
    
    def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        raise_on_error: bool = True,
        **kwargs
    ) -> requests.Response:
        """
        发送 GET 请求
        
        Args:
            endpoint: API 端点路径
            params: URL 查询参数
            raise_on_error: 是否在错误时抛出异常
            **kwargs: 其他 requests.get() 支持的参数
        
        Returns:
            响应对象
        
        Raises:
            requests.RequestException: 请求异常
            requests.HTTPError: HTTP 错误（当 raise_on_error=True 时）
        """
        url = self._build_url(endpoint)
        self._log_request('GET', url, params=params, **kwargs)
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                **kwargs
            )
            self.last_request = response.request
            return self._handle_response(response, raise_on_error)
        except requests.Timeout as e:
            logger.error(f"Request timeout: {url}")
            raise
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed: {url} - {e}")
            raise
    
    def post(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None, 
        json: Optional[Dict[str, Any]] = None,
        raise_on_error: bool = True,
        **kwargs
    ) -> requests.Response:
        """
        发送 POST 请求
        
        Args:
            endpoint: API 端点路径
            data: 表单数据
            json: JSON 数据
            raise_on_error: 是否在错误时抛出异常
            **kwargs: 其他 requests.post() 支持的参数
        
        Returns:
            响应对象
        """
        url = self._build_url(endpoint)
        self._log_request('POST', url, json=json, data=data, **kwargs)
        
        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                timeout=self.timeout,
                **kwargs
            )
            self.last_request = response.request
            return self._handle_response(response, raise_on_error)
        except requests.Timeout as e:
            logger.error(f"Request timeout: {url}")
            raise
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed: {url} - {e}")
            raise
    
    def put(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None, 
        json: Optional[Dict[str, Any]] = None,
        raise_on_error: bool = True,
        **kwargs
    ) -> requests.Response:
        """
        发送 PUT 请求
        
        Args:
            endpoint: API 端点路径
            data: 表单数据
            json: JSON 数据
            raise_on_error: 是否在错误时抛出异常
            **kwargs: 其他 requests.put() 支持的参数
        
        Returns:
            响应对象
        """
        url = self._build_url(endpoint)
        self._log_request('PUT', url, json=json, data=data, **kwargs)
        
        try:
            response = self.session.put(
                url,
                data=data,
                json=json,
                timeout=self.timeout,
                **kwargs
            )
            self.last_request = response.request
            return self._handle_response(response, raise_on_error)
        except requests.Timeout as e:
            logger.error(f"Request timeout: {url}")
            raise
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed: {url} - {e}")
            raise
    
    def delete(
        self, 
        endpoint: str,
        raise_on_error: bool = True,
        **kwargs
    ) -> requests.Response:
        """
        发送 DELETE 请求
        
        Args:
            endpoint: API 端点路径
            raise_on_error: 是否在错误时抛出异常
            **kwargs: 其他 requests.delete() 支持的参数
        
        Returns:
            响应对象
        """
        url = self._build_url(endpoint)
        self._log_request('DELETE', url, **kwargs)
        
        try:
            response = self.session.delete(
                url,
                timeout=self.timeout,
                **kwargs
            )
            self.last_request = response.request
            return self._handle_response(response, raise_on_error)
        except requests.Timeout as e:
            logger.error(f"Request timeout: {url}")
            raise
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed: {url} - {e}")
            raise
    
    def close(self) -> None:
        """关闭会话"""
        self.session.close()
        logger.debug("APIClient session closed") 