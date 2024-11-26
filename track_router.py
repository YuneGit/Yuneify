import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, 
    QLabel, QComboBox, QListWidget, QHBoxLayout, QListWidgetItem
)
import reapy

class TrackRouter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track Router")
        self.setGeometry(200, 100, 600, 400)
        
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
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
            QListWidget {
                background-color: #2A2A2A;
                border: 1px solid #5A5A5A;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #4A4A4A;
            }
            QComboBox {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #5A5A5A;
                min-width: 200px;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A2A;
                color: #FFFFFF;
                selection-background-color: #4A4A4A;
            }
        """)

        # Main layout
        main_layout = QHBoxLayout()
        
        # Left side (Source tracks)
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Source Tracks:"))
        self.source_list = QListWidget()
        self.source_list.setSelectionMode(QListWidget.ExtendedSelection)
        left_layout.addWidget(self.source_list)
        
        # Middle (Controls)
        middle_layout = QVBoxLayout()
        middle_layout.addStretch()
        self.destination_combo = QComboBox()
        middle_layout.addWidget(QLabel("Destination Track:"))
        middle_layout.addWidget(self.destination_combo)
        self.route_button = QPushButton("Create Send →")
        self.route_button.clicked.connect(self.create_send)
        middle_layout.addWidget(self.route_button)
        self.remove_button = QPushButton("Remove Send ×")
        self.remove_button.clicked.connect(self.remove_send)
        middle_layout.addWidget(self.remove_button)
        middle_layout.addStretch()
        
        # Right side (Existing sends)
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Existing Sends:"))
        self.sends_list = QListWidget()
        right_layout.addWidget(self.sends_list)
        
        # Add layouts to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        middle_widget = QWidget()
        middle_widget.setLayout(middle_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(middle_widget)
        main_layout.addWidget(right_widget)
        
        # Set the main widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Initialize track lists
        self.refresh_tracks()

    def refresh_tracks(self):
        """Refresh the lists of tracks and sends"""
        project = reapy.Project()
        
        # Clear existing items
        self.source_list.clear()
        self.destination_combo.clear()
        self.sends_list.clear()
        
        # Add all tracks to both source list and destination combo
        for track in project.tracks:
            self.source_list.addItem(track.name)
            self.destination_combo.addItem(track.name)
            
            # Add existing sends to sends list
            for send in track.sends:
                dest_track = project.tracks[send.destination]
                send_text = f"{track.name} → {dest_track.name}"
                self.sends_list.addItem(send_text)

    def create_send(self):
        """Create sends from selected source tracks to destination track"""
        project = reapy.Project()
        selected_items = self.source_list.selectedItems()
        destination_idx = self.destination_combo.currentIndex()
        
        if not selected_items:
            print("No source tracks selected")
            return
            
        # Get destination track
        dest_track = project.tracks[destination_idx]
        
        # Create sends for each selected source track
        for item in selected_items:
            source_idx = self.source_list.row(item)
            source_track = project.tracks[source_idx]
            
            # Skip if trying to send to self
            if source_idx == destination_idx:
                continue
                
            # Create the send
            source_track.add_send(dest_track)
            print(f"Created send: {source_track.name} → {dest_track.name}")
        
        # Refresh the display
        self.refresh_tracks()

    def remove_send(self):
        """Remove selected sends"""
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
                    dest_track = project.tracks[send.destination]
                    if dest_track.name == dest_name:
                        source_track.remove_send(send)
                        print(f"Removed send: {source_name} → {dest_name}")
        
        # Refresh the display
        self.refresh_tracks()

def main():
    app = QApplication(sys.argv)
    window = TrackRouter()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()