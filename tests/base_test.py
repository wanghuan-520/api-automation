"""
测试用例基类
===========

提供通用的测试用例基类，包含常用的测试方法和工具。
"""

import pytest
import allure
from typing import Optional
from utils.client import APIClient
from config.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class BaseAPITest:
    """
    API 测试用例基类
    
    提供通用的测试方法和工具，所有测试类应继承此类。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient, config: ConfigManager):
        """
        自动设置测试环境
        
        为每个测试用例自动注入 api_client 和 config
        """
        self.api_client = api_client
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def assert_success_response(
        self, 
        response, 
        expected_code: Optional[str] = None,
        expected_status: int = 200
    ) -> dict:
        """
        断言成功响应
        
        Args:
            response: 响应对象
            expected_code: 期望的业务状态码（可选）
            expected_status: 期望的HTTP状态码（默认200）
        
        Returns:
            响应数据字典
        
        Raises:
            AssertionError: 当响应不符合预期时
        """
        assert response.status_code == expected_status, \
            f"Expected status code {expected_status}, but got {response.status_code}"
        
        try:
            data = response.json()
        except Exception as e:
            raise AssertionError(f"Response is not valid JSON: {e}")
        
        # 如果指定了业务状态码，则验证
        if expected_code is not None:
            if isinstance(data, dict) and 'code' in data:
                assert data['code'] == expected_code or data['code'] in [expected_code] if isinstance(expected_code, str) else expected_code, \
                    f"Expected code {expected_code}, but got {data.get('code')}"
        
        return data
    
    def assert_error_response(
        self, 
        response, 
        expected_status: int = 400,
        expected_message: Optional[str] = None
    ) -> dict:
        """
        断言错误响应
        
        Args:
            response: 响应对象
            expected_status: 期望的HTTP状态码（默认400）
            expected_message: 期望的错误消息（可选）
        
        Returns:
            响应数据字典
        
        Raises:
            AssertionError: 当响应不符合预期时
        """
        assert response.status_code == expected_status, \
            f"Expected status code {expected_status}, but got {response.status_code}"
        
        try:
            data = response.json()
        except Exception:
            # 如果不是JSON，返回文本
            return {'error': response.text}
        
        # 如果指定了错误消息，则验证
        if expected_message is not None:
            if isinstance(data, dict):
                message = data.get('message') or data.get('error') or ''
                assert expected_message in message, \
                    f"Expected error message containing '{expected_message}', but got '{message}'"
        
        return data
    
    def assert_response_contains(
        self, 
        response, 
        expected_keys: list,
        data_path: Optional[str] = None
    ) -> None:
        """
        断言响应包含指定的键
        
        Args:
            response: 响应对象
            expected_keys: 期望的键列表
            data_path: 数据路径（如 'data.items'），如果为None则检查根级别
        
        Raises:
            AssertionError: 当响应不包含期望的键时
        """
        try:
            data = response.json()
        except Exception as e:
            raise AssertionError(f"Response is not valid JSON: {e}")
        
        # 如果指定了数据路径，则导航到该路径
        if data_path:
            keys = data_path.split('.')
            for key in keys:
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    raise AssertionError(f"Data path '{data_path}' not found in response")
        
        # 验证所有期望的键都存在
        missing_keys = []
        for key in expected_keys:
            if isinstance(data, dict) and key not in data:
                missing_keys.append(key)
        
        if missing_keys:
            raise AssertionError(f"Response missing keys: {', '.join(missing_keys)}")
    
    def log_request(self, method: str, endpoint: str, **kwargs) -> None:
        """
        记录请求信息（用于Allure报告）
        
        Args:
            method: HTTP方法
            endpoint: API端点
            **kwargs: 其他请求参数
        """
        allure.attach(
            f"{method} {endpoint}\n\nParameters: {kwargs}",
            name="Request",
            attachment_type=allure.attachment_type.TEXT
        )
    
    def log_response(self, response) -> None:
        """
        记录响应信息（用于Allure报告）
        
        Args:
            response: 响应对象
        """
        try:
            response_text = response.text[:1000]  # 限制长度
        except:
            response_text = str(response)
        
        allure.attach(
            f"Status: {response.status_code}\n\nResponse: {response_text}",
            name="Response",
            attachment_type=allure.attachment_type.TEXT
        )

