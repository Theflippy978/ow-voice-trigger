import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QRadioButton,
    QButtonGroup, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer

import core.config as config
from core.key_recorder import record_key


class BindingDialog(QDialog):

    def __init__(self, parent=None, binding=None, on_record_start=None, on_record_end=None):
        super().__init__(parent)
        self.binding = binding
        self.result_data = None
        self.sounds = list(binding.get("sounds", [])) if binding else []
        self.on_record_start = on_record_start
        self.on_record_end = on_record_end
        self.setWindowTitle("编辑绑定" if binding else "添加绑定")
        self.setFixedSize(440, 480)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        label = QLabel("绑定名称（如: 大招）")
        label.setObjectName("label")
        layout.addWidget(label)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入绑定名称")
        if self.binding:
            self.name_edit.setText(self.binding.get("name", ""))
        layout.addWidget(self.name_edit)

        key_row = QHBoxLayout()
        key_label = QLabel("按键")
        key_label.setObjectName("label")
        key_row.addWidget(key_label)
        key_row.addStretch(1)
        layout.addLayout(key_row)

        key_input_row = QHBoxLayout()
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("点击录制后按下键盘")
        if self.binding:
            self.key_edit.setText(self.binding.get("keyBinding", ""))
        key_input_row.addWidget(self.key_edit)

        self.record_btn = QPushButton("录制")
        self.record_btn.setObjectName("accent")
        self.record_btn.clicked.connect(self._start_recording)
        key_input_row.addWidget(self.record_btn)
        layout.addLayout(key_input_row)

        sound_label = QLabel("音频文件")
        sound_label.setObjectName("label")
        layout.addWidget(sound_label)

        sound_row = QHBoxLayout()
        self.sounds_list = QListWidget()
        self.sounds_list.setMaximumHeight(80)
        for s in self.sounds:
            self.sounds_list.addItem(os.path.basename(s))
        sound_row.addWidget(self.sounds_list)

        sound_btn_col = QVBoxLayout()
        add_sound_btn = QPushButton("+")
        add_sound_btn.setObjectName("accent")
        add_sound_btn.clicked.connect(self._add_sound)
        add_sound_btn.setFixedSize(44, 38)
        sound_btn_col.addWidget(add_sound_btn)

        del_sound_btn = QPushButton("-")
        del_sound_btn.setObjectName("danger")
        del_sound_btn.clicked.connect(self._remove_sound)
        del_sound_btn.setFixedSize(44, 38)
        sound_btn_col.addWidget(del_sound_btn)
        sound_btn_col.addStretch(1)
        sound_row.addLayout(sound_btn_col)
        layout.addLayout(sound_row)

        cd_row = QHBoxLayout()
        cd_label = QLabel("冷却时间(ms)")
        cd_label.setObjectName("label")
        cd_row.addWidget(cd_label)
        cd_row.addStretch(1)
        layout.addLayout(cd_row)

        self.cooldown_edit = QLineEdit()
        self.cooldown_edit.setPlaceholderText("1000")
        if self.binding:
            self.cooldown_edit.setText(str(self.binding.get("cooldownMs", 1000)))
        else:
            self.cooldown_edit.setText("1000")
        layout.addWidget(self.cooldown_edit)

        mode_label = QLabel("播放模式")
        mode_label.setObjectName("label")
        layout.addWidget(mode_label)

        mode_row = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.mode_random = QRadioButton("随机")
        self.mode_sequential = QRadioButton("顺序")
        self.mode_no_repeat = QRadioButton("随机不重复")
        self.mode_group.addButton(self.mode_random, 0)
        self.mode_group.addButton(self.mode_sequential, 1)
        self.mode_group.addButton(self.mode_no_repeat, 2)
        mode_row.addWidget(self.mode_random)
        mode_row.addWidget(self.mode_sequential)
        mode_row.addWidget(self.mode_no_repeat)
        mode_row.addStretch(1)
        layout.addLayout(mode_row)

        current_mode = self.binding.get("playMode", "random") if self.binding else "random"
        if current_mode == "random":
            self.mode_random.setChecked(True)
        elif current_mode == "sequential":
            self.mode_sequential.setChecked(True)
        else:
            self.mode_no_repeat.setChecked(True)

        layout.addStretch(1)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("accent")
        ok_btn.clicked.connect(self._on_ok)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    def _start_recording(self):
        self.key_edit.setText("按下按键中...")
        self.record_btn.setEnabled(False)
        if self.on_record_start:
            self.on_record_start()
        record_key(self._on_record_done)

    def _on_record_done(self, result):
        if result:
            self.key_edit.setText(result)
        else:
            self.key_edit.setText("")
        self.record_btn.setEnabled(True)
        if self.on_record_end:
            self.on_record_end()

    def _add_sound(self):
        base_dir = config.get_base_dir()
        sounds_dir = os.path.join(base_dir, "sounds")
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择音频文件",
            sounds_dir if os.path.exists(sounds_dir) else base_dir,
            "音频文件 (*.mp3 *.wav)"
        )
        for f in files:
            if f not in self.sounds:
                self.sounds.append(os.path.basename(f))
                self.sounds_list.addItem(os.path.basename(f))

    def _remove_sound(self):
        row = self.sounds_list.currentRow()
        if row >= 0:
            self.sounds_list.takeItem(row)
            self.sounds.pop(row)

    def _on_ok(self):
        name = self.name_edit.text().strip()
        key = self.key_edit.text().strip()
        if not name or not key or "按下按键中" in key:
            QMessageBox.warning(self, "提示", "请填写名称和按键")
            return

        mode = "random"
        if self.mode_sequential.isChecked():
            mode = "sequential"
        elif self.mode_no_repeat.isChecked():
            mode = "random_no_repeat"

        try:
            cooldown = int(self.cooldown_edit.text().strip())
        except ValueError:
            cooldown = 1000

        self.result_data = {
            "name": name, "keyBinding": key, "sounds": self.sounds,
            "cooldownMs": cooldown, "playMode": mode, "volume": 1.0
        }
        self.accept()
