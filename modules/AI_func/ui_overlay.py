from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QBrush, QPalette

class OverlayUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Configure label
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 24px;
                font-weight: bold;
                background-color: rgba(30, 30, 30, 150);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.label.resize(200, 60)
        
        # Fade animation
        self.fade_anim = QPropertyAnimation(self.label, b"windowOpacity")
        self.fade_anim.setDuration(2000)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutQuad)
        
    def show_message(self, text):
        """Show a message with fade animation"""
        self.label.setText(text)
        self.label.adjustSize()
        self.label.setWindowOpacity(1.0)
        self.fade_anim.start()

    def paintEvent(self, event):
        """Add rounded corners and subtle border"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(30, 30, 30, 150)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.label.geometry(), 10, 10)
