"""
统一配置管理器
=============

提供统一的配置管理接口，支持多环境配置。
配置优先级：环境变量 > config.yaml > 默认值

使用示例：
    from config.config_manager import ConfigManager
    
    config = ConfigManager()
    base_url = config.get('base_url')
    timeout = config.get('timeout', 30)
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """统一配置管理器（单例模式）"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if not self._initialized:
            self._load_config()
            ConfigManager._initialized = True
    
    def _load_config(self) -> None:
        """
        加载配置
        优先级：环境变量 > config.yaml > 默认值
        """
        # 1. 加载默认配置
        default_config = {
            'base_url': 'http://localhost:8000',
            'timeout': 30,
            'max_retries': 3,
            'test_project_id': '',
            'auth': {
                'token_url': '',
                'username': '',
                'password': '',
                'client_id': '',
                'scope': ''
            }
        }
        
        # 2. 加载 YAML 配置
        config_path = Path(__file__).parent / "config.yaml"
        yaml_config = {}
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    yaml_data = yaml.safe_load(f) or {}
                    # 根据环境选择配置
                    env = os.getenv('TEST_ENV', 'test')
                    env_config = yaml_data.get('env', {}).get(env, {})
                    yaml_config = {
                        'base_url': env_config.get('base_url', default_config['base_url']),
                        'timeout': env_config.get('timeout', default_config['timeout']),
                        'test_project_id': env_config.get('test_project_id', ''),
                    }
            except Exception as e:
                logger.warning(f"Failed to load config.yaml: {e}, using defaults")
        
        # 3. 环境变量覆盖（最高优先级）
        # 注意：移除业务特定的默认值，必须通过环境变量或配置文件显式配置
        self._config = {
            'base_url': os.getenv('API_BASE_URL') or yaml_config.get('base_url') or default_config['base_url'],
            'timeout': int(os.getenv('API_TIMEOUT', str(yaml_config.get('timeout', default_config['timeout'])))),
            'max_retries': int(os.getenv('API_MAX_RETRIES', str(default_config['max_retries']))),
            'test_project_id': os.getenv('TEST_PROJECT_ID') or yaml_config.get('test_project_id') or default_config['test_project_id'],
            'auth': {
                'token_url': os.getenv('AUTH_TOKEN_URL') or yaml_config.get('auth', {}).get('token_url') or '',
                'username': os.getenv('TEST_USERNAME') or yaml_config.get('auth', {}).get('username') or '',
                'password': os.getenv('TEST_PASSWORD') or yaml_config.get('auth', {}).get('password') or '',
                # 移除业务默认值，必须显式配置
                'client_id': os.getenv('AUTH_CLIENT_ID') or yaml_config.get('auth', {}).get('client_id') or '',
                'scope': os.getenv('AUTH_SCOPE') or yaml_config.get('auth', {}).get('scope') or '',
            }
        }
        
        logger.info(f"Configuration loaded: base_url={self._config['base_url']}, env={os.getenv('TEST_ENV', 'test')}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键（如 'auth.username'）
            default: 默认值
        
        Returns:
            配置值
        
        Example:
            config.get('base_url')
            config.get('auth.username')
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值（仅内存中，不持久化）
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置（敏感信息会被掩码）"""
        config_copy = self._config.copy()
        
        # 掩码敏感信息
        if 'auth' in config_copy and 'password' in config_copy['auth']:
            password = config_copy['auth']['password']
            if password:
                config_copy['auth']['password'] = '***' if len(password) <= 3 else f"{password[:2]}***{password[-2:]}"
        
        return config_copy
    
    def reload(self) -> None:
        """重新加载配置"""
        self._config = {}
        self._load_config()
        logger.info("Configuration reloaded")
    
    def validate_required(self, required_keys: list) -> tuple[bool, list]:
        """
        验证必要配置是否存在
        
        Args:
            required_keys: 必要配置键列表，支持点号分隔的嵌套键
        
        Returns:
            (是否全部存在, 缺失的键列表)
        
        Example:
            is_valid, missing = config.validate_required(['base_url', 'auth.username', 'auth.password'])
        """
        missing = []
        for key in required_keys:
            value = self.get(key)
            if not value:
                missing.append(key)
        
        return len(missing) == 0, missing
    
    def validate_and_raise(self, required_keys: list) -> None:
        """
        验证必要配置，如果缺失则抛出异常
        
        Args:
            required_keys: 必要配置键列表
        
        Raises:
            ValueError: 当必要配置缺失时
        """
        is_valid, missing = self.validate_required(required_keys)
        if not is_valid:
            raise ValueError(
                f"缺少必要配置: {', '.join(missing)}\n"
                f"请检查环境变量或配置文件。参考: docs/ENV_SETUP.md"
            )


# 导出单例实例
config = ConfigManager()

