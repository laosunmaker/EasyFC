"""共享样式模块"""

DIALOG_BASE_STYLE = """
QDialog {
    background-color: #ffffff;
}
QLabel {
    color: #555555;
    font-size: 13px;
}
"""

BUTTON_PRIMARY_STYLE = """
background-color: #2196F3;
color: white;
border: none;
border-radius: 6px;
padding: 9px 16px;
font-size: 14px;
min-height: 20px;
"""

BUTTON_PRIMARY_HOVER_STYLE = """
background-color: #1976D2;
"""

BUTTON_SUCCESS_STYLE = """
background-color: #4CAF50;
color: white;
border: none;
border-radius: 6px;
padding: 9px 16px;
font-size: 14px;
min-height: 20px;
"""

BUTTON_SUCCESS_HOVER_STYLE = """
background-color: #43A047;
"""

BUTTON_CANCEL_STYLE = """
background-color: #f5f5f5;
color: #666666;
border: none;
border-radius: 6px;
padding: 9px 16px;
font-size: 14px;
min-height: 20px;
"""

BUTTON_CANCEL_HOVER_STYLE = """
background-color: #eeeeee;
"""

BUTTON_DANGER_STYLE = """
background-color: #f44336;
color: white;
border: none;
border-radius: 6px;
padding: 9px 16px;
font-size: 14px;
min-height: 20px;
"""

BUTTON_DANGER_HOVER_STYLE = """
background-color: #d32f2f;
"""

BUTTON_DEFAULT_STYLE = """
background-color: #e3f2fd;
color: #1976D2;
border: none;
border-radius: 6px;
padding: 9px 16px;
font-size: 14px;
min-height: 20px;
"""

BUTTON_DEFAULT_HOVER_STYLE = """
background-color: #bbdefb;
"""

INPUT_STYLE = """
border: 1px solid #e0e0e0;
border-radius: 6px;
padding: 8px 12px;
font-size: 14px;
background-color: #ffffff;
color: #333333;
"""

INPUT_FOCUS_STYLE = """
border-color: #2196F3;
"""

INPUT_DISABLED_STYLE = """
background-color: #f5f5f5;
color: #9e9e9e;
"""

CHECKBOX_STYLE = """
spacing: 8px;
color: #555555;
font-size: 14px;
"""

CHECKBOX_INDICATOR_STYLE = """
width: 18px;
height: 18px;
border-radius: 4px;
border: 2px solid #bdbdbd;
background-color: #ffffff;
"""

CHECKBOX_INDICATOR_CHECKED_STYLE = """
border-color: #2196F3;
background-color: #2196F3;
"""

GROUPBOX_STYLE = """
font-weight: 600;
font-size: 14px;
color: #333333;
border: 1px solid #e0e0e0;
border-radius: 8px;
margin-top: 12px;
padding-top: 8px;
"""

GROUPBOX_TITLE_STYLE = """
subcontrol-origin: margin;
left: 12px;
padding: 0 8px;
"""

LIST_STYLE = """
border: 1px solid #e0e0e0;
border-radius: 6px;
padding: 4px;
font-size: 13px;
background-color: #fafafa;
"""

LIST_ITEM_STYLE = """
padding: 6px 8px;
border-radius: 4px;
"""

LIST_ITEM_SELECTED_STYLE = """
background-color: #e3f2fd;
color: #1976D2;
"""

TABLE_STYLE = """
border: 1px solid #e0e0e0;
border-radius: 6px;
background-color: #ffffff;
gridline-color: #f0f0f0;
"""

TABLE_ITEM_STYLE = """
padding: 8px;
"""

TABLE_ITEM_SELECTED_STYLE = """
background-color: #e3f2fd;
color: #1976D2;
"""

TABLE_HEADER_STYLE = """
background-color: #f5f5f5;
border: none;
border-bottom: 1px solid #e0e0e0;
padding: 10px;
font-weight: 600;
color: #555555;
"""

COMBOBOX_STYLE = """
border: 1px solid #e0e0e0;
border-radius: 6px;
padding: 8px 12px;
font-size: 10pt;
background-color: #ffffff;
color: #333333;
min-width: 200px;
"""

COMBOBOX_FOCUS_STYLE = """
border-color: #2196F3;
"""

COMBOBOX_DROPDOWN_STYLE = """
border: none;
width: 30px;
"""

COMBOBOX_POPUP_STYLE = """
border: 1px solid #e0e0e0;
background-color: #ffffff;
selection-background-color: #e3f2fd;
selection-color: #1976D2;
font-size: 10pt;
"""


def get_dialog_style() -> str:
    return DIALOG_BASE_STYLE


def get_button_style(button_type: str = "primary") -> str:
    styles = {
        "primary": BUTTON_PRIMARY_STYLE,
        "success": BUTTON_SUCCESS_STYLE,
        "cancel": BUTTON_CANCEL_STYLE,
        "danger": BUTTON_DANGER_STYLE,
        "default": BUTTON_DEFAULT_STYLE,
    }
    return styles.get(button_type, BUTTON_PRIMARY_STYLE)


def get_input_style() -> str:
    return INPUT_STYLE


def get_checkbox_style() -> str:
    return f"""
    QCheckBox {{
        {CHECKBOX_STYLE}
    }}
    QCheckBox::indicator {{
        {CHECKBOX_INDICATOR_STYLE}
    }}
    QCheckBox::indicator:checked {{
        {CHECKBOX_INDICATOR_CHECKED_STYLE}
    }}
    """


def get_groupbox_style() -> str:
    return f"""
    QGroupBox {{
        {GROUPBOX_STYLE}
    }}
    QGroupBox::title {{
        {GROUPBOX_TITLE_STYLE}
    }}
    """


def get_list_style() -> str:
    return f"""
    QListWidget {{
        {LIST_STYLE}
    }}
    QListWidget::item {{
        {LIST_ITEM_STYLE}
    }}
    QListWidget::item:selected {{
        {LIST_ITEM_SELECTED_STYLE}
    }}
    """


def get_table_style() -> str:
    return f"""
    QTableWidget {{
        {TABLE_STYLE}
    }}
    QTableWidget::item {{
        {TABLE_ITEM_STYLE}
    }}
    QTableWidget::item:selected {{
        {TABLE_ITEM_SELECTED_STYLE}
    }}
    QHeaderView::section {{
        {TABLE_HEADER_STYLE}
    }}
    """


def get_combobox_style() -> str:
    return f"""
    QComboBox {{
        {COMBOBOX_STYLE}
    }}
    QComboBox:focus {{
        {COMBOBOX_FOCUS_STYLE}
    }}
    QComboBox::drop-down {{
        {COMBOBOX_DROPDOWN_STYLE}
    }}
    QComboBox QAbstractItemView {{
        {COMBOBOX_POPUP_STYLE}
    }}
    QComboBox QAbstractItemView::item {{
        padding: 6px 12px;
        min-height: 20px;
        font-size: 10pt;
    }}
    """


RESULT_DIALOG_STYLE = f"""
{DIALOG_BASE_STYLE}
{get_groupbox_style()}
{get_list_style()}
QPushButton {{
    {BUTTON_PRIMARY_STYLE}
}}
QPushButton:hover {{
    {BUTTON_PRIMARY_HOVER_STYLE}
}}
"""

GENERAL_SETTINGS_DIALOG_STYLE = f"""
{DIALOG_BASE_STYLE}
{get_checkbox_style()}
QLineEdit {{
    {INPUT_STYLE}
}}
QLineEdit:focus {{
    {INPUT_FOCUS_STYLE}
}}
QLineEdit:disabled {{
    {INPUT_DISABLED_STYLE}
}}
QPushButton {{
    {BUTTON_PRIMARY_STYLE}
}}
QPushButton:hover {{
    {BUTTON_PRIMARY_HOVER_STYLE}
}}
QPushButton#okButton {{
    {BUTTON_SUCCESS_STYLE}
}}
QPushButton#okButton:hover {{
    {BUTTON_SUCCESS_HOVER_STYLE}
}}
QPushButton#cancelButton {{
    {BUTTON_CANCEL_STYLE}
}}
QPushButton#cancelButton:hover {{
    {BUTTON_CANCEL_HOVER_STYLE}
}}
"""

EXTENSION_SETTINGS_DIALOG_STYLE = f"""
{DIALOG_BASE_STYLE}
QLabel {{
    color: #555555;
    font-size: 13px;
}}
QLineEdit {{
    {INPUT_STYLE}
}}
QLineEdit:focus {{
    {INPUT_FOCUS_STYLE}
}}
{get_table_style()}
{get_groupbox_style()}
QPushButton {{
    {BUTTON_PRIMARY_STYLE}
}}
QPushButton:hover {{
    {BUTTON_PRIMARY_HOVER_STYLE}
}}
QPushButton#addButton {{
    {BUTTON_SUCCESS_STYLE}
}}
QPushButton#addButton:hover {{
    {BUTTON_SUCCESS_HOVER_STYLE}
}}
QPushButton#deleteButton {{
    {BUTTON_DANGER_STYLE}
}}
QPushButton#deleteButton:hover {{
    {BUTTON_DANGER_HOVER_STYLE}
}}
QPushButton#saveButton {{
    {BUTTON_SUCCESS_STYLE}
}}
QPushButton#saveButton:hover {{
    {BUTTON_SUCCESS_HOVER_STYLE}
}}
QPushButton#cancelButton {{
    {BUTTON_CANCEL_STYLE}
}}
QPushButton#cancelButton:hover {{
    {BUTTON_CANCEL_HOVER_STYLE}
}}
QPushButton#defaultButton {{
    {BUTTON_DEFAULT_STYLE}
}}
QPushButton#defaultButton:hover {{
    {BUTTON_DEFAULT_HOVER_STYLE}
}}
"""

DELIMITER_SETTINGS_DIALOG_STYLE = f"""
{DIALOG_BASE_STYLE}
QLabel {{
    color: #555555;
    font-size: 13px;
}}
QLineEdit {{
    {INPUT_STYLE}
}}
QLineEdit:focus {{
    {INPUT_FOCUS_STYLE}
}}
{get_checkbox_style()}
QPushButton {{
    {BUTTON_PRIMARY_STYLE}
}}
QPushButton:hover {{
    {BUTTON_PRIMARY_HOVER_STYLE}
}}
QPushButton#okButton {{
    {BUTTON_SUCCESS_STYLE}
}}
QPushButton#okButton:hover {{
    {BUTTON_SUCCESS_HOVER_STYLE}
}}
QPushButton#cancelButton {{
    {BUTTON_CANCEL_STYLE}
}}
QPushButton#cancelButton:hover {{
    {BUTTON_CANCEL_HOVER_STYLE}
}}
{get_combobox_style()}
"""
