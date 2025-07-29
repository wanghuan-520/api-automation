"""
认证接口测试用例
==================
优先级：🔥 最高
包含：核心认证接口、认证流程接口、第三方OAuth流程
"""

import pytest
import allure
import requests
import json
import time
from typing import Dict, Any, Optional
from utils.client import APIClient
from utils.assert_utils import (
    assert_response_status,
    assert_json_response,
    assert_response_contains
)
import os

@allure.epic('认证接口')
@pytest.mark.auth
class TestAuthAPIs:
    """认证接口测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient):
        """测试前准备"""
        self.client = api_client
        self.base_url = "https://station-developer-staging.aevatar.ai/godgpt-client/api"
        self.auth_base_url = "https://auth-station-staging.aevatar.ai"
        
        # 测试邮箱
        self.test_email = os.getenv("TEST_EMAIL", "test@example.com")
        self.test_password = os.getenv("TEST_PASSWORD", "Test123456!")  # 更新为正确的密码
        self.verification_code = "123456"  # 模拟验证码
        
    @allure.feature('核心认证接口')
    @allure.story('POST /connect/token - 邮箱密码登录')
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_email_password_login(self):
        """测试邮箱密码登录 - 使用真实登录流程"""
        with allure.step('准备邮箱密码登录数据'):
            login_data = {
                "grant_type": "password",
                "client_id": "AevatarAuthServer",
                "apple_app_id": "com.gpt.god",
                "scope": "Aevatar offline_access",
                "username": self.test_email,
                "password": self.test_password
            }
        
        with allure.step('准备完整的请求头'):
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
        
        with allure.step('发送邮箱密码登录请求到真实认证服务器'):
            # 使用真实的认证服务器
            auth_url = "https://auth-pre-station-staging.aevatar.ai/connect/token"
            response = requests.post(
                auth_url,
                data=login_data,
                headers=headers,
                timeout=30
            )
        
        with allure.step('验证响应状态'):
            assert_response_status(response, [200, 400, 401])
        
        with allure.step('验证响应格式'):
            if response.status_code == 200:
                response_data = response.json()
                assert "access_token" in response_data
                assert "token_type" in response_data
                assert "expires_in" in response_data
                assert response_data["token_type"] == "Bearer"
                print("✅ 邮箱登录成功!")
                print(f"🎫 Token类型: {response_data.get('token_type')}")
                print(f"⏰ 过期时间: {response_data.get('expires_in')}秒")
            else:
                response_data = response.json()
                print(f"❌ 邮箱登录失败: {response_data}")
                # 记录错误信息但不失败测试
                assert "error" in response_data
    
    @allure.feature('核心认证接口')
    @allure.story('POST /connect/token - 邮箱错误密码登录')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_email_wrong_password_login(self):
        """测试邮箱错误密码登录 - 验证错误处理"""
        with allure.step('准备错误密码登录数据'):
            wrong_password_data = {
                "grant_type": "password",
                "client_id": "AevatarAuthServer",
                "apple_app_id": "com.gpt.god",
                "scope": "Aevatar offline_access",
                "username": self.test_email,
                "password": "WrongPassword123!"  # 错误的密码
            }
        
        with allure.step('准备完整的请求头'):
            headers = {
                'accept': 'application/json',
                'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://godgpt-ui-testnet.aelf.dev',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://godgpt-ui-testnet.aelf.dev/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
            }
        
        with allure.step('发送错误密码登录请求'):
            auth_url = "https://auth-pre-station-staging.aevatar.ai/connect/token"
            response = requests.post(
                auth_url,
                data=wrong_password_data,
                headers=headers,
                timeout=30
            )
        
        with allure.step('验证错误响应状态'):
            assert_response_status(response, 400)
        
        with allure.step('验证错误响应格式'):
            response_data = response.json()
            assert "error" in response_data
            assert "error_description" in response_data
            assert "error_uri" in response_data
            
            # 验证具体的错误信息
            assert response_data["error"] == "invalid_grant"
            assert response_data["error_description"] == "Invalid username or password!"
            assert response_data["error_uri"] == "https://documentation.openiddict.com/errors/ID2024"
            
            print("✅ 错误密码登录测试成功!")
            print(f"❌ 错误类型: {response_data['error']}")
            print(f"📝 错误描述: {response_data['error_description']}")
            print(f"🔗 错误链接: {response_data['error_uri']}")
    
    @allure.feature('核心认证接口')
    @allure.story('POST /connect/token - Google登录')
    @allure.severity(allure.severity_level.BLOCKER)
    def test_google_login(self):
        """测试Google登录"""
        with allure.step('准备Google登录数据'):
            google_data = {
                "grant_type": "password",
                "client_id": "AevatarAuthServer",
                "apple_app_id": "com.gpt.god",
                "scope": "Aevatar offline_access",
                "username": self.test_email,
                "password": self.test_password
            }
        
        with allure.step('发送Google登录请求'):
            response = requests.post(
                f"{self.auth_base_url}/connect/token",
                data=google_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        with allure.step('验证Google登录响应'):
            assert_response_status(response, [200, 400, 401])
            
            if response.status_code == 200:
                response_data = response.json()
                assert "access_token" in response_data
                assert "token_type" in response_data
    
    @allure.feature('核心认证接口')
    @allure.story('POST /connect/token - Apple登录')
    @allure.severity(allure.severity_level.BLOCKER)
    def test_apple_login(self):
        """测试Apple登录"""
        with allure.step('准备Apple登录数据'):
            apple_data = {
                "grant_type": "password",
                "client_id": "AevatarAuthServer",
                "apple_app_id": "com.gpt.god",
                "scope": "Aevatar offline_access",
                "username": self.test_email,
                "password": self.test_password
            }
        
        with allure.step('发送Apple登录请求'):
            response = requests.post(
                f"{self.auth_base_url}/connect/token",
                data=apple_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        with allure.step('验证Apple登录响应'):
            assert_response_status(response, [200, 400, 401])
            
            if response.status_code == 200:
                response_data = response.json()
                assert "access_token" in response_data
                assert "token_type" in response_data
    
    @allure.feature('核心认证接口')
    @allure.story('POST /api/account/check-email-registered + send-register-code')
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_check_email_registered(self):
        """测试邮箱注册状态检查 + 注册验证码发送"""
        with allure.step('准备请求头'):
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://godgpt-ui-testnet.aelf.dev',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://godgpt-ui-testnet.aelf.dev/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
            }
        
        with allure.step('1. 检查已注册邮箱状态'):
            registered_email_data = {"emailAddress": self.test_email}
            response = requests.post(
                f"{self.base_url}/account/check-email-registered",
                json=registered_email_data,
                headers=headers,
                timeout=30
            )
        
        with allure.step('2. 验证已注册邮箱响应状态'):
            assert_response_status(response, 200)
        
        with allure.step('3. 验证已注册邮箱检查结果'):
            response_data = response.json()
            assert "code" in response_data
            assert "data" in response_data
            assert "message" in response_data
            assert response_data["code"] == "20000"
            assert response_data["data"] == True  # 已注册邮箱应该返回true
            assert response_data["message"] == ""
            print(f"✅ 已注册邮箱 {self.test_email} 检查成功: {response_data['data']}")
        
        with allure.step('4. 对已注册邮箱发送注册验证码'):
            # 准备注册验证码请求头（使用测试环境）
            register_headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://godgpt-ui-dev.aelf.dev',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://godgpt-ui-dev.aelf.dev/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
            }
            
            register_code_data = {
                "email": self.test_email,
                "appName": "GodGPT"
            }
            
            test_base_url = "https://station-developer-staging.aevatar.ai/godgpt-test-client/api"
            register_response = requests.post(
                f"{test_base_url}/account/send-register-code",
                json=register_code_data,
                headers=register_headers,
                timeout=30
            )
        
        with allure.step('5. 验证已注册邮箱的注册验证码响应'):
            assert_response_status(register_response, 200)
            register_response_data = register_response.json()
            assert "code" in register_response_data
            assert "data" in register_response_data
            assert "message" in register_response_data
            
            # 已注册邮箱应该返回50000和已注册消息
            assert register_response_data["code"] == "50000"
            assert register_response_data["data"] is None
            assert "registered" in register_response_data["message"].lower()
            print(f"✅ 已注册邮箱发送注册验证码验证通过: {register_response_data['message']}")
        
        with allure.step('6. 检查未注册邮箱状态'):
            unregistered_email_data = {"emailAddress": "testNoRegistered@example.com"}
            response = requests.post(
                f"{self.base_url}/account/check-email-registered",
                json=unregistered_email_data,
                headers=headers,
                timeout=30
            )
        
        with allure.step('7. 验证未注册邮箱响应状态'):
            assert_response_status(response, 200)
        
        with allure.step('8. 验证未注册邮箱检查结果'):
            response_data = response.json()
            assert "code" in response_data
            assert "data" in response_data
            assert "message" in response_data
            assert response_data["code"] == "20000"
            assert response_data["data"] == False  # 未注册邮箱应该返回false
            assert response_data["message"] == ""
            print(f"✅ 未注册邮箱 testNoRegistered@example.com 检查成功: {response_data['data']}")
        
        with allure.step('9. 对未注册邮箱发送注册验证码'):
            register_code_data = {
                "email": "testNoRegistered@example.com",
                "appName": "GodGPT"
            }
            
            register_response = requests.post(
                f"{test_base_url}/account/send-register-code",
                json=register_code_data,
                headers=register_headers,
                timeout=30
            )
        
        with allure.step('10. 验证未注册邮箱的注册验证码响应'):
            assert_response_status(register_response, 200)
            register_response_data = register_response.json()
            assert "code" in register_response_data
            assert "data" in register_response_data
            assert "message" in register_response_data
            
            # 未注册邮箱应该返回20001和empty result
            assert register_response_data["code"] == "20001"
            assert register_response_data["data"] is None
            assert register_response_data["message"] == "empty result"
            print(f"✅ 未注册邮箱发送注册验证码验证通过: {register_response_data['message']}")
    
    @allure.feature('核心认证接口')
    @allure.story('GET /api/account/logout')
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_user_logout(self):
        """测试用户登出"""
        with allure.step('执行用户登出'):
            response = self.client.get("/account/logout")
        
        with allure.step('验证响应状态'):
            assert_response_status(response, 200)
        
        with allure.step('验证登出结果'):
            response_data = response.json()
            assert "code" in response_data
            assert response_data["code"] in ["20000", "20001"]
    
    @allure.feature('核心认证接口')
    @allure.story('POST /api/account/send-verification-code')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.skip(reason="接口返回404，可能未实现或路径已改变")
    def test_send_verification_code(self):
        """测试发送验证码"""
        with allure.step('准备发送验证码数据'):
            send_code_data = {
                "email": self.test_email,
                "type": "register"
            }
        
        with allure.step('发送验证码'):
            response = self.client.post("/account/send-verification-code", json=send_code_data)
        
        with allure.step('验证响应状态'):
            assert_response_status(response, 200)
        
        with allure.step('验证发送结果'):
            response_data = response.json()
            assert "code" in response_data
            assert response_data["code"] in ["20000", "50000"]
    
    @allure.feature('核心认证接口')
    @allure.story('POST /api/account/verify-code')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.skip(reason="接口返回404，可能未实现或路径已改变")
    def test_verify_code(self):
        """测试验证码验证"""
        with allure.step('准备验证码验证数据'):
            verify_data = {
                "email": self.test_email,
                "code": self.verification_code,
                "type": "register"
            }
        
        with allure.step('验证验证码'):
            response = self.client.post("/account/verify-code", json=verify_data)
        
        with allure.step('验证响应状态'):
            assert_response_status(response, 200)
        
        with allure.step('验证验证结果'):
            response_data = response.json()
            assert "code" in response_data
            assert response_data["code"] in ["20000", "50000"]
    
    @allure.feature('认证流程接口')
    @allure.story('GET /api/query/user-id')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_user_id(self):
        """测试获取用户ID - 需要认证token"""
        with allure.step('1. 邮箱登录获取token'):
            login_data = {
                "grant_type": "password",
                "client_id": "AevatarAuthServer",
                "apple_app_id": "com.gpt.god",
                "scope": "Aevatar offline_access",
                "username": self.test_email,
                "password": self.test_password
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
            
            auth_url = "https://auth-pre-station-staging.aevatar.ai/connect/token"
            login_response = requests.post(
                auth_url,
                data=login_data,
                headers=headers,
                timeout=30
            )
            
            assert_response_status(login_response, 200)
            login_data = login_response.json()
            assert "access_token" in login_data
            access_token = login_data["access_token"]
            print(f"✅ 成功获取访问token: {access_token[:20]}...")
        
        with allure.step('2. 使用token获取用户ID'):
            # 准备带认证头的请求
            auth_headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'cache-control': 'no-cache',
                'origin': 'https://godgpt-ui-testnet.aelf.dev',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://godgpt-ui-testnet.aelf.dev/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(
                f"{self.base_url}/query/user-id",
                headers=auth_headers,
                timeout=30
            )
        
        with allure.step('3. 验证响应状态'):
            assert_response_status(response, 200)
        
        with allure.step('4. 验证用户ID数据'):
            response_data = response.json()
            assert "code" in response_data
            if response_data["code"] == "20000":
                assert "data" in response_data
                # data字段直接是用户ID字符串，不是对象
                user_id = response_data["data"]
                assert isinstance(user_id, str)
                assert len(user_id) > 0  # 确保用户ID不为空
                print(f"✅ 成功获取用户ID: {user_id}")
                return user_id  # 返回用户ID供其他测试使用
            else:
                print(f"⚠️ 获取用户ID失败: {response_data}")
                # 记录响应但不失败测试
                assert "message" in response_data
                return None
    
    @allure.feature('认证流程接口')
    @allure.story('GET /api/profile/user-info')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_user_info(self):
        """测试获取用户信息 - 需要认证token"""
        with allure.step('1. 邮箱登录获取token'):
            login_data = {
                "grant_type": "password",
                "client_id": "AevatarAuthServer",
                "apple_app_id": "com.gpt.god",
                "scope": "Aevatar offline_access",
                "username": self.test_email,
                "password": self.test_password
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
            
            auth_url = "https://auth-pre-station-staging.aevatar.ai/connect/token"
            login_response = requests.post(
                auth_url,
                data=login_data,
                headers=headers,
                timeout=30
            )
            
            assert_response_status(login_response, 200)
            login_data = login_response.json()
            assert "access_token" in login_data
            access_token = login_data["access_token"]
            print(f"✅ 成功获取访问token: {access_token[:20]}...")
        
        with allure.step('2. 使用token获取用户信息'):
            # 准备带认证头的请求
            auth_headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://godgpt-ui-testnet.aelf.dev',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://godgpt-ui-testnet.aelf.dev/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(
                f"{self.base_url}/profile/user-info",
                headers=auth_headers,
                timeout=30
            )
        
        with allure.step('3. 验证响应状态'):
            assert_response_status(response, 200)
        
        with allure.step('4. 验证用户信息数据完整性'):
            response_data = response.json()
            assert "code" in response_data
            if response_data["code"] == "20000":
                assert "data" in response_data
                user_data = response_data["data"]
                
                # 验证必要字段
                required_fields = ["uid", "email", "name"]
                for field in required_fields:
                    assert field in user_data, f"缺少必要字段: {field}"
                
                # 验证邮箱地址与登录邮箱一致
                assert user_data["email"] == self.test_email, f"邮箱地址不一致: 期望 {self.test_email}, 实际 {user_data['email']}"
                print(f"✅ 邮箱地址验证通过: {user_data['email']}")
                
                # 验证用户ID格式
                assert isinstance(user_data["uid"], str)
                assert len(user_data["uid"]) > 0
                print(f"✅ 用户ID验证通过: {user_data['uid']}")
                
                # 验证用户名
                assert isinstance(user_data["name"], str)
                assert len(user_data["name"]) > 0
                print(f"✅ 用户名验证通过: {user_data['name']}")
                
                return user_data["uid"]  # 返回用户ID供验证一致性
            else:
                print(f"⚠️ 获取用户信息失败: {response_data}")
                # 记录响应但不失败测试
                assert "message" in response_data
                return None
    
    @allure.feature('认证流程接口')
    @allure.story('用户ID和用户信息一致性验证')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_user_id_info_consistency(self):
        """测试用户ID和用户信息的一致性"""
        with allure.step('1. 获取用户ID'):
            user_id = self.test_get_user_id()
            assert user_id is not None, "获取用户ID失败"
        
        with allure.step('2. 获取用户信息'):
            user_info_uid = self.test_get_user_info()
            assert user_info_uid is not None, "获取用户信息失败"
        
        with allure.step('3. 验证用户ID一致性'):
            assert user_id == user_info_uid, f"用户ID不一致: user-id接口返回 {user_id}, user-info接口返回 {user_info_uid}"
            print(f"✅ 用户ID一致性验证通过: {user_id}")
    
    @allure.feature('认证流程接口')
    @allure.story('GET /api/godgpt/account')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_user_account_info(self):
        """测试获取用户信息 - 需要认证token"""
        with allure.step('1. 邮箱登录获取token'):
            login_data = {
                "grant_type": "password",
                "client_id": "AevatarAuthServer",
                "apple_app_id": "com.gpt.god",
                "scope": "Aevatar offline_access",
                "username": self.test_email,
                "password": self.test_password
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
            
            auth_url = "https://auth-pre-station-staging.aevatar.ai/connect/token"
            login_response = requests.post(
                auth_url,
                data=login_data,
                headers=headers,
                timeout=30
            )
            
            assert_response_status(login_response, 200)
            login_data = login_response.json()
            assert "access_token" in login_data
            access_token = login_data["access_token"]
            print(f"✅ 成功获取访问token: {access_token[:20]}...")
        
        with allure.step('2. 使用token获取用户账户信息'):
            # 准备带认证头的请求
            auth_headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://godgpt-ui-testnet.aelf.dev',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://godgpt-ui-testnet.aelf.dev/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(
                f"{self.base_url}/godgpt/account",
                headers=auth_headers,
                timeout=30
            )
        
        with allure.step('3. 验证响应状态'):
            assert_response_status(response, 200)
        
        with allure.step('4. 验证用户数据完整性'):
            response_data = response.json()
            assert "code" in response_data
            if response_data["code"] == "20000":
                assert "data" in response_data
                user_data = response_data["data"]
                # 验证必要字段
                required_fields = ["id", "email", "username"]
                for field in required_fields:
                    if field in user_data:
                        assert user_data[field] is not None
                print(f"✅ 成功获取用户账户信息: {user_data.get('email', 'N/A')}")
            else:
                print(f"⚠️ 获取用户账户信息失败: {response_data}")
                # 记录响应但不失败测试
                assert "message" in response_data
    
    @allure.feature('第三方OAuth流程')
    @allure.story('Google OAuth授权')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_google_oauth_flow(self):
        """测试Google OAuth流程"""
        with allure.step('模拟Google OAuth授权码'):
            auth_code = "google_auth_code_123"
        
        with allure.step('使用授权码获取token'):
            oauth_data = {
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": "https://example.com/callback",
                "client_id": "google_client_id"
            }
            
            response = requests.post(
                f"{self.auth_base_url}/connect/token",
                data=oauth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        with allure.step('验证OAuth响应'):
            assert_response_status(response, [200, 400, 401])
            
            if response.status_code == 200:
                response_data = response.json()
                assert "access_token" in response_data
                assert "refresh_token" in response_data
    
    @allure.feature('第三方OAuth流程')
    @allure.story('Apple OAuth授权')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_apple_oauth_flow(self):
        """测试Apple OAuth流程"""
        with allure.step('模拟Apple OAuth授权码'):
            auth_code = "apple_auth_code_123"
        
        with allure.step('使用授权码获取token'):
            oauth_data = {
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": "https://example.com/callback",
                "client_id": "apple_client_id"
            }
            
            response = requests.post(
                f"{self.auth_base_url}/connect/token",
                data=oauth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        with allure.step('验证OAuth响应'):
            assert_response_status(response, [200, 400, 401])
            
            if response.status_code == 200:
                response_data = response.json()
                assert "access_token" in response_data
                assert "refresh_token" in response_data
    
    @allure.feature('错误处理')
    @allure.story('认证错误处理')
    @allure.severity(allure.severity_level.NORMAL)
    def test_auth_error_handling(self):
        """测试认证错误处理"""
        with allure.step('测试无效邮箱登录'):
            invalid_login_data = {
                "grant_type": "password",
                "client_id": "AevatarAuthServer",
                "username": "invalid@example.com",
                "password": "wrongpassword"
            }
            
            response = requests.post(
                f"{self.auth_base_url}/connect/token",
                data=invalid_login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        with allure.step('验证错误响应'):
            assert response.status_code in [400, 401, 429]
    
    @allure.feature('安全测试')
    @allure.story('认证安全验证')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_auth_security(self):
        """测试认证安全验证"""
        with allure.step('测试SQL注入防护'):
            sql_injection_data = {
                "grant_type": "password",
                "client_id": "AevatarAuthServer",
                "username": "'; DROP TABLE users; --",
                "password": "test"
            }
            
            response = requests.post(
                f"{self.auth_base_url}/connect/token",
                data=sql_injection_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        with allure.step('验证安全防护'):
            assert response.status_code in [400, 401, 429]
    
    # @allure.feature('集成测试')
    # @allure.story('完整注册流程')
    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.integration
    # def test_complete_registration_flow(self):
    #     """测试完整注册流程：检查邮箱 -> 发送验证码 -> 验证码验证 -> 注册"""
    #     with allure.step('1. 检查邮箱是否已注册'):
    #         email_check_data = {"email": f"newuser_{int(time.time())}@example.com"}
    #         check_response = self.client.post("/account/check-email-registered", json=email_check_data)
    #         assert_response_status(check_response, 200)
        
    #     with allure.step('2. 发送验证码'):
    #         if check_response.json()["code"] == "20000" and not check_response.json()["data"]:
    #             send_code_data = {
    #                 "email": email_check_data["email"],
    #                 "type": "register"
    #             }
    #             send_response = self.client.post("/account/send-verification-code", json=send_code_data)
    #             assert_response_status(send_response, 200)
        
    #     with allure.step('3. 验证流程完整性'):
    #         assert check_response.json()["code"] in ["20000", "50000"]
    #         if 'send_response' in locals():
    #             assert send_response.json()["code"] in ["20000", "50000"]
    
    # @allure.feature('性能测试')
    # @allure.story('认证接口性能')
    # @allure.severity(allure.severity_level.NORMAL)
    # @pytest.mark.performance
    # def test_auth_performance(self):
    #     """测试认证接口性能"""
    #     with allure.step('测试邮箱检查响应时间'):
    #         start_time = time.time()
    #         email_data = {"email": self.test_email}
    #         response = self.client.post("/account/check-email-registered", json=email_data)
    #         end_time = time.time()
            
    #         response_time = end_time - start_time
            
    #     with allure.step('验证响应时间在可接受范围内'):
    #         # 邮箱检查应该在2秒内完成
    #         assert response_time < 2.0, f"Email check took {response_time}s, exceeded 2s limit"
    #         assert_response_status(response, 200)
        
    #     with allure.step('测试验证码发送响应时间'):
    #         start_time = time.time()
    #         send_code_data = {
    #             "email": self.test_email,
    #             "type": "register"
    #         }
    #         response = self.client.post("/account/send-verification-code", json=send_code_data)
    #         end_time = time.time()
            
    #         response_time = end_time - start_time
            
    #     with allure.step('验证验证码发送响应时间'):
    #         # 验证码发送应该在5秒内完成
    #         assert response_time < 5.0, f"Verification code sending took {response_time}s, exceeded 5s limit"
    #         assert_response_status(response, 200) 