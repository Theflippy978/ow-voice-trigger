import os
import threading
import time
from pynput import keyboard
import psutil
from PySide6.QtCore import QObject, Signal

import core.config as config
from core.config import get_sounds_dir


# 进程+窗口检测缓存，500ms 内有效
_process_cache = {'key': None, 'result': None, 'time': 0}
_process_cache_lock = threading.Lock()


def is_game_foreground(game_process_name, game_window_title):
    global _process_cache
    cache_key = (game_process_name, str(game_window_title))
    now = time.time()

    with _process_cache_lock:
        if _process_cache['key'] == cache_key and now - _process_cache['time'] < 0.5:
            return _process_cache['result']

    try:
        process_found = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() == game_process_name.lower():
                process_found = True
                break
        if not process_found:
            with _process_cache_lock:
                _process_cache = {'key': cache_key, 'result': False, 'time': now}
            return False

        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value.lower()

            # 支持多语言标题匹配（字符串或列表）
            titles = game_window_title if isinstance(game_window_title, list) else [game_window_title]
            result = any(t.lower() in title for t in titles)
        except Exception:
            result = False
    except Exception:
        result = False

    with _process_cache_lock:
        _process_cache = {'key': cache_key, 'result': result, 'time': now}
    return result


def parse_key_string(key_str):
    parts = key_str.lower().strip().split('+')
    modifiers = set()
    main_key = ''
    for part in parts:
        part = part.strip()
        if part in ('shift', 'ctrl', 'alt', 'win'):
            modifiers.add(part)
        else:
            main_key = part
    return modifiers, main_key


def pynput_key_to_string(pynput_key):
    if isinstance(pynput_key, keyboard.KeyCode):
        if pynput_key.char:
            return pynput_key.char.lower()
        return str(pynput_key.vk)
    key_name = str(pynput_key).replace('Key.', '')
    name_map = {
        'shift': 'shift', 'shift_l': 'shift', 'shift_r': 'shift',
        'ctrl': 'ctrl', 'ctrl_l': 'ctrl', 'ctrl_r': 'ctrl',
        'alt': 'alt', 'alt_l': 'alt', 'alt_r': 'alt',
        'cmd': 'win', 'cmd_l': 'win', 'cmd_r': 'win',
        'space': 'space', 'enter': 'enter', 'tab': 'tab',
        'backspace': 'backspace', 'esc': 'esc',
        'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right',
    }
    return name_map.get(key_name, key_name)


def _match_binding(modifiers, main_key, binding):
    bind_mods, bind_key = parse_key_string(binding.get('keyBinding', ''))
    return bind_key == main_key and bind_mods == modifiers


class KeyboardMonitor(QObject):
    trigger_signal = Signal(str, str)
    hero_switch_signal = Signal(str, str)

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.running = False
        self.hotkey_listener = None
        self.key_listener = None
        self.pressed_modifiers = set()
        self.cooldowns = {}
        self.pressed_keys = set()

    def start(self):
        if self.running:
            return
        self.running = True
        self._start_hotkey_listener()
        self._start_key_listener()

    def stop(self):
        self.running = False
        if self.key_listener:
            self.key_listener.stop()
            self.key_listener = None
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None

    def restart(self):
        self.stop()
        self.pressed_modifiers.clear()
        self.pressed_keys.clear()
        self.cooldowns.clear()
        self.start()

    def start_hotkey_listener(self):
        self._start_hotkey_listener()

    def stop_hotkey_listener(self):
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None

    def _start_hotkey_listener(self):
        hotkeys = {}
        for hero in self.cfg.get('heroes', []):
            hk = hero.get('hotkey', '').strip()
            if hk:
                pynput_str = self._convert_to_pynput_hotkey(hk, hero['id'])
                if pynput_str:
                    hotkeys[pynput_str] = lambda hid=hero['id'], hn=hero['name']: self._do_hero_switch(hid, hn)

        if hotkeys:
            self.hotkey_listener = keyboard.GlobalHotKeys(hotkeys)
            self.hotkey_listener.daemon = True
            self.hotkey_listener.start()

    def _convert_to_pynput_hotkey(self, hotkey_str, hero_id):
        parts = hotkey_str.lower().replace(' ', '').split('+')
        converted = []
        for part in parts:
            if part in ('ctrl', 'alt', 'shift', 'win'):
                converted.append(f'<{part}>')
            elif len(part) == 1:
                converted.append(part)
            elif part.startswith('f') and part[1:].isdigit():
                converted.append(part)
            else:
                return None
        return '+'.join(converted) if converted else None

    def _do_hero_switch(self, hero_id, hero_name):
        self.cfg['activeHeroId'] = hero_id
        config.save_config(self.cfg)
        self.hero_switch_signal.emit(hero_id, hero_name)

    def _start_key_listener(self):
        self.key_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
            suppress=False
        )
        self.key_listener.daemon = True
        self.key_listener.start()

    def _on_key_press(self, key):
        if not self.running:
            return
        key_str = pynput_key_to_string(key)

        if key_str in ('shift', 'ctrl', 'alt', 'win'):
            # 先检查游戏前台，再修改状态，避免残留
            if self.cfg.get('onlyTriggerWhenGameForeground', True):
                if not is_game_foreground(
                    self.cfg.get('gameProcessName', 'Overwatch.exe'),
                    self.cfg.get('gameWindowTitle', ['Overwatch', '守望先锋'])
                ):
                    return
            self.pressed_modifiers.add(key_str)
            hero = config.get_active_hero(self.cfg)
            if not hero:
                return
            current_modifiers = frozenset(self.pressed_modifiers)
            for binding in hero.get('bindings', []):
                if not binding.get('enabled', True):
                    continue
                if binding.get('triggerMode', 'keydown') != 'keydown':
                    continue
                bind_mods, bind_key = parse_key_string(binding.get('keyBinding', ''))
                if bind_key == '' and bind_mods == current_modifiers:
                    self._try_trigger(hero, binding)
            return

        if key_str in self.pressed_keys:
            return
        self.pressed_keys.add(key_str)

        if self.cfg.get('onlyTriggerWhenGameForeground', True):
            if not is_game_foreground(
                self.cfg.get('gameProcessName', 'Overwatch.exe'),
                self.cfg.get('gameWindowTitle', ['Overwatch', '守望先锋'])
            ):
                return

        hero = config.get_active_hero(self.cfg)
        if not hero:
            return

        current_modifiers = frozenset(self.pressed_modifiers)
        for binding in hero.get('bindings', []):
            if not binding.get('enabled', True):
                continue
            if binding.get('triggerMode', 'keydown') != 'keydown':
                continue
            bind_mods, bind_key = parse_key_string(binding.get('keyBinding', ''))
            if bind_key == key_str and bind_mods == current_modifiers:
                self._try_trigger(hero, binding)

    def _on_key_release(self, key):
        key_str = pynput_key_to_string(key)
        if key_str in ('shift', 'ctrl', 'alt', 'win'):
            self.pressed_modifiers.discard(key_str)
        self.pressed_keys.discard(key_str)

    def _try_trigger(self, hero, binding):
        now = time.time() * 1000
        binding_id = binding['id']
        cooldown = binding.get('cooldownMs', 1000)
        last_time = self.cooldowns.get(binding_id, 0)
        if now - last_time < cooldown:
            return
        self.cooldowns[binding_id] = now

        from core.audio import play_sounds
        sounds_dir = get_sounds_dir()
        sounds = [os.path.join(sounds_dir, s) for s in binding.get('sounds', [])]
        play_sounds(
            sounds,
            binding.get('playMode', 'random'),
            binding.get('volume', 1.0),
            self.cfg.get('masterVolume', 1.0)
        )
        self.trigger_signal.emit(hero['name'], binding['name'])
