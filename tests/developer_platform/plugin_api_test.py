"""
插件 API 测试文档
================

本测试套件涵盖了插件 API 的完整生命周期操作，包括：
1. 插件列表获取
2. 插件创建
3. 插件更新
4. 插件删除

每个测试用例都设计用于验证成功操作和错误处理场景。

测试用例概览：
============
1. 插件列表操作：
   - 成功获取有效项目的插件列表
   - 处理无效项目 ID 的场景

2. 插件创建操作：
   - 成功创建新插件
   - 处理无效输入数据的场景

3. 插件更新操作：
   - 成功更新现有插件
   - 处理更新不存在插件的场景

4. 插件删除操作：
   - 成功删除现有插件
   - 处理删除不存在插件的场景

环境要求：
============
- ACCESS_TOKEN:API 认证所需
- API_BASE_URL:API 端点的基础 URL(默认为测试环境）

响应码说明：
============
- 20000:成功
- 20001:成功（特定于删除操作）
- 50000:错误
- -1:替代成功码
"""

import pytest
import requests
import os
import logging
import allure
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import sys
import os
import subprocess
import shutil
from pathlib import Path
import platform
import time
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from docs.rules.test_rules import APITestCase, APITestSuite, APITestStatus, APITestResult

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('plugin_test.log')
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 加载环境变量
load_dotenv()

# 定义测试用例类型标记
pytestmark = pytest.mark.plugin_tests

@dataclass
class PluginItem:
    id: str
    name: str
    creationTime: int
    creatorName: str

@dataclass
class PluginResponse:
    code: str
    data: Optional[Dict[str, Union[List[PluginItem], str, int, None]]]
    message: str

@allure.feature('插件API测试')
class TestPluginAPI:
    BASE_URL = os.getenv('API_BASE_URL', 'https://aevatar-station-ui-staging.aevatar.ai/api/plugins')
    TEST_PROJECT_ID = os.getenv('TEST_PROJECT_ID', '4905508f-def5-ff31-f692-3a196ee1455d')
    
    @allure.step('编译并上传DLL文件')
    def compile_and_upload_dll(self, plugin_id: str) -> bool:
        """编译DLL并上传更新插件"""
        try:
            # 1. 编译DLL
            dll_path = "/Users/wanghuan/aelf/LoadTest/Dll/TestGAgent"
            compile_cmd = f"cd {dll_path} && dotnet build TestGAgent.Grains/TestGAgent.Grains.csproj -c Release"
            result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"DLL编译失败: {result.stderr}")
                return False
                
            logger.info("DLL编译成功")
            
            # 2. 获取编译后的DLL文件
            dll_file = os.path.join(dll_path, "TestGAgent.Grains/bin/Release/net9.0/TestGAgent.Grains.dll")
            if not os.path.exists(dll_file):
                logger.error(f"DLL文件不存在: {dll_file}")
                return False
                
            # 3. 上传DLL更新插件
            test_case = self.create_test_case(
                name="更新插件DLL",
                description="上传新编译的DLL更新插件",
                endpoint=f"/{plugin_id}",
                method="PUT",
                params={
                    'code': ('TestGAgent.Grains.dll', open(dll_file, 'rb'))
                },
                expected_status=200,
                expected_response={
                    'code': ['-1', '20000'],
                    'data': {
                        'id': str,
                        'name': str,
                        'creationTime': int,
                        'creatorName': str
                    }
                }
            )
            
            result = self.execute_test_case(test_case)
            return result.status == APITestStatus.PASSED
            
        except Exception as e:
            logger.error(f"编译和上传DLL失败: {str(e)}")
            return False

    def get_access_token(self) -> str:
        """获取访问令牌"""
        try:
            response = requests.post(
                'https://aevatar-station-ui-staging.aevatar.ai/connect/token',
                headers={
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': 'https://aevatar-station-ui-staging.aevatar.ai'
                },
                data={
                    'grant_type': 'password',
                    'scope': 'Aevatar offline_access',
                    'username': 'haylee-100@qq.com',
                    'password': 'Wh520520!',
                    'client_id': 'AevatarAuthServer'
                }
            )
            
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                logger.error(f"获取token失败: {response.text}")
                return None
        except Exception as e:
            logger.error(f"获取token时发生错误: {str(e)}")
            return None

    @allure.step('测试环境准备')
    def setup_method(self, method):
        """在每个测试方法之前设置认证头"""
        # 获取访问令牌
        access_token = self.get_access_token()
        if not access_token:
            logger.error("Failed to get access token")
            pytest.skip("Failed to get access token")
        
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Origin': 'https://aevatar-station-ui-staging.aevatar.ai',
            'Pragma': 'no-cache',
            'Priority': 'u=1, i',
            'Referer': 'https://aevatar-station-ui-staging.aevatar.ai/dashboard/dll',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }
        logger.info(f"Using BASE_URL: {self.BASE_URL}")
        logger.info(f"Using TEST_PROJECT_ID: {self.TEST_PROJECT_ID}")
        logger.info(f"Using headers: {json.dumps(self.headers, indent=2)}")
        
        # 编译DLL
        dll_path = "/Users/wanghuan/aelf/LoadTest/Dll/TestGAgent"
        compile_cmd = f"cd {dll_path} && dotnet build TestGAgent.Grains/TestGAgent.Grains.csproj -c Release"
        result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"DLL编译失败: {result.stderr}")
            pytest.skip("Failed to compile DLL")
            
        logger.info("DLL编译成功")
        
        # 获取编译后的DLL文件
        dll_file = os.path.join(dll_path, "TestGAgent.Grains/bin/Release/net9.0/TestGAgent.Grains.dll")
        if not os.path.exists(dll_file):
            logger.error(f"DLL文件不存在: {dll_file}")
            pytest.skip("DLL file not found")
            
        # 创建测试插件
        test_case = self.create_test_case(
            name="创建测试插件",
            description="创建用于测试的插件",
            endpoint="",
            method="POST",
            params={
                'projectId': '4905508f-def5-ff31-f692-3a196ee1455d',
                'code': ('TestGAgent.Grains.dll', open(dll_file, 'rb'), 'application/x-msdownload')
            },
            expected_status=200,
            expected_response={
                'code': ['-1', '20000'],
                'data': {
                    'id': str,
                    'displayName': str,
                    'memberCount': int,
                    'creationTime': int
                }
            }
        )
        
        result = self.execute_test_case(test_case)
        logger.info(f"Create plugin result: {json.dumps(result.__dict__, default=str, indent=2)}")
        
        if result.status == APITestStatus.PASSED and result.actual_response:
            try:
                logger.info(f"Full response data: {json.dumps(result.actual_response, indent=2)}")
                if result.actual_response.get('data'):
                    logger.info(f"Response data field: {json.dumps(result.actual_response['data'], indent=2)}")
                    if result.actual_response['data'].get('id'):
                        self.TEST_PLUGIN_ID = result.actual_response['data']['id']
                        logger.info(f"Created test plugin with ID: {self.TEST_PLUGIN_ID}")
                    else:
                        logger.error("No 'id' field in response data")
                        logger.error(f"Failed to get plugin ID from response: {result.actual_response}")
                        pytest.skip("Failed to get plugin ID from response")
                else:
                    logger.error("No 'data' field in response")
                    logger.error(f"Failed to get plugin ID from response: {result.actual_response}")
                    pytest.skip("Failed to get plugin ID from response")
            except Exception as e:
                logger.error(f"Error processing plugin creation response: {str(e)}")
                logger.error(f"Response: {result.actual_response}")
                pytest.skip(f"Error processing plugin creation response: {str(e)}")
        else:
            error_msg = f"Failed to create test plugin. Status: {result.status}"
            if hasattr(result, 'error_message'):
                error_msg += f", Error: {result.error_message}"
            if hasattr(result, 'actual_response'):
                error_msg += f", Response: {result.actual_response}"
            logger.error(error_msg)
            pytest.skip(error_msg)

        # 编译并上传DLL
        if hasattr(self, 'TEST_PLUGIN_ID'):
            self.compile_and_upload_dll(self.TEST_PLUGIN_ID)

    @allure.step('测试环境清理')
    def teardown_method(self, method):
        """在每个测试方法之后清理"""
        if hasattr(self, 'TEST_PLUGIN_ID'):
            # 尝试删除测试插件
            test_case = self.create_test_case(
                name="清理测试插件",
                description="删除测试用的插件",
                endpoint=f"/{self.TEST_PLUGIN_ID}",
                method="DELETE",
                params={},
                expected_status=200,
                expected_response={'code': ['-1', '20001', '50000']}
            )
            self.execute_test_case(test_case)

    @allure.step('创建测试用例')
    def create_test_case(self, name: str, description: str, endpoint: str, method: str, 
                        params: Dict[str, Any], expected_status: int, 
                        expected_response: Dict[str, Any]) -> APITestCase:
        """创建测试用例"""
        return APITestCase(
            name=name,
            description=description,
            endpoint=endpoint,
            method=method,
            headers=self.headers,
            params=params,
            expected_status=expected_status,
            expected_response=expected_response
        )

    @allure.step('执行测试用例')
    def execute_test_case(self, test_case: APITestCase) -> APITestResult:
        """执行测试用例"""
        try:
            logger.info(f"Executing test case: {test_case.name}")
            logger.info(f"Request URL: {self.BASE_URL}{test_case.endpoint}")
            logger.info(f"Request method: {test_case.method}")
            logger.info(f"Request headers: {json.dumps(test_case.headers, indent=2)}")
            
            # 安全地记录参数，避免序列化文件对象
            safe_params = {}
            for key, value in test_case.params.items():
                if isinstance(value, tuple) and len(value) >= 2:
                    safe_params[key] = f"<file: {value[0]}>"
                else:
                    safe_params[key] = value
            logger.info(f"Request params: {json.dumps(safe_params, indent=2)}")
            
            # 根据请求方法和参数类型处理请求
            if test_case.method in ['POST', 'PUT']:
                files = {}
                data = {}
                
                # 处理文件上传
                for key, value in test_case.params.items():
                    if isinstance(value, tuple) and len(value) >= 2:
                        if len(value) == 2:
                            files[key] = value
                        else:
                            files[key] = (value[0], value[1], value[2])
                    else:
                        data[key] = value
                
                # 开始计时（在发送请求前）
                api_start_time = time.time()
                
                if files:
                    # 文件上传请求
                    logger.info(f"Sending file upload request with files: {list(files.keys())} and data: {data}")
                    response = requests.request(
                        method=test_case.method,
                        url=f"{self.BASE_URL}{test_case.endpoint}",
                        headers=test_case.headers,
                        files=files,
                        data=data
                    )
                else:
                    # JSON 请求
                    headers = dict(test_case.headers)
                    headers['Content-Type'] = 'application/json'
                    logger.info(f"Sending JSON request with data: {json.dumps(data, indent=2)}")
                    response = requests.request(
                        method=test_case.method,
                        url=f"{self.BASE_URL}{test_case.endpoint}",
                        headers=headers,
                        json=data
                    )
            else:
                # GET 和 DELETE 请求
                # 开始计时（在发送请求前）
                api_start_time = time.time()
                logger.info(f"Sending request with params: {json.dumps(test_case.params, indent=2)}")
                response = requests.request(
                    method=test_case.method,
                    url=f"{self.BASE_URL}{test_case.endpoint}",
                    headers=test_case.headers,
                    params=test_case.params
                )
            
            # 计算接口调用时长
            api_execution_time = time.time() - api_start_time
            
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
            logger.info(f"Response text: {response.text}")
            
            # 添加接口响应时长监控
            if api_execution_time > 3.0:  # 如果接口响应时间超过3秒
                logger.warning(f"⚠️ 警告：接口响应时间过长！")
                logger.warning(f"⚠️ 接口耗时: {api_execution_time:.2f}秒")
            else:
                logger.info(f"接口响应时间: {api_execution_time:.2f}秒")
            
            try:
                response_data = response.json()
                logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse response as JSON. Response text: {response.text}")
                return APITestResult(
                    test_case=test_case,
                    status=APITestStatus.FAILED,
                    error_message=f"Failed to parse response as JSON: {response.text}",
                    execution_time=api_execution_time
                )
            
            if response.status_code == test_case.expected_status:
                if response_data.get('code') in ['-1', '20000', '20001']:
                    return APITestResult(
                        test_case=test_case,
                        status=APITestStatus.PASSED,
                        actual_response=response_data,
                        execution_time=api_execution_time
                    )
            
            return APITestResult(
                test_case=test_case,
                status=APITestStatus.FAILED,
                actual_response=response_data,
                error_message=f"Expected status {test_case.expected_status}, got {response.status_code}",
                execution_time=api_execution_time
            )
        except Exception as e:
            logger.error(f"Error executing test case: {str(e)}")
            return APITestResult(
                test_case=test_case,
                status=APITestStatus.FAILED,
                error_message=str(e),
                execution_time=time.time() - api_start_time if 'api_start_time' in locals() else 0
            )

    @allure.story('获取插件列表')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_plugin_list_success(self):
        """测试获取插件列表成功"""
        test_case = self.create_test_case(
            name="获取插件列表成功",
            description="验证成功获取有效项目ID的插件列表",
            endpoint="",
            method="GET",
            params={'projectId': self.TEST_PROJECT_ID},
            expected_status=200,
            expected_response={
                'code': ['-1', '20000'],
                'data': {'items': []}
            }
        )
        
        result = self.execute_test_case(test_case)
        assert result.status == APITestStatus.PASSED

    @allure.story('获取插件列表')
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_plugin_list_invalid_project_id(self):
        """测试使用无效项目ID获取插件列表"""
        test_case = self.create_test_case(
            name="获取插件列表-无效项目ID",
            description="验证使用无效项目ID请求插件列表时的错误处理",
            endpoint="",
            method="GET",
            params={'projectId': 'invalid-id'},
            expected_status=200,
            expected_response={'code': ['-1', '50000']}
        )
        
        result = self.execute_test_case(test_case)
        assert result.status == APITestStatus.PASSED

    @allure.story('创建插件')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.plugin_creation
    def test_create_plugin_success(self):
        """测试创建插件成功"""
        test_start_time = time.time()
        
        logger.info(format_test_header("创建插件"))
        
        # 编译DLL
        logger.info(format_test_step(1, "编译DLL"))
        dll_path = "/Users/wanghuan/aelf/LoadTest/Dll/TestGAgent"
        compile_cmd = f"cd {dll_path} && dotnet build TestGAgent.Grains/TestGAgent.Grains.csproj -c Release"
        result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ DLL编译失败: {result.stderr}")
            pytest.skip("Failed to compile DLL")
            
        logger.info("✅ DLL编译成功")
        
        # 获取编译后的DLL文件
        logger.info(format_test_step(2, "获取DLL文件"))
        dll_file = os.path.join(dll_path, "TestGAgent.Grains/bin/Release/net9.0/TestGAgent.Grains.dll")
        if not os.path.exists(dll_file):
            logger.error(f"❌ DLL文件不存在: {dll_file}")
            pytest.skip("DLL file not found")
            
        logger.info("✅ DLL文件就绪")
        
        # 创建测试用例
        logger.info(format_test_step(3, "准备创建插件"))
        test_case = self.create_test_case(
            name="创建插件成功",
            description="验证成功创建新插件",
            endpoint="",
            method="POST",
            params={
                'projectId': '4905508f-def5-ff31-f692-3a196ee1455d',
                'code': ('TestGAgent.Grains.dll', open(dll_file, 'rb'), 'application/x-msdownload')
            },
            expected_status=200,
            expected_response={
                'code': ['-1', '20000'],
                'data': {
                    'id': str,
                    'displayName': str,
                    'memberCount': int,
                    'creationTime': int
                }
            }
        )
        
        # 执行测试用例
        logger.info(format_test_step(4, "执行插件创建"))
        result = self.execute_test_case(test_case)
        
        # 验证结果
        logger.info(format_test_step(5, "验证测试结果"))
        test_duration = time.time() - test_start_time
        
        if result.status == APITestStatus.PASSED:
            logger.info(format_test_result('PASSED', test_duration, result.execution_time))
        else:
            logger.error(format_test_result('FAILED', test_duration, result.execution_time))
            logger.error(f"错误信息: {result.error_message}")
        
        assert result.status == APITestStatus.PASSED
        return result

    @allure.story('创建插件')
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.plugin_creation
    def test_create_plugin_invalid_input(self):
        """
        测试用例：使用无效输入创建插件
        描述：验证使用无效输入数据创建插件时的错误处理
        预期结果：
            - 状态码 200
            - 响应码 50000 或 -1
        """
        test_case = self.create_test_case(
            name="创建插件-无效输入",
            description="验证使用无效输入数据创建插件时的错误处理",
            endpoint="",
            method="POST",
            params={
                'projectId': '',
                'code': ('test_code', 'test code content')
            },
            expected_status=200,
            expected_response={'code': ['-1', '50000']}
        )
        
        result = self.execute_test_case(test_case)
        assert result.status == APITestStatus.PASSED

    @allure.story('更新插件')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_plugin_success(self):
        """测试更新插件成功"""
        test_case = self.create_test_case(
            name="更新插件成功",
            description="验证成功更新现有插件",
            endpoint=f"/{self.TEST_PLUGIN_ID}",
            method="PUT",
            params={
                'code': ('updated_code', 'updated code content')
            },
            expected_status=200,
            expected_response={
                'code': ['-1', '20000'],
                'data': {
                    'id': str,
                    'name': str,
                    'creationTime': int,
                    'creatorName': str
                }
            }
        )
        
        result = self.execute_test_case(test_case)
        assert result.status == APITestStatus.PASSED

    @allure.story('更新插件')
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_plugin_nonexistent(self):
        """
        测试用例：更新不存在的插件
        描述：验证更新不存在插件时的错误处理
        预期结果：
            - 状态码 200
            - 响应码 50000 或 -1
        """
        test_case = self.create_test_case(
            name="更新插件-不存在",
            description="验证更新不存在插件时的错误处理",
            endpoint="/non-existent-id",
            method="PUT",
            params={
                'code': ('test_code', 'test code content')
            },
            expected_status=200,
            expected_response={'code': ['-1', '50000']}
        )
        
        result = self.execute_test_case(test_case)
        assert result.status == APITestStatus.PASSED

    @allure.story('删除插件')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_plugin_success(self):
        """测试删除插件成功"""
        test_case = self.create_test_case(
            name="删除插件成功",
            description="验证成功删除现有插件",
            endpoint=f"/{self.TEST_PLUGIN_ID}",
            method="DELETE",
            params={},
            expected_status=200,
            expected_response={'code': ['-1', '20001', '50000']}
        )
        
        result = self.execute_test_case(test_case)
        assert result.status == APITestStatus.PASSED

    @allure.story('删除插件')
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_plugin_nonexistent(self):
        """
        测试用例：删除不存在的插件
        描述：验证删除不存在插件时的错误处理
        预期结果：
            - 状态码 200
            - 响应码 50000 或 -1
        """
        test_case = self.create_test_case(
            name="删除插件-不存在",
            description="验证删除不存在插件时的错误处理",
            endpoint="/non-existent-id",
            method="DELETE",
            params={},
            expected_status=200,
            expected_response={'code': ['-1', '50000']}
        )
        
        result = self.execute_test_case(test_case)
        assert result.status == APITestStatus.PASSED

# 创建测试套件
PLUGIN_TEST_SUITE = APITestSuite(
    name="插件管理API测试套件",
    description="插件管理相关API的完整测试套件",
    test_cases=[
        APITestCase(
            name="获取插件列表",
            description="验证获取插件列表的API接口",
            endpoint="",
            method="GET",
            headers={},
            params={'projectId': 'test-project-id'},
            expected_status=200,
            expected_response={'code': ['-1', '20000']}
        ),
        APITestCase(
            name="创建插件",
            description="验证创建插件的API接口",
            endpoint="",
            method="POST",
            headers={},
            params={'projectId': 'test-project-id'},
            expected_status=200,
            expected_response={'code': ['-1', '20000']}
        ),
        APITestCase(
            name="更新插件",
            description="验证更新插件的API接口",
            endpoint="/{plugin_id}",
            method="PUT",
            headers={},
            params={},
            expected_status=200,
            expected_response={'code': ['-1', '20000']}
        ),
        APITestCase(
            name="删除插件",
            description="验证删除插件的API接口",
            endpoint="/{plugin_id}",
            method="DELETE",
            headers={},
            params={},
            expected_status=200,
            expected_response={'code': ['-1', '20001']}
        )
    ],
    environment="staging",
    dependencies=["plugin_service", "auth_service"]
)

def format_test_header(test_name: str) -> str:
    """格式化测试用例标题"""
    return f"\n{'='*50}\n🔍 测试用例: {test_name}\n{'='*50}"

def format_test_step(step_num: int, description: str) -> str:
    """格式化测试步骤"""
    return f"\n📝 步骤 {step_num}: {description}"

def format_test_result(status: str, duration: float, api_time: float = None) -> str:
    """格式化测试结果"""
    result = f"\n{'='*50}\n"
    result += f"✨ 测试结果: {'✅ 通过' if status == 'PASSED' else '❌ 失败'}\n"
    if api_time is not None:
        result += f"⏱️  接口耗时: {api_time:.2f}秒 {'⚠️ ' if api_time > 3.0 else ''}\n"
    result += f"⌛ 总耗时: {duration:.2f}秒\n"
    result += f"{'='*50}\n"
    return result

def format_api_info(method: str, url: str) -> str:
    """格式化API信息"""
    return f"\n🌐 API请求: [{method}] {url}"

def format_api_response(status_code: int, response_data: dict) -> str:
    """格式化API响应"""
    return f"\n📊 响应状态: {status_code}\n📋 响应数据:\n{json.dumps(response_data, indent=2, ensure_ascii=False)}" 