"""分隔符设置对话框"""

import os
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QComboBox
)

from views.styles import DELIMITER_SETTINGS_DIALOG_STYLE


class DelimiterSettingsDialog(QDialog):
    """分隔符设置对话框"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._config_manager = None
        self._setup_ui()
        self._setup_connections()
        self._load_configs()

    def _load_configs(self):
        """加载配置列表"""
        from utils.delimiter_config_manager import DelimiterConfigManager

        self._config_manager = DelimiterConfigManager()
        success = self._config_manager.load_configs()

        self.config_combo.clear()
        self.config_combo.addItem("-- 请选择配置方案 --")

        if success:
            for config in self._config_manager.configs:
                self.config_combo.addItem(config.name)
        elif self._config_manager.load_error:
            self.config_combo.addItem(f"[加载失败] {self._config_manager.load_error}")

    def _on_config_selected(self, index: int):
        """配置选择改变"""
        if index <= 0:
            return

        config_name = self.config_combo.currentText()
        if not self._config_manager:
            return

        config = self._config_manager.get_config_by_name(config_name)
        if not config:
            return

        self.delimiter_start_edit.blockSignals(True)
        self.delimiter_end_edit.blockSignals(True)
        self.delimiter_start_pos_spin.blockSignals(True)
        self.delimiter_end_pos_spin.blockSignals(True)

        self.delimiter_start_edit.setText(config.delimiter_start)
        self.delimiter_end_edit.setText(config.delimiter_end)
        self.delimiter_start_pos_spin.setText(str(config.start_pos))
        self.delimiter_end_pos_spin.setText(str(config.end_pos))

        self.delimiter_start_edit.blockSignals(False)
        self.delimiter_end_edit.blockSignals(False)
        self.delimiter_start_pos_spin.blockSignals(False)
        self.delimiter_end_pos_spin.blockSignals(False)

        self._update_preview()

    def _generate_demo_filename(self, start_delim: str, end_delim: str, start_pos: int, end_pos: int) -> str:
        if start_pos == -1 and end_pos == -1:
            return "2026年2月1日.png"

        if start_pos == -1:
            end_count = end_pos if end_pos > 0 else 1
            if start_delim == end_delim:
                parts = ["2026年2月1日"]
                for i in range(end_count):
                    parts.append(f"part{i + 1}")
                return end_delim.join(parts) + ".png"
            else:
                parts = ["2026年2月1日"]
                for i in range(end_count):
                    parts.append(f"part{i + 1}")
                return end_delim.join(parts) + ".png"

        if end_pos == -1:
            start_count = start_pos if start_pos > 0 else 1
            if start_delim == end_delim:
                parts = ["img"]
                for i in range(start_count):
                    if i == 0:
                        parts.append("2026年2月1日")
                    else:
                        parts.append(f"part{i + 1}")
                return start_delim.join(parts) + ".png"
            else:
                parts = ["img"]
                for i in range(start_count):
                    if i == 0:
                        parts.append("2026年2月1日")
                    else:
                        parts.append(f"part{i + 1}")
                return start_delim.join(parts) + ".png"

        start_count = start_pos if start_pos > 0 else 1
        end_count = end_pos if end_pos > 0 else 1

        if start_delim == end_delim:
            total_parts = max(start_count, end_count) + 1
            parts = []
            for i in range(total_parts):
                if i == 0:
                    parts.append("img")
                elif i == 1:
                    parts.append("2026年2月1日")
                elif i == 2:
                    parts.append("54864848")
                else:
                    parts.append(f"part{i}")
            return start_delim.join(parts) + ".png"
        else:
            start_parts = start_count + 1
            end_parts = end_count + 1

            start_segments = []
            for i in range(start_parts):
                if i == 0:
                    start_segments.append("img")
                elif i == 1:
                    start_segments.append("2026年2月1日")
                else:
                    start_segments.append(f"s{i}")

            end_segments = []
            for i in range(end_parts):
                if i == 0:
                    end_segments.append("category")
                elif i == 1:
                    end_segments.append("54864848")
                else:
                    end_segments.append(f"e{i}")

            start_result = start_delim.join(start_segments)
            end_result = end_delim.join(end_segments)

            return f"{start_result}{end_result}.png"

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("分隔符设置")
        self.setMinimumSize(500, 320)
        self.resize(550, 380)
        self.setStyleSheet(DELIMITER_SETTINGS_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        config_layout = QHBoxLayout()
        config_layout.setSpacing(10)

        config_label = QLabel("配置方案:")
        self.config_combo = QComboBox()

        config_layout.addWidget(config_label)
        config_layout.addWidget(self.config_combo, 1)

        layout.addLayout(config_layout)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)

        start_label = QLabel("起始分隔符:")
        self.delimiter_start_edit = QLineEdit()
        self.delimiter_start_edit.setText("_")
        self.delimiter_start_edit.setMaximumWidth(150)

        end_label = QLabel("结束分隔符:")
        self.delimiter_end_edit = QLineEdit()
        self.delimiter_end_edit.setText("_")
        self.delimiter_end_edit.setMaximumWidth(150)

        start_pos_label = QLabel("起始位置:")
        self.delimiter_start_pos_spin = QLineEdit()
        self.delimiter_start_pos_spin.setText("1")
        self.delimiter_start_pos_spin.setMaximumWidth(80)

        end_pos_label = QLabel("结束位置:")
        self.delimiter_end_pos_spin = QLineEdit()
        self.delimiter_end_pos_spin.setText("2")
        self.delimiter_end_pos_spin.setMaximumWidth(80)

        grid_layout.addWidget(start_label, 0, 0)
        grid_layout.addWidget(self.delimiter_start_edit, 0, 1)
        grid_layout.addWidget(end_label, 0, 2)
        grid_layout.addWidget(self.delimiter_end_edit, 0, 3)

        grid_layout.addWidget(start_pos_label, 1, 0)
        grid_layout.addWidget(self.delimiter_start_pos_spin, 1, 1)
        grid_layout.addWidget(end_pos_label, 1, 2)
        grid_layout.addWidget(self.delimiter_end_pos_spin, 1, 3)

        layout.addLayout(grid_layout)

        demo_group = QGroupBox("预览")
        demo_layout = QVBoxLayout(demo_group)

        self.demo_label = QLabel()
        self.demo_label.setTextFormat(Qt.TextFormat.RichText)
        self.demo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.demo_label.setStyleSheet("font-size: 14px; padding: 8px;")
        demo_layout.addWidget(self.demo_label)

        layout.addWidget(demo_group)

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

        self.config_combo.currentIndexChanged.connect(self._on_config_selected)

        self.delimiter_start_edit.textChanged.connect(self._update_preview)
        self.delimiter_end_edit.textChanged.connect(self._update_preview)
        self.delimiter_start_pos_spin.textChanged.connect(self._update_preview)
        self.delimiter_end_pos_spin.textChanged.connect(self._update_preview)

        self._update_preview()

    def _update_preview(self):
        """更新预览显示"""
        start_delim = self.delimiter_start_edit.text()
        end_delim = self.delimiter_end_edit.text()

        try:
            start_pos = int(self.delimiter_start_pos_spin.text())
        except ValueError:
            start_pos = 1

        try:
            end_pos = int(self.delimiter_end_pos_spin.text())
        except ValueError:
            end_pos = 2

        filename = self._generate_demo_filename(start_delim, end_delim, start_pos, end_pos)
        filename_no_ext = os.path.splitext(filename)[0]

        start_indices = []
        end_indices = []

        if start_delim:
            idx = -len(start_delim)
            while True:
                idx = filename_no_ext.find(start_delim, idx + len(start_delim))
                if idx == -1:
                    break
                start_indices.append(idx)

        if end_delim:
            idx = -len(end_delim)
            while True:
                idx = filename_no_ext.find(end_delim, idx + len(end_delim))
                if idx == -1:
                    break
                end_indices.append(idx)

        extract_start = -1
        extract_end = -1

        if start_pos == -1:
            extract_start = 0
        elif start_delim and start_pos > 0:
            if start_pos <= len(start_indices):
                extract_start = start_indices[start_pos - 1] + len(start_delim)

        if end_pos == -1:
            extract_end = len(filename_no_ext)
        elif end_delim and end_pos > 0:
            if end_pos <= len(end_indices):
                extract_end = end_indices[end_pos - 1]

        result = ""
        for i, char in enumerate(filename):
            if extract_start != -1 and extract_end != -1 and extract_start < extract_end:
                if i == extract_start:
                    result += '<span style="background-color: #4CAF50; color: white;">'
                if i == extract_end:
                    result += '</span>'
            result += char

        if extract_start != -1 and extract_end != -1 and extract_start < extract_end:
            if extract_end >= len(filename):
                result += '</span>'

        extracted = ""
        if extract_start != -1 and extract_end != -1 and extract_start < extract_end:
            extracted = filename[extract_start:extract_end]

        if extracted:
            preview_text = f'{result}  →  <b style="color: #4CAF50;">{extracted}</b>'
        else:
            preview_text = f'{result}  →  <span style="color: #f44336;">无法提取</span>'

        self.demo_label.setText(preview_text)

    def get_delimiter_start(self) -> str:
        return self.delimiter_start_edit.text()

    def set_delimiter_start(self, value: str):
        self.delimiter_start_edit.blockSignals(True)
        self.delimiter_start_edit.setText(value)
        self.delimiter_start_edit.blockSignals(False)
        self._update_preview()

    def get_delimiter_end(self) -> str:
        return self.delimiter_end_edit.text()

    def set_delimiter_end(self, value: str):
        self.delimiter_end_edit.blockSignals(True)
        self.delimiter_end_edit.setText(value)
        self.delimiter_end_edit.blockSignals(False)
        self._update_preview()

    def get_delimiter_start_pos(self) -> int:
        try:
            return int(self.delimiter_start_pos_spin.text())
        except ValueError:
            return 1

    def set_delimiter_start_pos(self, value: int):
        self.delimiter_start_pos_spin.blockSignals(True)
        self.delimiter_start_pos_spin.setText(str(value))
        self.delimiter_start_pos_spin.blockSignals(False)
        self._update_preview()

    def get_delimiter_end_pos(self) -> int:
        try:
            return int(self.delimiter_end_pos_spin.text())
        except ValueError:
            return 2

    def set_delimiter_end_pos(self, value: int):
        self.delimiter_end_pos_spin.blockSignals(True)
        self.delimiter_end_pos_spin.setText(str(value))
        self.delimiter_end_pos_spin.blockSignals(False)
        self._update_preview()
