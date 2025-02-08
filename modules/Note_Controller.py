from Note import create_midi_notes

# Duration mappings (in beats)
DURATIONS = {
    "whole": 4,
    "half": 2,
    "quarter": 1,
    "eighth": 0.5,
    "sixteenth": 0.25,
    "thirty_second": 0.125
}

# Define notes using (pitch, velocity, measure, beat_in_measure, duration)
# Pitches are now in Scientific Pitch Notation (SPN)
note_params = [
    ("C4", 100, 1, 0, DURATIONS["quarter"]),       # C4, Measure 1, Beat 0 (Quarter note)
    ("D4", 100, 1, 1, DURATIONS["eighth"]),        # D4, Measure 1, Beat 1 (Eighth note)
    ("F#4", 100, 1, 1.5, DURATIONS["eighth"]),     # F#4, Measure 1, Beat 1.5 (Eighth note)
    ("A4", 100, 1, 2, DURATIONS["eighth"]),        # A4, Measure 1, Beat 2 (Eighth note)

    ("F4", 100, 2, 2, DURATIONS["half"]),          # F4, Measure 2, Beat 2 (Half note)
    ("A4", 100, 2, 2, DURATIONS["half"]),          # A4, Measure 2, Beat 2 (Half note)
    ("C5", 100, 2, 2, DURATIONS["half"]),          # C5, Measure 2, Beat 2 (Half note)

    ("F#4", 100, 5, 0, DURATIONS["half"]),         # F#4, Measure 5, Beat 0 (Half note)
    ("A4", 100, 5, 0, DURATIONS["half"]),          # A4, Measure 5, Beat 0 (Half note)
    ("C5", 100, 5, 0, DURATIONS["half"]),          # C5, Measure 5, Beat 0 (Half note)
]

# Create the MIDI notes
create_midi_notes(note_params)
