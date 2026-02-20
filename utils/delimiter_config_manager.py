"""分隔符配置管理器"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .path_utils import get_config_path


@dataclass
class DelimiterConfig:
    """分隔符配置数据类"""
    name: str
    description: str
    delimiter_start: str
    delimiter_end: str
    start_pos: int
    end_pos: int
    preview_example: str

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "delimiter_start": self.delimiter_start,
            "delimiter_end": self.delimiter_end,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "preview_example": self.preview_example
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DelimiterConfig":
        """从字典创建配置对象"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            delimiter_start=data.get("delimiter_start", "_"),
            delimiter_end=data.get("delimiter_end", "_"),
            start_pos=data.get("start_pos", 1),
            end_pos=data.get("end_pos", 2),
            preview_example=data.get("preview_example", "")
        )

    def validate(self) -> tuple[bool, str]:
        """
        验证配置参数的有效性
        
        Returns:
            (是否有效, 错误信息)
        """
        if not self.name:
            return False, "配置名称不能为空"

        if not self.delimiter_start:
            return False, "起始分隔符不能为空"

        if not self.delimiter_end:
            return False, "结束分隔符不能为空"

        if self.start_pos == 0:
            return False, "起始位置不能为0"

        if self.end_pos == 0:
            return False, "结束位置不能为0"

        if self.start_pos == -1 and self.end_pos == -1:
            return False, "起始位置和结束位置不能同时为-1"

        return True, ""


class DelimiterConfigManager:
    """分隔符配置管理器"""

    DEFAULT_CONFIG_FILE = "delimiter_configs.json"

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

        self._configs: List[DelimiterConfig] = []
        self._load_error: Optional[str] = None

    @property
    def configs(self) -> List[DelimiterConfig]:
        """获取配置列表"""
        return self._configs

    @property
    def load_error(self) -> Optional[str]:
        """获取加载错误信息"""
        return self._load_error

    @property
    def config_file_path(self) -> Path:
        """获取配置文件路径"""
        return self.config_dir / self.DEFAULT_CONFIG_FILE

    def load_configs(self) -> bool:
        """
        加载配置文件
        
        Returns:
            是否加载成功
        """
        self._configs = []
        self._load_error = None

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

        if not isinstance(data, list):
            self._load_error = "配置文件格式错误: 根元素必须是数组"
            return False

        valid_configs = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                self._load_error = f"配置项 {index + 1} 格式错误: 必须是对象"
                return False

            config = DelimiterConfig.from_dict(item)
            is_valid, error_msg = config.validate()

            if not is_valid:
                self._load_error = f"配置项 '{config.name or index + 1}' 验证失败: {error_msg}"
                return False

            valid_configs.append(config)

        self._configs = valid_configs
        return True

    def get_config_by_name(self, name: str) -> Optional[DelimiterConfig]:
        """
        根据名称获取配置
        
        Args:
            name: 配置名称
            
        Returns:
            配置对象，未找到返回None
        """
        for config in self._configs:
            if config.name == name:
                return config
        return None

    def get_config_names(self) -> List[str]:
        """获取所有配置名称列表"""
        return [config.name for config in self._configs]

    def save_configs(self, configs: List[DelimiterConfig]) -> tuple[bool, str]:
        """
        保存配置到文件
        
        Args:
            configs: 配置列表
            
        Returns:
            (是否成功, 错误信息)
        """
        if not self.config_dir.exists():
            try:
                self.config_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                return False, f"创建配置目录失败: {str(e)}"

        data = [config.to_dict() for config in configs]

        try:
            with open(self.config_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            return False, f"写入配置文件失败: {str(e)}"

        self._configs = configs
        return True, ""

    def add_config(self, config: DelimiterConfig) -> tuple[bool, str]:
        """
        添加新配置
        
        Args:
            config: 配置对象
            
        Returns:
            (是否成功, 错误信息)
        """
        is_valid, error_msg = config.validate()
        if not is_valid:
            return False, error_msg

        if self.get_config_by_name(config.name):
            return False, f"配置名称 '{config.name}' 已存在"

        self._configs.append(config)
        return self.save_configs(self._configs)

    def update_config(self, old_name: str, config: DelimiterConfig) -> tuple[bool, str]:
        """
        更新配置
        
        Args:
            old_name: 原配置名称
            config: 新配置对象
            
        Returns:
            (是否成功, 错误信息)
        """
        is_valid, error_msg = config.validate()
        if not is_valid:
            return False, error_msg

        for i, c in enumerate(self._configs):
            if c.name == old_name:
                if old_name != config.name and self.get_config_by_name(config.name):
                    return False, f"配置名称 '{config.name}' 已存在"
                self._configs[i] = config
                return self.save_configs(self._configs)

        return False, f"未找到配置 '{old_name}'"

    def delete_config(self, name: str) -> tuple[bool, str]:
        """
        删除配置
        
        Args:
            name: 配置名称
            
        Returns:
            (是否成功, 错误信息)
        """
        for i, config in enumerate(self._configs):
            if config.name == name:
                self._configs.pop(i)
                return self.save_configs(self._configs)

        return False, f"未找到配置 '{name}'"
