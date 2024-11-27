import reapy
import time

class TrackHeightLock:
    def __init__(self):
        # Initial state, we don't need to track the last track count
        pass

    def lock_track_heights(self):
        """Lock the height of all tracks in the project."""
        reapy.core.reaper.reaper.perform_action(42336)  # Lock track heights using action ID 42336

    def check_for_track_changes(self):
        """Continuously check for changes in the track count at a 0.2 second interval."""
        project = reapy.Project()

        last_track_count = project.n_tracks  # Get the initial track count

        while True:
            time.sleep(0.2)  # Check for changes every 0.2 seconds
            current_track_count = project.n_tracks  # Get the current track count

            # If the track count has changed, lock the track heights and update the count
            if current_track_count != last_track_count:
                self.lock_track_heights()
                last_track_count = current_track_count  # Update the track count to the new value

if __name__ == "__main__":
    track_locker = TrackHeightLock()
    track_locker.check_for_track_changes()
