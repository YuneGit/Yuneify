import reapy
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QLabel
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject
from modules.AI_composition_review import MidiNote  # Corrected import path
from modules.styles import apply_dark_theme  # Import the stylesheet function

class MidiWorker(QObject):
    notes_ready = Signal(list)

    def fetch_notes(self):
        project = reapy.Project()
        item = project.get_selected_item(0)
        if not item:
            self.notes_ready.emit([])
            return

        take = item.active_take
        if not take:
            self.notes_ready.emit([])
            return

        notes = [MidiNote(
            start=note.start,
            end=note.end,
            pitch=note.pitch,
            velocity=note.velocity,
            channel=note.channel,
            selected=note.selected,
            muted=note.muted
        ) for note in take.notes]
        self.notes_ready.emit(notes)

class MidiVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.notes = None  # Cache notes to avoid repeated fetching
        self.note_items = []  # Store QGraphicsLineItem references

        # Setup worker thread
        self.thread = QThread()
        self.worker = MidiWorker()
        self.worker.moveToThread(self.thread)
        self.worker.notes_ready.connect(self.on_notes_ready)
        self.thread.start()

        # Timer for showing instructions
        self.idle_timer = QTimer()
        self.idle_timer.setInterval(3000)  # 3 seconds
        self.idle_timer.timeout.connect(self.show_instructions)

    def initUI(self):
        self.setWindowTitle('MIDI Visualizer')
        self.setFixedSize(800, 600)

        apply_dark_theme(self)
        main_layout = QVBoxLayout()

        self.visualize_button = QPushButton('Visualize MIDI', self)
        self.visualize_button.setObjectName("visualizeButton")
        self.visualize_button.clicked.connect(self.load_and_visualize_midi)
        main_layout.addWidget(self.visualize_button)

        self.graphics_view = CustomGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)
        main_layout.addWidget(self.graphics_view)

        # Instructions label
        self.instructions_label = QLabel("Use Shift + Scroll for horizontal zoom, Ctrl + Scroll for vertical zoom", self)
        self.instructions_label.setObjectName("instructions")
        self.instructions_label.setVisible(False)
        main_layout.addWidget(self.instructions_label)

        # Create a layout for the zoom buttons
        zoom_layout = QHBoxLayout()

        # Horizontal zoom buttons
        zoom_in_h = QPushButton(self)
        zoom_in_h.setObjectName("zoomButton")
        zoom_in_h.clicked.connect(lambda: self.zoom(1.1, 'horizontal'))
        zoom_layout.addWidget(zoom_in_h)

        zoom_out_h = QPushButton(self)
        zoom_out_h.setObjectName("zoomButton")
        zoom_out_h.clicked.connect(lambda: self.zoom(0.9, 'horizontal'))
        zoom_layout.addWidget(zoom_out_h)

        # Vertical zoom buttons
        zoom_in_v = QPushButton(self)
        zoom_in_v.setObjectName("zoomButton")
        zoom_in_v.clicked.connect(lambda: self.zoom(1.1, 'vertical'))
        zoom_layout.addWidget(zoom_in_v)

        zoom_out_v = QPushButton(self)
        zoom_out_v.setObjectName("zoomButton")
        zoom_out_v.clicked.connect(lambda: self.zoom(0.9, 'vertical'))
        zoom_layout.addWidget(zoom_out_v)

        main_layout.addLayout(zoom_layout)


        self.setLayout(main_layout)

    def load_and_visualize_midi(self):
        self.scene.clear()
        self.note_items.clear()  # Clear previous note items
        QTimer.singleShot(0, self.worker.fetch_notes)

    def on_notes_ready(self, notes):
        self.notes = notes
        if not self.notes:
            self.show_message("No MIDI notes.")
            return

        self.draw_notes()

    def draw_notes(self):
        if self.notes is None:
            return

        pen = QPen(QColor("#FFFFFF"))
        pen.setWidth(2)

        # Mapping of MIDI pitch values to note names
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        for note in self.notes:
            start_x = note.start * 100  # Fixed scale for initial drawing
            end_x = note.end * 100
            y = 127 - note.pitch
            line_item = QGraphicsLineItem(start_x, y, end_x, y)
            line_item.setPen(pen)
            self.scene.addItem(line_item)
            self.note_items.append(line_item)

            # Convert pitch to note name
            note_name = note_names[note.pitch % 12] + str(note.pitch // 12)

            # Add text item for note name with smaller font size
            text_item = self.scene.addText(note_name)
            text_item.setDefaultTextColor(QColor("#FFFFFF"))
            text_item.setPos(start_x, y - 2)  # Move text one pixel lower
            font = text_item.font()
            font.setPointSize(3)  # Further reduce font size
            text_item.setFont(font)

        # Ensure the first note is at the left side of the window
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def show_message(self, message):
        self.scene.clear()
        text_item = self.scene.addText(message)
        text_item.setDefaultTextColor(QColor("#FFFFFF"))

    def zoom(self, factor, direction):
        if direction == 'horizontal':
            self.graphics_view.scale(factor, 1)
        elif direction == 'vertical':
            self.graphics_view.scale(1, factor)

    def show_instructions(self):
        self.instructions_label.setVisible(True)

    def mouseMoveEvent(self, event):
        self.instructions_label.setVisible(False)
        self.idle_timer.start()

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event):
        # Determine the zoom factor based on the scroll direction
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        modifiers = QApplication.keyboardModifiers()

        # Check for modifier keys and apply the appropriate zoom
        if modifiers == Qt.ShiftModifier:
            self.scale(factor, 1)  # Horizontal zoom
        elif modifiers == Qt.ControlModifier:
            self.scale(1, factor)  # Vertical zoom
        else:
            self.scale(factor, factor)  # Uniform zoom

if __name__ == "__main__":
    app = QApplication([])
    visualizer = MidiVisualizer()
    visualizer.show()
    sys.exit(app.exec()) 