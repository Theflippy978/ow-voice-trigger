import sys
import os

# DPI 感知 - 解决字体模糊
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from ui.styles import get_style, detect_system_theme
from core import config


def get_app_dir():
    """兼容开发模式与 PyInstaller 冻结模式"""
    if getattr(sys, 'frozen', False):
        # one-file 模式下 bundle 资源解压到 sys._MEIPASS，不是 exe 旁边
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _ensure_dirs(config_data):
    """Create required directories on first run."""
    base = config.get_base_dir()
    sounds_dir = os.path.join(base, 'sounds')
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir, exist_ok=True)

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 窗口图标 - 路径兼容开发与打包两种模式
    icon_path = os.path.join(get_app_dir(), "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    cfg = config.load_config()
    mode = cfg.get("themeMode", "system")
    qss = get_style(mode)
    app.setStyleSheet(qss)

    # Ensure required directories exist
    _ensure_dirs(cfg)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
