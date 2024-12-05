import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from Yuneify_Settings import KeybindUI  # Import the KeybindUI class

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yuneify Main Menu")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #1E1E1E; color: #E0E0E0;")

        # Main layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Stacked widget to switch between main menu and settings
        self.stacked_widget = QStackedWidget(self)
        self.layout.addWidget(self.stacked_widget)

        # Main menu widget
        self.main_menu_widget = QWidget()
        self.main_menu_layout = QHBoxLayout(self.main_menu_widget)
        self.stacked_widget.addWidget(self.main_menu_widget)

        # Add logo and buttons to main menu
        self.add_logo(self.main_menu_layout)
        self.add_buttons(self.main_menu_layout)

        # Keybind settings widget
        self.keybind_ui = KeybindUI(self)
        self.stacked_widget.addWidget(self.keybind_ui)

        # Context Wheel process
        self.context_wheel_process = None

    def add_logo(self, layout):
        logo_label = QLabel(self)
        pixmap = QPixmap()
        if pixmap.load("TwitchLogo.png"):
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            print("Failed to load TwitchLogo.png")
        logo_label.setFixedSize(150, 150)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

    def add_buttons(self, layout):
        button_layout = QVBoxLayout()

        self.context_wheel_button = QPushButton("Start Context Wheel", self)
        self.context_wheel_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        self.context_wheel_button.clicked.connect(self.toggle_context_wheel)
        button_layout.addWidget(self.context_wheel_button)

        ai_ui_button = QPushButton("Open AI UI", self)
        ai_ui_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        ai_ui_button.clicked.connect(self.open_ai_ui)
        button_layout.addWidget(ai_ui_button)

        settings_button = QPushButton("Keybind Settings", self)
        settings_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        settings_button.clicked.connect(self.show_keybind_settings)
        button_layout.addWidget(settings_button)

        layout.addLayout(button_layout)

    def toggle_context_wheel(self):
        if self.context_wheel_process is None:
            self.context_wheel_process = subprocess.Popen([sys.executable, 'Yuneify_ContextWheel.py'])
            self.context_wheel_button.setText("Stop Context Wheel")
            print("Context Wheel started.")
        else:
            self.context_wheel_process.terminate()
            self.context_wheel_process = None
            self.context_wheel_button.setText("Start Context Wheel")
            print("Context Wheel stopped.")

    def open_ai_ui(self):
        subprocess.Popen([sys.executable, 'Yuneify_AI.py'])
        print("AI UI opened.")

    def show_keybind_settings(self):
        self.stacked_widget.setCurrentWidget(self.keybind_ui)

def main():
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
