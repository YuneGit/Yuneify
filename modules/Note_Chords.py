from Note import create_midi_notes
import random

# Duration mappings (in beats)
DURATIONS = {
    "whole": 4,
    "half": 2,
    "quarter": 1,
    "eighth": 0.5,
    "sixteenth": 0.25,
    "thirty_second": 0.125
}

# Define chord types and their note structures (in intervals from root)
CHORDS = {
    "major": [0, 4, 7],  # Root, Major Third, Perfect Fifth
    "minor": [0, 3, 7],  # Root, Minor Third, Perfect Fifth
    "diminished": [0, 3, 6],  # Root, Minor Third, Diminished Fifth
    "augmented": [0, 4, 8],  # Root, Major Third, Augmented Fifth
}

# Helper dictionary for note-to-MIDI conversion
NOTE_OFFSETS = {
    'C': 0,
    'C#': 1,
    'Db': 1,
    'D': 2,
    'D#': 3,
    'Eb': 3,
    'E': 4,
    'F': 5,
    'F#': 6,
    'Gb': 6,
    'G': 7,
    'G#': 8,
    'Ab': 8,
    'A': 9,
    'A#': 10,
    'Bb': 10,
    'B': 11
}

def spn_to_midi(spn):
    """
    Convert Scientific Pitch Notation (e.g., "C4", "F#3") to a MIDI note number.
    """
    if len(spn) == 2:
        note = spn[0]
        octave = int(spn[1])
    elif len(spn) == 3:
        if spn[1] in ['#', 'b']:
            note = spn[:2]
            octave = int(spn[2])
        else:
            note = spn[0]
            octave = int(spn[1:])
    elif len(spn) == 4:
        note = spn[:2]
        octave = int(spn[2:])
    else:
        raise ValueError("Invalid SPN format: " + spn)
    
    # MIDI note number formula (C4 is 60)
    midi_number = 12 * (octave + 1) + NOTE_OFFSETS[note]
    return midi_number

def midi_to_spn(midi_number):
    """
    Convert a MIDI note number to Scientific Pitch Notation.
    """
    octave = (midi_number // 12) - 1
    note_number = midi_number % 12
    # Prefer a note name with sharp notation when possible
    for note, offset in NOTE_OFFSETS.items():
        if offset == note_number and ("#" in note or len(note) == 1):
            return f"{note}{octave}"
    # Fallback: return the first match
    for note, offset in NOTE_OFFSETS.items():
        if offset == note_number:
            return f"{note}{octave}"
    return None

def generate_chord(root, chord_type):
    """
    Generate a chord based on the root note and the chord type.
    Returns:
        chord_notes (list): List of MIDI notes that make up the chord.
    """
    # Get the intervals for the selected chord type
    intervals = CHORDS[chord_type]
    
    # Convert root note to MIDI number
    root_midi = spn_to_midi(root)
    
    # Calculate the MIDI notes for the chord
    chord_notes = [root_midi + interval for interval in intervals]
    
    # Convert MIDI numbers back to SPN
    chord_spn = [midi_to_spn(note) for note in chord_notes]
    
    return chord_spn

def generate_chord_inversion(chord_notes):
    """
    Generate an inversion of the chord (root, first, or second inversion).
    Returns:
        inversion_chord (list): List of MIDI notes representing the chord inversion.
    """
    inversion_type = random.choice([0, 1, 2])  # Root, first, or second inversion
    if inversion_type == 0:
        return chord_notes  # Root position
    elif inversion_type == 1:
        # First inversion: move the root note to the top
        return chord_notes[1:] + [chord_notes[0]]
    else:
        # Second inversion: move the root and third notes to the top
        return chord_notes[2:] + chord_notes[:2]

def generate_chords_for_exercise(num_measures=25):
    """
    Generate 25 measures of random chords with inversions.
    Returns:
        all_note_params (list): A list of note parameters to pass to create_midi_notes().
    """
    all_note_params = []
    
    root_notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4"]  # Choose from these roots
    
    for measure in range(1, num_measures + 1):
        # Randomly pick a root note and a chord type for each measure
        root = random.choice(root_notes)
        chord_type = random.choice(list(CHORDS.keys()))
        
        # Generate the chord and its inversion
        chord_notes = generate_chord(root, chord_type)
        inversion_chord = generate_chord_inversion(chord_notes)
        
        # Add all chord notes to the note parameters for this measure (play all notes at once)
        for i, note in enumerate(inversion_chord):
            all_note_params.append((note, 100, measure, 0, DURATIONS["quarter"]))  # All notes at the same beat (0)
    
    return all_note_params

def main():
    print("Generating an ear training exercise with 25 random chords...")
    
    # Generate 25 measures of random chords
    note_params = generate_chords_for_exercise(num_measures=25)
    
    # Create the MIDI notes (play them all at once in each measure)
    create_midi_notes(note_params)
    
    print("25 measures of chords generated and played successfully!")

if __name__ == "__main__":
    main()
