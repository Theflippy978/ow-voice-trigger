import time
import threading
from pynput import keyboard as kb
from PySide6.QtCore import QObject, Signal


class _RecordBridge(QObject):
    """跨线程信号桥：工作线程 -> 主线程"""
    finished = Signal(str)


# 模块级实例，创建于主线程，生命周期跟随模块
_bridge = _RecordBridge()


def record_key(callback):
    """
    录制按键，完成后调用 callback(result_str)。
    支持纯修饰键、组合键，释放所有按键后结束。
    回调通过信号在主线程执行。
    """
    # 断开旧连接，避免多次调用时回调叠加
    try:
        _bridge.finished.disconnect()
    except RuntimeError:
        pass
    _bridge.finished.connect(callback)

    pressed_keys = set()
    modifiers = set()
    active_keys = set()

    def on_press(key):
        active_keys.add(key)
        if isinstance(key, kb.KeyCode) and key.char:
            pressed_keys.add(key.char.lower())
        elif isinstance(key, kb.Key):
            name = str(key).replace("Key.", "")
            mod_map = {"shift": "shift", "shift_l": "shift", "shift_r": "shift",
                       "ctrl": "ctrl", "ctrl_l": "ctrl", "ctrl_r": "ctrl",
                       "alt": "alt", "alt_l": "alt", "alt_r": "alt"}
            if name in mod_map:
                modifiers.add(mod_map[name])

    def on_release(key):
        active_keys.discard(key)

    def worker():
        with kb.Listener(on_press=on_press, on_release=on_release) as listener:
            start = time.time()
            while True:
                time.sleep(0.05)
                if (pressed_keys or modifiers) and len(active_keys) == 0:
                    break
                if time.time() - start > 5:
                    break
            listener.stop()
        parts = sorted(modifiers) + sorted(pressed_keys)
        result = "+".join(parts) if parts else ""
        _bridge.finished.emit(result)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
