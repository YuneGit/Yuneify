import reapy
import time

class TrackHeightLock:
    def __init__(self):
        self.last_track_count = 0  # Initialize last_track_count
        self.check_for_track_changes()

    def lock_track_heights(self):
        """Lock the height of all tracks in the project."""
        reapy.core.reaper.reaper.perform_action(42336)  # Lock track heights using action ID 42336

    def check_for_track_changes(self):
        """Continuously check for changes in the track count."""
        while True:
            project = reapy.Project()
            current_track_count = project.n_tracks

            if current_track_count != self.last_track_count:
                self.lock_track_heights()
                self.last_track_count = current_track_count

            time.sleep(0.2)  # Sleep for 200 milliseconds

if __name__ == "__main__":
    track_locker = TrackHeightLock()
