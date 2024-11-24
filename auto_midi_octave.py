import reapy
import time


class MidiPitchTransposer:
    def __init__(self):
        self.project = reapy.Project()

    def run(self):
        item = self.project.get_selected_item(0)
        if not item:
            print("No selected item.")
            return

        take = item.active_take
        if not take:
            print("No active take.")
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Found {len(notes)} notes.")
        note_infos = [note.infos for note in notes]

        self.duplicate_notes_an_octave_above(take, note_infos)

    def duplicate_notes_an_octave_above(self, take, note_infos):
        """Duplicates notes an octave above."""
        for note_info in note_infos:
            # Convert start and end time to PPQ using the take's time_to_ppq method
            start_ppq = take.time_to_ppq(note_info["start"])
            end_ppq = take.time_to_ppq(note_info["end"])
            print(end_ppq)
            # Duplicate each note and raise its pitch by 12 semitones (1 octave)
            new_note_info = note_info.copy()
            new_note_info["pitch"] += 12  # Increase pitch by an octave

            take.add_note(
                start=start_ppq,
                end=end_ppq,
                pitch=new_note_info["pitch"],
                velocity=new_note_info["velocity"],
                channel=new_note_info["channel"],
                selected=new_note_info["selected"],
                muted=new_note_info["muted"],
                unit="ppq",  # We're now working in PPQ
                sort=True
            )


def wait_for_stop_recording():
    project = reapy.Project()
    was_recording = project.is_recording
    midi_transposer = MidiPitchTransposer()

    while True:
        is_recording = project.is_recording
        if was_recording and not is_recording:
            print("Recording stopped.")
            midi_transposer.run()
        was_recording = is_recording
        time.sleep(0.5)


if __name__ == "__main__":
    wait_for_stop_recording()
