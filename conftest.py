import pytest
import os
from typing import Generator
from utils.client import APIClient
import subprocess

@pytest.fixture(scope="session")
def api_client():
    """全局API客户端fixture"""
    base_url = os.getenv("API_BASE_URL", "https://station-developer-staging.aevatar.ai/godgpt-client/api")
    client = APIClient(base_url=base_url)
    yield client

@pytest.fixture(scope="function")
def test_data_dir() -> str:
    """返回测试数据目录路径"""
    return os.path.join(os.path.dirname(__file__), "test_data")

@pytest.fixture(autouse=True)
def setup_teardown():
    """每个测试用例前后的设置和清理"""
    # 测试前的设置
    yield
    # 测试后的清理 

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """在测试完成后自动打开 HTML 报告"""
    report_path = os.path.join(os.getcwd(), 'reports', 'report.html')
    if os.path.exists(report_path):
        subprocess.run(['open', report_path]) 