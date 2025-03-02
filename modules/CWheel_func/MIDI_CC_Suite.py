import sys
import reapy
import random
import statistics
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                              QWidget, QSpinBox, QLabel, QComboBox, QGridLayout, 
                              QGroupBox, QScrollArea)
from PySide6.QtCore import Qt, QTimer
from reapy import reascript_api as RPR
from modules.styles import apply_dark_theme

class MidiCCSuite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI CC Suite")
        self.setGeometry(100, 100, 400, 300)
        apply_dark_theme(self)
        
        # Create scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)
        
        # Main content widget
        self.main_content = QWidget()
        self.scroll.setWidget(self.main_content)
        
        # Main vertical layout
        self.main_layout = QVBoxLayout(self.main_content)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add CC controls
        self.add_cc_controls()
        
        # Initialize MIDI operation classes
        self.cc_controller = MidiCCController()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._process_operations)
        self._pending_operations = []

    def add_cc_controls(self):
        """Add CC control interface"""
        cc_group = QGroupBox("CC Controls")
        layout = QGridLayout()
        
        # MIDI Learn button
        self.learn_button = QPushButton("MIDI Learn")
        self.learn_button.setCheckable(True)
        self.learn_button.clicked.connect(self.toggle_midi_learn)
        layout.addWidget(self.learn_button, 0, 0, 1, 2)
        
        # CC Selection
        self.cc_combobox = QComboBox()
        self.cc_combobox.addItems([f"CC {i}" for i in range(128)])
        layout.addWidget(self.cc_combobox, 1, 0)
        
        # CC Value control
        self.cc_spinbox = QSpinBox()
        self.cc_spinbox.setRange(0, 127)
        self.cc_spinbox.setValue(64)
        layout.addWidget(self.cc_spinbox, 1, 1)
        
        # Apply button
        self.apply_cc_button = QPushButton("Set CC Values")
        self.apply_cc_button.clicked.connect(self.apply_cc_values)
        layout.addWidget(self.apply_cc_button, 2, 0, 1, 2)
        
        # Add CC manipulation buttons
        cc_tools_layout = QGridLayout()
        
        self.randomize_cc_button = QPushButton("Randomize")
        self.randomize_cc_button.clicked.connect(self.randomize_cc_values)
        cc_tools_layout.addWidget(self.randomize_cc_button, 0, 0)
        
        self.humanize_cc_button = QPushButton("Humanize")
        self.humanize_cc_button.clicked.connect(self.humanize_cc_values)
        cc_tools_layout.addWidget(self.humanize_cc_button, 0, 1)
        
        self.scale_cc_button = QPushButton("Scale")
        self.scale_cc_button.clicked.connect(self.scale_cc_values)
        cc_tools_layout.addWidget(self.scale_cc_button, 1, 0)
        
        self.normalize_cc_button = QPushButton("Normalize")
        self.normalize_cc_button.clicked.connect(self.normalize_cc_values)
        cc_tools_layout.addWidget(self.normalize_cc_button, 1, 1)
        
        layout.addLayout(cc_tools_layout, 3, 0, 1, 2)
        
        cc_group.setLayout(layout)
        self.main_layout.addWidget(cc_group)

    def toggle_midi_learn(self, enabled):
        """Toggle MIDI learn mode"""
        self.cc_controller.toggle_learn(enabled)
        self.learn_button.setChecked(enabled)
        print(f"MIDI Learn {'activated' if enabled else 'deactivated'}")

    def apply_cc_values(self):
        """Apply CC values from UI controls"""
        cc_num = int(self.cc_combobox.currentText().split()[-1])
        value = self.cc_spinbox.value()
        self.cc_controller.set_cc_values(cc_num, value)
        print(f"Set CC{cc_num} to {value} for selected notes")

    def randomize_cc_values(self):
        """Randomize CC values"""
        cc_num = int(self.cc_combobox.currentText().split()[-1])
        self.cc_controller.randomize_cc_values()
        print(f"Randomized CC{cc_num} values")

    def humanize_cc_values(self):
        """Humanize CC values"""
        cc_num = int(self.cc_combobox.currentText().split()[-1])
        self.cc_controller.humanize_cc_values()
        print(f"Humanized CC{cc_num} values")

    def scale_cc_values(self):
        """Scale CC values"""
        cc_num = int(self.cc_combobox.currentText().split()[-1])
        self.cc_controller.scale_cc_values()
        print(f"Scaled CC{cc_num} values")

    def normalize_cc_values(self):
        """Normalize CC values"""
        cc_num = int(self.cc_combobox.currentText().split()[-1])
        self.cc_controller.normalize_cc_values()
        print(f"Normalized CC{cc_num} values")

    def _process_operations(self):
        """Process queued MIDI operations in the main thread"""
        while self._pending_operations:
            try:
                func, args = self._pending_operations.pop(0)
                func(*args)
            except Exception as e:
                print(f"Error processing operation: {str(e)}")

    def queue_operation(self, func, *args):
        """Add an operation to be processed in the main thread"""
        self._pending_operations.append((func, args))
        if not self._timer.isActive():
            self._timer.start(100)

class MidiCCController:
    def __init__(self):
        self.learn_mode = False
        self.last_cc = None
        self.cc_value = 0
        
    def toggle_learn(self, enabled):
        self.learn_mode = enabled
        if enabled:
            print("MIDI Learn active - move a controller now...")
            self.start_cc_listener()
            
    def start_cc_listener(self):
        def callback(event):
            if event.midiId == 0xB0:  # CC message
                self.last_cc = event.data1
                print(f"Learned CC: {self.last_cc}")
                self.learn_mode = False
        reapy.set_midi_input_callback(callback)
        
    def set_cc_values(self, cc_num, value):
        take = self.get_active_take()
        if not take:
            return
            
        for note in take.selected_notes:
            retval, _, _, _, _, _, _, _ = RPR.MIDI_GetCC(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0)
            RPR.MIDI_SetCC(
                take.id, note.index,
                note.selected, note.muted,
                note.ppqpos, note.msg2, value,
                note.channel, note.msg, 0)
                
        RPR.MIDI_Sort(take.id)
        print(f"Set CC{cc_num} to {value} for {len(take.selected_notes)} notes")

    def randomize_cc_values(self):
        take = self.get_active_take()
        if not take:
            return
            
        for note in take.selected_notes:
            new_value = random.randint(0, 127)
            retval, _, _, _, _, _, _, _ = RPR.MIDI_GetCC(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0)
            RPR.MIDI_SetCC(
                take.id, note.index,
                note.selected, note.muted,
                note.ppqpos, note.msg2, new_value,
                note.channel, note.msg, 0)
                
        RPR.MIDI_Sort(take.id)
        print(f"Randomized CC values for {len(take.selected_notes)} notes")

    def humanize_cc_values(self):
        take = self.get_active_take()
        if not take:
            return
            
        for note in take.selected_notes:
            retval, _, _, _, _, _, _, current_value = RPR.MIDI_GetCC(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0)
            variation = random.randint(-5, 5)
            new_value = min(max(current_value + variation, 0), 127)
            RPR.MIDI_SetCC(
                take.id, note.index,
                note.selected, note.muted,
                note.ppqpos, note.msg2, new_value,
                note.channel, note.msg, 0)
                
        RPR.MIDI_Sort(take.id)
        print(f"Humanized CC values for {len(take.selected_notes)} notes")

    def scale_cc_values(self, factor=1.2):
        take = self.get_active_take()
        if not take:
            return
            
        for note in take.selected_notes:
            retval, _, _, _, _, _, _, current_value = RPR.MIDI_GetCC(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0)
            new_value = min(max(int(current_value * factor), 0), 127)
            RPR.MIDI_SetCC(
                take.id, note.index,
                note.selected, note.muted,
                note.ppqpos, note.msg2, new_value,
                note.channel, note.msg, 0)
                
        RPR.MIDI_Sort(take.id)
        print(f"Scaled CC values by {factor}x for {len(take.selected_notes)} notes")

    def normalize_cc_values(self):
        take = self.get_active_take()
        if not take:
            return
            
        values = []
        for note in take.selected_notes:
            retval, _, _, _, _, _, _, current_value = RPR.MIDI_GetCC(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0)
            values.append(current_value)
            
        if not values:
            return
            
        median_value = statistics.median(values)
        for note in take.selected_notes:
            RPR.MIDI_SetCC(
                take.id, note.index,
                note.selected, note.muted,
                note.ppqpos, note.msg2, median_value,
                note.channel, note.msg, 0)
                
        RPR.MIDI_Sort(take.id)
        print(f"Normalized CC values to median {median_value} for {len(take.selected_notes)} notes")

def main():
    app = QApplication([])
    window = MidiCCSuite()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
