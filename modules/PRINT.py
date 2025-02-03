import reapy

def create_print_tracks():
    with reapy.inside_reaper():
        project = reapy.Project()
        original_tracks = project.tracks

        # Check if any track contains items
        has_items = any(track.items for track in original_tracks)

        if not has_items:
            print("No item in tracks present")
            return  # Exit the function early if no items are found

        for track in original_tracks:
            if track.items:  # Only process tracks that have items
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
