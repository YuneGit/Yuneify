import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget, QLabel, QHBoxLayout, QTextBrowser
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap
from modules.Yuneify_Settings import KeybindUI
from modules.Yuneify_ContextWheel import main as context_wheel_main
from Yuneify_AI import MainApplication as yuneify_ai_main
from modules.utils import setup_logger
import subprocess
import shutil

def initialize_logger():
    """Initialize a logger with a unique filename for each session."""
    return setup_logger('Yuneify', 'yuneify')

class DebugThread(QThread):
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        while self._running:
            self.log_signal.emit("Checking state...")
            self.sleep(2)

    def stop(self):
        self._running = False
        self.wait()  # Wait for the thread to finish

class DebugWindow(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.logger.info("DebugWindow initialized.")
        self.setWindowTitle("Debugging Information")
        self.setGeometry(200, 100, 400, 300)
        self.setStyleSheet("background-color: #1E1E1E; color: #E0E0E0;")
        self.layout = QVBoxLayout(self)
        self.text_browser = QTextBrowser(self)
        self.layout.addWidget(self.text_browser)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_logs)
        self.timer.start(2000)
        self.file_positions = {}  # Track file read positions

    def update_log(self, message):
        self.text_browser.append(message)

    def read_logs(self):
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules', 'logs')
        log_files = [f for f in os.listdir(base_path) if f.endswith('.log')]
        log_files.sort(reverse=True)

        for log_file in log_files[:3]:
            log_path = os.path.join(base_path, log_file)
            try:
                with open(log_path, 'r') as file:
                    # Get the last position read for this file
                    last_position = self.file_positions.get(log_file, 0)
                    file.seek(last_position)  # Move to the last read position
                    new_content = file.read()  # Read new content

                    if new_content:  # If there is new content, append it
                        self.text_browser.append(new_content)
                        self.file_positions[log_file] = file.tell()  # Update the read position
            except FileNotFoundError:
                self.text_browser.append(f"Log file {log_file} not found at {log_path}.")
class MainMenu(QMainWindow):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.setWindowTitle("Yuneify Main Menu")
        self.setGeometry(100, 100, 100, 150)
        self.setStyleSheet("background-color: #1E1E1E; color: #E0E0E0;")
        self.debug_window = DebugWindow(self.logger)
        self.debug_window.show()
        self.debug_thread = DebugThread()
        self.debug_thread.log_signal.connect(self.debug_window.update_log)
        self.debug_thread.start()
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.stacked_widget = QStackedWidget(self)
        self.layout.addWidget(self.stacked_widget)
        self.main_menu_widget = QWidget()
        self.main_menu_layout = QHBoxLayout(self.main_menu_widget)
        self.stacked_widget.addWidget(self.main_menu_widget)
        self.add_logo(self.main_menu_layout)
        self.add_buttons(self.main_menu_layout)
        self.keybind_ui = KeybindUI(self)
        self.stacked_widget.addWidget(self.keybind_ui)
        self.context_wheel_process = None
        self.destroyed.connect(self.cleanup)

    def cleanup(self):
        if self.debug_thread.isRunning():
            self.debug_thread.stop()  # Ensure the thread is stopped

    def get_resource_path(self, relative_path):
        # Directly return the absolute path in the expected folder
        base_path = os.path.abspath(".")  # This will point to the current working directory
        return os.path.join(base_path, relative_path)
    
    def add_logo(self, layout):
        logo_label = QLabel(self)
        pixmap = QPixmap()
        logo_path = self.get_resource_path("dependencies/TwitchLogo.png")
        if pixmap.load(logo_path):
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            self.debug_window.update_log(f"Failed to load {logo_path}")
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
        ai_ui_button.clicked.connect(self.open_ai_ui)  # Connect to the missing method
        button_layout.addWidget(ai_ui_button)
        
        settings_button = QPushButton("Keybind Settings", self)
        settings_button.setStyleSheet("background-color: #4A4A4A; color: #FFFFFF; border-radius: 5px; padding: 5px;")
        settings_button.clicked.connect(self.show_keybind_settings)
        button_layout.addWidget(settings_button)
        
        layout.addLayout(button_layout)

    def toggle_context_wheel(self):
        if self.context_wheel_process is None:
            self.debug_window.update_log("Starting Context Wheel...")
            try:
                context_wheel_main()
                self.context_wheel_button.setText("Stop Context Wheel")
                self.debug_window.update_log("Context Wheel started.")
            except Exception as e:
                self.debug_window.update_log(f"Error starting Context Wheel: {str(e)}")
        else:
            self.debug_window.update_log("Stopping Context Wheel...")
            try:
                self.context_wheel_process = None
                self.context_wheel_button.setText("Start Context Wheel")
                self.debug_window.update_log("Context Wheel stopped.")
            except Exception as e:
                self.debug_window.update_log(f"Error stopping Context Wheel: {str(e)}")

    def show_keybind_settings(self):
        self.stacked_widget.setCurrentWidget(self.keybind_ui)

    # Define the missing open_ai_ui method here
    def open_ai_ui(self):
        self.debug_window.update_log("Opening AI UI...")
        exe_path = None  # Initialize exe_path variable to avoid undefined error
        try:
            # Get the path to the executable and script
            exe_path = self.get_resource_path("Yuneify_AI.exe")
            script_path = self.get_resource_path("Yuneify_AI.py")

            # Check if we are running from the correct directory
            if os.path.exists(exe_path):
                self.debug_window.update_log(f"Found executable at {exe_path}, launching...")
                subprocess.Popen([exe_path])
            elif os.path.exists(script_path):
                self.debug_window.update_log(f"Executable not found at {exe_path}, launching Python script at {script_path}...")
                python_executable = shutil.which("python") or shutil.which("python3")
                if python_executable:
                    subprocess.Popen([python_executable, script_path])
                else:
                    raise EnvironmentError("Python executable not found.")
            else:
                self.debug_window.update_log(f"Neither executable nor script found. exe_path: {exe_path}, script_path: {script_path}")
                raise FileNotFoundError("Neither executable nor script found.")
            
            self.debug_window.update_log("AI UI opened successfully.")
        except Exception as e:
            # Log the exe_path for debugging
            if exe_path:
                self.debug_window.update_log(f"Executable path: {exe_path}")
            self.debug_window.update_log(f"Error opening AI UI: {str(e)}")

def main():
    logger = initialize_logger()
    app = QApplication([])
    window = MainMenu(logger)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
