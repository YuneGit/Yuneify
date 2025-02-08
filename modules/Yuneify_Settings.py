import sys
import json
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit, QFormLayout, QHBoxLayout
from PySide6.QtGui import QPixmap, QKeySequence
from PySide6.QtCore import Qt
from modules.utils import setup_logger

class KeybindUI(QWidget):
    def __init__(self, main_menu):
        super().__init__(main_menu)
        self.logger = setup_logger('KeybindUI', 'keybind_ui')
        self.logger.info("KeybindUI initialized.")

        self.main_menu = main_menu
        self.setStyleSheet("background-color: #1E1E1E; color: #E0E0E0;")

        # Load existing keybinds
        self.keybinds = self.load_keybinds()

        # Main layout
        self.layout = QVBoxLayout(self)

        # Add keybind change form
        self.add_keybind_form()

        # Add back button
        self.add_back_button()

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

        self.layout.addLayout(vertical_layout)

    def add_back_button(self):
        back_button = QPushButton("Back", self)
        back_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        back_button.clicked.connect(self.go_back)
        self.layout.addWidget(back_button)

    def go_back(self):
        self.main_menu.stacked_widget.setCurrentIndex(0)

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

    def load_keybinds(self):
        script_folder = os.path.dirname(os.path.abspath(__file__))
        config_folder = os.path.join(script_folder, "config-files")
        keybind_file = os.path.join(config_folder, "keybinds.json")
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
        config_folder = os.path.join(script_folder, "config-files")
        keybind_file = os.path.join(config_folder, "keybinds.json")
        for action, input_field in self.keybind_inputs.items():
            self.keybinds[action] = input_field.text()
        with open(keybind_file, 'w') as file:
            json.dump(self.keybinds, file)
        self.logger.info("Keybinds saved: %s", self.keybinds)

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
        self.logger.info("Keybinds reset to defaults.")

def main():
    app = QApplication([])
    window = KeybindUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
