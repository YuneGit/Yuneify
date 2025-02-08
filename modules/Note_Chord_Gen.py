# Note_Chord_Gen.py

import random
from Note import create_midi_notes  # Centralizing here

DURATIONS = {
    "whole": 4,
    "half": 2,
    "quarter": 1,
    "eighth": 0.5,
    "sixteenth": 0.25,
    "thirty_second": 0.125
}

CHORD_TYPES = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "diminished": [0, 3, 6],
    "augmented": [0, 4, 8],
}

NOTE_OFFSETS = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

COMMON_PROGRESSIONS = {
    "I-V-I-IV": [("C4", "major"), ("G4", "major"), ("C4", "major"), ("F4", "major")],
    "ii-V-I-vi": [("D4", "minor"), ("G4", "major"), ("C4", "major"), ("A4", "minor")],
    "I-IV-V": [("C4", "major"), ("F4", "major"), ("G4", "major")],
    "ii-V-I": [("D4", "minor"), ("G4", "major"), ("C4", "major")],
    "I-vi-IV-V": [("C4", "major"), ("A4", "minor"), ("F4", "major"), ("G4", "major")]
}

def spn_to_midi(spn: str) -> int:
    note = spn[:-1] if spn[1] in "0123456789" else spn[:2]
    octave = int(spn[-1])
    return 12 * (octave + 1) + NOTE_OFFSETS[note]

def midi_to_spn(midi_number: int) -> str:
    octave = (midi_number // 12) - 1
    note_number = midi_number % 12
    for note, offset in NOTE_OFFSETS.items():
        if offset == note_number:
            return f"{note}{octave}"
    return ""

def generate_chord(root_spn: str, chord_type: str) -> list:
    root_midi = spn_to_midi(root_spn)
    intervals = CHORD_TYPES[chord_type]
    chord_midi = [root_midi + interval for interval in intervals]
    return [midi_to_spn(note) for note in chord_midi]

def ensure_four_chords(chord_prog: list) -> list:
    while len(chord_prog) < 4:
        chord_prog.append(chord_prog[-1])
    return chord_prog

def get_random_progression(prog_choice: list) -> list:
    return ensure_four_chords(prog_choice)

def create_pattern(pattern_type: str) -> list:
    progression_a = get_random_progression(random.choice(list(COMMON_PROGRESSIONS.values())))
    progression_b = get_random_progression(random.choice(list(COMMON_PROGRESSIONS.values())))

    full_pattern = []
    for section in pattern_type:
        if section == 'A':
            full_pattern.append(progression_a)
        elif section == 'B':
            full_pattern.append(progression_b)
    return full_pattern

def generate_chords_for_pattern(pattern: list) -> list:
    note_params = []
    measure = 1
    for section in pattern:
        for _ in range(4):  # 16 measures per section
            for chord_info in section:
                root, chord_type = chord_info
                chord_notes = generate_chord(root, chord_type)
                for note in chord_notes:
                    note_params.append((note, 100, measure, 0, DURATIONS["whole"]))
                measure += 1
    return note_params

def generate_music(pattern_type: str) -> list:
    pattern = create_pattern(pattern_type)
    note_params = generate_chords_for_pattern(pattern)
    return note_params

# Moved from Note.py to centralize
def export_midi(note_params):
    take = create_midi_notes(note_params)  # Now the 'take' is captured here
