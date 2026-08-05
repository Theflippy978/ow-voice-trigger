def detect_system_theme():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if val == 1 else "dark"
    except Exception:
        return "dark"


# ============================================================
# 颜色变量定义
# ============================================================
DARK_COLORS = {
    'c0': '#e6e7eb',
    'c1': '#e6e7eb',
    'c2': '#2f3440',
    'c3': '#f5f6f8',
    'c4': '#9aa0a6',
    'c5': '#e6e7eb',
    'c6': '#22c55e',
    'c7': '#b91c1c',
    'c8': '#acce',
    'c9': '#acce',
    'c10': '#2f343e',
    'c11': '#2b2f3a',
    'c12': '#e6e7eb',
    'c13': '#2f3440',
    'c14': '#4f8cff',
    'c15': '#4f8cff',
    'c16': '#2f3440',
    'c17': '#242832',
    'c18': '#262a35',
}

LIGHT_COLORS = {
    'c0': '#1f2937',
    'c1': '#ffffff',
    'c2': '#1f2937',
    'c3': '#e5e7eb',
    'c4': '#166534',
    'c5': '#acce',
    'c6': '#d1d5db',
    'c7': '#f9fafb',
    'c8': '#d1d5db',
    'c9': '#3b82f6',
    'c10': '#3b82f6',
    'c11': '#d1d5db',
    'c12': '#3b82f6',
    'c13': '#3b82f6',
    'c14': '#d1d5db',
    'c15': '#3b82f6',
    'c16': '#2563eb',
    'c17': '#1f2937',
    'c18': '#f3f4f6',
}

# ============================================================
# QSS 模板
# ============================================================
_QSS_TEMPLATE = """
* {{
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 10pt;
    color: {c0};
}}

QWidget {{
    background: #1a1d23;
}}

QLabel {{
    background: transparent;
    color: {c0};
}}

/* Card */
QFrame#card {{
    background: {c17};
    border: 1px solid {c2};
    border-radius: 10px;
}}

/* Title */
QLabel#title {{
    color: {c3};
    font-size: 15pt;
    font-weight: bold;
    padding: 2px 0 6px 0;
}}

QLabel#card_title {{
    color: {c3};
    font-size: 11pt;
    font-weight: bold;
}}

QLabel#label {{
    color: {c4};
}}

/* Button */
QPushButton {{
    background: {c10};
    color: {c0};
    border: 0;
    border-radius: 6px;
    padding: 8px 18px;
    min-height: 20px;
    font-weight: 600;
}}
QPushButton:hover {{ background: #363b47; }}
QPushButton:pressed {{ background: #272b34; }}

QPushButton#primary {{
    background: {c6};
    color: #ffffff;
}}
QPushButton#primary:hover {{ background: #16a34a; }}
QPushButton#primary:pressed {{ background: #15803d; }}

QPushButton#danger {{
    background: #ef4444;
    color: #ffffff;
}}
QPushButton#danger:hover {{ background: #dc2626; }}
QPushButton#danger:pressed {{ background: {c7}; }}

QPushButton{c8}nt {{
    background: {c14};
    color: #ffffff;
}}
QPushButton{c8}nt:hover {{ background: #3b73e6; }}
QPushButton{c8}nt:pressed {{ background: #2e5fc4; }}

QPushButton#icon_btn {{
    background: {c2};
    color: {c0};
    font-size: 10pt;
    padding: 4px 8px;
    border-radius: 6px;
}}
QPushButton#icon_btn:hover {{ background: {c10}; }}

QPushButton#small_btn {{
    padding: 4px 8px;
    min-height: 24px;
    font-size: 14pt;
    font-weight: bold;
}}

/* Input */
QLineEdit {{
    background: {c11};
    color: {c0};
    border: 1px solid {c2};
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 20px;
    selection-background-color: {c14};
}}
QLineEdit:focus {{ border-color: {c14}; }}
QLineEdit:disabled {{ color: #6b7280; background: #23262e; }}

/* List */
QListWidget {{
    background: {c11};
    border: 0;
    border-radius: 6px;
    padding: 4px;
}}
QListWidget::item {{ padding: 6px 10px; border-radius: 4px; margin: 1px 0; }}
QListWidget::item:selected {{ background: {c14}; color: #ffffff; }}
QListWidget::item:hover {{ background: {c2}; }}
QListWidget::item:selected:hover {{ background: {c14}; }}

/* Table */
QTreeWidget {{ background: {c17}; border: 0; alternate-background-color: {c18}; }}
QTreeWidget::item {{ padding: 4px 6px; border-bottom: 1px solid #2a2e38; }}
QTreeWidget::item:selected {{ background: {c14}; color: #ffffff; }}
QTreeWidget::item:hover {{ background: {c2}; }}
QHeaderView::section {{ background: #2a2e38; color: {c4}; padding: 6px; border: 0; font-weight: 600; }}

/* Checkbox */
QCheckBox {{ color: {c4}; spacing: 8px; font-size: 10pt; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border: 1px solid #3a3f4b; border-radius: 4px; background: {c11}; }}
QCheckBox::indicator:hover {{ border-color: {c14}; }}
QCheckBox::indicator:checked {{ background: {c14}; border-color: {c14}; }}

/* Scrollbar */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #3a3f4b; border-radius: 4px; min-height: 24px; }}
QScrollBar::handle:vertical:hover {{ background: #4a5060; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ background: transparent; height: 0; border: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: #3a3f4b; border-radius: 4px; min-width: 24px; }}
QScrollBar::handle:horizontal:hover {{ background: #4a5060; }}

/* Progress */
QProgressBar {{ background: {c11}; border: 0; border-radius: 4px; min-height: 6px; max-height: 6px; }}
QProgressBar::chunk {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {c14},stop:1 #7aa7ff); border-radius: 4px; }}

/* Slider */
QSlider::groove:horizontal {{ background: {c11}; height: 4px; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {c14}; width: 14px; height: 14px; border-radius: 7px; margin: -5px 0; }}
QSlider::handle:horizontal:hover {{ background: #3b73e6; }}
QSlider::sub-page:horizontal {{ background: {c14}; border-radius: 2px; }}

/* Tooltip */
QToolTip {{ background: {c2}; color: {c0}; border: 1px solid #3a3f4b; padding: 4px 8px; border-radius: 4px; }}
"""


# ============================================================
# Light theme
# ============================================================
LIGHT_STYLE = """
* {
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 10pt;
    color: #1f2937;
}

QWidget { background: #f3f4f6; }

QLabel { background: transparent; color: #1f2937; }

/* ---- 卡片 ---- */
QFrame#card {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 10px;
}

/* ---- 标题 ---- */
QLabel#title { color: #1f2937; font-size: 15pt; font-weight: bold; padding: 2px 0 6px 0; }
QLabel#card_title { color: #1f2937; font-size: 11pt; font-weight: bold; }
QLabel#label { color: #6b7280; }

/* ---- 按钮 ---- */
QPushButton {
    background: #e5e7eb;
    color: #1f2937;
    border: 0;
    border-radius: 6px;
    padding: 8px 18px;
    min-height: 20px;
    font-weight: 600;
}
QPushButton:hover { background: #d1d5db; }
QPushButton:pressed { background: #9ca3af; }

QPushButton#primary { background: #16a34a; color: #ffffff; }
QPushButton#primary:hover { background: #15803d; }
QPushButton#primary:pressed { background: #166534; }

QPushButton#danger { background: #dc2626; color: #ffffff; }
QPushButton#danger:hover { background: {c7}; }
QPushButton#danger:pressed { background: #991b1b; }

QPushButton{c8}nt { background: #3b82f6; color: #ffffff; }
QPushButton{c8}nt:hover { background: #2563eb; }
QPushButton{c8}nt:pressed { background: #1d4ed8; }

QPushButton#icon_btn {
    background: #e5e7eb;
    color: #1f2937;
    font-size: 10pt;
    padding: 4px 8px;
    border-radius: 6px;
}
QPushButton#icon_btn:hover { background: #d1d5db; }

QPushButton#small_btn {
    padding: 4px 8px;
    min-height: 24px;
    font-size: 14pt;
    font-weight: bold;
}

/* ---- 输入框 ---- */
QLineEdit {
    background: #f9fafb;
    color: #1f2937;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 20px;
    selection-background-color: #3b82f6;
}
QLineEdit:focus { border-color: #3b82f6; }
QLineEdit:disabled { color: #9ca3af; background: #e5e7eb; }

/* ---- 列表 ---- */
QListWidget { background: #f9fafb; border: 0; border-radius: 6px; padding: 4px; }
QListWidget::item { padding: 6px 10px; border-radius: 4px; margin: 1px 0; }
QListWidget::item:selected { background: #3b82f6; color: #ffffff; }
QListWidget::item:hover { background: #e5e7eb; }
QListWidget::item:selected:hover { background: #3b82f6; }

/* ---- 表格 ---- */
QTreeWidget { background: #ffffff; border: 0; alternate-background-color: #f9fafb; }
QTreeWidget::item { padding: 4px 6px; border-bottom: 1px solid #e5e7eb; }
QTreeWidget::item:selected { background: #3b82f6; color: #ffffff; }
QTreeWidget::item:hover { background: #e5e7eb; }
QHeaderView::section { background: #f3f4f6; color: #6b7280; padding: 6px; border: 0; font-weight: 600; }

/* ---- 复选框 ---- */
QCheckBox { color: #6b7280; spacing: 8px; font-size: 10pt; }
QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #d1d5db; border-radius: 4px; background: #f9fafb; }
QCheckBox::indicator:hover { border-color: #3b82f6; }
QCheckBox::indicator:checked { background: #3b82f6; border-color: #3b82f6; }

/* ---- 滚动条 ---- */
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #d1d5db; border-radius: 4px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #9ca3af; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: transparent; height: 0; border: 0; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal { background: #d1d5db; border-radius: 4px; min-width: 24px; }
QScrollBar::handle:horizontal:hover { background: #9ca3af; }

/* ---- 进度条 ---- */
QProgressBar { background: #e5e7eb; border: 0; border-radius: 4px; min-height: 6px; max-height: 6px; }
QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #3b82f6,stop:1 #60a5fa); border-radius: 4px; }

/* ---- 滑块 ---- */
QSlider::groove:horizontal { background: #e5e7eb; height: 4px; border-radius: 2px; }
QSlider::handle:horizontal { background: #3b82f6; width: 14px; height: 14px; border-radius: 7px; margin: -5px 0; }
QSlider::handle:horizontal:hover { background: #2563eb; }
QSlider::sub-page:horizontal { background: #3b82f6; border-radius: 2px; }

/* ---- 工具提示 ---- */
QToolTip { background: #1f2937; color: #f3f4f6; border: 1px solid #374151; padding: 4px 8px; border-radius: 4px; }
"""


def get_style(theme_mode="system"):
    if theme_mode == "dark":
        return _QSS_TEMPLATE.format(**DARK_COLORS)
    elif theme_mode == "light":
        return _QSS_TEMPLATE.format(**LIGHT_COLORS)
    else:
        colors = DARK_COLORS if detect_system_theme() == "dark" else LIGHT_COLORS
        return _QSS_TEMPLATE.format(**colors)
