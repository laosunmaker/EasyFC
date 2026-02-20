"""文件分类器模型"""

import os
from pathlib import Path
from typing import Callable, Optional

from utils.file_utils import (
    copy_file,
    create_dir_if_not_exists,
    get_extension,
)


class FileClassifier:
    """文件分类器基类"""

    def __init__(self, target_dir: str):
        """
        初始化分类器

        Args:
            target_dir: 目标目录
        """
        if not target_dir:
            raise ValueError("target_dir参数不能为空")
        self.target_dir = target_dir
        self.result = {
            "success_count": 0,
            "failed_count": 0,
            "failed_files": [],
            "success_files": []
        }

    def _add_failed_file(self, file_path: str, file_name: str, error: str):
        """添加失败文件记录"""
        self.result["failed_count"] += 1
        self.result["failed_files"].append({
            "file_path": file_path,
            "file_name": file_name,
            "error": error
        })

    def _add_success_file(self, file_path: str, file_name: str, category: str):
        """添加成功文件记录"""
        self.result["success_count"] += 1
        self.result["success_files"].append({
            "file_path": file_path,
            "file_name": file_name,
            "category": category
        })

    def _create_category_dir(self, category_dir: str) -> bool:
        """
        创建分类目录

        Args:
            category_dir: 分类目录路径

        Returns:
            是否成功
        """
        try:
            create_dir_if_not_exists(category_dir)
            return True
        except Exception:
            return False

    def _process_file(self, file_path: str, file_name: str, category_dir: str, delete_source: bool = False) -> bool:
        """
        处理单个文件

        Args:
            file_path: 文件路径
            file_name: 文件名
            category_dir: 分类目录
            delete_source: 是否删除源文件

        Returns:
            是否成功
        """
        success, error_msg = copy_file(category_dir, file_path, delete_source)
        return success


class ExtensionClassifier(FileClassifier):
    """使用扩展名分类文件的分类器"""

    def __init__(self, extensions_map: dict, target_dir: str, delete_source: bool = False):
        """
        初始化扩展名分类器

        Args:
            extensions_map: 扩展名映射表，键为扩展名，值为分类名称
            target_dir: 目标目录
            delete_source: 是否删除源文件
        """
        super().__init__(target_dir)
        self.extensions_map = {k.lower(): v for k, v in extensions_map.items()}
        self.delete_source = delete_source

    def classify(self, files: list, progress_callback: Optional[Callable[[int, str], None]] = None) -> dict:
        """
        使用扩展名分类文件

        Args:
            files: 文件列表，每个元素为(绝对路径, 文件名, 层级深度)
            progress_callback: 进度回调函数，参数为(已处理数量, 当前文件名)

        Returns:
            处理结果字典
        """
        self.result = {
            "success_count": 0,
            "failed_count": 0,
            "failed_files": [],
            "success_files": []
        }

        total_files = len(files)
        for index, file_info in enumerate(files):
            file_path = file_info[0]
            file_name = file_info[1]

            if progress_callback:
                progress_callback(index + 1, file_name)

            extension = get_extension(file_name)

            if not extension:
                continue

            extension_lower = extension.lower()

            if extension_lower in self.extensions_map:
                category_name = self.extensions_map[extension_lower]
            else:
                category_name = extension.upper()

            category_dir = os.path.join(self.target_dir, category_name)

            if not self._create_category_dir(category_dir):
                self._add_failed_file(file_path, file_name, "创建目录失败")
                continue

            if self._process_file(file_path, file_name, category_dir, self.delete_source):
                self._add_success_file(file_path, file_name, category_name)
            else:
                self._add_failed_file(file_path, file_name, "复制文件失败")

        return self.result


class DelimiterClassifier(FileClassifier):
    """使用分隔符分类文件的分类器"""

    def __init__(
        self,
        target_dir: str,
        delimiter_start_str: str = "_",
        delimiter_end_str: str = "_",
        delimiter_start_pos: int = 1,
        delimiter_end_pos: int = 2,
        delete_source: bool = False
    ):
        """
        初始化分隔符分类器

        Args:
            target_dir: 目标目录
            delimiter_start_str: 起始分隔符字符串
            delimiter_end_str: 结束分隔符字符串
            delimiter_start_pos: 起始分隔符位置
            delimiter_end_pos: 结束分隔符位置
            delete_source: 是否删除源文件
        """
        super().__init__(target_dir)

        if not delimiter_start_str or not delimiter_end_str:
            raise ValueError("分隔符字符串不能为空")
        if delimiter_end_pos == -1 and delimiter_start_pos == -1:
            raise ValueError("起始分隔符位置和结束分隔符位置不能同时为-1")

        self.delimiter_start_str = delimiter_start_str
        self.delimiter_end_str = delimiter_end_str
        self.delimiter_start_pos = delimiter_start_pos
        self.delimiter_end_pos = delimiter_end_pos
        self.delete_source = delete_source

    def _find_nth_occurrence(self, text: str, substring: str, n: int) -> int:
        """查找字符串中第n个子串的位置"""
        if n < 1 or not substring:
            return -1

        index = -len(substring)
        for _ in range(n):
            index = text.find(substring, index + len(substring))
            if index == -1:
                return -1
        return index

    def _extract_category_name(self, file_name: str) -> str:
        """从文件名中提取分类名称"""
        if not file_name or not self.delimiter_start_str:
            return ""

        file_name_no_ext = os.path.splitext(file_name)[0]

        if self.delimiter_end_pos == -1:
            start_idx = self._find_nth_occurrence(file_name_no_ext, self.delimiter_start_str, self.delimiter_start_pos)
            if start_idx == -1:
                return ""
            return file_name_no_ext[start_idx + len(self.delimiter_start_str):]

        if self.delimiter_start_pos == -1:
            end_idx = self._find_nth_occurrence(file_name_no_ext, self.delimiter_end_str, self.delimiter_end_pos)
            if end_idx == -1:
                return ""
            return file_name_no_ext[:end_idx]

        start_idx = self._find_nth_occurrence(file_name_no_ext, self.delimiter_start_str, self.delimiter_start_pos)
        end_idx = self._find_nth_occurrence(file_name_no_ext, self.delimiter_end_str, self.delimiter_end_pos)

        if start_idx == -1 or end_idx == -1:
            return ""

        return file_name_no_ext[start_idx + len(self.delimiter_start_str):end_idx]

    def classify(self, files: list, progress_callback: Optional[Callable[[int, str], None]] = None) -> dict:
        """
        使用分隔符分类文件

        Args:
            files: 文件列表，每个元素为(绝对路径, 文件名, 层级深度)
            progress_callback: 进度回调函数，参数为(已处理数量, 当前文件名)

        Returns:
            处理结果字典
        """
        self.result = {
            "success_count": 0,
            "failed_count": 0,
            "failed_files": [],
            "success_files": []
        }

        for index, file_info in enumerate(files):
            file_path = file_info[0]
            file_name = file_info[1]

            if progress_callback:
                progress_callback(index + 1, file_name)

            category_name = self._extract_category_name(file_name)

            if not category_name:
                self._add_failed_file(
                    file_path,
                    file_name,
                    f"无法提取分类名称：起始分隔符位置{self.delimiter_start_pos}或结束分隔符位置{self.delimiter_end_pos}未找到"
                )
                continue

            category_dir = os.path.join(self.target_dir, category_name)

            if not self._create_category_dir(category_dir):
                self._add_failed_file(file_path, file_name, "创建目录失败")
                continue

            if self._process_file(file_path, file_name, category_dir, self.delete_source):
                self._add_success_file(file_path, file_name, category_name)
            else:
                self._add_failed_file(file_path, file_name, "复制文件失败")

        return self.result
