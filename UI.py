import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import QThread

# Import the classes from each script
from State_Suite import TrackControlApp
from Send_Manager import TrackRouter
from Plugin_Suggestion_Suite import PluginSuggestionApp
from MIDI_Suite import MidiSuite
from MIDI_AI import AIOrchestrationStyleSelector
from Height_Lock import TrackHeightLock
from Auto_VST_Window import FloatingFXController

class BackgroundWorker(QThread):
    """Generic worker thread to run a background process."""
    def __init__(self, target_object, target_method):
        super().__init__()
        self.target_object = target_object
        self.target_method = target_method

    def run(self):
        """Execute the specified method from the target object."""
        method = getattr(self.target_object, self.target_method)
        method()
        # Emit a signal if you need to update the UI after the method completes
        # self.finished.emit()  # Uncomment if you have a signal to emit

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unified Audio Suite")
        self.setGeometry(100, 100, 1200, 800)

        # Create a tab widget to hold different functionalities
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add each functionality as a tab
        self.add_tab(TrackControlApp(), "Track Control")
        self.add_tab(TrackRouter(), "Track Router")
        self.add_tab(PluginSuggestionApp(), "Plugin Suggestion")
        self.add_tab(MidiSuite(), "MIDI Suite")
        self.add_tab(AIOrchestrationStyleSelector(), "MIDI AI")

        # Create a control panel for script buttons
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout()
        self.control_panel.setLayout(self.control_layout)

        # Add control panel to the main layout
        self.tabs.addTab(self.control_panel, "Control Panel")

        # Dictionary to store threads and components
        self.threads = {}

        # Add buttons for scripts
        self.create_control_buttons()

    def add_tab(self, widget, title):
        """Add a new tab with the given widget and title."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(widget)
        tab.setLayout(layout)
        self.tabs.addTab(tab, title)

    def create_control_buttons(self):
        """Create buttons for loading and activating scripts."""
        scripts = [
            ("Track Height Lock", TrackHeightLock, "check_for_track_changes"),
            ("Floating FX Controller", FloatingFXController, "show_floating_fx_on_alt_and_mouse"),
            # Add more scripts here
            ("MIDI AI", AIOrchestrationStyleSelector, "background_analysis"),  # Example
        ]

        for label, cls, method in scripts:
            button = QPushButton(f"Load {label}")
            button.clicked.connect(lambda _, c=cls, m=method, l=label: self.load_script(c, m, l))
            self.control_layout.addWidget(button)

    def load_script(self, cls, method, label):
        """Initialize and activate the thread for the selected script."""
        if label in self.threads:
            # If the script is already loaded, notify the user
            print(f"{label} is already running!")
            return

        # Instantiate the class and create the worker thread
        instance = cls()
        thread = BackgroundWorker(instance, method)

        # Start the thread
        thread.start()

        # Store the thread to prevent garbage collection and allow tracking
        self.threads[label] = thread
        print(f"{label} loaded and running!")

def main():
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
