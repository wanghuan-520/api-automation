import re
import json
from typing import Dict, Any, Optional

class CurlParser:
    @staticmethod
    def parse_curl(curl_command: str) -> Dict[str, Any]:
        """解析 curl 命令，返回请求信息"""
        result = {
            "method": "GET",
            "url": "",
            "headers": {},
            "data": None
        }
        
        # 解析方法
        method_match = re.search(r'-X\s+(\w+)', curl_command)
        if method_match:
            result["method"] = method_match.group(1)
            
        # 解析 URL
        url_match = re.search(r'curl\s+[\'"]?([^\s\'\"]+)', curl_command)
        if url_match:
            result["url"] = url_match.group(1)
            
        # 解析 headers
        header_matches = re.finditer(r'-H\s+[\'"]?([^\'\"]+)[\'"]?', curl_command)
        for match in header_matches:
            header = match.group(1)
            key, value = header.split(':', 1)
            result["headers"][key.strip()] = value.strip()
            
        # 解析请求体
        data_match = re.search(r'-d\s+[\'"]?([^\'\"]+)[\'"]?', curl_command)
        if data_match:
            try:
                result["data"] = json.loads(data_match.group(1))
            except json.JSONDecodeError:
                result["data"] = data_match.group(1)
                
        return result
    
    @staticmethod
    def generate_test_case(curl_file: str) -> str:
        """从 curl 文件生成测试用例代码"""
        with open(curl_file, 'r') as f:
            content = f.read()
            
        # 分离 curl 命令和预期响应
        curl_part = content.split('# Expected Response:')[0].strip()
        expected_response = None
        if '# Expected Response:' in content:
            expected_response = content.split('# Expected Response:')[1].strip()
            try:
                expected_response = json.loads(expected_response)
            except json.JSONDecodeError:
                expected_response = None
                
        # 解析 curl 命令
        request_info = CurlParser.parse_curl(curl_part)
        
        # 生成测试用例代码
        test_case = f"""import pytest
import requests
import json

class Test{request_info['method'].title()}:
    def test_{request_info['url'].split('/')[-1]}(self):
        url = "{request_info['url']}"
        headers = {json.dumps(request_info['headers'], indent=4)}
        data = {json.dumps(request_info['data'], indent=4)}
        
        response = requests.{request_info['method'].lower()}(
            url=url,
            headers=headers,
            json=data
        )
        
        assert response.status_code == 200
        response_data = response.json()
        """
        
        if expected_response:
            test_case += f"""
        # 验证响应数据
        assert response_data['status'] == '{expected_response['status']}'
        assert 'token' in response_data
        assert response_data['user']['username'] == '{expected_response['user']['username']}'
        """
            
        return test_case 