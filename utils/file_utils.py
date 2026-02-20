"""文件操作工具类"""

import os
import shutil
from pathlib import Path
from typing import Literal


def get_folder_files(folder_path: str) -> list[tuple[str, str]]:
    """
    获取指定文件夹中所有文件的绝对路径和文件名（含扩展名）

    Args:
        folder_path: 文件夹绝对路径

    Returns:
        包含(绝对路径, 文件名)的元组列表

    Raises:
        ValueError: 文件夹路径不存在或不是目录
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise ValueError(f"路径不存在: {folder_path}")
    if not folder.is_dir():
        raise ValueError(f"不是有效目录: {folder_path}")

    files = []
    for file_path in folder.iterdir():
        if file_path.is_file():
            files.append((str(file_path.absolute()), file_path.name))

    return files


def get_folder_files_recursive(folder_path: str) -> list[tuple[str, str]]:
    """
    递归获取指定文件夹中所有文件的绝对路径和文件名（含扩展名）

    Args:
        folder_path: 文件夹绝对路径

    Returns:
        包含(绝对路径, 文件名)的元组列表

    Raises:
        ValueError: 文件夹路径不存在或不是目录
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise ValueError(f"路径不存在: {folder_path}")
    if not folder.is_dir():
        raise ValueError(f"不是有效目录: {folder_path}")

    files = []
    for file_path in folder.rglob("*"):
        if file_path.is_file():
            files.append((str(file_path.absolute()), file_path.name))

    return files


def get_files_by_extension(
    folder_path: str,
    extensions: str | list[str],
    recursive: bool = False
) -> list[tuple[str, str]]:
    """
    获取指定文件夹中指定扩展名的文件

    Args:
        folder_path: 文件夹绝对路径
        extensions: 文件扩展名（不含点），支持单个或列表
        recursive: 是否递归搜索子目录，默认False

    Returns:
        包含(绝对路径, 文件名)的元组列表

    Raises:
        ValueError: 文件夹路径不存在或不是目录
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise ValueError(f"路径不存在: {folder_path}")
    if not folder.is_dir():
        raise ValueError(f"不是有效目录: {folder_path}")

    if isinstance(extensions, str):
        extensions = [extensions]

    ext_set = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions}

    files = []
    iterator = folder.rglob("*") if recursive else folder.iterdir()

    for file_path in iterator:
        if file_path.is_file() and file_path.suffix.lower() in ext_set:
            files.append((str(file_path.absolute()), file_path.name))

    return files


def get_folder_files_by_depth(
    folder_path: str,
    max_depth: int = 1
) -> list[tuple[str, str, int]]:
    """
    按指定深度遍历嵌套文件夹获取文件

    Args:
        folder_path: 文件夹绝对路径
        max_depth: 最大遍历深度，1表示仅当前目录，2表示当前目录+一级子目录，以此类推

    Returns:
        包含(绝对路径, 文件名, 层级深度)的元组列表，层级从1开始计数

    Raises:
        ValueError: 文件夹路径不存在或不是目录
        ValueError: max_depth必须大于等于1
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise ValueError(f"路径不存在: {folder_path}")
    if not folder.is_dir():
        raise ValueError(f"不是有效目录: {folder_path}")
    if max_depth < 1:
        raise ValueError(f"max_depth必须大于等于1，当前值: {max_depth}")

    files = []

    def _traverse(current_path: Path, current_depth: int):
        if current_depth > max_depth:
            return

        for item in current_path.iterdir():
            if item.is_file():
                files.append((str(item.absolute()), item.name, current_depth))
            elif item.is_dir() and current_depth < max_depth:
                _traverse(item, current_depth + 1)

    _traverse(folder, 1)
    return files


def get_extension(file_name: str) -> str:
    """
    获取文件扩展名（从后往前遇到的第一个点到文件名末尾）

    Args:
        file_name: 文件名

    Returns:
        扩展名（小写，不含点）
    """
    if "." not in file_name:
        return ""
    return file_name.rsplit(".", 1)[-1].lower()


def create_dir_if_not_exists(dir_path: str) -> None:
    """
    如果目录不存在，则创建它。

    Args:
        dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def _generate_unique_filename(file_path: str) -> str:
    """
    生成唯一的文件名，如果文件已存在则在文件名后添加数字编号

    Args:
        file_path: 原始文件路径

    Returns:
        唯一的文件路径
    """
    directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    name, ext = os.path.splitext(file_name)
    counter = 1

    while True:
        new_name = f"{name} ({counter}){ext}"
        new_path = os.path.join(directory, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def copy_file(target_dir: str, file: str, delete_source: bool = False) -> tuple[bool, str]:
    """
    复制文件。

    Args:
        target_dir: 目标目录
        file: 文件路径
        delete_source: 是否删除源文件

    Returns:
        (是否成功, 错误信息)
    """
    try:
        file_name = os.path.basename(file)
        target_path = os.path.join(target_dir, file_name)

        if os.path.exists(target_path):
            target_path = _generate_unique_filename(target_path)

        shutil.copy2(file, target_path)
        if delete_source:
            os.remove(file)
        return True, ""
    except Exception as e:
        return False, str(e)


def get_extension(file_name: str) -> str:
    """
    获取文件扩展名（从后往前遇到的第一个点到文件名末尾）

    Args:
        file_name: 文件名

    Returns:
        扩展名（小写，不含点）
    """
    if "." not in file_name:
        return ""
    return file_name.rsplit(".", 1)[-1].lower()


def create_dir_if_not_exists(dir_path: str) -> None:
    """
    如果目录不存在，则创建它。

    Args:
        dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def _generate_unique_filename(file_path: str) -> str:
    """
    生成唯一的文件名，如果文件已存在则在文件名后添加数字编号

    Args:
        file_path: 原始文件路径

    Returns:
        唯一的文件路径
    """
    directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    name, ext = os.path.splitext(file_name)
    counter = 1

    while True:
        new_name = f"{name} ({counter}){ext}"
        new_path = os.path.join(directory, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1
