import reapy
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QLabel, QComboBox
from PyQt5.QtCore import Qt
from styles import apply_dark_theme  # Import the stylesheet function

class TrackControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track Control")
        self.setGeometry(100, 100, 275, 275)  # Fixed window size
        self.setFixedWidth(275)

        # Apply modern dark mode style
        apply_dark_theme(self)

        # Main layout
        layout = QGridLayout()
        layout.setContentsMargins(8, 8, 8, 8)  # Set margins
        layout.setSpacing(5)  # Set spacing between widgets

        # Add label to layout in the top middle
        layout.addWidget(QLabel("Control all tracks in REAPER:"), 0, 0, 1, 2, alignment=Qt.AlignCenter)

        # Add a stretchable space to push the label to the top
        layout.setRowStretch(1, 1)

        # Add buttons for track control
        self.mute_button = QPushButton("Mute All Tracks")
        self.unmute_button = QPushButton("Un-Mute All Tracks")
        self.solo_button = QPushButton("Solo All Tracks")
        self.unsolo_button = QPushButton("Un-Solo All Tracks")
        self.solo_group_button = QPushButton("Solo Group")
        self.unsolo_group_button = QPushButton("Un-Solo Group")
        self.mute_group_button = QPushButton("Mute Group")
        self.unmute_group_button = QPushButton("Un-Mute Group")

        # Set reduced button size to prevent window from resizing
        button_width = 124  # Reduce the width from 130 to 124
        button_height = 30
        for button in [self.mute_button, self.unmute_button, self.solo_button, self.unsolo_button,
                       self.solo_group_button, self.unsolo_group_button, self.mute_group_button, self.unmute_group_button]:
            button.setFixedSize(button_width, button_height)

        # Connect buttons to their respective functions
        self.mute_button.clicked.connect(self.mute_all_tracks)
        self.unmute_button.clicked.connect(self.unmute_all_tracks)
        self.solo_button.clicked.connect(self.solo_all_tracks)
        self.unsolo_button.clicked.connect(self.unsolo_all_tracks)
        self.solo_group_button.clicked.connect(self.solo_selected_track_group)
        self.unsolo_group_button.clicked.connect(self.unsolo_selected_track_group)
        self.mute_group_button.clicked.connect(self.mute_selected_track_group)
        self.unmute_group_button.clicked.connect(self.unmute_selected_track_group)

        # Add buttons to layout in a grid
        layout.addWidget(self.mute_button, 2, 0)
        layout.addWidget(self.unmute_button, 2, 1)
        layout.addWidget(self.solo_button, 3, 0)
        layout.addWidget(self.unsolo_button, 3, 1)
        layout.addWidget(self.solo_group_button, 4, 0)
        layout.addWidget(self.unsolo_group_button, 4, 1)
        layout.addWidget(self.mute_group_button, 5, 0)
        layout.addWidget(self.unmute_group_button, 5, 1)

        # Set the main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def mute_all_tracks(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            for track in project.tracks:
                track.mute()
                print(track.name)
            print("All tracks muted.")

    def unmute_all_tracks(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            for track in project.tracks:
                track.unmute()
            print("All tracks unmuted.")

    def solo_all_tracks(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            for track in project.tracks:
                track.solo()
            print("All tracks soloed.")

    def unsolo_all_tracks(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            for track in project.tracks:
                track.unsolo()
            print("All tracks unsoloed.")

    def solo_selected_track_group(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            selected_tracks = [track for track in project.tracks if track.is_selected]

            if not selected_tracks:
                print("No track selected.")
                return

            parent_tracks = set(track.parent_track for track in selected_tracks if track.parent_track)

            if not parent_tracks:
                print("Selected tracks have no parent.")
                return

            for parent_track in parent_tracks:
                # Solo all tracks with the same parent
                for track in project.tracks:
                    if track.parent_track == parent_track:
                        track.solo()
                        print(f"Soloed track: {track.name}")

                # Solo the parent track
                parent_track.solo()
                print(f"Soloed parent track: {parent_track.name}")

    def unsolo_selected_track_group(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            selected_tracks = [track for track in project.tracks if track.is_selected]

            if not selected_tracks:
                print("No track selected.")
                return

            parent_tracks = set(track.parent_track for track in selected_tracks if track.parent_track)

            if not parent_tracks:
                print("Selected tracks have no parent.")
                return

            for parent_track in parent_tracks:
                # Unsolo all tracks with the same parent
                for track in project.tracks:
                    if track.parent_track == parent_track:
                        track.unsolo()
                        print(f"Unsoloed track: {track.name}")

                # Unsolo the parent track
                parent_track.unsolo()
                print(f"Unsoloed parent track: {parent_track.name}")

    def mute_selected_track_group(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            selected_tracks = [track for track in project.tracks if track.is_selected]

            if not selected_tracks:
                print("No track selected.")
                return

            parent_tracks = set(track.parent_track for track in selected_tracks if track.parent_track)

            if not parent_tracks:
                print("Selected tracks have no parent.")
                return

            for parent_track in parent_tracks:
                # Mute all tracks with the same parent
                for track in project.tracks:
                    if track.parent_track == parent_track:
                        track.mute()
                        print(f"Muted track: {track.name}")

                # Mute the parent track
                parent_track.mute()
                print(f"Muted parent track: {parent_track.name}")

    def unmute_selected_track_group(self):
        with reapy.inside_reaper():
            project = reapy.Project()
            selected_tracks = [track for track in project.tracks if track.is_selected]

            if not selected_tracks:
                print("No track selected.")
                return

            parent_tracks = set(track.parent_track for track in selected_tracks if track.parent_track)

            if not parent_tracks:
                print("Selected tracks have no parent.")
                return

            for parent_track in parent_tracks:
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
    apply_dark_theme(app)
    window = TrackControlApp()
    window.show()
    sys.exit(app.exec_())