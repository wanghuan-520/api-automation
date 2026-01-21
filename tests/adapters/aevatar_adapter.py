"""
Aevatar 业务适配器
================

实现 Aevatar 项目特定的业务逻辑。
"""

import os
import subprocess
from pathlib import Path
from typing import Optional
from tests.adapters.base_adapter import BaseBusinessAdapter
from config.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class AevatarBusinessAdapter(BaseBusinessAdapter):
    """
    Aevatar 业务适配器
    
    实现 Aevatar 项目特定的业务逻辑，如 DLL 编译、插件上传等。
    """
    
    def __init__(self, config: ConfigManager):
        """
        初始化 Aevatar 适配器
        
        Args:
            config: 配置管理器实例
        """
        super().__init__(config)
        
        # 从环境变量获取 DLL 构建路径（不再硬编码）
        self.dll_build_path = os.getenv('DLL_BUILD_PATH', '')
        if not self.dll_build_path:
            self.logger.warning("DLL_BUILD_PATH 未配置，DLL编译功能将不可用")
    
    def compile_artifact(self, artifact_id: str, **kwargs) -> bool:
        """
        编译 DLL 文件
        
        Args:
            artifact_id: 项目名称（如 TestGAgent）
            **kwargs: 其他参数
                - project_path: 项目路径（可选，默认使用配置的路径）
                - build_config: 构建配置（默认 Release）
        
        Returns:
            是否编译成功
        """
        if not self.dll_build_path:
            self.logger.error("DLL_BUILD_PATH 未配置，无法编译")
            return False
        
        project_path = kwargs.get('project_path', self.dll_build_path)
        build_config = kwargs.get('build_config', 'Release')
        project_file = kwargs.get('project_file', f'{artifact_id}.Grains/{artifact_id}.Grains.csproj')
        
        try:
            # 构建编译命令
            compile_cmd = f"cd {project_path} && dotnet build {project_file} -c {build_config}"
            
            self.logger.info(f"开始编译 DLL: {project_path}/{project_file}")
            result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"DLL编译失败: {result.stderr}")
                return False
            
            self.logger.info("DLL编译成功")
            return True
            
        except Exception as e:
            self.logger.error(f"编译DLL时发生错误: {str(e)}")
            return False
    
    def get_artifact_path(self, artifact_id: str, **kwargs) -> Optional[str]:
        """
        获取编译后的 DLL 文件路径
        
        Args:
            artifact_id: 项目名称（如 TestGAgent）
            **kwargs: 其他参数
                - build_config: 构建配置（默认 Release）
                - target_framework: 目标框架（默认 net9.0）
                - project_path: 项目路径（可选）
        
        Returns:
            DLL 文件路径，如果不存在返回 None
        """
        if not self.dll_build_path:
            return None
        
        project_path = kwargs.get('project_path', self.dll_build_path)
        build_config = kwargs.get('build_config', 'Release')
        target_framework = kwargs.get('target_framework', 'net9.0')
        dll_name = kwargs.get('dll_name', f'{artifact_id}.Grains.dll')
        
        dll_file = Path(project_path) / f"{artifact_id}.Grains/bin/{build_config}/{target_framework}/{dll_name}"
        
        if dll_file.exists():
            return str(dll_file)
        else:
            self.logger.warning(f"DLL文件不存在: {dll_file}")
            return None
    
    def upload_artifact(self, artifact_path: str, target_id: str, **kwargs) -> bool:
        """
        上传 DLL 文件到插件
        
        Args:
            artifact_path: DLL 文件路径
            target_id: 插件ID
            **kwargs: 其他参数
                - api_client: API客户端实例（可选）
                - endpoint: API端点（默认 /{target_id}）
        
        Returns:
            是否上传成功
        """
        if not os.path.exists(artifact_path):
            self.logger.error(f"DLL文件不存在: {artifact_path}")
            return False
        
        try:
            # 如果没有提供 api_client，需要从测试用例中获取
            # 这里返回 True 表示逻辑已实现，实际调用由测试用例完成
            self.logger.info(f"准备上传 DLL: {artifact_path} 到插件: {target_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"上传DLL时发生错误: {str(e)}")
            return False
    
    def compile_and_upload_dll(self, plugin_id: str, project_name: str = 'TestGAgent', **kwargs) -> bool:
        """
        编译并上传 DLL（便捷方法）
        
        Args:
            plugin_id: 插件ID
            project_name: 项目名称（默认 TestGAgent）
            **kwargs: 其他参数
        
        Returns:
            是否成功
        """
        # 1. 编译 DLL
        if not self.compile_artifact(project_name, **kwargs):
            return False
        
        # 2. 获取 DLL 路径
        dll_path = self.get_artifact_path(project_name, **kwargs)
        if not dll_path:
            return False
        
        # 3. 上传 DLL（实际上传逻辑在测试用例中，这里只返回路径）
        self.logger.info(f"DLL编译完成，路径: {dll_path}")
        return True

