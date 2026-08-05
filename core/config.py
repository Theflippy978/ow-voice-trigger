import json
import os
import sys
import time
import uuid
import tempfile


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_sounds_dir():
    return os.path.join(get_base_dir(), 'sounds')


CONFIG_FILE = os.path.join(get_base_dir(), 'config.json')

DEFAULT_CONFIG = {
    "gameProcessName": "Overwatch.exe",
    "gameWindowTitle": ["Overwatch", "守望先锋"],
    "onlyTriggerWhenGameForeground": True,
    "masterVolume": 1.0,
    "activeHeroId": None,
    "heroes": [],
    "themeMode": "system",
    "windowGeometry": ""
}


def _migrate_config(config):
    """向后兼容：将字符串标题转换为列表"""
    title = config.get('gameWindowTitle')
    if isinstance(title, str):
        config['gameWindowTitle'] = [title] if title else ["Overwatch", "守望先锋"]
    elif not isinstance(title, list):
        config['gameWindowTitle'] = ["Overwatch", "守望先锋"]
    return config


def create_hero(name):
    return {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "enabled": True,
        "hotkey": "",
        "bindings": [],
        "createdAt": int(time.time()),
        "updatedAt": int(time.time())
    }


def create_binding(name, key_binding):
    return {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "keyBinding": key_binding,
        "triggerMode": "keydown",
        "sounds": [],
        "playMode": "random",
        "volume": 1.0,
        "cooldownMs": 1000,
        "overlapPolicy": "ignore_new",
        "enabled": True
    }


def load_config():
    if not os.path.exists(CONFIG_FILE):
        config = DEFAULT_CONFIG.copy()
        save_config(config)
        return config
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        for key in DEFAULT_CONFIG:
            if key not in config:
                config[key] = DEFAULT_CONFIG[key]
        return _migrate_config(config)
    except (json.JSONDecodeError, IOError):
        # 尝试从最新备份恢复
        config_dir = os.path.dirname(CONFIG_FILE)
        backups = sorted([f for f in os.listdir(config_dir)
                         if f.startswith('config.json.') and f.endswith('.backup')], reverse=True)
        for backup in backups:
            try:
                with open(os.path.join(config_dir, backup), 'r', encoding='utf-8') as f:
                    return _migrate_config(json.load(f))
            except Exception:
                continue
        # 所有备份都损坏，创建新配置
        backup_name = f'config.json.{int(time.time())}.backup'
        if os.path.exists(CONFIG_FILE):
            os.rename(CONFIG_FILE, os.path.join(config_dir, backup_name))
        config = DEFAULT_CONFIG.copy()
        save_config(config)
        return config


def save_config(config):
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    # 原子写入：先写临时文件，再替换
    fd, tmp = tempfile.mkstemp(dir=config_dir, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CONFIG_FILE)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def get_active_hero(config):
    if not config.get('activeHeroId'):
        return None
    for hero in config.get('heroes', []):
        if hero['id'] == config['activeHeroId'] and hero.get('enabled', True):
            return hero
    return None


def set_active_hero(config, hero_id):
    config['activeHeroId'] = hero_id
    save_config(config)


def get_hero_by_hotkey(config, hotkey_str):
    if not hotkey_str:
        return None
    hotkey_lower = hotkey_str.lower().strip()
    for hero in config.get('heroes', []):
        if hero.get('hotkey', '').lower().strip() == hotkey_lower:
            return hero
    return None
