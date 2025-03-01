import sys
import math
import keyboard
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSizePolicy
from PySide6.QtCore import Qt, QPoint, Signal, QObject, QEvent, QThread, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QCursor
from modules.State_Suite import TrackControlApp
from modules.MIDI_Suite import MidiSuite
from Fast_MIDI_Suite import FastMidiSuite
from modules.Send_Manager import TrackRouter
import json
from modules.PRINT import create_print_tracks
from modules.Height_Lock import TrackHeightLock
from modules.Auto_VST_Window import FloatingFXController
from modules.utils import setup_logger
from modules.Insert_Kontakt_Track import create_vst_preset_manager
from modules.Marker_Manager import MarkerAdjustWindow

class MouseFilter(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.window.hide()
        return super().eventFilter(obj, event)

class SubButton(QPushButton):
    def __init__(self, label, callback, parent=None):
        super().__init__(label, parent)
        self.callback = callback
        self.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #E0E0E0;
                padding: 5px;
                font-size: 12px;
                border: 1px solid #444444;
                border-radius: 3px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        self.clicked.connect(self.execute)
        self.hide()

    def execute(self):
        self.callback()
        self.parent().hide()

class ContextWheel(QMainWindow):
    show_signal = Signal()
    current_instance = None  # Class variable to track the active instance

    def __init__(self, actions, show_navigation=False, navigate_next=None, navigate_prev=None):
        super().__init__()
        # Close any existing instance before creating new one
        if ContextWheel.current_instance:
            ContextWheel.current_instance.hide()
        self.logger = setup_logger('ContextWheel', 'context_wheel')
        self.logger.info("ContextWheel initialized with actions: %s", actions)
        
        # Initialize MIDI Suite reference
        self.midi_suite = None
        self.sub_buttons = {}
        
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
        
        # Store main button reference
        self.sub_buttons[button] = []
        
        # Add hover events
        button.enterEvent = lambda event: self.show_sub_buttons(button)
        button.leaveEvent = lambda event: self.hide_sub_buttons(button)
        
        # If callback is a list, it contains sub-actions
        if isinstance(callback, list):
            for sub_label, sub_cb in callback:
                sub_button = SubButton(sub_label, sub_cb, button)
                self.sub_buttons[button].append(sub_button)
            button.clicked.connect(lambda: None)  # Disable direct click
        else:
            button.clicked.connect(lambda checked, cb=callback: self.button_action(cb))

    def show_sub_buttons(self, main_button):
        if main_button in self.sub_buttons:
            angle = math.atan2(main_button.y() - self.height()//2, 
                             main_button.x() - self.width()//2)
            radius = 60
            
            for i, sub_button in enumerate(self.sub_buttons[main_button]):
                offset = (i - len(self.sub_buttons[main_button])/2) * 0.3
                x = main_button.x() + radius * math.cos(angle + offset)
                y = main_button.y() + radius * math.sin(angle + offset)
                sub_button.move(int(x), int(y))
                sub_button.show()
                sub_button.raise_()

    def hide_sub_buttons(self, main_button):
        if main_button in self.sub_buttons:
            for sub_button in self.sub_buttons[main_button]:
                sub_button.hide()

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
            print(f"Button pressed, executing callback: {callback.__name__ if hasattr(callback, '__name__') else 'anonymous'}")
            self.logger.info("Executing callback")
            self.hide()  # Close context wheel first
            callback()
        except Exception as e:
            print(f"Error executing callback: {e}")
            self.logger.error("Error executing callback: %s", e)

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

    def show_marker_manager(self):
        """Handle marker manager window creation"""
        self.hide()  # Close the context wheel first
        self.marker_window = MarkerAdjustWindow()
        self.marker_window.show()

    def closeEvent(self, event):
        """Clean up window references"""
        app = QApplication.instance()
        if self in app.window_references:
            app.window_references.remove(self)
        if self.midi_suite:
            self.midi_suite.close()
        event.accept()

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
    app = QApplication.instance() or QApplication([])
    app.window_references = []

    keybinds = load_keybinds()

    # Initialize the TrackControlApp, MidiSuite, and TrackRouter to access their methods
    track_control_app = TrackControlApp()
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
        ("Toggle Height Lock", lambda: TrackHeightLock().toggle_lock()),
        ("Toggle Auto VST Window", lambda: FloatingFXController().toggle_windows()),
        ("VST Presets", create_vst_preset_manager),
        ("Print Tracks", create_print_tracks),
        ("Marker Manager", lambda: [app.window_references.append(MarkerAdjustWindow()), app.window_references[-1].show()])
    ]

    # Create MIDI Suite wheel with proper instance handling
    midi_suite_actions = [
        ("Open Fast MIDI Suite", lambda: [app.window_references.append(FastMidiSuite()), app.window_references[-1].show()]),
        ("Adjust Velocities", lambda: FastMidiSuite().adjust_velocity_up()),
        ("Humanize", lambda: FastMidiSuite().humanize_notes()),
        ("Quantize", lambda: FastMidiSuite().quantize_notes()),
        ("Legato", lambda: FastMidiSuite().make_legato()),
        ("CC Adjust", lambda: FastMidiSuite().adjust_cc_right())
    ]
    midi_suite_wheel = ContextWheel(midi_suite_actions)
    app.window_references.append(midi_suite_wheel)

    # Create context wheels
    state_suite_wheel = ContextWheel(state_suite_actions)
    send_manager_wheel = ContextWheel(send_manager_actions)
    
    # Set up the global hotkeys using loaded keybinds
    keyboard.add_hotkey(keybinds['state_suite'], lambda: state_suite_wheel.show_signal.emit())
    keyboard.add_hotkey(keybinds['send_manager'], lambda: send_manager_wheel.show_signal.emit())
    keyboard.add_hotkey(keybinds['midi_suite'], lambda: midi_suite_wheel.show_signal.emit())

    app.exec()
    
if __name__ == "__main__":
    main()
