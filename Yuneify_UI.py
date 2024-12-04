# UI.py

import sys
import json
import subprocess
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit, QFormLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import Qt

class KeybindUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keybind Settings")
        self.setGeometry(100, 100, 516, 219)
        self.setStyleSheet("background-color: #1E1E1E; color: #E0E0E0;")

        # Center the window on the screen
        self.center_window()

        # Load existing keybinds
        self.keybinds = self.load_keybinds()

        # Main layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)

        # Add Twitch logo
        self.add_twitch_logo()

        # Add keybind change form
        self.add_keybind_form()

    def center_window(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height() - 100) // 2
        self.move(x, y)

    def add_twitch_logo(self):
        logo_label = QLabel(self)
        pixmap = QPixmap("TwitchLogo.png")
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(logo_label)

    def add_keybind_form(self):
        form_layout = QFormLayout()
        self.keybind_inputs = {}

        # Add a label for the keybinds section
        keybinds_label = QLabel("Context Wheel Keybinds", self)
        keybinds_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        form_layout.addRow(keybinds_label)

        for action, keybind in self.keybinds.items():
            input_field = QLineEdit(keybind)
            input_field.setStyleSheet("background-color: #3A3A3A; color: #FFFFFF; border: 1px solid #555555; border-radius: 5px;")
            input_field.setPlaceholderText("Press new keybind")
            input_field.setReadOnly(True)
            input_field.mousePressEvent = lambda event, field=input_field: self.capture_keybind(field)
            form_layout.addRow(action.replace('_', ' ').title(), input_field)
            self.keybind_inputs[action] = input_field

        # Create a vertical layout to center the form and buttons
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(form_layout)

        save_button = QPushButton("Save Keybinds", self)
        save_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        save_button.clicked.connect(self.save_keybinds)
        vertical_layout.addWidget(save_button)

        reset_button = QPushButton("Reset Keybinds", self)
        reset_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        reset_button.clicked.connect(self.reset_keybinds)
        vertical_layout.addWidget(reset_button)

        # Add VS Code launch button underneath the keybinds
        vscode_button = QPushButton("Launch VS Code", self)
        vscode_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        vscode_button.clicked.connect(self.launch_vscode)
        vertical_layout.addWidget(vscode_button)

        # Create a widget to hold the vertical layout and add it to the main layout
        form_widget = QWidget()
        form_widget.setLayout(vertical_layout)
        self.layout.addWidget(form_widget, alignment=Qt.AlignCenter)  # Center the form widget

    def capture_keybind(self, input_field):
        input_field.setText("Press a key...")
        input_field.setFocus()
        input_field.setReadOnly(False)
        input_field.keyPressEvent = lambda event: self.set_keybind(event, input_field)

    def set_keybind(self, event, input_field):
        key = event.key()
        modifiers = QApplication.keyboardModifiers()

        key_sequence = []
        if modifiers & Qt.ControlModifier:
            key_sequence.append("CTRL")
        if modifiers & Qt.ShiftModifier:
            key_sequence.append("SHIFT")
        if modifiers & Qt.AltModifier:
            key_sequence.append("ALT")

        key_name = event.text().upper() if event.text() else QKeySequence(key).toString()
        if key_name and key_name not in key_sequence:
            key_sequence.append(key_name)

        input_field.setText('+'.join(key_sequence))
        input_field.setReadOnly(True)

    def launch_vscode(self):
        default_code_path = "C:\\Program Files\\Microsoft VS Code\\Code.exe"
        script_folder = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(default_code_path):
            try:
                subprocess.Popen([default_code_path, script_folder])
            except Exception as e:
                print(f"Could not open VS Code: {e}")

    def load_keybinds(self):
        script_folder = os.path.dirname(os.path.abspath(__file__))
        keybind_file = os.path.join(script_folder, "keybinds.json")
        try:
            with open(keybind_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {
                'state_suite': 'CTRL+SHIFT+ALT+Q',
                'send_manager': 'CTRL+SHIFT+ALT+W',
                'midi_suite': 'CTRL+SHIFT+ALT+E'
            }

    def save_keybinds(self):
        script_folder = os.path.dirname(os.path.abspath(__file__))
        keybind_file = os.path.join(script_folder, "keybinds.json")
        for action, input_field in self.keybind_inputs.items():
            self.keybinds[action] = input_field.text()
        with open(keybind_file, 'w') as file:
            json.dump(self.keybinds, file)

    def reset_keybinds(self):
        default_keybinds = {
            'state_suite': 'CTRL+SHIFT+ALT+Q',
            'send_manager': 'CTRL+SHIFT+ALT+W',
            'midi_suite': 'CTRL+SHIFT+ALT+E'
        }
        for action, keybind in default_keybinds.items():
            self.keybind_inputs[action].setText(keybind)
        self.keybinds = default_keybinds
        self.save_keybinds()

def main():
    app = QApplication(sys.argv)
    window = KeybindUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
