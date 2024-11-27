import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QComboBox
import reapy

class TrackControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track Control")
        self.setGeometry(200, 100, 300, 350)

        # Apply modern dark mode style
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border-radius: 10px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                margin: 5px;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 14px;
                border: 1px solid #5A5A5A;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
            QComboBox {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #5A5A5A;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A2A;
                color: #FFFFFF;
                selection-background-color: #4A4A4A;
            }
        """)

        # Main layout
        layout = QVBoxLayout()

        # Add buttons for track control
        self.mute_button = QPushButton("Mute All Tracks")
        self.unmute_button = QPushButton("Unmute All Tracks")
        self.solo_button = QPushButton("Solo All Tracks")
        self.unsolo_button = QPushButton("Unsolo All Tracks")
        self.solo_group_button = QPushButton("Solo Selected Track Group")
        self.unsolo_group_button = QPushButton("Unsolo Selected Track Group")
        self.mute_group_button = QPushButton("Mute Selected Track Group")
        self.unmute_group_button = QPushButton("Unmute Selected Track Group")

        # Connect buttons to their respective functions
        self.mute_button.clicked.connect(self.mute_all_tracks)
        self.unmute_button.clicked.connect(self.unmute_all_tracks)
        self.solo_button.clicked.connect(self.solo_all_tracks)
        self.unsolo_button.clicked.connect(self.unsolo_all_tracks)
        self.solo_group_button.clicked.connect(self.solo_selected_track_group)
        self.unsolo_group_button.clicked.connect(self.unsolo_selected_track_group)
        self.mute_group_button.clicked.connect(self.mute_selected_track_group)
        self.unmute_group_button.clicked.connect(self.unmute_selected_track_group)

        # Add buttons to layout
        layout.addWidget(QLabel("Control all tracks in REAPER:"))
        layout.addWidget(self.mute_button)
        layout.addWidget(self.unmute_button)
        layout.addWidget(self.solo_button)
        layout.addWidget(self.unsolo_button)
        layout.addWidget(self.solo_group_button)
        layout.addWidget(self.unsolo_group_button)
        layout.addWidget(self.mute_group_button)
        layout.addWidget(self.unmute_group_button)

        # Set the main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def mute_all_tracks(self):
        project = reapy.Project()
        for track in project.tracks:
            track.mute()
            print(track.name)
        print("All tracks muted.")

    def unmute_all_tracks(self):
        project = reapy.Project()
        for track in project.tracks:
            track.unmute()
        print("All tracks unmuted.")

    def solo_all_tracks(self):
        project = reapy.Project()
        for track in project.tracks:
            track.solo()
        print("All tracks soloed.")

    def unsolo_all_tracks(self):
        project = reapy.Project()
        for track in project.tracks:
            track.unsolo()
        print("All tracks unsoloed.")

    def solo_selected_track_group(self):
        project = reapy.Project()
        selected_tracks = [track for track in project.tracks if track.is_selected]

        if not selected_tracks:
            print("No track selected.")
            return

        selected_track = selected_tracks[0]
        parent_track = selected_track.parent_track

        if parent_track is None:
            print("Selected track has no parent.")
            return

        # Solo all tracks with the same parent
        for track in project.tracks:
            if track.parent_track == parent_track:
                track.solo()
                print(f"Soloed track: {track.name}")

        # Mute the parent track
        parent_track.solo()
        print(f"Muted parent track: {parent_track.name}")

    def unsolo_selected_track_group(self):
        project = reapy.Project()
        selected_tracks = [track for track in project.tracks if track.is_selected]

        if not selected_tracks:
            print("No track selected.")
            return

        selected_track = selected_tracks[0]
        parent_track = selected_track.parent_track

        if parent_track is None:
            print("Selected track has no parent.")
            return

        # Unsolo all tracks with the same parent
        for track in project.tracks:
            if track.parent_track == parent_track:
                track.unsolo()
                print(f"Unsoloed track: {track.name}")

        # Unmute the parent track
        parent_track.unsolo()
        print(f"Unmuted parent track: {parent_track.name}")

    def mute_selected_track_group(self):
        project = reapy.Project()
        selected_tracks = [track for track in project.tracks if track.is_selected]

        if not selected_tracks:
            print("No track selected.")
            return

        selected_track = selected_tracks[0]
        parent_track = selected_track.parent_track

        if parent_track is None:
            print("Selected track has no parent.")
            return

        # Mute all tracks with the same parent
        for track in project.tracks:
            if track.parent_track == parent_track:
                track.mute()
                print(f"Muted track: {track.name}")

        # Mute the parent track
        parent_track.mute()
        print(f"Muted parent track: {parent_track.name}")

    def unmute_selected_track_group(self):
        project = reapy.Project()
        selected_tracks = [track for track in project.tracks if track.is_selected]

        if not selected_tracks:
            print("No track selected.")
            return

        selected_track = selected_tracks[0]
        parent_track = selected_track.parent_track

        if parent_track is None:
            print("Selected track has no parent.")
            return

        # Unmute all tracks with the same parent
        for track in project.tracks:
            if track.parent_track == parent_track:
                track.unmute()
                print(f"Unmuted track: {track.name}")

        # Unmute the parent track
        parent_track.unmute()
        print(f"Unmuted parent track: {parent_track.name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrackControlApp()
    window.show()
    sys.exit(app.exec_()) 