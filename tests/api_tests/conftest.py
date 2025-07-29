"""
API测试配置文件
==============
包含测试数据管理、环境设置和通用fixtures
"""

import pytest
import os
import json
import yaml
from typing import Dict, Any, Generator
from utils.client import APIClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@pytest.fixture(scope="session")
def api_client() -> Generator[APIClient, None, None]:
    """全局API客户端fixture，支持自动认证"""
    base_url = os.getenv("API_BASE_URL", "https://station-developer-staging.aevatar.ai/godgpt-client/api")
    
    # 检查认证配置
    client_id = os.getenv("AUTH_CLIENT_ID")
    client_secret = os.getenv("AUTH_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        import warnings
        warnings.warn("AUTH_CLIENT_ID 或 AUTH_CLIENT_SECRET 未设置，API调用可能失败")
    
    client = APIClient(base_url=base_url, auto_auth=True)
    yield client

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """测试配置数据"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def test_data() -> Dict[str, Any]:
    """测试数据fixture"""
    return {
        # 用户测试数据
        "users": {
            "valid_user": {
                "email": "test@example.com",
                "username": "test_user",
                "password": "Test123456!"
            },
            "invalid_user": {
                "email": "invalid_email",
                "username": "",
                "password": "123"
            }
        },
        
        # 会话测试数据
        "sessions": {
            "valid_session": {
                "title": "Test Session",
                "type": "chat",
                "sessionId": "test_session_001"
            },
            "invalid_session": {
                "title": "",
                "type": "invalid_type"
            }
        },
        
        # 支付测试数据
        "payments": {
            "valid_product": {
                "productId": "premium_monthly",
                "price": 9.99,
                "currency": "USD"
            },
            "invalid_product": {
                "productId": "invalid_product",
                "price": -1,
                "currency": "INVALID"
            }
        },
        
        # 邀请测试数据
        "invitations": {
            "valid_code": {
                "invitationCode": "TEST123",
                "newUserId": "new_user_001"
            },
            "invalid_code": {
                "invitationCode": "",
                "newUserId": ""
            }
        },
        
        # 分享测试数据
        "shares": {
            "valid_share": {
                "shareId": "test_share_001",
                "title": "Test Share",
                "content": "Test content"
            },
            "invalid_share": {
                "shareId": "nonexistent_share"
            }
        },
        
        # 音频测试数据
        "voice": {
            "valid_audio": {
                "audioData": "base64_encoded_audio_data",
                "sessionId": "voice_session_001",
                "format": "wav"
            },
            "invalid_audio": {
                "audioData": "invalid_data",
                "sessionId": "",
                "format": "invalid_format"
            }
        },
        
        # 系统配置测试数据
        "config": {
            "valid_prompt": {
                "prompt": "You are a helpful AI assistant.",
                "version": "2.0.0",
                "description": "Updated system prompt"
            },
            "invalid_prompt": {
                "prompt": "",
                "version": "invalid_version"
            }
        }
    }

@pytest.fixture(scope="function")
def clean_test_environment():
    """清理测试环境"""
    # 测试前清理
    yield
    # 测试后清理

@pytest.fixture(scope="session")
def auth_headers() -> Dict[str, str]:
    """认证头信息"""
    token = os.getenv("ACCESS_TOKEN", "test_token")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="session")
def admin_headers() -> Dict[str, str]:
    """管理员认证头信息"""
    admin_token = os.getenv("ADMIN_TOKEN", "admin_test_token")
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="function")
def mock_session_id() -> str:
    """模拟会话ID"""
    import uuid
    return f"test_session_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="function")
def mock_user_id() -> str:
    """模拟用户ID"""
    import uuid
    return f"test_user_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="function")
def mock_share_id() -> str:
    """模拟分享ID"""
    import uuid
    return f"test_share_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="function")
def create_session_fixture(api_client: APIClient) -> str:
    """全局创建会话fixture，供所有需要session的测试使用"""
    session_data = {
        "title": "Global Test Session",
        "type": "chat"
    }
    response = api_client.post("/godgpt/create-session", json=session_data)
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data["code"] == "20000":
            return response_data["data"]["sessionId"]
    
    # 如果创建失败，返回一个模拟的session ID
    import uuid
    return f"mock_session_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="function")
def create_guest_session_fixture(api_client: APIClient) -> str:
    """全局创建访客会话fixture"""
    guest_data = {
        "deviceId": f"guest_device_{os.getpid()}",
        "userAgent": "Mozilla/5.0 (Global Test Browser)"
    }
    response = api_client.post("/godgpt/guest/create-session", json=guest_data)
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data["code"] == "20000":
            return response_data["data"]["sessionId"]
    
    # 如果创建失败，返回一个模拟的guest session ID
    import uuid
    return f"mock_guest_session_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="session")
def expected_response_codes() -> Dict[str, str]:
    """期望的响应码"""
    return {
        "success": "20000",
        "success_delete": "20001",
        "error": "50000",
        "bad_request": "40000",
        "unauthorized": "40100",
        "forbidden": "40300",
        "not_found": "40400"
    }

@pytest.fixture(scope="session")
def test_timeouts() -> Dict[str, int]:
    """测试超时配置"""
    return {
        "short_timeout": 5,
        "medium_timeout": 10,
        "long_timeout": 30,
        "very_long_timeout": 60
    }

@pytest.fixture(scope="function")
def performance_monitor():
    """性能监控fixture"""
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        def get_duration(self) -> float:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0.0
        
        def assert_within_limit(self, limit: float):
            duration = self.get_duration()
            assert duration <= limit, f"Operation took {duration}s, exceeded limit of {limit}s"
    
    return PerformanceMonitor()

@pytest.fixture(scope="session")
def test_environment() -> str:
    """测试环境标识"""
    return os.getenv("TEST_ENV", "staging")

@pytest.fixture(scope="session")
def is_production() -> bool:
    """是否为生产环境"""
    return os.getenv("TEST_ENV", "staging").lower() == "production"

@pytest.fixture(scope="function")
def skip_in_production(request, is_production):
    """在生产环境中跳过测试的装饰器"""
    if is_production and request.node.get_closest_marker('skip_in_production'):
        pytest.skip("Test skipped in production environment")

@pytest.fixture(scope="function")
def data_cleanup():
    """数据清理fixture"""
    cleanup_tasks = []
    
    def add_cleanup_task(task):
        cleanup_tasks.append(task)
    
    yield add_cleanup_task
    
    # 执行清理任务
    for task in cleanup_tasks:
        try:
            task()
        except Exception as e:
            print(f"Cleanup task failed: {e}")

@pytest.fixture(scope="session")
def test_logger():
    """测试日志记录器"""
    import logging
    
    logger = logging.getLogger("api_test")
    logger.setLevel(logging.INFO)
    
    # 添加文件处理器
    log_file = os.path.join(os.path.dirname(__file__), "..", "..", "logs", "api_test.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

@pytest.fixture(scope="function")
def session_manager(api_client: APIClient):
    """会话管理器fixture，提供session的创建、管理和清理"""
    created_sessions = []
    
    class SessionManager:
        def __init__(self, client: APIClient):
            self.client = client
            self.sessions = []
        
        def create_session(self, title: str = "Test Session", session_type: str = "chat") -> str:
            """创建会话"""
            session_data = {
                "title": title,
                "type": session_type
            }
            response = self.client.post("/godgpt/create-session", json=session_data)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data["code"] == "20000":
                    session_id = response_data["data"]["sessionId"]
                    self.sessions.append(session_id)
                    return session_id
            
            # 如果创建失败，返回模拟ID
            import uuid
            mock_id = f"mock_session_{uuid.uuid4().hex[:8]}"
            self.sessions.append(mock_id)
            return mock_id
        
        def create_guest_session(self, device_id: str = None) -> str:
            """创建访客会话"""
            if not device_id:
                import uuid
                device_id = f"guest_device_{uuid.uuid4().hex[:8]}"
            
            guest_data = {
                "deviceId": device_id,
                "userAgent": "Mozilla/5.0 (Session Manager Test Browser)"
            }
            response = self.client.post("/godgpt/guest/create-session", json=guest_data)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data["code"] == "20000":
                    session_id = response_data["data"]["sessionId"]
                    self.sessions.append(session_id)
                    return session_id
            
            # 如果创建失败，返回模拟ID
            import uuid
            mock_id = f"mock_guest_session_{uuid.uuid4().hex[:8]}"
            self.sessions.append(mock_id)
            return mock_id
        
        def cleanup_sessions(self):
            """清理所有创建的会话"""
            for session_id in self.sessions:
                try:
                    if session_id.startswith("mock_"):
                        continue  # 跳过模拟的session
                    self.client.delete(f"/godgpt/chat/{session_id}")
                except Exception as e:
                    print(f"Failed to cleanup session {session_id}: {e}")
    
    manager = SessionManager(api_client)
    yield manager
    
    # 测试结束后清理会话
    manager.cleanup_sessions() 