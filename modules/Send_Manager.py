import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, 
    QLabel, QComboBox, QListWidget, QHBoxLayout, QListWidgetItem
)
from PySide6.QtCore import QTimer, QThread, Signal
import reapy
from modules.styles import apply_dark_theme  # Import the stylesheet function

class TrackProcessingThread(QThread):
    tracks_processed = Signal(list)

    def run(self):
        project = reapy.Project()
        tracks = project.tracks
        # Convert TrackList to a standard Python list
        processed_tracks = self.process_tracks(list(tracks))
        self.tracks_processed.emit(processed_tracks)

    def process_tracks(self, tracks):
        # Implement track processing logic here
        return tracks
class TrackRouter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track Router")
        self.setGeometry(100, 100, 275, 175)
        
        # Set a fixed width for the window
        self.setFixedWidth(275)
        
        # Apply modern dark mode style
        apply_dark_theme(self)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Middle (Controls)
        middle_layout = QVBoxLayout()
        middle_layout.addStretch()
        self.destination_combo = QComboBox()
        middle_layout.addWidget(QLabel("Destination Track:"))
        middle_layout.addWidget(self.destination_combo)
        self.route_button = QPushButton("Create Send")
        self.route_button.clicked.connect(self.create_send)
        middle_layout.addWidget(self.route_button)
        self.remove_button = QPushButton("Remove Send")
        self.remove_button.clicked.connect(self.remove_send)
        middle_layout.addWidget(self.remove_button)
        middle_layout.addStretch()
        
        # Right side (Existing sends)
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Existing Sends:"))
        self.sends_list = QListWidget()
        right_layout.addWidget(self.sends_list)
        
        # Add layouts to main layout
        middle_widget = QWidget()
        middle_widget.setLayout(middle_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        main_layout.addWidget(middle_widget)
        main_layout.addWidget(right_widget)
        
        # Set the main widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initialize track lists
        self.refresh_tracks()

    def refresh_tracks(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            
            # Preserve the current destination track selection
            current_dest_index = self.destination_combo.currentIndex()
            
            # Only update if the number of tracks has changed
            if self.destination_combo.count() != len(project.tracks):
                self.destination_combo.clear()
                for track in project.tracks:
                    self.destination_combo.addItem(track.name)
            
            # Restore the previous destination track selection if possible
            if current_dest_index >= 0 and current_dest_index < self.destination_combo.count():
                self.destination_combo.setCurrentIndex(current_dest_index)
            
            # Update sends list only if necessary
            current_sends = set(self.sends_list.item(i).text() for i in range(self.sends_list.count()))
            new_sends = set()
            sends_by_dest = {}
            for track in project.tracks:
                for send in track.sends:
                    dest_track = send.dest_track
                    if dest_track.name not in sends_by_dest:
                        sends_by_dest[dest_track.name] = []
                    sends_by_dest[dest_track.name].append(track.name)
            
            for dest_name, source_names in sends_by_dest.items():
                new_sends.add(f"→ {dest_name}")
                for source_name in source_names:
                    new_sends.add(f"    {source_name}")
            if current_sends != new_sends:
                self.sends_list.clear()
                for send in new_sends:
                    self.sends_list.addItem(send)

    def create_send(self):
        with reapy.inside_reaper():
            self.refresh_tracks()  # Refresh tracks when the button is pressed
            project = reapy.Project()
            
            # Get all currently selected tracks in Reaper
            selected_tracks = project.selected_tracks
            if len(selected_tracks) < 2:
                print("Select at least two tracks in Reaper: one as source and one as destination")
                return
            
            # Assume the last selected track is the destination
            dest_track = selected_tracks[-1]
            
            for source_track in selected_tracks[:-1]:
                # Debugging: Print source and destination track names
                print(f"Attempting to create send from {source_track.name} to {dest_track.name}")
                
                if source_track == dest_track:
                    continue
                    
                source_track.add_send(dest_track)
                print(f"Created send: {source_track.name} → {dest_track.name}")
            
            self.refresh_tracks()

    def remove_send(self):
        with reapy.inside_reaper():
            self.refresh_tracks()  # Refresh tracks when the button is pressed
            project = reapy.Project()
            selected_sends = self.sends_list.selectedItems()
            
            if not selected_sends:
                print("No sends selected")
                return
            
            for send_item in selected_sends:
                # Parse the send text to get source and destination
                source_name, dest_name = send_item.text().split(" → ")
                
                # Find the corresponding tracks
                source_track = None
                for track in project.tracks:
                    if track.name == source_name:
                        source_track = track
                        break
                
                if source_track:
                    # Remove all sends to the destination track
                    for send in source_track.sends:
                        dest_track = send.dest_track
                        if dest_track.name == dest_name:
                            send.delete()
                            print(f"Removed send: {source_name} → {dest_name}")
            
            # Refresh the display
            self.refresh_tracks()

    def get_tracks(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            return project.tracks

    def create_send_to_track(self, dest_track):
        with reapy.inside_reaper():
            project = reapy.Project()
            selected_tracks = project.selected_tracks

            for source_track in selected_tracks:
                if source_track != dest_track:
                    source_track.add_send(dest_track)
                    print(f"Created send: {source_track.name} → {dest_track.name}")

    def update_ui_with_tracks(self, tracks):
        # Update the UI with processed track data
        ...
    
def main():
    app = QApplication([])
    window = TrackRouter()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()