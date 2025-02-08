# Note_Melody_Gen.py

import random
from Note_Chord_Gen import generate_music, spn_to_midi, midi_to_spn, DURATIONS

def generate_phrase(chord_measures, measure_start):
    phrase_params = []
    for measure_offset in range(2):  # Each phrase = 2 measures
        measure = measure_start + measure_offset
        chords_in_measure = chord_measures[measure - 1]

        chord_notes = [note for note, _, m, _, _ in chords_in_measure if m == measure]
        if not chord_notes:
            continue  # Skip empty measures

        chord_midi_notes = [spn_to_midi(note) for note in chord_notes]
        melody_notes = [midi_to_spn(note + 12) for note in chord_midi_notes]  # Octave above

        # Keep track of notes placed in this measure
        measure_beats = {i: None for i in range(4)}  # 4 beats in a measure

        beat = 0
        while beat < 4:
            duration = random.choice([DURATIONS["quarter"], DURATIONS["eighth"]])
            if beat + duration > 4:
                duration = DURATIONS["quarter"]

            # Ensure no overlap by placing the melody note only if the beat is available
            if measure_beats[int(beat)] is None:  # Check the current beat
                melody_note = random.choice(melody_notes) if melody_notes else "C5"
                phrase_params.append((melody_note, 100, measure, int(beat), duration))
                measure_beats[int(beat)] = melody_note  # Mark this beat as occupied

            beat += duration

    return phrase_params

def vary_phrase(phrase_params):
    # Slight variations: change one random note or adjust duration
    if not phrase_params:
        return phrase_params

    varied_phrase = phrase_params.copy()
    index_to_change = random.randint(0, len(varied_phrase) - 1)

    note, velocity, measure, beat, duration = varied_phrase[index_to_change]
    varied_note = note  # Default

    # Random variation: change pitch slightly or duration
    if random.choice([True, False]):
        midi_note = spn_to_midi(note)
        varied_note = midi_to_spn(midi_note + random.choice([-1, 1]))  # Step up or down
    else:
        duration = random.choice([DURATIONS["quarter"], DURATIONS["eighth"]])

    varied_phrase[index_to_change] = (varied_note, velocity, measure, beat, duration)
    return varied_phrase

def generate_melody(chord_progression):
    melody_params = []
    total_measures = len(chord_progression)
    current_measure = 1

    while current_measure <= total_measures:
        # Generate 4 phrases (each 2 measures long) = 8 measures
        phrases = [generate_phrase(chord_progression, current_measure + i * 2) for i in range(4)]

        # Ensure no overlapping notes in the melody
        all_phrase_notes = {}
        for phrase in phrases:
            for melody_note, velocity, measure, beat, duration in phrase:
                if (measure, beat) not in all_phrase_notes:
                    all_phrase_notes[(measure, beat)] = melody_note

        # First iteration: Original melody
        original_notes = [(melody_note, 100, measure, beat, DURATIONS["quarter"]) for (measure, beat), melody_note in all_phrase_notes.items()]
        melody_params.extend(original_notes)

        # Second iteration: Slight variation of the same phrases
        varied_all_notes = vary_phrase(original_notes)  # Now, this should be the original notes replaced by the varied ones
        melody_params.extend(varied_all_notes)

        current_measure += 8  # Move to the next section

    return melody_params

def generate_song_with_melody(pattern_type='ABAB'):
    print("Generating Melody")
    
    chord_params = generate_music(pattern_type)
    measures = max(chord[2] for chord in chord_params)

    grouped_chords = [
        [chord for chord in chord_params if chord[2] == measure]
        for measure in range(1, measures + 1)
    ]

    melody_params = generate_melody(grouped_chords)

    # Now create the MIDI take for both chord and melody parameters
    all_params = chord_params + melody_params

    return all_params
