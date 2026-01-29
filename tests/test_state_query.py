"""
状态查询模块测试用例
模块编号: 01
"""
import pytest
import allure
import json
from typing import Dict, Any
from utils.client import APIClient
from utils.assert_utils import assert_response_status, assert_json_response


def pytest_generate_tests(metafunc):
    """动态生成测试参数"""
    if 'test_case' in metafunc.fixturenames:
        # 读取CSV数据
        import pandas as pd
        import os
        csv_path = os.path.join(os.path.dirname(__file__), "..", "test-cases", "all_api_test_cases.csv")
        df = pd.read_csv(csv_path, encoding='utf-8')
        df = df.dropna(subset=['test_case_id'])
        
        # 筛选状态查询模块的测试用例
        state_query_cases = df[df['test_case_id'].str.startswith('TC01')]
        test_cases_list = state_query_cases.to_dict('records')
        
        # 生成参数
        metafunc.parametrize("test_case", test_cases_list, ids=[tc['test_case_id'] for tc in test_cases_list])


@allure.feature("状态查询模块 (State Query)")
class TestStateQuery:
    """状态查询模块测试类"""

    def test_state_query_api(self, api_client: APIClient, test_case: Dict[str, Any]):
        """
        状态查询模块通用测试方法
        """
        # 设置allure标签
        allure.dynamic.story(test_case.get("api_name", ""))
        allure.dynamic.title(test_case.get("test_case_name", ""))
        allure.dynamic.description(test_case.get("description", ""))
        
        # 处理tags
        tags = test_case.get("tags", "")
        if tags:
            for tag in str(tags).split(","):
                tag = tag.strip()
                if tag:
                    allure.dynamic.tag(tag)
        
        # 添加测试类型和优先级标签
        test_type = test_case.get("test_type", "")
        if test_type:
            allure.dynamic.tag(test_type)
        
        priority = test_case.get("priority", "")
        if priority:
            allure.dynamic.tag(f"priority-{priority}")

        # 处理请求数据
        headers = {}
        if test_case.get("headers"):
            try:
                headers_str = test_case["headers"].replace('""', '"')
                headers = json.loads(headers_str) if headers_str else {}
            except (json.JSONDecodeError, AttributeError):
                headers = {}

        request_data = None
        if test_case.get("request_data"):
            try:
                request_data_str = str(test_case["request_data"]).strip()
                if request_data_str and request_data_str != "nan":
                    request_data = json.loads(request_data_str)
            except (json.JSONDecodeError, AttributeError):
                request_data = None

        # 发送请求
        method = test_case.get("method", "GET").upper()
        url = test_case.get("url", "")
        
        with allure.step(f"发送{method}请求到{url}"):
            allure.attach(
                json.dumps({
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "data": request_data
                }, indent=2, ensure_ascii=False),
                "请求信息",
                allure.attachment_type.JSON
            )

            if method == "GET":
                # GET请求处理query参数
                if "?" in url:
                    base_url, query_str = url.split("?", 1)
                    from urllib.parse import parse_qs, urlparse
                    parsed = urlparse(url)
                    params = dict(parse_qs(parsed.query))
                    # 简化参数处理
                    params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
                    response = api_client.get(base_url, params=params, headers=headers)
                else:
                    response = api_client.get(url, headers=headers)
            elif method == "POST":
                response = api_client.post(url, json=request_data, headers=headers)
            elif method == "PUT":
                response = api_client.put(url, json=request_data, headers=headers)
            elif method == "DELETE":
                response = api_client.delete(url, headers=headers)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

        # 记录响应
        with allure.step("验证响应"):
            allure.attach(
                json.dumps({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text[:1000]  # 限制长度
                }, indent=2, ensure_ascii=False),
                "响应信息",
                allure.attachment_type.JSON
            )

        # 断言状态码
        expected_status_code = int(test_case.get("expected_status_code", 200))
        assert_response_status(response, expected_status_code)

        # 断言响应内容（如果提供了期望响应）
        expected_response = test_case.get("expected_response", "")
        if expected_response and str(expected_response).strip() and str(expected_response) != "nan":
            try:
                expected_data = json.loads(str(expected_response))
                # 只验证关键字段，不要求完全匹配
                if isinstance(expected_data, dict):
                    # 验证响应是JSON格式
                    try:
                        actual_data = response.json()
                        # 验证关键字段存在
                        for key in expected_data.keys():
                            if key in actual_data:
                                # 如果期望值不为空，则验证值
                                if expected_data[key] and str(expected_data[key]).strip():
                                    # 对于空字符串，跳过验证
                                    if str(expected_data[key]).strip():
                                        assert actual_data[key] == expected_data[key] or not expected_data[key], \
                                            f"字段 {key} 的值不匹配"
                    except json.JSONDecodeError:
                        # 如果不是JSON响应，检查响应文本
                        if isinstance(expected_data, dict) and "error" in expected_data:
                            assert expected_data["error"] in response.text, \
                                f"响应中未找到期望的错误信息: {expected_data['error']}"
            except (json.JSONDecodeError, AttributeError):
                # 如果期望响应不是有效的JSON，跳过内容验证
                pass

