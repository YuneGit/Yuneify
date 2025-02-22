from PySide6.QtWidgets import QApplication

def apply_dark_theme(app):
    """Applies a consistent dark theme to the entire PySide6 application."""
    app.setStyleSheet("""                      
        QMainWindow, QWidget {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border-radius: 10px;
        }
        QLabel {
            color: #FFFFFF;
            font-size: 13px;
            margin: 5px;
        }
        QPushButton {
            background-color: #3A3A3A;
            color: #FFFFFF;
            border-radius: 12px;
            padding: 4px 4px;
            font-size: 14px;
            border: 1px solid #5A5A5A;
        }
        QPushButton:hover {
            background-color: #4A4A4A;
        }
        QPushButton:pressed {
            background-color: #2A2A2A;
        }
        QListWidget {
            background-color: #2A2A2A;
            border: 1px solid #5A5A5A;
            border-radius: 5px;
            padding: 2px;
            font-size: 12px;
        }
        QListWidget::item {
            padding: 1px;
            border-radius: 3px;
        }
        QListWidget::item:selected {
            background-color: #4A4A4A;
        }
        QComboBox {
            background-color: #3A3A3A;
            color: #FFFFFF;
            border-radius: 3px;
            padding: 3px;
            border: 1px solid #5A5A5A;
            min-width: 20px;
            font-size: 13px;
        }
        QComboBox QAbstractItemView {
            background-color: #2A2A2A;
            color: #FFFFFF;
            selection-background-color: #4A4A4A;
        }
        QLineEdit {
            background-color: #2A2A2A;
            color: #FFFFFF;
            border-radius: 3px;
            padding: 3px;
            border: 1px solid #5A5A5A;
        }
        QSpinBox {
            background-color: #2A2A2A;
            color: #FFFFFF;
            border-radius: 3px;
            padding: 3px;
            border: 1px solid #5A5A5A;
        }
        QTabWidget::pane {
            border: 1px solid #5A5A5A;
            background-color: #1E1E1E;
        }
        QTabBar::tab {
            background: #3A3A3A;
            color: #FFFFFF;
            padding: 5px;
            border: 1px solid #5A5A5A;
            border-bottom-color: #1E1E1E; /* same as pane color */
        }
        QTabBar::tab:selected {
            background: #4A4A4A;
            border-bottom-color: #4A4A4A; /* same as tab color */
        }
        QTabBar::tab:hover {
            background: #5A5A5A;
        }
        QPushButton#visualizeButton {
            background-color: #3A3A3A;
            color: #FFFFFF;
            border-radius: 12px;
            padding: 4px 4px;
            font-size: 14px;
            border: 1px solid #5A5A5A;
        }
        QPushButton#visualizeButton:hover {
            background-color: #4A4A4A;
        }
        QPushButton#visualizeButton:pressed {
            background-color: #2A2A2A;
        }
        QPushButton#zoomButton {
            background-color: #3A3A3A;
            border-radius: 2px;
            min-width: 7px;
            min-height: 7px;
            max-width: 7px;
            max-height: 7px;
        }
        QPushButton#zoomButton:hover {
            background-color: #4A4A4A;
        }
        QPushButton#zoomButton:pressed {
            background-color: #2A2A2A;
        }
        QLabel#instructions {
            color: #AAAAAA;
            font-size: 12px;
            margin: 5px;
        }
        # Add these styles to the existing stylesheet
        QTreeWidget#presetTree {
            background-color: #2A2A2A;
            color: #FFFFFF;
            border: 1px solid #5A5A5A;
            border-radius: 5px;
        }

        QTreeWidget::item {
            padding: 5px;
        }

        QTreeWidget::item:selected {
            background-color: #4A4A4A;
        }

        QPushButton#saveButton, QPushButton#loadButton {
            min-width: 90px;
            padding: 8px;
        }

        QPushButton#refreshButton {
            padding: 6px;
            font-size: 12px;
        }                      
    """)