import os
import random
import threading

import pygame

_audio_initialized = False
_sound_cache = {}
_seq_indices = {}
_recent_played = {}
_state_lock = threading.Lock()
_channel = None  # 专用声道


def init_audio():
    global _audio_initialized
    if not _audio_initialized:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            _audio_initialized = True
        except Exception:
            pass


def play_sound(file_path, volume=1.0, master_volume=1.0):
    global _channel
    init_audio()
    if not os.path.exists(file_path):
        return
    try:
        if file_path not in _sound_cache:
            _sound_cache[file_path] = pygame.mixer.Sound(file_path)
        sound = _sound_cache[file_path]
        sound.set_volume(volume * master_volume)
        # 停止专用声道（同步），避免竞争
        if _channel and _channel.get_busy():
            _channel.stop()
        _channel = sound.play()
    except Exception:
        pass


def play_sounds(sounds, play_mode, volume, master_volume):
    if not sounds:
        return
    if len(sounds) == 1:
        play_sound(sounds[0], volume, master_volume)
        return

    if play_mode == 'random':
        chosen = random.choice(sounds)
    elif play_mode == 'sequential':
        idx_key = tuple(sounds)
        with _state_lock:
            current = _seq_indices.get(idx_key, 0)
            chosen = sounds[current]
            _seq_indices[idx_key] = (current + 1) % len(sounds)
    elif play_mode == 'random_no_repeat':
        recent_key = tuple(sounds)
        with _state_lock:
            recent = _recent_played.get(recent_key, [])
            candidates = [s for s in sounds if s not in recent]
            if not candidates:
                candidates = list(sounds)
                recent = []
            chosen = random.choice(candidates)
            recent.append(chosen)
            max_history = max(1, len(sounds) // 2)
            _recent_played[recent_key] = recent[-max_history:]
    else:
        chosen = random.choice(sounds)

    play_sound(chosen, volume, master_volume)


def stop_all():
    global _channel
    if _audio_initialized:
        pygame.mixer.stop()
    _channel = None
