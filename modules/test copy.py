import reapy

# Create a new project
project = reapy.Project()

# Create a new track in the project
track = project.add_track()

# Create a new MIDI take on the track
take = track.add_midi_item(start=0, end=1)

note = take.add_note(start=0, end=1, pitch=60)
