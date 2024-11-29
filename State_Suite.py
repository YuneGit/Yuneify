import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QGridLayout
from PyQt5.QtCore import Qt
import reapy

class TrackControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track Control")
        self.setGeometry(100, 100, 275, 275)  # Fixed window size

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
                margin: 3px;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border-radius: 12px;
                padding: 4px 4px;
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
                border-radius: 3px;
                padding: 3px;
                border: 1px solid #5A5A5A;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A2A;
                color: #FFFFFF;
                selection-background-color: #4A4A4A;
            }
        """)

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
        project = reapy.Project()
        for track in project.tracks:
            track.Mute()
            print(track.name)
        print("All tracks muted.")

    def unmute_all_tracks(self):
        project = reapy.Project()
        for track in project.tracks:
            track.Un-Mute()
        print("All tracks unmuted.")

    def solo_all_tracks(self):
        project = reapy.Project()
        for track in project.tracks:
            track.Solo()
        print("All tracks soloed.")

    def unsolo_all_tracks(self):
        project = reapy.Project()
        for track in project.tracks:
            track.Un-Solo()
        print("All tracks unsoloed.")

    def solo_selected_track_group(self):
        project = reapy.Project()
        selected_tracks = [track for track in project.tracks if track.is_selected]

        if not selected_tracks:
            print("No track .")
            return

        selected_track = selected_tracks[0]
        parent_track = selected_track.parent_track

        if parent_track is None:
            print(" track has no parent.")
            return

        # Solo all tracks with the same parent
        for track in project.tracks:
            if track.parent_track == parent_track:
                track.Solo()
                print(f"Soloed track: {track.name}")

        # Mute the parent track
        parent_track.Solo()
        print(f"Muted parent track: {parent_track.name}")

    def unsolo_selected_track_group(self):
        project = reapy.Project()
        selected_tracks = [track for track in project.tracks if track.is_selected]

        if not selected_tracks:
            print("No track .")
            return

        selected_track = selected_tracks[0]
        parent_track = selected_track.parent_track

        if parent_track is None:
            print(" track has no parent.")
            return

        # Un-Solo all tracks with the same parent
        for track in project.tracks:
            if track.parent_track == parent_track:
                track.Un-Solo()
                print(f"Unsoloed track: {track.name}")

        # Un-Mute the parent track
        parent_track.Un-Solo()
        print(f"Unmuted parent track: {parent_track.name}")

    def mute_selected_track_group(self):
        project = reapy.Project()
        selected_tracks = [track for track in project.tracks if track.is_selected]

        if not selected_tracks:
            print("No track .")
            return

        selected_track = selected_tracks[0]
        parent_track = selected_track.parent_track

        if parent_track is None:
            print(" track has no parent.")
            return

        # Mute all tracks with the same parent
        for track in project.tracks:
            if track.parent_track == parent_track:
                track.Mute()
                print(f"Muted track: {track.name}")

        # Mute the parent track
        parent_track.Mute()
        print(f"Muted parent track: {parent_track.name}")

    def unmute_selected_track_group(self):
        project = reapy.Project()
        selected_tracks = [track for track in project.tracks if track.is_selected]

        if not selected_tracks:
            print("No track .")
            return

        selected_track = selected_tracks[0]
        parent_track = selected_track.parent_track

        if parent_track is None:
            print(" track has no parent.")
            return

        # Un-Mute all tracks with the same parent
        for track in project.tracks:
            if track.parent_track == parent_track:
                track.Un-Mute()
                print(f"Unmuted track: {track.name}")

        # Un-Mute the parent track
        parent_track.Un-Mute()
        print(f"Unmuted parent track: {parent_track.name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrackControlApp()
    window.show()
    sys.exit(app.exec_())
