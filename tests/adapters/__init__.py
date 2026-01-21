"""
业务适配器模块
=============

提供业务逻辑抽象层，将业务特定的逻辑从测试用例中分离出来。

使用示例：
    from tests.adapters import get_business_adapter
    
    adapter = get_business_adapter()
    adapter.compile_artifact('plugin-id')
"""

from tests.adapters.base_adapter import BaseBusinessAdapter
from tests.adapters.aevatar_adapter import AevatarBusinessAdapter

__all__ = ['BaseBusinessAdapter', 'AevatarBusinessAdapter', 'get_business_adapter']


def get_business_adapter() -> BaseBusinessAdapter:
    """
    获取业务适配器实例
    
    根据配置自动选择适配器类型
    
    Returns:
        业务适配器实例
    """
    import os
    from config.config_manager import ConfigManager
    
    config = ConfigManager()
    adapter_type = os.getenv('BUSINESS_ADAPTER_TYPE', 'aevatar').lower()
    
    if adapter_type == 'aevatar':
        return AevatarBusinessAdapter(config)
    else:
        # 默认返回通用适配器（需要实现）
        return BaseBusinessAdapter(config)

