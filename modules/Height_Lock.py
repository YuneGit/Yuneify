import reapy
class TrackHeightLock:
    def __init__(self):
        self.last_track_count = 0  # Initialize last_track_count
        if reapy.is_inside_reaper():
            self.check_for_track_changes()  # Start the non-blocking loop
    def lock_track_heights(self):
        """Lock the height of all tracks in the project."""
        reapy.core.reaper.reaper.perform_action(42336)  # Lock track heights using action ID 42336
    def check_for_track_changes(self):
        """Check for changes in the track count."""
        project = reapy.Project()
        current_track_count = project.n_tracks
        if current_track_count != self.last_track_count:
            self.lock_track_heights()
            self.last_track_count = current_track_count
        # Schedule the next call to this function
        if reapy.is_inside_reaper():
            reapy.defer(self.check_for_track_changes)
if __name__ == "__main__":
    track_locker = TrackHeightLock()