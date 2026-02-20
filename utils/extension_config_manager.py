"""扩展名映射配置管理器"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .path_utils import get_config_path


@dataclass
class ExtensionMapping:
    """扩展名映射数据类"""
    extension: str
    category: str

    def validate(self) -> Tuple[bool, str]:
        """
        验证映射参数的有效性
        
        Returns:
            (是否有效, 错误信息)
        """
        if not self.extension:
            return False, "扩展名不能为空"

        if not self.category:
            return False, "分类名称不能为空"

        if not all(c.isalnum() or c == '_' for c in self.extension):
            return False, "扩展名只能包含字母、数字和下划线"

        return True, ""


class ExtensionConfigManager:
    """扩展名映射配置管理器"""

    DEFAULT_CONFIG_FILE = "extension_configs.json"
    DEFAULT_PROFILE = "default"

    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，默认为应用根目录下的 config
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = get_config_path()

        self._mappings: Dict[str, str] = {}
        self._profiles: List[str] = []
        self._current_profile: str = self.DEFAULT_PROFILE
        self._load_error: Optional[str] = None

    @property
    def mappings(self) -> Dict[str, str]:
        """获取当前映射表"""
        return self._mappings

    @property
    def load_error(self) -> Optional[str]:
        """获取加载错误信息"""
        return self._load_error

    @property
    def config_file_path(self) -> Path:
        """获取配置文件路径"""
        return self.config_dir / self.DEFAULT_CONFIG_FILE

    @property
    def profiles(self) -> List[str]:
        """获取所有配置方案名称"""
        return self._profiles

    @property
    def current_profile(self) -> str:
        """获取当前配置方案名称"""
        return self._current_profile

    def load_configs(self, profile: Optional[str] = None) -> bool:
        """
        加载配置文件
        
        Args:
            profile: 配置方案名称，默认为 default
            
        Returns:
            是否加载成功
        """
        self._mappings = {}
        self._load_error = None
        target_profile = profile or self.DEFAULT_PROFILE

        if not self.config_file_path.exists():
            self._load_error = f"配置文件不存在: {self.config_file_path}"
            return False

        try:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self._load_error = f"配置文件JSON格式错误: {str(e)}"
            return False
        except IOError as e:
            self._load_error = f"读取配置文件失败: {str(e)}"
            return False

        if not isinstance(data, dict):
            self._load_error = "配置文件格式错误: 根元素必须是对象"
            return False

        self._profiles = list(data.keys())

        if target_profile not in data:
            self._load_error = f"配置方案 '{target_profile}' 不存在"
            return False

        profile_data = data[target_profile]
        if not isinstance(profile_data, dict):
            self._load_error = f"配置方案 '{target_profile}' 格式错误: 必须是对象"
            return False

        valid_mappings = {}
        for ext, category in profile_data.items():
            if not isinstance(ext, str) or not isinstance(category, str):
                continue
            ext_lower = ext.lower().lstrip(".")
            valid_mappings[ext_lower] = category

        self._mappings = valid_mappings
        self._current_profile = target_profile
        return True

    def get_category(self, extension: str) -> Optional[str]:
        """
        根据扩展名获取分类
        
        Args:
            extension: 扩展名
            
        Returns:
            分类名称，未找到返回None
        """
        ext_lower = extension.lower().lstrip(".")
        return self._mappings.get(ext_lower)

    def get_all_extensions(self) -> List[str]:
        """获取所有扩展名列表（排序后）"""
        return sorted(self._mappings.keys())

    def add_mapping(self, extension: str, category: str) -> Tuple[bool, str]:
        """
        添加新映射
        
        Args:
            extension: 扩展名
            category: 分类名称
            
        Returns:
            (是否成功, 错误信息)
        """
        mapping = ExtensionMapping(extension=extension.lstrip("."), category=category)
        is_valid, error_msg = mapping.validate()
        if not is_valid:
            return False, error_msg

        ext_lower = mapping.extension.lower()
        self._mappings[ext_lower] = mapping.category
        return True, ""

    def update_mapping(self, extension: str, category: str) -> Tuple[bool, str]:
        """
        更新映射
        
        Args:
            extension: 扩展名
            category: 新的分类名称
            
        Returns:
            (是否成功, 错误信息)
        """
        ext_lower = extension.lower().lstrip(".")
        if ext_lower not in self._mappings:
            return False, f"扩展名 '{extension}' 不存在"

        if not category:
            return False, "分类名称不能为空"

        self._mappings[ext_lower] = category
        return True, ""

    def delete_mapping(self, extension: str) -> Tuple[bool, str]:
        """
        删除映射
        
        Args:
            extension: 扩展名
            
        Returns:
            (是否成功, 错误信息)
        """
        ext_lower = extension.lower().lstrip(".")
        if ext_lower not in self._mappings:
            return False, f"扩展名 '{extension}' 不存在"

        del self._mappings[ext_lower]
        return True, ""

    def save_configs(self) -> Tuple[bool, str]:
        """
        保存配置到文件
        
        Returns:
            (是否成功, 错误信息)
        """
        if not self.config_dir.exists():
            try:
                self.config_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                return False, f"创建配置目录失败: {str(e)}"

        existing_data = {}
        if self.config_file_path.exists():
            try:
                with open(self.config_file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                existing_data = {}

        if not isinstance(existing_data, dict):
            existing_data = {}

        existing_data[self._current_profile] = self._mappings

        try:
            with open(self.config_file_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            return False, f"写入配置文件失败: {str(e)}"

        return True, ""

    def import_from_dict(self, mappings: Dict[str, str]) -> Tuple[bool, str]:
        """
        从字典导入映射
        
        Args:
            mappings: 映射字典
            
        Returns:
            (是否成功, 错误信息)
        """
        if not isinstance(mappings, dict):
            return False, "导入数据必须是字典格式"

        valid_count = 0
        for ext, category in mappings.items():
            if not isinstance(ext, str) or not isinstance(category, str):
                continue
            ext_lower = ext.lower().lstrip(".")
            if ext_lower and category:
                self._mappings[ext_lower] = category
                valid_count += 1

        return True, f"成功导入 {valid_count} 条映射"

    def export_to_dict(self) -> Dict[str, str]:
        """导出映射为字典"""
        return dict(self._mappings)

    def clear_mappings(self):
        """清空所有映射"""
        self._mappings.clear()

    def search_mappings(self, keyword: str) -> Dict[str, str]:
        """
        搜索映射
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的映射字典
        """
        keyword_lower = keyword.lower()
        return {
            ext: cat
            for ext, cat in self._mappings.items()
            if keyword_lower in ext.lower() or keyword_lower in cat.lower()
        }
