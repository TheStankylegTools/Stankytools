
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor

def _glow(widget, blur=32, alpha=60):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0,4)
    effect.setColor(QColor(120,160,255,alpha))
    widget.setGraphicsEffect(effect)

class GlassCard(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("GlassCard")
        self.setStyleSheet("""
        QFrame#GlassCard{
            background:rgba(20,24,34,230);
            border:none;
            border-radius:18px;
        }
        """)
        _glow(self)

class SidebarButton(QPushButton):
    def __init__(self,text="",parent=None):
        super().__init__(text,parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(48)
        self.setStyleSheet("""
        QPushButton{
            background:rgba(255,255,255,0.03);
            border:none;
            border-radius:18px;
            padding:14px;
            text-align:left;
            font-size:14px;
        }
        QPushButton:hover{
            background:rgba(255,255,255,0.08);
        }
        QPushButton:checked{
            background:rgba(90,120,255,0.18);
        }
        """)

class StatusPill(QLabel):
    def __init__(self,text,parent=None):
        super().__init__(text,parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
        QLabel{
            background:rgba(80,180,120,0.18);
            border-radius:12px;
            padding:4px 10px;
        }
        """)

class StatCard(GlassCard):
    def __init__(self,title,value="-",parent=None):
        super().__init__(parent)
        layout=QVBoxLayout(self)
        layout.setContentsMargins(22,22,22,22)
        t=QLabel(title.upper())
        v=QLabel(str(value))
        t.setStyleSheet("font-size:12px;color:#9aa4b2;")
        v.setStyleSheet("font-size:28px;font-weight:700;")
        layout.addWidget(t)
        layout.addStretch()
        layout.addWidget(v)

class MemberCard(GlassCard):
    def __init__(self,name,role,parent=None):
        super().__init__(parent)
        l=QHBoxLayout(self)
        n=QLabel(name)
        r=StatusPill(role)
        l.addWidget(n)
        l.addStretch()
        l.addWidget(r)

class QuickActionButton(GlassCard):
    def __init__(self,title,parent=None):
        super().__init__(parent)
        l=QVBoxLayout(self)
        lbl=QLabel(title)
        lbl.setStyleSheet("font-size:15px;font-weight:600;")
        l.addWidget(lbl)
