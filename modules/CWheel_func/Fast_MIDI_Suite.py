import sys
import json
from PySide6.QtGui import QPainterPath, QKeySequence, QAction
import reapy
import random
import statistics
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                              QWidget, QSpinBox, QLabel, QComboBox, QGridLayout, 
                              QGroupBox, QScrollArea, QSlider, QCheckBox, QTabWidget, QTextEdit, QHBoxLayout)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QPen
from reapy import reascript_api as RPR
from modules.AI_func.ui_overlay import OverlayUI
from modules.styles import apply_dark_theme
from modules.AI_func.ops.velocity_ops import VelocityOperations
from modules.AI_func.ops.cc_ops import CCOperations
from modules.AI_func.ops.filter_ops import FilterOperations
from modules.AI_func.ops.script_ops import ScriptOperations
import os
from modules.context_tools import ContextToolsWindow
from reapy.core.reaper.midi import get_active_editor as get_active_midi_editor

class FastMidiSuite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fast MIDI Suite")
        self.setGeometry(100, 100, 800, 600)
        apply_dark_theme(self)
        
        # Create context-aware tools window
        self.context_tools = ContextToolsWindow(self)
        self.context_tools.show()
        
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
        
        # Initialize keybinds after loading
        self.setup_keybind_actions()

        # Create overlay UI
        self.overlay = OverlayUI(self)
        self.overlay.move(10, self.height() - 100)  # Position at bottom-left
        
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
        
        # Scale controls
        self.scale_btn = QPushButton("Scale")
        self.scale_btn.clicked.connect(self.scale_velocities)
        tools_layout.addWidget(self.scale_btn, 1, 1)

        # Add scale factor slider
        scale_group = QGroupBox("Scale Factor (100-200%)")
        scale_layout = QHBoxLayout()
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(0, 100)
        self.scale_slider.setValue(20)  # Default 120% (1.2x)
        scale_layout.addWidget(self.scale_slider)
        
        self.scale_label = QLabel("120%")
        scale_layout.addWidget(self.scale_label)
        
        # Connect slider to label update
        self.scale_slider.valueChanged.connect(
            lambda v: self.scale_label.setText(f"{100 + v}%")
        )
        
        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)
        
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
        
        # CC value controls
        self.cc_value = QSlider(Qt.Horizontal)
        self.cc_value.setRange(0, 127)
        cc_select_layout.addWidget(QLabel("CC Value:"), 1, 0)
        cc_select_layout.addWidget(self.cc_value, 1, 1)

        # CC delta controls
        self.cc_delta = QSpinBox()
        self.cc_delta.setRange(1, 64)
        self.cc_delta.setValue(5)
        cc_select_layout.addWidget(QLabel("Adjust Delta:"), 2, 0)
        cc_select_layout.addWidget(self.cc_delta, 2, 1)
        
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
        config_dir = "config files"
        config_path = os.path.join(config_dir, "keybinds.json")
        
        try:
            # Create config directory if it doesn't exist
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            # Try loading from config files directory first
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default keybinds if file doesn't exist
            default_keybinds = {
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
            with open(config_path, "w") as f:
                json.dump(default_keybinds, f, indent=2)
            return default_keybinds
        except json.JSONDecodeError:
            print("Invalid keybinds.json, using defaults")
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
        """Randomize selected note velocities with bulk edit"""
        try:
            # Batch process all selected notes at once
            editor = get_active_midi_editor()
            if not editor:
                return
                
            take = editor.take
            if not take:
                return
                
            # Get all selected notes in one call
            selected_notes = take.get_selected_notes()
            if not selected_notes:
                return
                
            min_vel = self.min_velocity.value()
            max_vel = self.max_velocity.value()
            
            # Generate all random velocities at once
            new_velocities = [random.randint(min_vel, max_vel) 
                            for _ in selected_notes]
            
            # Update notes in bulk
            with reapy.undo_block("Randomize Velocities"):
                for note, vel in zip(selected_notes, new_velocities):
                    note.velocity = vel
                    
                RPR.UpdateArrange()
                
            self.overlay.show_message(f"Randomized {len(selected_notes)} notes")
            
        except Exception as e:
            print(f"Randomize error: {e}")
        
    def normalize_velocities(self):
        """Normalize velocities to median with bulk edit"""
        try:
            editor = get_active_midi_editor()
            if not editor:
                return
                
            take = editor.take
            if not take:
                return
                
            selected_notes = take.get_selected_notes()
            if not selected_notes:
                return

            # Calculate median velocity
            velocities = [n.velocity for n in selected_notes]
            median_vel = int(statistics.median(velocities))
            
            with reapy.undo_block("Normalize Velocities"):
                for note in selected_notes:
                    note.velocity = median_vel
                RPR.UpdateArrange()
                
            self.overlay.show_message(f"Normalized {len(selected_notes)} notes to {median_vel}")
            
        except Exception as e:
            print(f"Normalize error: {e}")
        
    def compress_velocities(self):
        """Compress velocity range with bulk edit"""
        try:
            editor = get_active_midi_editor()
            if not editor:
                return
                
            take = editor.take
            if not take:
                return
                
            selected_notes = take.get_selected_notes()
            if not selected_notes:
                return

            min_target = self.min_velocity.value()
            max_target = self.max_velocity.value()
            current_min = min(n.velocity for n in selected_notes)
            current_max = max(n.velocity for n in selected_notes)
            range_scale = (max_target - min_target) / (current_max - current_min)
            
            with reapy.undo_block("Compress Velocities"):
                for note in selected_notes:
                    scaled = (note.velocity - current_min) * range_scale + min_target
                    note.velocity = int(max(min_target, min(max_target, scaled)))
                RPR.UpdateArrange()
                
            self.overlay.show_message(f"Compressed {len(selected_notes)} notes to {min_target}-{max_target}")
            
        except Exception as e:
            print(f"Compress error: {e}")
        
    def scale_velocities(self):
        """Scale velocities with dynamic factor and bulk edit"""
        try:
            editor = get_active_midi_editor()
            if not editor:
                return
                
            take = editor.take
            if not take:
                return
                
            selected_notes = take.get_selected_notes()
            if not selected_notes:
                return

            # Calculate scale factor based on slider position (1.0-2.0)
            scale_factor = 1.0 + (self.scale_slider.value() / 100)
            
            with reapy.undo_block("Scale Velocities"):
                for note in selected_notes:
                    new_vel = int(note.velocity * scale_factor)
                    note.velocity = max(0, min(127, new_vel))
                RPR.UpdateArrange()
                
            self.overlay.show_message(f"Scaled {len(selected_notes)} notes by {scale_factor:.2f}x")
            
        except Exception as e:
            print(f"Scale error: {e}")
        
    def run_script(self):
        """Execute MIDI script"""
        script = self.script_editor.toPlainText()
        self.script_ops.execute(script)
        
    def adjust_cc_right(self):
        """Adjust CC values to the right with bulk editing"""
        delta = self.cc_delta.value()
        self.cc_ops.adjust_cc_bulk(delta, self.overlay)
        self._refresh_cc_display()

    def adjust_cc_left(self):
        """Adjust CC values to the left with bulk editing"""
        delta = -self.cc_delta.value()
        self.cc_ops.adjust_cc_bulk(delta, self.overlay)
        self._refresh_cc_display()

    def _refresh_cc_display(self):
        """Update CC visualization after changes"""
        if self.tabs.currentIndex() == 1:  # CC Editor tab
            self.canvas.update()
            self.visualizer.update()
        
    def setup_keybind_actions(self):
        """Create actions for keybinds"""
        self.actions = {}
        for name, shortcut in self.keybinds.items():
            action = QAction(self)
            action.setShortcut(QKeySequence(shortcut))
            self.actions[name] = action
            
        # Connect actions to methods
        self.actions["velocity_up"].triggered.connect(self.velocity_up)
        self.actions["velocity_down"].triggered.connect(self.velocity_down)
        self.actions["cc_left"].triggered.connect(self.adjust_cc_left)
        self.actions["cc_right"].triggered.connect(self.adjust_cc_right)
        # Add more connections as needed
        
    def velocity_up(self):
        """Increase selected velocities with bulk processing"""
        delta = 5
        count = self.velocity_ops.adjust_velocity_bulk(delta)
        self.overlay.show_message(f"Velocity +{delta} ({count} notes)")
        self._refresh_velocity_display()
        
    def velocity_down(self):
        """Decrease selected velocities with bulk processing"""
        delta = -5
        count = self.velocity_ops.adjust_velocity_bulk(delta)
        self.overlay.show_message(f"Velocity {delta} ({count} notes)")
        self._refresh_velocity_display()

    def _refresh_velocity_display(self):
        """Update velocity visualization after changes"""
        if self.tabs.currentIndex() == 0:  # Velocity tab
            self.visualizer.update()
            # Update velocity range display immediately
            self.min_velocity.repaint()
            self.max_velocity.repaint()
        
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
