import sys
import math
import keyboard
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject, QEvent, QThread
from PyQt5.QtGui import QPainter, QColor, QPen, QCursor
from modules.State_Suite import TrackControlApp
from modules.MIDI_Suite import MidiSuite
from modules.Send_Manager import TrackRouter
import json
from modules.PRINT import create_print_tracks
from modules.Height_Lock import TrackHeightLock
from modules.Auto_VST_Window import FloatingFXController

class MouseFilter(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.window.hide()
        return super().eventFilter(obj, event)

class ContextWheel(QMainWindow):
    show_signal = pyqtSignal()

    def __init__(self, actions, show_navigation=False, navigate_next=None, navigate_prev=None):
        super().__init__()
        self.setup_window()
        self.show_signal.connect(self.show_at_cursor)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        self.create_buttons(actions)
        self.add_hide_button()

        if show_navigation:
            self.add_navigation_buttons(navigate_next, navigate_prev)

        self.mouse_filter = MouseFilter(self)
        self.height_lock_enabled = False
        self.auto_vst_window_enabled = False
        self.height_lock_instance = None
        self.auto_vst_window_instance = None

    def setup_window(self):
        self.setWindowTitle("Context Wheel")
        self.setGeometry(100, 100, 400, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def show_at_cursor(self):
        cursor_pos = QCursor.pos()
        self.move(cursor_pos.x() - self.width() // 2, cursor_pos.y() - self.height() // 2)
        self.setWindowOpacity(0.0)
        self.show()
        self.fade_in()

    def fade_in(self):
        for i in range(10):
            self.setWindowOpacity(i / 10)
            QApplication.processEvents()
            QThread.msleep(30)

    def create_buttons(self, actions):
        radius = 130
        angle_step = 2 * math.pi / len(actions)
        center_x, center_y = self.width() // 2, self.height() // 2

        for i, (label, callback) in enumerate(actions):
            angle = angle_step * i
            position = QPoint(
                int(center_x + radius * math.cos(angle)),
                int(center_y + radius * math.sin(angle))
            )
            self.add_button(label, callback, position)

    def add_button(self, label, callback, position):
        button = QPushButton(label, self)
        button.setStyleSheet(self.button_style())
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.adjustSize()
        button.move(position.x() - button.size().width() // 2, position.y() - button.size().height() // 2)
        button.clicked.connect(lambda checked, cb=callback: self.button_action(cb))

    def button_style(self):
        return """
            QPushButton {
                background-color: #2A2A2A;
                color: #E0E0E0;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
            QPushButton:pressed {
                background-color: #1A1A1A;
            }
        """

    def button_action(self, callback):
        try:
            print(f"Button pressed, executing callback: {callback.__name__}")
            callback()
        except Exception as e:
            print(f"Error executing callback: {e}")
        self.hide()

    def add_hide_button(self):
        hide_button = QPushButton("X", self)
        hide_button.setStyleSheet(self.hide_button_style())
        hide_button.setFixedSize(30, 30)
        hide_button.move(self.width() // 2 - 15, self.height() // 2 - 15)
        hide_button.clicked.connect(self.hide)

    def hide_button_style(self):
        return """
            QPushButton {
                background-color: #2A2A2A;
                color: #E0E0E0;
                padding: 5px;
                font-size: 12px;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
            QPushButton:pressed {
                background-color: #1A1A1A;
            }
        """

    def add_navigation_buttons(self, navigate_next, navigate_prev):
        self.create_navigation_button(">", navigate_next, self.width() // 2 + 25)
        self.create_navigation_button("<", navigate_prev, self.width() // 2 - 55)

    def create_navigation_button(self, label, callback, x_position):
        button = QPushButton(label, self)
        button.setStyleSheet(self.hide_button_style())
        button.setFixedSize(30, 30)
        button.move(x_position, self.height() // 2 - 15)
        button.clicked.connect(callback)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(255, 255, 255, 50), 2)
        painter.setPen(pen)
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = min(self.width(), self.height()) // 3
        painter.drawEllipse(center, radius, radius)

    def toggle_height_lock(self):
        if self.height_lock_enabled:
            self.height_lock_instance = None
            print("Height Lock disabled")
        else:
            self.height_lock_instance = TrackHeightLock()
            print("Height Lock enabled")
        self.height_lock_enabled = not self.height_lock_enabled

    def toggle_auto_vst_window(self):
        if self.auto_vst_window_enabled:
            self.auto_vst_window_instance = None
            print("Auto VST Window disabled")
        else:
            self.auto_vst_window_instance = FloatingFXController()
            print("Auto VST Window enabled")
        self.auto_vst_window_enabled = not self.auto_vst_window_enabled

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
        ("Remove Send", track_router.remove_send),
        ("Toggle Height Lock", lambda: send_manager_wheel.toggle_height_lock()),
        ("Toggle Auto VST Window", lambda: send_manager_wheel.toggle_auto_vst_window()),
        ("Print Tracks", create_print_tracks)
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