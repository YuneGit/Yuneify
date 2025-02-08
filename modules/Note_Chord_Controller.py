from Note_Melody_Gen import generate_song_with_melody
from Note_Chord_Gen import export_midi

def create_song(pattern_type: str = 'ABAB'):

    note_params = generate_song_with_melody(pattern_type)
    export_midi(note_params)

if __name__ == "__main__":
    create_song(pattern_type="ABAB")
