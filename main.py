import sys

from pathlib import Path



from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import QIcon

from views import FileClassifierWindow
from viewmodels import FileClassifierViewModel


def load_stylesheet() -> str:
    """加载样式表"""
    style_path = Path(__file__).parent / "styles" / "file_classifier.qss"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_icon() -> QIcon:
    """加载图标"""
    icon_path = Path(__file__).parent / "file.ico"
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()


def main() -> int:
    """应用入口函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("EasyFc")
    app.setOrganizationName("EasyFc")

    app_icon = load_icon()
    app.setWindowIcon(app_icon)

    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    viewmodel = FileClassifierViewModel()
    main_window = FileClassifierWindow()
    main_window.viewmodel = viewmodel
    main_window.setWindowIcon(app_icon)

    viewmodel.progress_updated.connect(main_window._on_progress_updated)
    viewmodel.status_changed.connect(main_window._on_status_changed)
    viewmodel.classification_started.connect(main_window._on_classification_started)
    viewmodel.classification_finished.connect(main_window._on_classification_finished)
    viewmodel.error_occurred.connect(main_window._on_error_occurred)

    main_window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
