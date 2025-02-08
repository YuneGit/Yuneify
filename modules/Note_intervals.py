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

# Define interval names and their semitone distances
INTERVALS = {
    "minor second": 1,
    "major second": 2,
    "minor third": 3,
    "major third": 4,
    "perfect fourth": 5,
    "tritone": 6,
    "perfect fifth": 7,
    "minor sixth": 8,
    "major sixth": 9,
    "minor seventh": 10,
    "major seventh": 11,
    "octave": 12,
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

def generate_random_interval_within_range():
    """
    Generate a random interval and ensure the notes are within a 3-octave range.
    Returns:
        root (str): The root note in SPN.
        second_note (str): The second note after applying the random interval.
    """
    # Define the note range: C3 to B5 (3 octaves)
    note_range = ["C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
                  "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
                  "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5"]
    
    # Randomly pick a root note from the range
    root = random.choice(note_range)
    root_midi = spn_to_midi(root)
    
    # Randomly pick an interval (from the predefined INTERVALS dictionary)
    interval_name, semitones = random.choice(list(INTERVALS.items()))
    
    # Calculate the second note's MIDI number
    second_midi = root_midi + semitones
    
    # Ensure the second note is within the 3-octave range
    while second_midi < spn_to_midi("C3") or second_midi > spn_to_midi("B5"):
        # If the note is out of range, pick a new interval
        interval_name, semitones = random.choice(list(INTERVALS.items()))
        second_midi = root_midi + semitones
    
    # Convert the second note back to SPN
    second_note = midi_to_spn(second_midi)
    
    return root, second_note

def generate_batch_of_intervals(batch_size=25):
    """
    Generate a batch of intervals (25 intervals by default).
    Returns:
        all_note_params (list): A list of all note parameters to pass to create_midi_notes().
    """
    all_note_params = []
    
    for measure in range(1, batch_size + 1):  # 25 measures
        root, second_note = generate_random_interval_within_range()
        
        # Create note parameters for the current measure
        all_note_params.append((root, 100, measure, 0, DURATIONS["quarter"]))  # First note of the measure
        all_note_params.append((second_note, 100, measure, 1, DURATIONS["quarter"]))  # Second note of the measure
    
    return all_note_params

def main():
    print("Generating a batch of 25 random intervals across 25 measures...")
    
    # Generate the batch of 25 notes (25 measures, each with two notes)
    note_params = generate_batch_of_intervals(batch_size=25)
    
    print("Playing the batch of intervals...")
    create_midi_notes(note_params)  # Create the MIDI notes from the batch
    
    print("Batch of intervals generated and played successfully!")
    input("Press Enter to exit.")

if __name__ == "__main__":
    main()
