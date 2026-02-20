"""文件分类器主窗口视图层"""

from typing import Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QRadioButton, QProgressBar, QMessageBox, QFileDialog,
    QDialog
)
from PySide6.QtCore import Qt

from viewmodels.file_classifier_viewmodel import FileClassifierViewModel
from .dialogs import (
    ResultDialog,
    GeneralSettingsDialog,
    ExtensionSettingsDialog,
    DelimiterSettingsDialog,
)


class FileClassifierWindow(QMainWindow):
    """文件分类器主窗口"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._viewmodel: Optional[FileClassifierViewModel] = None
        self._extension_dialog: Optional[ExtensionSettingsDialog] = None
        self._delimiter_dialog: Optional[DelimiterSettingsDialog] = None
        self._result_dialog: Optional[ResultDialog] = None
        self._general_dialog: Optional[GeneralSettingsDialog] = None
        self._setup_ui()
        self._setup_connections()

    @property
    def viewmodel(self) -> Optional[FileClassifierViewModel]:
        return self._viewmodel

    @viewmodel.setter
    def viewmodel(self, value: FileClassifierViewModel):
        self._viewmodel = value

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("EasyFc")
        self.setMinimumSize(500, 400)
        self.resize(550, 450)

        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        self._create_header(main_layout)
        self._create_path_section(main_layout)
        self._create_classification_mode_section(main_layout)
        self._create_action_section(main_layout)
        self._create_progress_section(main_layout)
        main_layout.addStretch(1)

    def _create_header(self, parent_layout: QVBoxLayout):
        """创建标题区域"""
        title_label = QLabel("EasyFc")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(title_label)

    def _create_path_section(self, parent_layout: QVBoxLayout):
        """创建路径设置区域"""
        group = QGroupBox("路径设置")
        group.setObjectName("pathGroup")

        layout = QVBoxLayout()
        layout.setSpacing(8)

        source_layout = QHBoxLayout()
        source_layout.setSpacing(10)

        source_label = QLabel("源文件夹:")
        self.source_path_edit = QLineEdit()
        self.source_path_edit.setPlaceholderText("选择要分类的文件夹...")
        self.source_path_edit.setReadOnly(True)
        self.browse_source_button = QPushButton("浏览...")
        self.browse_source_button.setObjectName("browseButton")

        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_path_edit, 1)
        source_layout.addWidget(self.browse_source_button)

        target_layout = QHBoxLayout()
        target_layout.setSpacing(10)

        target_label = QLabel("目标文件夹:")
        self.target_path_edit = QLineEdit()
        self.target_path_edit.setPlaceholderText("选择分类结果保存位置...")
        self.browse_target_button = QPushButton("浏览...")
        self.browse_target_button.setObjectName("browseButton")

        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_path_edit, 1)
        target_layout.addWidget(self.browse_target_button)

        layout.addLayout(source_layout)
        layout.addLayout(target_layout)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _create_classification_mode_section(self, parent_layout: QVBoxLayout):
        """创建分类方式选择区域"""
        group = QGroupBox("分类方式")
        group.setObjectName("modeGroup")

        layout = QHBoxLayout()
        layout.setSpacing(20)

        self.extension_radio = QRadioButton("按扩展名分类")
        self.extension_radio.setChecked(True)
        self.extension_radio.setObjectName("extensionRadio")

        self.delimiter_radio = QRadioButton("按分隔符分类")
        self.delimiter_radio.setObjectName("delimiterRadio")

        self.settings_button = QPushButton("分类设置")
        self.settings_button.setObjectName("actionButton")

        layout.addWidget(self.extension_radio)
        layout.addWidget(self.delimiter_radio)
        layout.addStretch(1)
        layout.addWidget(self.settings_button)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _create_action_section(self, parent_layout: QVBoxLayout):
        """创建操作按钮区域"""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.general_settings_button = QPushButton("通用设置")
        self.general_settings_button.setObjectName("generalButton")

        self.result_button = QPushButton("查看结果")
        self.result_button.setObjectName("resultButton")

        self.reset_button = QPushButton("重置")
        self.reset_button.setObjectName("resetButton")

        self.start_button = QPushButton("开始分类")
        self.start_button.setObjectName("startButton")

        layout.addStretch(1)
        layout.addWidget(self.general_settings_button)
        layout.addWidget(self.result_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.start_button)
        layout.addStretch(1)

        parent_layout.addLayout(layout)

    def _create_progress_section(self, parent_layout: QVBoxLayout):
        """创建进度显示区域"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")

        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        parent_layout.addWidget(self.progress_bar)
        parent_layout.addWidget(self.status_label)

    def _setup_connections(self):
        """设置信号槽连接"""
        self.browse_source_button.clicked.connect(self._on_browse_source)
        self.browse_target_button.clicked.connect(self._on_browse_target)
        self.extension_radio.toggled.connect(self._on_mode_changed)
        self.settings_button.clicked.connect(self._on_open_settings)
        self.general_settings_button.clicked.connect(self._on_open_general_settings)
        self.result_button.clicked.connect(self._on_show_result)
        self.start_button.clicked.connect(self._on_start)
        self.reset_button.clicked.connect(self._on_reset)

    @Slot()
    def _on_browse_source(self):
        """浏览选择源文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择源文件夹",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.source_path_edit.setText(folder)

    @Slot()
    def _on_browse_target(self):
        """浏览选择目标文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择目标文件夹",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.target_path_edit.setText(folder)

    @Slot(bool)
    def _on_mode_changed(self, checked: bool):
        """分类方式改变"""
        is_extension_mode = self.extension_radio.isChecked()
        if self._viewmodel:
            self._viewmodel.classification_mode = 0 if is_extension_mode else 1

    @Slot()
    def _on_open_settings(self):
        """打开设置对话框"""
        if not self._viewmodel:
            return

        is_extension_mode = self.extension_radio.isChecked()

        if is_extension_mode:
            dialog = ExtensionSettingsDialog(self)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._viewmodel.extension_map_json = dialog.get_extension_map_json()
        else:
            dialog = DelimiterSettingsDialog(self)
            dialog.set_delimiter_start(self._viewmodel.delimiter_start)
            dialog.set_delimiter_end(self._viewmodel.delimiter_end)
            dialog.set_delimiter_start_pos(self._viewmodel.delimiter_start_pos)
            dialog.set_delimiter_end_pos(self._viewmodel.delimiter_end_pos)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._viewmodel.delimiter_start = dialog.get_delimiter_start()
                self._viewmodel.delimiter_end = dialog.get_delimiter_end()
                self._viewmodel.delimiter_start_pos = dialog.get_delimiter_start_pos()
                self._viewmodel.delimiter_end_pos = dialog.get_delimiter_end_pos()

    @Slot()
    def _on_open_general_settings(self):
        """打开通用设置对话框"""
        if not self._viewmodel:
            return

        dialog = GeneralSettingsDialog(self)
        dialog.set_delete_source(self._viewmodel.delete_source)
        dialog.set_scan_subfolder(self._viewmodel.scan_subfolder)
        dialog.set_specify_depth(self._viewmodel.specify_depth)
        dialog.set_depth(self._viewmodel.scan_depth)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._viewmodel.delete_source = dialog.get_delete_source()
            self._viewmodel.scan_subfolder = dialog.get_scan_subfolder()
            self._viewmodel.specify_depth = dialog.get_specify_depth()
            self._viewmodel.scan_depth = dialog.get_depth()

    @Slot()
    def _on_show_result(self):
        """显示分类结果对话框"""
        if self._result_dialog is None:
            self._result_dialog = ResultDialog(self)

        if self._viewmodel:
            result = self._viewmodel.classification_result
            if result:
                success_files = result.get("success_files", [])
                failed_files = result.get("failed_files", [])
                self._result_dialog.set_results(success_files, failed_files)

        self._result_dialog.show()

    @Slot()
    def _on_start(self):
        """开始分类"""
        if self._viewmodel:
            self._viewmodel.source_folder = self.source_path_edit.text()
            self._viewmodel.target_folder = self.target_path_edit.text()
            self._viewmodel.start_classification()

    @Slot()
    def _on_reset(self):
        """重置设置"""
        self.source_path_edit.clear()
        self.target_path_edit.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("就绪")

        if self._result_dialog:
            self._result_dialog.clear_results()

        if self._viewmodel:
            self._viewmodel.reset_settings()

    @Slot(int, str)
    def _on_progress_updated(self, value: int, message: str):
        """进度更新"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    @Slot(str)
    def _on_status_changed(self, status: str):
        """状态改变"""
        self.status_label.setText(status)

    @Slot()
    def _on_classification_started(self):
        """分类开始"""
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(False)
        self.status_label.setText("正在分类...")

    @Slot(dict)
    def _on_classification_finished(self, result: dict):
        """分类完成"""
        self.progress_bar.setValue(100)
        self.start_button.setEnabled(True)

        success_count = result.get("success_count", 0)
        failed_count = result.get("failed_count", 0)
        total_files = result.get("total_files", 0)

        self.status_label.setText(f"分类完成！共 {total_files} 个文件，成功: {success_count} 个，失败: {failed_count} 个")

        if self._result_dialog is None:
            self._result_dialog = ResultDialog(self)

        success_files = result.get("success_files", [])
        failed_files = result.get("failed_files", [])
        self._result_dialog.set_results(success_files, failed_files)
        self._result_dialog.show()

    @Slot(str)
    def _on_error_occurred(self, error: str):
        """发生错误"""
        self.start_button.setEnabled(True)
        self.status_label.setText("发生错误")
        QMessageBox.critical(self, "错误", error)
