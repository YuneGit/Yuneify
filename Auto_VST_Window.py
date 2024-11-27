import reapy  # A Python library for interacting with REAPER DAW using ReaScript
import keyboard  # A library for detecting keyboard input in Python
from pynput import mouse  # Library for detecting mouse events
import time  # Used for creating a small delay in the code loop

class FloatingFXController:
    def __init__(self):
        """Initialize the controller with placeholders for tracking keys, mouse events, and the last selected track."""
        self.last_selected_track = None
        self.mouse_pressed = False  # State variable for mouse press

        # Start a listener for mouse events
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

    def on_mouse_click(self, x, y, button, pressed):
        """
        Callback function for mouse events.
        Updates the state variable `mouse_pressed` when the mouse is clicked or released.
        """
        self.mouse_pressed = pressed

    def show_floating_fx_on_alt_and_mouse(self):
        """
        Continuously monitor if the 'Alt' key and a mouse press occur simultaneously.
        When both are detected, it shows the floating FX window for the selected track in REAPER.
        """
        while True:  # Create an infinite loop to continuously check for key presses and mouse clicks
            # Get the currently selected tracks in the REAPER project
            selected_tracks = reapy.Project().selected_tracks

            # Check if the 'Alt' key is pressed and a mouse button is also pressed
            if keyboard.is_pressed('alt') and self.mouse_pressed:
                # If there are selected tracks in REAPER
                if selected_tracks:
                    selected_track = selected_tracks[0]  # Use the first selected track

                    # If the selected track has changed since the last check
                    if selected_track != self.last_selected_track:
                        self.last_selected_track = selected_track  # Update the last selected track
                        
                        # Perform a ReaScript action to ensure FX are online
                        # Action ID 40536 corresponds to "Set FX online" in REAPER
                        reapy.perform_action(40536)
                        
                        # Show the floating FX window using the custom action by SWS/S&M extension
                        # The action "_S&M_WNTSHW3" must be set up in REAPER (custom command)
                        reapy.perform_action(reapy.get_command_id("_S&M_WNTSHW3"))

            # Reset the last selected track when 'Alt' is released or mouse is not pressed
            if not keyboard.is_pressed('alt') or not self.mouse_pressed:
                self.last_selected_track = None

            # Pause briefly to reduce CPU usage
            time.sleep(0.1)

# Run the script only if this file is executed directly
if __name__ == "__main__":
    # Create an instance of the FloatingFXController class
    fx_controller = FloatingFXController()
    # Start monitoring for 'Alt' key and mouse presses to show floating FX
    fx_controller.show_floating_fx_on_alt_and_mouse()
