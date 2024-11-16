import reapy  # A Python library to interact with REAPER, a popular DAW (Digital Audio Workstation)
import time  # Standard Python library for managing time intervals
from reapy import reascript_api as RPR  # Import REAPER's API functions for low-level MIDI operations

class MidiVelocityAdjuster:
    """Class to adjust MIDI note velocities in a REAPER project.
    
    This class contains methods to automate the adjustment of MIDI note velocities 
    in all selected MIDI items in a REAPER project, especially for notes with low velocities.
    """

    def __init__(self):
        """Initialize the MidiVelocityAdjuster with the current project."""
        # Create a reference to the current REAPER project
        self.project = reapy.Project()

    def select_all_midi_items(self):
        """Select all MIDI items in the project using REAPER's API."""
        # Execute a REAPER command to select all MIDI items
        RPR.Main_OnCommand(RPR.NamedCommandLookup("_BR_SEL_ALL_ITEMS_MIDI"), 0)
        print("Selected all MIDI items.")

    def adjust_midi_velocities(self):
        """Adjust velocities of MIDI notes that are below a certain threshold."""
        # Get a list of all selected items in the project
        selected_items = self.project.selected_items

        # Loop through each selected item and process it
        for item in selected_items:
            self._process_item(item)

    def _process_item(self, item):
        """Process each MIDI item to adjust note velocities.
        
        Args:
            item: A MIDI item in the REAPER project.
        """
        # Iterate over each take in the item and adjust velocities if the take is a MIDI take
        for take in item.takes:
            if take.is_midi:
                self._adjust_take_velocities(take)

    def _adjust_take_velocities(self, take):
        """Adjust the velocities of all MIDI notes in the take.
        
        Args:
            take: A MIDI take containing the MIDI notes to adjust.
        """
        # Retrieve all MIDI notes from the take
        notes = take.notes

        # Iterate over each note and adjust its velocity
        for note in notes:
            self._adjust_note_velocity(note, take)

        # Sort MIDI events after updating to keep them in the correct order
        RPR.MIDI_Sort(take.id)
        print(f"Sorted MIDI events for take ID: {take.id}.")

    def _adjust_note_velocity(self, note, take):
        """Adjust the velocity of a single MIDI note if it is below the threshold.
        
        Args:
            note: A single MIDI note object.
            take: The MIDI take to which the note belongs.
        """
        note_index = note.index  # The index of the note in the take
        velocity = note.velocity  # Current velocity of the note
        pitch = note.pitch  # Pitch of the note
        start = note.start  # Start time of the note in seconds

        print(f"Note (Pitch: {pitch}) has velocity: {velocity}, original start time: {start:.2f}")

        # Check if the velocity is below the threshold (10 in this case)
        if velocity < 10:
            new_velocity = min(velocity + 10, 127)  # Increase velocity but cap at 127 (max MIDI velocity)
            print(f"Adjusting note (Pitch: {pitch}) velocity from {velocity} to {new_velocity}.")

            # Retrieve existing note properties from the REAPER API
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, note_index, 0, 0, 0, 0, 0, 0, 0
            )

            # Extract the relevant note properties from the returned values
            muted, start, end, channel, original_pitch, _ = other_values[-6:]

            # Update the note velocity using REAPER's API
            RPR.MIDI_SetNote(
                take.id,
                note_index,
                note.selected,
                muted,
                start,
                end,
                channel,
                pitch,
                new_velocity,
                False  # noSort=False because we will sort all notes at the end
            )
            print(f"({take.id})Updated note (Pitch: {pitch}) to new velocity: {new_velocity}. Original start time: {start:.2f}")

    def run(self):
        """Execute the MIDI velocity adjustment process."""
        self.select_all_midi_items()  # Select all MIDI items
        self.adjust_midi_velocities()  # Adjust velocities of selected items
        print("Completed MIDI velocity adjustment.")


def wait_for_stop_recording():
    """Poll for the recording state and run MidiVelocityAdjuster when recording stops."""
    project = reapy.Project()  # Reference to the current REAPER project
    was_recording = project.is_recording  # Check if REAPER is currently recording

    # Create an instance of MidiVelocityAdjuster
    midi_adjuster = MidiVelocityAdjuster()

    while True:
        # Check if the recording state has changed
        is_recording = project.is_recording

        # If we were recording and now we're not, run the MIDI velocity adjustment
        if was_recording and not is_recording:
            print("Recording stopped. Running MIDI velocity adjustment...")
            midi_adjuster.run()
        
        # Update the recording state
        was_recording = is_recording
        
        # Sleep for 0.5 seconds before checking the recording state again
        time.sleep(0.5)


if __name__ == "__main__":
    # Entry point of the script: wait for recording to stop and adjust velocities
    wait_for_stop_recording()
