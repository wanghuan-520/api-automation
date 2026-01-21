"""
通用API测试用例模板
=================

这是一个通用的API测试用例模板，可以作为创建新测试用例的起点。

使用方法：
1. 复制此文件到 tests/ 目录下
2. 重命名为 test_<your_api>_api.py
3. 根据实际API修改测试用例
"""

import pytest
import allure
from tests.base_test import BaseAPITest
from tests.adapters import get_business_adapter


@allure.feature('API测试')
class TestGenericAPI(BaseAPITest):
    """
    通用API测试类
    
    这是一个模板类，展示了如何编写API测试用例。
    """
    
    @pytest.fixture(autouse=True)
    def setup_adapter(self):
        """设置业务适配器"""
        self.adapter = get_business_adapter()
    
    @allure.story('获取资源列表')
    def test_get_resource_list(self):
        """
        测试获取资源列表
        
        这是一个示例测试用例，展示如何测试GET接口
        """
        # 1. 准备测试数据
        endpoint = "/api/resources"
        params = {
            'page': 1,
            'pageSize': 10
        }
        
        # 2. 发送请求
        self.log_request('GET', endpoint, params=params)
        response = self.api_client.get(endpoint, params=params)
        self.log_response(response)
        
        # 3. 断言响应
        data = self.assert_success_response(response, expected_status=200)
        
        # 4. 验证响应结构
        self.assert_response_contains(response, ['items', 'total'])
        
        # 5. 验证业务逻辑
        assert isinstance(data.get('items'), list), "items should be a list"
        assert data.get('total') >= 0, "total should be non-negative"
    
    @allure.story('创建资源')
    def test_create_resource(self):
        """
        测试创建资源
        
        这是一个示例测试用例，展示如何测试POST接口
        """
        # 1. 准备测试数据
        endpoint = "/api/resources"
        request_data = {
            'name': 'Test Resource',
            'description': 'This is a test resource'
        }
        
        # 2. 发送请求
        self.log_request('POST', endpoint, json=request_data)
        response = self.api_client.post(endpoint, json=request_data)
        self.log_response(response)
        
        # 3. 断言响应
        data = self.assert_success_response(response, expected_status=201)
        
        # 4. 验证响应数据
        assert 'id' in data, "Response should contain resource id"
        assert data.get('name') == request_data['name'], "Resource name should match"
    
    @allure.story('更新资源')
    def test_update_resource(self, test_resource_id: str):
        """
        测试更新资源
        
        这是一个示例测试用例，展示如何测试PUT接口
        
        Args:
            test_resource_id: 测试资源ID（需要先创建）
        """
        # 1. 准备测试数据
        endpoint = f"/api/resources/{test_resource_id}"
        request_data = {
            'name': 'Updated Resource',
            'description': 'This is an updated resource'
        }
        
        # 2. 发送请求
        self.log_request('PUT', endpoint, json=request_data)
        response = self.api_client.put(endpoint, json=request_data)
        self.log_response(response)
        
        # 3. 断言响应
        data = self.assert_success_response(response, expected_status=200)
        
        # 4. 验证更新结果
        assert data.get('name') == request_data['name'], "Resource name should be updated"
    
    @allure.story('删除资源')
    def test_delete_resource(self, test_resource_id: str):
        """
        测试删除资源
        
        这是一个示例测试用例，展示如何测试DELETE接口
        
        Args:
            test_resource_id: 测试资源ID
        """
        # 1. 准备测试数据
        endpoint = f"/api/resources/{test_resource_id}"
        
        # 2. 发送请求
        self.log_request('DELETE', endpoint)
        response = self.api_client.delete(endpoint)
        self.log_response(response)
        
        # 3. 断言响应
        self.assert_success_response(response, expected_status=204)
    
    @allure.story('错误处理')
    def test_error_handling(self):
        """
        测试错误处理
        
        这是一个示例测试用例，展示如何测试错误场景
        """
        # 1. 测试不存在的资源
        endpoint = "/api/resources/non-existent-id"
        
        # 2. 发送请求
        response = self.api_client.get(endpoint, raise_on_error=False)
        
        # 3. 断言错误响应
        self.assert_error_response(response, expected_status=404)
    
    @allure.story('业务逻辑测试')
    def test_business_logic(self):
        """
        测试业务逻辑
        
        这是一个示例测试用例，展示如何使用业务适配器
        """
        # 1. 使用业务适配器执行业务操作
        if hasattr(self.adapter, 'compile_artifact'):
            success = self.adapter.compile_artifact('test-artifact')
            assert success, "Artifact compilation should succeed"
        
        # 2. 验证业务结果
        # ... 你的业务验证逻辑


# ============================================
# 测试数据 Fixtures
# ============================================

@pytest.fixture
def test_resource_id(api_client, clean_test_data):
    """
    创建测试资源并返回ID
    
    测试结束后自动清理
    """
    # 创建测试资源
    response = api_client.post(
        "/api/resources",
        json={
            'name': 'Test Resource',
            'description': 'Auto-created test resource'
        }
    )
    
    data = response.json()
    resource_id = data.get('id')
    
    # 记录到清理列表
    clean_test_data.append(resource_id)
    
    return resource_id

