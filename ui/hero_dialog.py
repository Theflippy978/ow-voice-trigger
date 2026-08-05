from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt


class HeroDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = None
        self.setWindowTitle("新建英雄")
        self.setFixedSize(360, 180)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        label = QLabel("英雄名称")
        label.setObjectName("label")
        layout.addWidget(label)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入英雄名称")
        self.name_edit.setFocus()
        layout.addWidget(self.name_edit)

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

        self.name_edit.returnPressed.connect(self._on_ok)

    def _on_ok(self):
        name = self.name_edit.text().strip()
        if name:
            self.result_data = {"name": name}
            self.accept()
        else:
            self.name_edit.setFocus()
