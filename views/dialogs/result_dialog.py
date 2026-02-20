"""分类结果对话框"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QGroupBox,
    QListWidget, QListWidgetItem, QPushButton
)

from views.styles import RESULT_DIALOG_STYLE


class ResultDialog(QDialog):
    """分类结果对话框"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("分类结果")
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        self.setStyleSheet(RESULT_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        group = QGroupBox("处理结果")
        layout.addWidget(group)

        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)

        self.result_list = QListWidget()
        group_layout.addWidget(self.result_list)

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignCenter)

    def set_results(self, success_files: list, failed_files: list):
        """设置分类结果"""
        self.result_list.clear()

        for success_file in success_files:
            item = QListWidgetItem()
            file_name = success_file.get("file_name", "未知文件")
            max_length = 40
            if len(file_name) > max_length:
                file_name = file_name[:max_length - 3] + "..."
            category = success_file.get("category", "未知分类")
            item.setText(f"✓ {file_name} → {category}")
            self.result_list.addItem(item)

        for failed_file in failed_files:
            item = QListWidgetItem()
            file_name = failed_file.get("file_name", "未知文件")
            max_length = 40
            if len(file_name) > max_length:
                file_name = file_name[:max_length - 3] + "..."
            error = failed_file.get("error", "未知错误")
            item.setText(f"✗ {file_name} - {error}")
            self.result_list.addItem(item)

    def clear_results(self):
        """清空结果"""
        self.result_list.clear()
