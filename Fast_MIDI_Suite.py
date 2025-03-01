import sys
import json
from PySide6.QtGui import QPainterPath
import reapy
import random
import statistics
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                              QWidget, QSpinBox, QLabel, QComboBox, QGridLayout, 
                              QGroupBox, QScrollArea, QSlider, QCheckBox, QTabWidget, QTextEdit)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QPen
from reapy import reascript_api as RPR
from modules.styles import apply_dark_theme
from modules.ops.velocity_ops import VelocityOperations
from modules.ops.cc_ops import CCOperations
from modules.ops.filter_ops import FilterOperations
from modules.ops.script_ops import ScriptOperations

class FastMidiSuite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fast MIDI Suite")
        self.setGeometry(100, 100, 800, 600)
        apply_dark_theme(self)
        
        # Main tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Add core tabs
        self.add_velocity_tab()
        self.add_cc_tab() 
        self.add_filter_tab()
        self.add_visualization_tab()
        self.add_scripting_tab()
        
        # Initialize MIDI operations
        self.init_midi_operations()
        
        # Keybind manager
        self.keybinds = self.load_keybinds()
        
    def add_velocity_tab(self):
        """Velocity editing interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Velocity range controls
        range_group = QGroupBox("Velocity Range")
        range_layout = QGridLayout()
        
        self.min_velocity = QSpinBox()
        self.min_velocity.setRange(0, 127)
        range_layout.addWidget(QLabel("Min Velocity:"), 0, 0)
        range_layout.addWidget(self.min_velocity, 0, 1)
        
        self.max_velocity = QSpinBox() 
        self.max_velocity.setRange(0, 127)
        self.max_velocity.setValue(127)
        range_layout.addWidget(QLabel("Max Velocity:"), 1, 0)
        range_layout.addWidget(self.max_velocity, 1, 1)
        
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)
        
        # Velocity tools
        tools_group = QGroupBox("Tools")
        tools_layout = QGridLayout()
        
        self.randomize_btn = QPushButton("Randomize")
        self.randomize_btn.clicked.connect(self.randomize_velocities)
        tools_layout.addWidget(self.randomize_btn, 0, 0)
        
        self.normalize_btn = QPushButton("Normalize")
        self.normalize_btn.clicked.connect(self.normalize_velocities)
        tools_layout.addWidget(self.normalize_btn, 0, 1)
        
        self.compress_btn = QPushButton("Compress")
        self.compress_btn.clicked.connect(self.compress_velocities)
        tools_layout.addWidget(self.compress_btn, 1, 0)
        
        self.scale_btn = QPushButton("Scale")
        self.scale_btn.clicked.connect(self.scale_velocities)
        tools_layout.addWidget(self.scale_btn, 1, 1)
        
        tools_group.setLayout(tools_layout)
        layout.addWidget(tools_group)
        
        self.tabs.addTab(tab, "Velocity")
        
    def add_cc_tab(self):
        """CC editing interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # CC selection
        cc_select_group = QGroupBox("CC Selection")
        cc_select_layout = QGridLayout()
        
        self.cc_combobox = QComboBox()
        self.cc_combobox.addItems([f"CC {i}" for i in range(128)])
        cc_select_layout.addWidget(QLabel("CC Number:"), 0, 0)
        cc_select_layout.addWidget(self.cc_combobox, 0, 1)
        
        self.cc_value = QSlider(Qt.Horizontal)
        self.cc_value.setRange(0, 127)
        cc_select_layout.addWidget(QLabel("CC Value:"), 1, 0)
        cc_select_layout.addWidget(self.cc_value, 1, 1)
        
        cc_select_group.setLayout(cc_select_layout)
        layout.addWidget(cc_select_group)
        
        # CC curve editor
        curve_group = QGroupBox("CC Curve Editor")
        curve_layout = QVBoxLayout()
        
        self.canvas = CC_Canvas()
        curve_layout.addWidget(self.canvas)
        
        curve_group.setLayout(curve_layout)
        layout.addWidget(curve_group)
        
        self.tabs.addTab(tab, "CC Editor")
        
    def add_filter_tab(self):
        """MIDI event filtering"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Event type filters
        type_group = QGroupBox("Event Types")
        type_layout = QGridLayout()
        
        self.note_filter = QCheckBox("Notes")
        self.note_filter.setChecked(True)
        type_layout.addWidget(self.note_filter, 0, 0)
        
        self.cc_filter = QCheckBox("CC")
        type_layout.addWidget(self.cc_filter, 0, 1)
        
        self.pitch_filter = QCheckBox("Pitch Bend")
        type_layout.addWidget(self.pitch_filter, 1, 0)
        
        self.prog_filter = QCheckBox("Program Change")
        type_layout.addWidget(self.prog_filter, 1, 1)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Value range filters
        range_group = QGroupBox("Value Ranges")
        range_layout = QGridLayout()
        
        self.min_value = QSpinBox()
        self.min_value.setRange(0, 127)
        range_layout.addWidget(QLabel("Min Value:"), 0, 0)
        range_layout.addWidget(self.min_value, 0, 1)
        
        self.max_value = QSpinBox()
        self.max_value.setRange(0, 127)
        self.max_value.setValue(127)
        range_layout.addWidget(QLabel("Max Value:"), 1, 0)
        range_layout.addWidget(self.max_value, 1, 1)
        
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)
        
        self.tabs.addTab(tab, "Filters")
        
    def add_visualization_tab(self):
        """Real-time MIDI visualization"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.visualizer = MIDI_Visualizer()
        layout.addWidget(self.visualizer)
        
        self.tabs.addTab(tab, "Visualizer")
        
    def add_scripting_tab(self):
        """MIDI scripting interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Script editor
        editor_group = QGroupBox("Script Editor")
        editor_layout = QVBoxLayout()
        
        self.script_editor = QTextEdit()
        editor_layout.addWidget(self.script_editor)
        
        # Example scripts
        self.example_combobox = QComboBox()
        self.example_combobox.addItems([
            "Velocity Ramp",
            "CC LFO",
            "Arpeggiator",
            "Humanize Timing"
        ])
        editor_layout.addWidget(self.example_combobox)
        
        # Run button
        self.run_btn = QPushButton("Run Script")
        self.run_btn.clicked.connect(self.run_script)
        editor_layout.addWidget(self.run_btn)
        
        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)
        
        self.tabs.addTab(tab, "Scripting")
        
    def init_midi_operations(self):
        """Initialize MIDI operation classes"""
        self.velocity_ops = VelocityOperations()
        self.cc_ops = CCOperations()
        self.filter_ops = FilterOperations()
        self.script_ops = ScriptOperations()
        
    def load_keybinds(self):
        """Load keybind presets"""
        try:
            with open("keybinds.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "velocity_up": "ctrl+shift+alt+up",
                "velocity_down": "ctrl+shift+alt+down",
                "cc_left": "ctrl+shift+alt+left",
                "cc_right": "ctrl+shift+alt+right",
                "quantize": "ctrl+shift+alt+q",
                "humanize": "ctrl+shift+alt+h",
                "legato": "ctrl+shift+alt+l",
                "chord_gen": "ctrl+shift+alt+c",
                "chord_cycle": "ctrl+shift+alt+v",
                "select_velocity": "ctrl+shift+alt+s",
                "select_cc": "ctrl+shift+alt+d"
            }
            
    def randomize_velocities(self):
        """Randomize selected note velocities"""
        self.velocity_ops.randomize(
            self.min_velocity.value(),
            self.max_velocity.value()
        )
        
    def normalize_velocities(self):
        """Normalize velocities to median"""
        self.velocity_ops.normalize()
        
    def compress_velocities(self):
        """Compress velocity range"""
        self.velocity_ops.compress(
            self.min_velocity.value(),
            self.max_velocity.value()
        )
        
    def scale_velocities(self):
        """Scale velocities by factor"""
        self.velocity_ops.scale(1.2)
        
    def run_script(self):
        """Execute MIDI script"""
        script = self.script_editor.toPlainText()
        self.script_ops.execute(script)
        
class CC_Canvas(QWidget):
    """CC curve editing canvas"""
    from PySide6.QtGui import QPainterPath
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 200)
        self.points = []
        
    def paintEvent(self, event):
        """Draw CC curve"""
        painter = QPainter(self)
        pen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(pen)
        
        # Draw grid
        painter.drawLine(0, self.height()//2, self.width(), self.height()//2)
        painter.drawLine(self.width()//2, 0, self.width()//2, self.height())
        
        # Draw curve
        if len(self.points) > 1:
            path = QPainterPath()
            path.moveTo(self.points[0])
            for p in self.points[1:]:
                path.lineTo(p)
            painter.drawPath(path)
            
class MIDI_Visualizer(QWidget):
    """Real-time MIDI visualization"""
    from PySide6.QtGui import QPainterPath
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 400)
        self.notes = []
        self.cc_values = []
        
    def paintEvent(self, event):
        """Draw MIDI data"""
        painter = QPainter(self)
        
        # Draw notes
        pen = QPen(QColor(0, 255, 0), 2)
        painter.setPen(pen)
        for note in self.notes:
            x = note['time'] * self.width()
            y = (127 - note['velocity']) * self.height() / 127
            painter.drawEllipse(x, y, 5, 5)
            
        # Draw CC
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        if len(self.cc_values) > 1:
            path = QPainterPath()
            path.moveTo(0, self.cc_values[0] * self.height() / 127)
            for i, val in enumerate(self.cc_values[1:]):
                x = i * self.width() / len(self.cc_values)
                y = val * self.height() / 127
                path.lineTo(x, y)
            painter.drawPath(path)
            
def main():
    app = QApplication([])
    window = FastMidiSuite()
    window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
