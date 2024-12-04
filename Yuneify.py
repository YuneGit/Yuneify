import sys
import subprocess
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from Yuneify_Settings import KeybindUI  # Import the KeybindUI class

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yuneify Main Menu")
        self.setGeometry(100, 100, 400, 250)
        self.setStyleSheet("background-color: #1E1E1E; color: #E0E0E0;")

        # Main layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Add buttons
        self.add_buttons()

        # Context Wheel process
        self.context_wheel_process = None

    def add_buttons(self):
        self.context_wheel_button = QPushButton("Start Context Wheel", self)
        self.context_wheel_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        self.context_wheel_button.clicked.connect(self.toggle_context_wheel)
        self.layout.addWidget(self.context_wheel_button)

        ai_ui_button = QPushButton("Open AI UI", self)
        ai_ui_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        ai_ui_button.clicked.connect(self.open_ai_ui)
        self.layout.addWidget(ai_ui_button)

        settings_button = QPushButton("Keybind Settings", self)
        settings_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        settings_button.clicked.connect(self.open_keybind_settings)
        self.layout.addWidget(settings_button)

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

    def open_keybind_settings(self):
        self.keybind_window = KeybindUI()
        self.keybind_window.show()

def main():
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
