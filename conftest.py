"""
Pytest 全局配置和 Fixtures
==========================

提供全局的测试配置和共享 fixtures
"""

import pytest
import os
from typing import Generator
from pathlib import Path
import subprocess
import sys

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.client import APIClient
from config.config_manager import ConfigManager

# 加载环境变量（如果使用 .env 文件）
try:
    from dotenv import load_dotenv
    env_file = project_root / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass  # python-dotenv 未安装时忽略


@pytest.fixture(scope="session")
def config() -> ConfigManager:
    """
    配置管理器 fixture（session 级别）
    
    提供统一的配置访问接口，并在启动时验证必要配置
    """
    config = ConfigManager()
    
    # 验证必要配置（可根据需要调整）
    required_configs = ['base_url']  # 只验证base_url，其他配置根据测试需要验证
    is_valid, missing = config.validate_required(required_configs)
    
    if not is_valid:
        import warnings
        warnings.warn(
            f"缺少必要配置: {', '.join(missing)}\n"
            f"请检查环境变量或配置文件。参考: docs/ENV_SETUP.md",
            UserWarning
        )
    
    return config


@pytest.fixture(scope="function")
def api_client(config: ConfigManager) -> Generator[APIClient, None, None]:
    """
    API 客户端 fixture（function 级别）
    
    为每个测试用例提供独立的 API 客户端实例
    """
    base_url = config.get('base_url')
    timeout = config.get('timeout', 30)
    max_retries = config.get('max_retries', 3)
    
    client = APIClient(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries
    )
    
    yield client
    
    # 清理：关闭 session
    client.close()


@pytest.fixture(scope="function")
def test_data_dir() -> Path:
    """
    测试数据目录 fixture
    
    Returns:
        测试数据目录路径
    """
    data_dir = project_root / "test_data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture(scope="function")
def clean_test_data(api_client: APIClient):
    """
    测试数据清理 fixture
    
    记录测试过程中创建的资源，测试结束后自动清理
    
    Yields:
        创建的资源 ID 列表
    """
    created_resources = []
    yield created_resources
    
    # 清理创建的资源
    for resource_id in created_resources:
        try:
            api_client.delete(f"/resources/{resource_id}", raise_on_error=False)
        except Exception as e:
            # 清理失败不影响测试结果，只记录警告
            import logging
            logging.warning(f"Failed to clean up resource {resource_id}: {e}")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    在测试完成后自动打开 HTML 报告（仅 macOS）
    """
    if os.name == 'posix' and sys.platform == 'darwin':  # macOS
        report_path = project_root / 'reports' / 'report.html'
        if report_path.exists():
            subprocess.run(['open', str(report_path)]) 