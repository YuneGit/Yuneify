import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QPixmap

# Import the classes from each script
from State_Suite import TrackControlApp
from Send_Manager import TrackRouter
from Plugin_Suggestion_Suite import PluginSuggestionApp
from MIDI_AI import AIOrchestrationStyleSelector
from MIDI_Suite import MidiSuite

def main():
    # Initialize the PyQt5 application
    app = QApplication(sys.argv)
    window = QMainWindow()
    central_widget = QWidget()
    layout = QGridLayout(central_widget)

    # Set the background color to dark mode
    central_widget.setStyleSheet("background-color: #1E1E1E;")

    # Create instances of each PyQt5 class
    track_control_app = TrackControlApp()
    track_router = TrackRouter()
    plugin_suggestion_app = PluginSuggestionApp()
    midi_ai = AIOrchestrationStyleSelector()
    midi_suite = MidiSuite()

    # Add widgets to the grid layout
    layout.addWidget(track_control_app, 0, 0)
    layout.addWidget(track_router, 0, 1)
    layout.addWidget(plugin_suggestion_app, 1, 0)
    layout.addWidget(midi_ai, 1, 1)

    # Add the TwitchLogo.png to the grid
    logo_label = QLabel()
    pixmap = QPixmap("TwitchLogo.png")
    logo_label.setPixmap(pixmap)
    layout.addWidget(logo_label, 2, 1)  # Place the image in the second grid slot

    # Add the MidiSuite to the grid
    layout.addWidget(midi_suite, 2, 0)  # Place MidiSuite in the first grid slot

    window.setCentralWidget(central_widget)
    window.setWindowTitle("Unified Audio Suite")
    window.setGeometry(100, 100, 550, 550)  # Set window size to fit the grid
    window.show()

    # Start the PyQt5 event loop
    app.exec_()

if __name__ == "__main__":
    main()
