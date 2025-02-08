import reapy  # A Python library for interacting with REAPER DAW using ReaScript
import keyboard  # A library for detecting keyboard input in Python
from pynput import mouse  # Library for detecting mouse events
import time  # Used for creating a small delay in the code loop
from PySide6.QtCore import QTimer

class FloatingFXController:
    def __init__(self):
        """Initialize the controller with placeholders for tracking keys, mouse events, and the last selected track."""
        self.last_selected_track = None
        self.mouse_pressed = False  # State variable for mouse press

        # Start a listener for mouse events
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_alt_and_mouse)
        self.timer.start(100)  # Check every 100 milliseconds

    def on_mouse_click(self, x, y, button, pressed):
        """
        Callback function for mouse events.
        Updates the state variable `mouse_pressed` when the mouse is clicked or released.
        """
        self.mouse_pressed = pressed

    def check_alt_and_mouse(self):
        """
        Continuously monitor if the 'Alt' key and a mouse press occur simultaneously.
        When both are detected, it shows the floating FX window for the selected track in REAPER.
        """
        selected_tracks = reapy.Project().selected_tracks

        if keyboard.is_pressed('alt') and self.mouse_pressed:
            if selected_tracks:
                selected_track = selected_tracks[0]

                if selected_track != self.last_selected_track:
                    self.last_selected_track = selected_track
                    reapy.perform_action(40536)
                    reapy.perform_action(reapy.get_command_id("_S&M_WNTSHW3"))

        if not keyboard.is_pressed('alt') or not self.mouse_pressed:
            self.last_selected_track = None

# Run the script only if this file is executed directly
if __name__ == "__main__":
    # Create an instance of the FloatingFXController class
    fx_controller = FloatingFXController()
    # Start monitoring for 'Alt' key and mouse presses to show floating FX
    fx_controller.check_alt_and_mouse()
