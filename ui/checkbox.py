from PySide6.QtWidgets import QCheckBox, QStyleOptionButton, QStyle
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen


class CheckMarkCheckBox(QCheckBox):
    """带对号的复选框，选中时显示勾号而非仅变色"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制方形指示器
        indicator_size = 18
        x = 0
        y = (self.height() - indicator_size) // 2
        rect = QRect(x, y, indicator_size, indicator_size)

        # 背景
        if opt.state & QStyle.State_On:
            painter.fillRect(rect, self.palette().highlight())
            painter.setPen(QPen(self.palette().highlight().color().lighter(120), 1))
        else:
            painter.fillRect(rect, self.palette().base())
            painter.setPen(QPen(self.palette().mid().color(), 1))
        painter.drawRoundedRect(rect, 4, 4)

        # 对号
        if opt.state & QStyle.State_On:
            painter.setPen(QPen(self.palette().highlightedText(), 2))
            painter.drawLine(x + 4, y + 9, x + 8, y + 13)
            painter.drawLine(x + 8, y + 13, x + 14, y + 5)

        # 文本
        text_rect = QRect(x + indicator_size + 8, 0, self.width() - indicator_size - 8, self.height())
        painter.setPen(QPen(self.palette().text(), 1))
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())
