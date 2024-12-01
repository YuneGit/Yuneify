import sys
import math
import keyboard  # You may need to install this package
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject, QEvent
from PyQt5.QtGui import QPainter, QColor, QPen, QCursor
from State_Suite import TrackControlApp  # Import the TrackControlApp class
from MIDI_Suite import MidiSuite  # Import the MidiSuite class
from Send_Manager import TrackRouter  # Import the TrackRouter class
import json

class MouseFilter(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.window.close()
        return super().eventFilter(obj, event)

class ContextWheel(QMainWindow):
    show_signal = pyqtSignal()  # Define a custom signal

    def __init__(self, actions, show_navigation=False, navigate_next=None, navigate_prev=None):
        super().__init__()
        self.setWindowTitle("Context Wheel")
        self.setGeometry(100, 100, 400, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Connect the custom signal to a new method that handles showing the window
        self.show_signal.connect(self.show_at_cursor)

        # Main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Create buttons in a circular layout
        self.create_circular_buttons(actions)

        # Add a central "X" button to close the window
        self.add_close_button()

        # Optionally add navigation buttons
        if show_navigation:
            self.add_navigation_buttons(navigate_next, navigate_prev)

        # Install the event filter
        self.mouse_filter = MouseFilter(self)
        QApplication.instance().installEventFilter(self.mouse_filter)

    def show_at_cursor(self):
        # Get the current mouse position
        cursor_pos = QCursor.pos()
        
        # Move the window so that its center is at the cursor position
        self.move(cursor_pos.x() - self.width() // 2, cursor_pos.y() - self.height() // 2)
        
        # Show the window
        self.show()

    def create_circular_buttons(self, actions):
        # Calculate positions for buttons in a circle
        radius = 130  # Increase the radius to move buttons outward
        angle_step = 2 * math.pi / len(actions)  # Use radians for trigonometric functions
        center_x = self.width() // 2
        center_y = self.height() // 2
        for i, (label, callback) in enumerate(actions):
            angle = angle_step * i
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            self.add_button(label, callback, QPoint(x, y))

    def add_button(self, label, callback, position):
        button = QPushButton(label, self)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                padding: 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.adjustSize()
        
        # Calculate the center of the button
        button_size = button.size()
        button_center_x = button_size.width() // 2
        button_center_y = button_size.height() // 2
        
        # Move the button to center it on the calculated position
        button.move(position.x() - button_center_x, position.y() - button_center_y)
        button.clicked.connect(lambda: self.button_action(callback))

    def add_close_button(self):
        close_button = QPushButton("X", self)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                padding: 5px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        close_button.setFixedSize(30, 30)
        close_button.move(self.width() // 2 - 15, self.height() // 2 - 15)
        close_button.clicked.connect(self.close)

    def add_navigation_buttons(self, navigate_next, navigate_prev):
        next_button = QPushButton(">", self)
        next_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                padding: 5px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        next_button.setFixedSize(30, 30)
        next_button.move(self.width() // 2 + 25, self.height() // 2 - 15)
        next_button.clicked.connect(navigate_next)

        prev_button = QPushButton("<", self)
        prev_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                padding: 5px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        prev_button.setFixedSize(30, 30)
        prev_button.move(self.width() // 2 - 55, self.height() // 2 - 15)
        prev_button.clicked.connect(navigate_prev)

    def button_action(self, callback):
        callback()
        self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(255, 255, 255, 50), 2)
        painter.setPen(pen)
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = min(self.width(), self.height()) // 3
        painter.drawEllipse(center, radius, radius)

def create_send_sub_wheel(track_router, start_index=0):
    tracks = track_router.get_tracks()
    num_tracks = len(tracks)

    # Define actions for the sub-context wheel
    actions = []
    for i in range(start_index, min(start_index + 9, num_tracks)):
        track_name = tracks[i].name
        actions.append((track_name, lambda t=tracks[i]: track_router.create_send_to_track(t)))

    # Create and show the sub-context wheel with navigation buttons
    sub_wheel = ContextWheel(
        actions,
        show_navigation=True,
        navigate_next=lambda: create_send_sub_wheel(track_router, start_index + 9),
        navigate_prev=lambda: create_send_sub_wheel(track_router, max(0, start_index - 9))
    )
    sub_wheel.show_signal.emit()

def load_keybinds():
    try:
        with open("keybinds.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            'state_suite': 'ctrl+shift+alt+q',
            'send_manager': 'ctrl+shift+alt+w',
            'midi_suite': 'ctrl+shift+alt+e'
        }

def main():
    app = QApplication(sys.argv)

    # Load keybinds
    keybinds = load_keybinds()

    # Initialize the TrackControlApp, MidiSuite, and TrackRouter to access their methods
    track_control_app = TrackControlApp()
    midi_suite_app = MidiSuite()
    track_router = TrackRouter()

    # Define actions for each context wheel
    state_suite_actions = [
        ("Mute All Tracks", track_control_app.mute_all_tracks),
        ("Un-Mute All Tracks", track_control_app.unmute_all_tracks),
        ("Solo All Tracks", track_control_app.solo_all_tracks),
        ("Un-Solo All Tracks", track_control_app.unsolo_all_tracks),
        ("Solo Group", track_control_app.solo_selected_track_group),
        ("Un-Solo Group", track_control_app.unsolo_selected_track_group),
        ("Mute Group", track_control_app.mute_selected_track_group),
        ("Un-Mute Group", track_control_app.unmute_selected_track_group)
    ]

    send_manager_actions = [
        ("Create Send", lambda: create_send_sub_wheel(track_router)),
        ("Remove Send", track_router.remove_send)
    ]

    midi_suite_actions = [
        ("Adjust Velocities", midi_suite_app.adjust_velocities),
        ("Transpose Notes", midi_suite_app.transpose_notes),
        ("Randomize Velocities", midi_suite_app.randomize_velocities),
        ("Quantize Notes", midi_suite_app.quantize_notes),
        ("Humanize Timing", midi_suite_app.humanize_timing),
        ("Scale Velocities", midi_suite_app.scale_velocities),
        ("Normalize Velocities", midi_suite_app.normalize_velocities),
        ("Invert Pitch", midi_suite_app.invert_pitch),
        ("Make Legato", midi_suite_app.make_legato)
    ]

    # Create context wheels
    state_suite_wheel = ContextWheel(state_suite_actions)
    send_manager_wheel = ContextWheel(send_manager_actions)
    midi_suite_wheel = ContextWheel(midi_suite_actions)

    # Set up the global hotkeys using loaded keybinds
    keyboard.add_hotkey(keybinds['state_suite'], lambda: state_suite_wheel.show_signal.emit())
    keyboard.add_hotkey(keybinds['send_manager'], lambda: send_manager_wheel.show_signal.emit())
    keyboard.add_hotkey(keybinds['midi_suite'], lambda: midi_suite_wheel.show_signal.emit())

    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 