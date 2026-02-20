"""通用设置对话框"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox
)

from views.styles import GENERAL_SETTINGS_DIALOG_STYLE


class GeneralSettingsDialog(QDialog):
    """通用设置对话框"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._updating_from_viewmodel: bool = False
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("通用设置")
        self.setMinimumSize(400, 280)
        self.resize(450, 320)
        self.setStyleSheet(GENERAL_SETTINGS_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        self.delete_source_check = QCheckBox("分类后删除源文件")
        layout.addWidget(self.delete_source_check)

        self.scan_subfolder_check = QCheckBox("扫描子文件夹")
        self.scan_subfolder_check.setChecked(True)
        self.scan_subfolder_check.toggled.connect(self._on_scan_subfolder_toggled)
        layout.addWidget(self.scan_subfolder_check)

        depth_layout = QHBoxLayout()
        depth_layout.setSpacing(10)

        self.specify_depth_check = QCheckBox("指定深度")
        self.specify_depth_check.toggled.connect(self._on_specify_depth_toggled)
        depth_layout.addWidget(self.specify_depth_check)

        depth_label = QLabel("扫描深度:")
        depth_layout.addWidget(depth_label)

        self.depth_input = QLineEdit()
        self.depth_input.setText("1")
        self.depth_input.setMaximumWidth(60)
        self.depth_input.setEnabled(False)
        depth_layout.addWidget(self.depth_input)

        depth_layout.addStretch(1)
        layout.addLayout(depth_layout)

        layout.addStretch(1)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.ok_button = QPushButton("确定")
        self.ok_button.setObjectName("okButton")

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("cancelButton")

        button_layout.addStretch(1)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)

    def _setup_connections(self):
        """设置信号连接"""
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def _on_scan_subfolder_toggled(self, checked: bool):
        """扫描子文件夹状态改变"""
        if not checked:
            self.specify_depth_check.setChecked(False)
            self.specify_depth_check.setEnabled(False)
        else:
            self.specify_depth_check.setEnabled(True)

    def _on_specify_depth_toggled(self, checked: bool):
        """指定深度状态改变"""
        self.depth_input.setEnabled(checked)

    def get_delete_source(self) -> bool:
        return self.delete_source_check.isChecked()

    def set_delete_source(self, value: bool):
        self._updating_from_viewmodel = True
        self.delete_source_check.setChecked(value)
        self._updating_from_viewmodel = False

    def get_scan_subfolder(self) -> bool:
        return self.scan_subfolder_check.isChecked()

    def set_scan_subfolder(self, value: bool):
        self._updating_from_viewmodel = True
        self.scan_subfolder_check.setChecked(value)
        self._on_scan_subfolder_toggled(value)
        self._updating_from_viewmodel = False

    def get_specify_depth(self) -> bool:
        return self.specify_depth_check.isChecked()

    def set_specify_depth(self, value: bool):
        self._updating_from_viewmodel = True
        self.specify_depth_check.setChecked(value)
        self._on_specify_depth_toggled(value)
        self._updating_from_viewmodel = False

    def get_depth(self) -> int:
        try:
            return int(self.depth_input.text())
        except ValueError:
            return 1

    def set_depth(self, value: int):
        self._updating_from_viewmodel = True
        self.depth_input.setText(str(value))
        self._updating_from_viewmodel = False
