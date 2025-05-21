import json
from typing import Any, Dict, List, Union
import requests

def assert_response_status(response: requests.Response, expected_status: int) -> None:
    """断言响应状态码"""
    assert response.status_code == expected_status, \
        f"Expected status code {expected_status}, but got {response.status_code}"

def assert_json_response(response: requests.Response, expected_data: Dict[str, Any]) -> None:
    """断言JSON响应内容"""
    try:
        response_data = response.json()
    except json.JSONDecodeError:
        raise AssertionError("Response is not valid JSON")
    
    for key, value in expected_data.items():
        assert key in response_data, f"Key '{key}' not found in response"
        assert response_data[key] == value, \
            f"Expected {key}={value}, but got {key}={response_data[key]}"

def assert_response_contains(response: requests.Response, expected_text: str) -> None:
    """断言响应包含特定文本"""
    assert expected_text in response.text, \
        f"Expected text '{expected_text}' not found in response"

def assert_list_length(response: requests.Response, expected_length: int) -> None:
    """断言响应中的列表长度"""
    try:
        data = response.json()
        assert isinstance(data, list), "Response is not a list"
        assert len(data) == expected_length, \
            f"Expected list length {expected_length}, but got {len(data)}"
    except json.JSONDecodeError:
        raise AssertionError("Response is not valid JSON") 