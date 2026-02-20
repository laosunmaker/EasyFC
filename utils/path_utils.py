"""路径工具模块"""

import os
import sys
from pathlib import Path


def get_base_path() -> Path:
    """
    获取应用基础路径，兼容开发环境和打包后环境
    
    Returns:
        开发环境: 返回项目根目录
        打包后: 返回 exe 所在目录
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    
    nuitka_dir = os.environ.get('NUITKA_ONEFILE_DIRECTORY', '')
    if nuitka_dir:
        return Path(nuitka_dir)
    
    base_exe = getattr(sys, '_base_executable', None)
    if base_exe and base_exe != sys.executable:
        return Path(base_exe).parent
    
    return Path(__file__).parent.parent


def get_config_path() -> Path:
    """获取配置文件目录"""
    return get_base_path() / "config"


def get_styles_path() -> Path:
    """获取样式文件目录"""
    return get_base_path() / "styles"


def get_resource_path(relative_path: str) -> Path:
    """
    获取资源文件的绝对路径
    
    Args:
        relative_path: 相对于应用根目录的路径
        
    Returns:
        资源文件的绝对路径
    """
    return get_base_path() / relative_path
