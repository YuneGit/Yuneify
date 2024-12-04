import reapy

def create_print_tracks():
    project = reapy.Project()
    original_tracks = project.tracks

    for track in original_tracks:
        # Create a new track named "PRINT+track_name"
        print_track_name = f"PRINT+{track.name}"
        print_track = project.add_track(name=print_track_name)

        # Create a send from the original track to the new "PRINT" track
        track.add_send(print_track)

        # Debugging: Print the creation of the print track and send
        print(f"Created print track: {print_track_name}")
        print(f"Created send: {track.name} → {print_track_name}")

if __name__ == "__main__":
    create_print_tracks()
