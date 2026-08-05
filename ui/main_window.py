import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QLineEdit, QListWidget,
    QTreeWidget, QTreeWidgetItem, QListWidgetItem, QSlider,
    QFileDialog, QMessageBox, QDialog,
)
from PySide6.QtCore import Qt, QTimer

from ui.styles import get_style, detect_system_theme
from ui.checkbox import CheckMarkCheckBox
from ui.hero_dialog import HeroDialog
from ui.binding_dialog import BindingDialog
from core.keyboard import KeyboardMonitor
from core.audio import play_sounds, init_audio
from core.config import get_sounds_dir
from core.key_recorder import record_key
from core import config


def confirm_dialog(parent, title, message):
    """统一风格的确认弹窗，返回 True/False"""
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setFixedSize(320, 140)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(16)

    label = QLabel(message)
    label.setObjectName("label")
    label.setWordWrap(True)
    layout.addWidget(label)
    layout.addStretch(1)

    btn_row = QHBoxLayout()
    btn_row.addStretch(1)

    cancel_btn = QPushButton("取消")
    cancel_btn.setFixedSize(80, 32)
    cancel_btn.clicked.connect(dlg.reject)
    btn_row.addWidget(cancel_btn)

    ok_btn = QPushButton("确定")
    ok_btn.setObjectName("accent")
    ok_btn.setFixedSize(80, 32)
    ok_btn.clicked.connect(dlg.accept)
    btn_row.addWidget(ok_btn)

    layout.addLayout(btn_row)

    result = dlg.exec()
    return result == QDialog.Accepted


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("守望先锋语音触发器")
        self.resize(1040, 760)
        self.setMinimumSize(860, 620)

        self.cfg = config.load_config()
        self.monitor = None
        self._monitoring = False

        self._apply_theme()
        init_audio()
        self._build_ui()
        self._refresh_hero_list()

        if self.cfg.get("activeHeroId"):
            self._select_hero_by_id(self.cfg["activeHeroId"])
            self._on_hero_selected()

        self._restore_geometry()

        self._start_hotkey_only()

    def _apply_theme(self):
        mode = self.cfg.get("themeMode", "system")
        self.setStyleSheet(get_style(mode))

    def _toggle_theme(self):
        mode = self.cfg.get("themeMode", "system")
        if mode == "system":
            new_mode = "light" if detect_system_theme() == "dark" else "dark"
        elif mode == "dark":
            new_mode = "light"
        else:
            new_mode = "dark"
        self.cfg["themeMode"] = new_mode
        config.save_config(self.cfg)
        self._apply_theme()
        self._update_monitor_button()
        if new_mode == "dark":
            self.theme_btn.setText("\u660e\u4eae\u6a21\u5f0f")
        else:
            self.theme_btn.setText("\u6df1\u8272\u6a21\u5f0f")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        header = QHBoxLayout()
        self.title_label = QLabel("守望先锋语音触发器")
        self.title_label.setObjectName("title")
        header.addWidget(self.title_label)
        header.addStretch(1)
        self.status_label = QLabel("")
        header.addWidget(self.status_label)
        self.game_status_label = QLabel()
        self.game_status_label.setObjectName("label")
        header.addWidget(self.game_status_label)
        mode = self.cfg.get("themeMode", "system")
        if mode == "system":
            mode = detect_system_theme()
        if mode == "dark":
            self.theme_btn = QPushButton("\u660e\u4eae\u6a21\u5f0f")
        else:
            self.theme_btn = QPushButton("\u6df1\u8272\u6a21\u5f0f")
        self.theme_btn.setObjectName("icon_btn")
        self.theme_btn.setFixedSize(100, 40)
        self.theme_btn.clicked.connect(self._toggle_theme)
        header.addWidget(self.theme_btn)
        root.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(12)

        left_card = QFrame()
        left_card.setObjectName("card")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(16, 14, 16, 14)
        left_layout.setSpacing(8)
        hero_title = QLabel("英雄列表")
        hero_title.setObjectName("card_title")
        left_layout.addWidget(hero_title)
        self.hero_list = QListWidget()
        self.hero_list.itemSelectionChanged.connect(self._on_hero_selected)
        left_layout.addWidget(self.hero_list)
        hero_btn_row = QHBoxLayout()
        add_hero_btn = QPushButton("新建")
        add_hero_btn.setObjectName("accent")
        add_hero_btn.clicked.connect(self._add_hero)
        hero_btn_row.addWidget(add_hero_btn)
        del_hero_btn = QPushButton("删除")
        del_hero_btn.setObjectName("danger")
        del_hero_btn.clicked.connect(self._delete_hero)
        hero_btn_row.addWidget(del_hero_btn)
        left_layout.addLayout(hero_btn_row)
        content.addWidget(left_card, 0)

        right_card = QFrame()
        right_card.setObjectName("card")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(16, 14, 16, 14)
        right_layout.setSpacing(8)

        hero_info_row = QHBoxLayout()
        self.hero_name_label = QLabel("请选择一个英雄")
        self.hero_name_label.setObjectName("title")
        hero_info_row.addWidget(self.hero_name_label)
        hero_info_row.addStretch(1)
        hotkey_label = QLabel("快捷键:")
        hotkey_label.setObjectName("label")
        hero_info_row.addWidget(hotkey_label)
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("如: alt+1")
        self.hotkey_edit.setFixedWidth(100)
        hero_info_row.addWidget(self.hotkey_edit)
        self.hotkey_record_btn = QPushButton("录制")
        self.hotkey_record_btn.setObjectName("icon_btn")
        self.hotkey_record_btn.setFixedSize(72, 32)
        self.hotkey_record_btn.clicked.connect(self._record_hero_hotkey)
        hero_info_row.addWidget(self.hotkey_record_btn)
        self.hotkey_clear_btn = QPushButton("清空")
        self.hotkey_clear_btn.setObjectName("icon_btn")
        self.hotkey_clear_btn.setFixedSize(72, 32)
        self.hotkey_clear_btn.clicked.connect(self._clear_hero_hotkey)
        hero_info_row.addWidget(self.hotkey_clear_btn)
        save_hotkey_btn = QPushButton("保存")
        save_hotkey_btn.setObjectName("icon_btn")
        save_hotkey_btn.setFixedSize(72, 32)
        save_hotkey_btn.clicked.connect(self._save_hotkey)
        hero_info_row.addWidget(save_hotkey_btn)
        right_layout.addLayout(hero_info_row)

        bind_header = QHBoxLayout()
        bind_title = QLabel("按键绑定")
        bind_title.setObjectName("label")
        bind_header.addWidget(bind_title)
        bind_header.addStretch(1)
        add_bind_btn = QPushButton("+ 添加绑定")
        add_bind_btn.setObjectName("accent")
        add_bind_btn.clicked.connect(self._add_binding)
        bind_header.addWidget(add_bind_btn)
        right_layout.addLayout(bind_header)

        self.bind_tree = QTreeWidget()
        self.bind_tree.setHeaderLabels(["名称", "按键", "音频", "冷却(ms)", "播放方式"])
        self.bind_tree.setColumnWidth(0, 120)
        self.bind_tree.setColumnWidth(1, 70)
        self.bind_tree.setColumnWidth(2, 60)
        self.bind_tree.setColumnWidth(3, 70)
        self.bind_tree.setColumnWidth(4, 80)
        self.bind_tree.setAlternatingRowColors(True)
        self.bind_tree.itemDoubleClicked.connect(self._edit_binding)
        right_layout.addWidget(self.bind_tree)

        bind_btn_row = QHBoxLayout()
        self.edit_bind_btn = QPushButton("编辑")
        self.edit_bind_btn.clicked.connect(self._edit_binding)
        bind_btn_row.addWidget(self.edit_bind_btn)
        self.del_bind_btn = QPushButton("删除")
        self.del_bind_btn.setObjectName("danger")
        self.del_bind_btn.clicked.connect(self._delete_binding)
        bind_btn_row.addWidget(self.del_bind_btn)
        self.test_bind_btn = QPushButton("测试播放")
        self.test_bind_btn.clicked.connect(self._test_play)
        bind_btn_row.addWidget(self.test_bind_btn)
        bind_btn_row.addStretch(1)
        right_layout.addLayout(bind_btn_row)

        content.addWidget(right_card, 1)
        root.addLayout(content)

        footer = QHBoxLayout()
        self.toggle_btn = QPushButton("")
        self.toggle_btn.setMinimumHeight(36)
        self.toggle_btn.clicked.connect(self._toggle_monitor)
        footer.addWidget(self.toggle_btn)

        self.game_only_cb = CheckMarkCheckBox("仅游戏触发")
        self.game_only_cb.setChecked(self.cfg.get("onlyTriggerWhenGameForeground", True))
        self.game_only_cb.stateChanged.connect(self._toggle_game_only)
        footer.addWidget(self.game_only_cb)

        footer.addStretch(1)
        self.log_label = QLabel("")
        self.log_label.setStyleSheet("color:#4f8cff;")
        footer.addWidget(self.log_label)
        footer.addSpacing(12)

        vol_label = QLabel("主音量")
        vol_label.setObjectName("label")
        footer.addWidget(vol_label)
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(int(self.cfg.get("masterVolume", 1.0) * 100))
        self.vol_slider.setFixedWidth(120)
        self.vol_slider.valueChanged.connect(self._on_volume_changed)
        footer.addWidget(self.vol_slider)
        self.vol_value_label = QLabel("")
        self.vol_value_label.setObjectName("label")
        footer.addWidget(self.vol_value_label)
        root.addLayout(footer)

        self._update_monitor_button()
        self._update_status_display()
        self._update_game_status_label()
        self._update_volume_display()

    def _update_monitor_button(self):
        if self._monitoring:
            self.toggle_btn.setObjectName("danger")
            self.toggle_btn.setText("停止监听")
        else:
            self.toggle_btn.setObjectName("primary")
            self.toggle_btn.setText("开始监听")
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)

    def _update_status_display(self):
        if self._monitoring:
            self.status_label.setText("\u25cf 监听中")
            self.status_label.setStyleSheet("color:#22c55e;font-weight:600;")
        else:
            self.status_label.setText("\u25cf 未监听")
            self.status_label.setStyleSheet("color:#ef4444;font-weight:600;")

    def _update_game_status_label(self):
        if self.cfg.get("onlyTriggerWhenGameForeground", True):
            self.game_status_label.setText("仅游戏触发: 开")
        else:
            self.game_status_label.setText("仅游戏触发: 关")

    def _update_volume_display(self):
        self.vol_value_label.setText(f"{self.vol_slider.value()}%")

    def _stop_monitor_for_record(self):
        """录制前暂停监听器，避免双监听器干扰"""
        if self.monitor:
            self.monitor.stop()

    def _start_monitor_after_record(self):
        """录制后恢复监听器"""
        if self.monitor:
            self.monitor.start()

    def _restore_geometry(self):
        geo = self.cfg.get("windowGeometry")
        if geo:
            parts = geo.replace("+", "x").split("x")
            if len(parts) >= 4:
                try:
                    self.setGeometry(int(parts[2]), int(parts[3]), int(parts[0]), int(parts[1]))
                except (ValueError, IndexError):
                    pass

    def _save_geometry(self):
        geo = f"{self.width()}x{self.height()}+{self.x()}+{self.y()}"
        self.cfg["windowGeometry"] = geo
        config.save_config(self.cfg)

    def _start_hotkey_only(self):
        """仅启动热键监听（不启动技能监听）"""
        if not self.cfg.get("heroes"):
            return
        if not self.monitor:
            self.monitor = KeyboardMonitor(self.cfg)
            self.monitor.trigger_signal.connect(self._on_trigger)
            self.monitor.hero_switch_signal.connect(self._on_hero_switch)
        self.monitor.start_hotkey_listener()

    def _toggle_monitor(self):
        if self._monitoring:
            self._stop_monitor()
        else:
            self._start_monitor()

    def _start_monitor(self):
        if self._monitoring:
            return
        if not self.monitor:
            self.monitor = KeyboardMonitor(self.cfg)
            self.monitor.trigger_signal.connect(self._on_trigger)
            self.monitor.hero_switch_signal.connect(self._on_hero_switch)
        self.monitor.start()
        self._monitoring = True
        self._update_monitor_button()
        self._update_status_display()

    def _stop_monitor(self):
        if self.monitor:
            self.monitor.stop()
        self._monitoring = False
        self._update_monitor_button()
        self._update_status_display()

    def _select_hero_by_id(self, hero_id):
        for i in range(self.hero_list.count()):
            item = self.hero_list.item(i)
            if item.data(Qt.UserRole) == hero_id:
                self.hero_list.setCurrentRow(i)
                return

    def _on_hero_selected(self):
        row = self.hero_list.currentRow()
        heroes = self.cfg.get("heroes", [])
        if row < 0 or row >= len(heroes):
            return
        hero = heroes[row]
        self.hero_name_label.setText(f"  {hero['name']}")
        self.hotkey_edit.setText(hero.get("hotkey", ""))
        self.cfg["activeHeroId"] = hero["id"]
        config.save_config(self.cfg)
        self._refresh_bindings()

    def _add_hero(self):
        dialog = HeroDialog(self)
        if dialog.exec() == HeroDialog.Accepted and dialog.result_data:
            hero = config.create_hero(dialog.result_data["name"])
            idx = len(self.cfg.get("heroes", [])) + 1
            if idx <= 9:
                hero["hotkey"] = f"alt+{idx}"
            else:
                hero["hotkey"] = ""
            self.cfg.setdefault("heroes", []).append(hero)
            config.save_config(self.cfg)
            self._refresh_hero_list()
            self._select_hero_by_id(hero["id"])
            self._on_hero_selected()

    def _delete_hero(self):
        row = self.hero_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个英雄")
            return
        heroes = self.cfg.get("heroes", [])
        if row >= len(heroes):
            return
        hero = heroes[row]
        if confirm_dialog(self, "确认", f"确定删除英雄 '{hero['name']}'?"):
            heroes.pop(row)
            if self.cfg.get("activeHeroId") == hero["id"]:
                self.cfg["activeHeroId"] = heroes[0]["id"] if heroes else None
            config.save_config(self.cfg)
            self._refresh_hero_list()
            self._refresh_bindings()

    def _record_hero_hotkey(self):
        """录制英雄切换快捷键"""
        self.hotkey_record_btn.setEnabled(False)
        self.hotkey_edit.setText("按下按键中...")
        self._recording = True
        if self.monitor:
            self.monitor.stop()
        record_key(self._on_hero_hotkey_done)

    def _on_hero_hotkey_done(self, result):
        if result:
            self.hotkey_edit.setText(result)
        else:
            self.hotkey_edit.setText("")
        self.hotkey_record_btn.setEnabled(True)
        self._recording = False
        if self.monitor:
            self.monitor.start()

    def _clear_hero_hotkey(self):
        self.hotkey_edit.setText("")

    def _save_hotkey(self):
        row = self.hero_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个英雄")
            return
        heroes = self.cfg.get("heroes", [])
        if row >= len(heroes):
            return
        heroes[row]["hotkey"] = self.hotkey_edit.text().strip()
        config.save_config(self.cfg)
        self._refresh_hero_list()
        if self.monitor:
            self.monitor.restart()
        self.log_label.setText("\u2713 快捷键已保存")
        QTimer.singleShot(2000, lambda: self.log_label.setText(""))

    def _refresh_hero_list(self, keep_blocked=False):
        self.hero_list.blockSignals(True)
        self.hero_list.clear()
        for hero in self.cfg.get("heroes", []):
            item = QListWidgetItem(hero.get("name", ""))
            item.setData(Qt.UserRole, hero["id"])
            self.hero_list.addItem(item)
        if not keep_blocked: self.hero_list.blockSignals(False)

    def _refresh_bindings(self):
        self.bind_tree.clear()
        row = self.hero_list.currentRow()
        heroes = self.cfg.get("heroes", [])
        if row < 0 or row >= len(heroes):
            return
        hero = heroes[row]
        for b in hero.get("bindings", []):
            mode_map = {"random": "随机", "sequential": "顺序", "random_no_repeat": "随机不重复"}
            item = QTreeWidgetItem([
                b.get("name", ""),
                b.get("keyBinding", ""),
                f"{len(b.get('sounds', []))}个",
                str(b.get("cooldownMs", 1000)),
                mode_map.get(b.get("playMode", "random"), "随机")
            ])
            item.setData(0, Qt.UserRole, b["id"])
            self.bind_tree.addTopLevelItem(item)

    def _add_binding(self):
        row = self.hero_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个英雄")
            return
        dialog = BindingDialog(self, on_record_start=self._stop_monitor_for_record, on_record_end=self._start_monitor_after_record)
        if dialog.exec() == BindingDialog.Accepted and dialog.result_data:
            binding = config.create_binding(dialog.result_data["name"], dialog.result_data["keyBinding"])
            binding.update(dialog.result_data)
            heroes = self.cfg.get("heroes", [])
            heroes[row].setdefault("bindings", []).append(binding)
            config.save_config(self.cfg)
            self._refresh_bindings()
            if self.monitor:
                self.monitor.restart()

    def _edit_binding(self):
        item = self.bind_tree.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选择一个绑定")
            return
        bind_id = item.data(0, Qt.UserRole)
        row = self.hero_list.currentRow()
        heroes = self.cfg.get("heroes", [])
        if row < 0 or row >= len(heroes):
            return
        hero = heroes[row]
        binding = None
        for b in hero.get("bindings", []):
            if b["id"] == bind_id:
                binding = b
                break
        if not binding:
            return
        dialog = BindingDialog(self, binding, on_record_start=self._stop_monitor_for_record, on_record_end=self._start_monitor_after_record)
        if dialog.exec() == BindingDialog.Accepted and dialog.result_data:
            binding.update(dialog.result_data)
            config.save_config(self.cfg)
            self._refresh_bindings()
            if self.monitor:
                self.monitor.restart()

    def _delete_binding(self):
        item = self.bind_tree.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选择一个绑定")
            return
        bind_id = item.data(0, Qt.UserRole)
        row = self.hero_list.currentRow()
        heroes = self.cfg.get("heroes", [])
        if row < 0 or row >= len(heroes):
            return
        hero = heroes[row]
        if confirm_dialog(self, "确认", "确定删除此绑定?"):
            hero["bindings"] = [b for b in hero.get("bindings", []) if b["id"] != bind_id]
            config.save_config(self.cfg)
            self._refresh_bindings()

    def _test_play(self):
        item = self.bind_tree.currentItem()
        if not item:
            return
        bind_id = item.data(0, Qt.UserRole)
        row = self.hero_list.currentRow()
        heroes = self.cfg.get("heroes", [])
        if row < 0 or row >= len(heroes):
            return
        hero = heroes[row]
        for b in hero.get("bindings", []):
            if b["id"] == bind_id:
                sounds = b.get("sounds", [])
                if sounds:
                    sounds_dir = get_sounds_dir()
                    resolved = [os.path.join(sounds_dir, s) for s in sounds]
                    play_sounds(resolved, b.get("playMode", "random"),
                                b.get("volume", 1.0),
                                self.cfg.get("masterVolume", 1.0))
                else:
                    QMessageBox.information(self, "提示", "该绑定没有音频文件")
                break

    def _on_trigger(self, hero_name, binding_name):
        self.log_label.setText(f"\u25b6 {hero_name} - {binding_name}")

    def _on_hero_switch(self, hero_id, hero_name):
        if getattr(self, "_recording", False):
            return
        self.cfg["activeHeroId"] = hero_id
        config.save_config(self.cfg)
        self.hero_list.blockSignals(True)
        self._refresh_hero_list(keep_blocked=True)
        self._select_hero_by_id(hero_id)
        self.hero_list.blockSignals(False)
        self._on_hero_selected()
        self.log_label.setText(f"\u25ba \u5207\u6362\u5230: {hero_name}")

    def _toggle_game_only(self):
        self.cfg["onlyTriggerWhenGameForeground"] = self.game_only_cb.isChecked()
        config.save_config(self.cfg)
        self._update_game_status_label()

    def _on_volume_changed(self, val):
        self.cfg["masterVolume"] = val / 100.0
        config.save_config(self.cfg)
        self._update_volume_display()

    def closeEvent(self, event):
        self._save_geometry()
        self._stop_monitor()
        super().closeEvent(event)









