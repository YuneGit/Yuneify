import reapy

# Mapping for note names to MIDI offsets
NOTE_OFFSETS = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4, "E#": 5,
    "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11, "B#": 0
}

def spn_to_midi(pitch):
    """
    Converts Scientific Pitch Notation (SPN) to MIDI note number.
    Supports enharmonic equivalents like C#, Db, etc.
    """
    if isinstance(pitch, int):  # Already a MIDI number
        return pitch

    # Extract note and octave from SPN (e.g., "C#4")
    import re
    match = re.match(r"^([A-Ga-g][#b]?)(-?\d+)$", pitch.strip())
    if not match:
        raise ValueError(f"Invalid pitch format: {pitch}")

    note, octave = match.groups()
    note = note.upper()
    octave = int(octave)

    # Calculate MIDI number
    midi_note = (octave + 1) * 12 + NOTE_OFFSETS[note]
    return midi_note

def create_midi_notes(note_params):
    use_selected_track = True
    use_selected_item = True

    project = reapy.Project()
    tempo, beats_per_measure = project.time_signature

    selected_track = project.get_selected_track(0) if use_selected_track else None
    selected_item = project.get_selected_item(0) if use_selected_item else None

    latest_end_time = 0

    if selected_item and selected_item.has_valid_id:
        take = selected_item.takes[0]
        print("Using the selected MIDI item.")
    elif selected_track and selected_track.has_valid_id:
        position = project.cursor_position
        item = selected_track.add_midi_item(start=position, end=position + 1)
        take = item.takes[0]
        print("Created a new MIDI item on the selected track.")
    else:
        track = project.add_track()
        position = project.play_position
        item = track.add_midi_item(start=position, end=position + 1)
        take = item.takes[0]
        print("Created a new track and a new MIDI item.")

    for pitch, velocity, measure, beat_in_measure, duration in note_params:
        # Convert SPN to MIDI
        midi_pitch = spn_to_midi(pitch)

        # Calculate beats
        start_beat = (measure - 1) * beats_per_measure + beat_in_measure
        end_beat = start_beat + duration

        # Add the note
        note = take.add_note(start=start_beat, end=end_beat, pitch=midi_pitch, velocity=velocity, unit="beats")

        # Track the latest end time
        end_time_beats = project.beats_to_time(end_beat)
        latest_end_time = max(latest_end_time, end_time_beats)
        item.length = latest_end_time


    item.length = latest_end_time
    print("Notes successfully added.")

    return take  # Return the 'take' to the calling script

