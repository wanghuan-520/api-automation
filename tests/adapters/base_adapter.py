"""
业务适配器基类
=============

定义业务适配器的通用接口，所有业务适配器都应继承此类。
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from config.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class BaseBusinessAdapter(ABC):
    """
    业务适配器基类
    
    定义业务逻辑的通用接口，子类需要实现具体的业务逻辑。
    """
    
    def __init__(self, config: ConfigManager):
        """
        初始化业务适配器
        
        Args:
            config: 配置管理器实例
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def compile_artifact(self, artifact_id: str, **kwargs) -> bool:
        """
        编译构建产物（如DLL、JAR等）
        
        Args:
            artifact_id: 构建产物ID
            **kwargs: 其他参数
        
        Returns:
            是否编译成功
        """
        raise NotImplementedError("Subclass must implement compile_artifact")
    
    @abstractmethod
    def get_artifact_path(self, artifact_id: str, **kwargs) -> Optional[str]:
        """
        获取构建产物路径
        
        Args:
            artifact_id: 构建产物ID
            **kwargs: 其他参数
        
        Returns:
            构建产物路径，如果不存在返回None
        """
        raise NotImplementedError("Subclass must implement get_artifact_path")
    
    @abstractmethod
    def upload_artifact(self, artifact_path: str, target_id: str, **kwargs) -> bool:
        """
        上传构建产物
        
        Args:
            artifact_path: 构建产物路径
            target_id: 目标ID（如插件ID）
            **kwargs: 其他参数
        
        Returns:
            是否上传成功
        """
        raise NotImplementedError("Subclass must implement upload_artifact")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        获取认证请求头
        
        Returns:
            包含认证信息的请求头字典
        """
        # 默认实现：从配置获取token
        token = self._get_access_token()
        if not token:
            return {}
        
        return {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json, text/plain, */*',
        }
    
    def _get_access_token(self) -> Optional[str]:
        """
        获取访问令牌（内部方法）
        
        Returns:
            访问令牌，如果获取失败返回None
        """
        token_url = self.config.get('auth.token_url')
        username = self.config.get('auth.username')
        password = self.config.get('auth.password')
        client_id = self.config.get('auth.client_id')
        scope = self.config.get('auth.scope')
        
        if not all([token_url, username, password]):
            self.logger.error("认证配置不完整")
            return None
        
        try:
            import requests
            from urllib.parse import urlparse
            
            parsed_url = urlparse(token_url)
            origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            response = requests.post(
                token_url,
                headers={
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': origin
                },
                data={
                    'grant_type': 'password',
                    'scope': scope or '',
                    'username': username,
                    'password': password,
                    'client_id': client_id or ''
                },
                timeout=30
            )
            
            if response.status_code == 200:
                token = response.json().get('access_token')
                self.logger.info("成功获取访问令牌")
                return token
            else:
                self.logger.error(f"获取token失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"获取token时发生错误: {str(e)}")
            return None

