"""扩展名映射设置对话框"""

import json
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QAbstractItemView
)

from views.styles import EXTENSION_SETTINGS_DIALOG_STYLE


class ExtensionSettingsDialog(QDialog):
    """扩展名映射设置对话框"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._updating_from_viewmodel: bool = False
        self._config_manager = None
        self._setup_ui()
        self._setup_connections()
        self._load_configs()

    def _load_configs(self):
        """加载配置"""
        from utils.extension_config_manager import ExtensionConfigManager

        self._config_manager = ExtensionConfigManager()
        success = self._config_manager.load_configs()

        self._refresh_table()

        if not success and self._config_manager.load_error:
            QMessageBox.warning(self, "加载配置失败", self._config_manager.load_error)

    def _refresh_table(self, filter_text: str = ""):
        """刷新映射表"""
        self.mapping_table.setRowCount(0)

        if not self._config_manager:
            return

        if filter_text:
            mappings = self._config_manager.search_mappings(filter_text)
        else:
            mappings = self._config_manager.mappings

        for ext, category in sorted(mappings.items()):
            row = self.mapping_table.rowCount()
            self.mapping_table.insertRow(row)
            self.mapping_table.setItem(row, 0, QTableWidgetItem(ext))
            self.mapping_table.setItem(row, 1, QTableWidgetItem(category))

        self.count_label.setText(f"共 {len(mappings)} 条映射")

    def _on_search_changed(self, text: str):
        """搜索文本改变"""
        self._refresh_table(text)

    def _on_add_mapping(self):
        """添加映射"""
        ext = self.ext_input.text().strip().lstrip(".")
        category = self.category_input.text().strip()

        if not ext:
            QMessageBox.warning(self, "输入错误", "请输入扩展名")
            return

        if not category:
            QMessageBox.warning(self, "输入错误", "请输入分类名称")
            return

        success, error_msg = self._config_manager.add_mapping(ext, category)
        if not success:
            QMessageBox.warning(self, "添加失败", error_msg)
            return

        self.ext_input.clear()
        self.category_input.clear()
        self._refresh_table(self.search_input.text())

    def _on_delete_mapping(self):
        """删除映射"""
        current_row = self.mapping_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "删除失败", "请先选择要删除的映射")
            return

        ext_item = self.mapping_table.item(current_row, 0)
        if not ext_item:
            return

        ext = ext_item.text()
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除扩展名 '{ext}' 的映射吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._config_manager.delete_mapping(ext)
            self._refresh_table(self.search_input.text())

    def _on_save(self):
        """保存配置"""
        success, error_msg = self._config_manager.save_configs()
        if success:
            QMessageBox.information(self, "保存成功", "扩展名映射配置已保存")
            self.accept()
        else:
            QMessageBox.warning(self, "保存失败", error_msg)

    def _on_load_default(self):
        """加载默认配置"""
        from utils.extension_config_manager import ExtensionConfigManager

        self._config_manager = ExtensionConfigManager()
        success = self._config_manager.load_configs()

        if success:
            self._refresh_table(self.search_input.text())
            QMessageBox.information(self, "加载成功", "已加载默认扩展名映射")
        else:
            QMessageBox.warning(self, "加载失败", self._config_manager.load_error or "未知错误")

    def get_extension_map_json(self) -> str:
        """获取扩展名映射JSON"""
        return json.dumps(self._config_manager.mappings, ensure_ascii=False, indent=4)

    def set_extension_map_json(self, value: str):
        """设置扩展名映射JSON"""
        try:
            mappings = json.loads(value)
            if isinstance(mappings, dict):
                self._config_manager.import_from_dict(mappings)
                self._refresh_table()
        except json.JSONDecodeError:
            pass

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("扩展名映射设置")
        self.setMinimumSize(600, 500)
        self.resize(700, 550)
        self.setStyleSheet(EXTENSION_SETTINGS_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        search_label = QLabel("搜索:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入扩展名或分类名称...")

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)

        layout.addLayout(search_layout)

        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(2)
        self.mapping_table.setHorizontalHeaderLabels(["扩展名", "分类名称"])
        self.mapping_table.horizontalHeader().setStretchLastSection(True)
        self.mapping_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.mapping_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.mapping_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.mapping_table)

        self.count_label = QLabel("共 0 条映射")
        self.count_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.count_label)

        add_group = QGroupBox("添加新映射")
        add_layout = QHBoxLayout(add_group)
        add_layout.setSpacing(10)

        ext_label = QLabel("扩展名:")
        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText("如: pdf")
        self.ext_input.setMaximumWidth(100)

        category_label = QLabel("分类:")
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("如: PDF 文件")

        self.add_button = QPushButton("添加")
        self.add_button.setObjectName("addButton")

        add_layout.addWidget(ext_label)
        add_layout.addWidget(self.ext_input)
        add_layout.addWidget(category_label)
        add_layout.addWidget(self.category_input, 1)
        add_layout.addWidget(self.add_button)

        layout.addWidget(add_group)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.default_button = QPushButton("加载默认")
        self.default_button.setObjectName("defaultButton")

        self.delete_button = QPushButton("删除选中")
        self.delete_button.setObjectName("deleteButton")

        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("saveButton")

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("cancelButton")

        button_layout.addWidget(self.default_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _setup_connections(self):
        """设置信号连接"""
        self.search_input.textChanged.connect(self._on_search_changed)
        self.add_button.clicked.connect(self._on_add_mapping)
        self.delete_button.clicked.connect(self._on_delete_mapping)
        self.save_button.clicked.connect(self._on_save)
        self.cancel_button.clicked.connect(self.reject)
        self.default_button.clicked.connect(self._on_load_default)
