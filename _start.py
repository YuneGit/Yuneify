import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt

# Use the current Python executable dynamically
PYTHON_EXECUTABLE = sys.executable

class ScriptToggleApp(QMainWindow):
    def __init__(self, scripts_directory):
        super().__init__()
        self.scripts_directory = scripts_directory
        self.processes = {}  # Store subprocesses for running scripts

        # Set up the main window
        self.setWindowTitle("Script Toggle")
        self.setGeometry(200, 100, 400, 275)

        # Set dark mode style with sleeker UI
        self.setStyleSheet("""
            QMainWindow {
                background-color: #222222;
                border-radius: 10px;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 16px;
                font-weight: normal;
                margin: 5px;
            }
            QPushButton {
                background-color: #444444;
                color: #E0E0E0;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
            QScrollArea {
                background-color: #222222;
            }
            QWidget {
                background-color: #222222;
                border-radius: 10px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()

        # Add a scroll area to handle a large number of scripts
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Load scripts and create buttons
        self.script_buttons = {}
        self.load_scripts(scroll_layout)

        # Set the scroll area properties
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout.addWidget(scroll_area)

        # Set the main widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_scripts(self, layout):
        """Load Python scripts from the specified directory and create buttons."""
        for file_name in os.listdir(self.scripts_directory):
            # Exclude "Yuneify.py" and the launch script itself
            if file_name.endswith('.py') and file_name != "Yuneify.py" and file_name != os.path.basename(__file__):  
                script_path = os.path.join(self.scripts_directory, file_name)

                # Create layout for each script with sleek appearance
                script_layout = QHBoxLayout()
                script_label = QLabel(file_name)
                toggle_button = QPushButton("Start")
                
                # Add to the dictionary for tracking
                self.script_buttons[script_path] = toggle_button

                # Connect the toggle button with a function
                toggle_button.clicked.connect(lambda checked, path=script_path: self.toggle_script(path))

                # Add elements to the script layout
                script_layout.addWidget(script_label)
                script_layout.addWidget(toggle_button)
                script_layout.setSpacing(10)

                # Add the script layout to the main layout
                layout.addLayout(script_layout)

    def toggle_script(self, script_path):
        """Start or stop the script based on its current state."""
        button = self.script_buttons[script_path]

        if script_path in self.processes:
            # Stop the script if it's already running
            self.processes[script_path].terminate()
            self.processes[script_path].wait()
            del self.processes[script_path]
            button.setText("Start")
        else:
            # Start the script
            try:
                process = subprocess.Popen([PYTHON_EXECUTABLE, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes[script_path] = process
                button.setText("Stop")
            except Exception as e:
                print(f"Error starting script {script_path}: {e}")
                button.setText("Error")

    def closeEvent(self, event):
        """Override closeEvent to ensure all running scripts are terminated."""
        for process in self.processes.values():
            process.terminate()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the directory containing Python scripts to the current script directory
    scripts_directory = os.path.dirname(os.path.abspath(__file__))

    # Create and show the main window
    window = ScriptToggleApp(scripts_directory)
    window.show()

    sys.exit(app.exec_())
