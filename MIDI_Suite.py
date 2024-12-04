import sys
import reapy
import time
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSpinBox, QLabel, QComboBox, QGridLayout
from PyQt5.QtCore import Qt
from reapy import reascript_api as RPR
import statistics

class MidiSuite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI Suite")
        self.setGeometry(100, 100, 275, 275)
        self.setFixedWidth(275)

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
                margin: 0px;
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
        
        # Initialize the main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        
        # Main vertical layout
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Add a label at the top
        self.title_label = QLabel("MIDI Suite", self)
        self.title_label.setAlignment(Qt.AlignCenter)  # Center the label text
        self.main_layout.addWidget(self.title_label)
        
        # Grid layout for buttons
        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)
        
        # Add controls for velocity adjustment
        self.add_velocity_controls()
        
        # Add controls for pitch transposition
        self.add_transpose_controls()
        
        # Add controls for randomizing MIDI velocities
        self.add_randomize_controls()
        
        # Add controls for quantizing MIDI notes
        self.add_quantize_controls()

        # Add controls for humanizing MIDI timing
        self.add_humanize_controls()

        # Add controls for scaling MIDI velocities
        self.add_scale_controls()

        # Add controls for normalizing MIDI velocities
        self.add_normalize_controls()

        # Add controls for inverting MIDI pitch
        self.add_invert_pitch_controls()

        # Add controls for legato feature
        self.add_legato_controls()

        # Initialize MIDI operation classes
        self.init_midi_operations()

    def add_velocity_controls(self):
        self.velocity_spinbox = QSpinBox(self)
        self.velocity_spinbox.setRange(-127, 127)
        self.velocity_spinbox.setValue(10)  # Default value
        self.grid_layout.addWidget(self.velocity_spinbox, 0, 0)
        
        self.velocity_button = QPushButton("Adjust Velocities", self)
        self.velocity_button.clicked.connect(self.adjust_velocities)
        self.grid_layout.addWidget(self.velocity_button, 0, 1)

    def add_transpose_controls(self):
        self.transpose_combobox = QComboBox(self)
        self.transpose_combobox.addItems(["Octave", "Major Third", "Minor Third", "Perfect Fifth"])
        self.grid_layout.addWidget(self.transpose_combobox, 1, 0)
        
        self.transpose_button = QPushButton("Transpose Notes", self)
        self.transpose_button.clicked.connect(self.transpose_notes)
        self.grid_layout.addWidget(self.transpose_button, 1, 1)

    def add_randomize_controls(self):
        self.randomize_velocity_button = QPushButton("Randomize Velocities", self)
        self.randomize_velocity_button.clicked.connect(self.randomize_velocities)
        self.grid_layout.addWidget(self.randomize_velocity_button, 2, 0)

    def add_quantize_controls(self):
        self.quantize_button = QPushButton("Quantize Notes", self)
        self.quantize_button.clicked.connect(self.quantize_notes)
        self.grid_layout.addWidget(self.quantize_button, 2, 1)

    def add_humanize_controls(self):
        self.humanize_button = QPushButton("Humanize Timing", self)
        self.humanize_button.clicked.connect(self.humanize_timing)
        self.grid_layout.addWidget(self.humanize_button, 3, 0)

    def add_scale_controls(self):
        self.scale_velocity_button = QPushButton("Scale Velocities", self)
        self.scale_velocity_button.clicked.connect(self.scale_velocities)
        self.grid_layout.addWidget(self.scale_velocity_button, 3, 1)

    def add_normalize_controls(self):
        self.normalize_velocity_button = QPushButton("Normalize Velocities", self)
        self.normalize_velocity_button.clicked.connect(self.normalize_velocities)
        self.grid_layout.addWidget(self.normalize_velocity_button, 4, 0)

    def add_invert_pitch_controls(self):
        self.invert_pitch_button = QPushButton("Invert Pitch", self)
        self.invert_pitch_button.clicked.connect(self.invert_pitch)
        self.grid_layout.addWidget(self.invert_pitch_button, 4, 1)

    def add_legato_controls(self):
        self.legato_button = QPushButton("Make Legato", self)
        self.legato_button.clicked.connect(self.make_legato)
        self.grid_layout.addWidget(self.legato_button, 5, 0)

    def init_midi_operations(self):
        self.velocity_adjuster = MidiVelocityAdjuster()
        self.pitch_transposer = MidiPitchTransposer()
        self.velocity_randomizer = MidiVelocityRandomizer()
        self.note_quantizer = MidiNoteQuantizer()
        self.timing_humanizer = MidiTimingHumanizer()
        self.velocity_scaler = MidiVelocityScaler()
        self.velocity_normalizer = MidiVelocityNormalizer()
        self.pitch_inverter = MidiPitchInverter()
        self.legato_maker = MidiLegatoMaker()

    def adjust_velocities(self):
        """Adjust MIDI velocities using MidiVelocityAdjuster."""
        velocity_change = self.velocity_spinbox.value()
        self.velocity_adjuster.run(velocity_change)
        print("Velocities adjusted.")

    def transpose_notes(self):
        """Transpose MIDI notes by selected interval using MidiPitchTransposer."""
        interval_map = {
            "Octave": 12,
            "Major Third": 4,
            "Minor Third": 3,
            "Perfect Fifth": 7
        }
        interval = interval_map[self.transpose_combobox.currentText()]
        self.pitch_transposer.run(interval)
        print(f"Notes transposed by {interval} semitones.")

    def randomize_velocities(self):
        """Randomize MIDI velocities within a specified range."""
        self.velocity_randomizer.run()
        print("Velocities randomized.")

    def quantize_notes(self):
        """Quantize MIDI notes to the nearest grid line."""
        self.note_quantizer.run()
        print("Notes quantized.")

    def humanize_timing(self):
        """Add slight random variations to MIDI note start times."""
        self.timing_humanizer.run()
        print("Timing humanized.")

    def scale_velocities(self):
        """Scale MIDI velocities by a given factor."""
        self.velocity_scaler.run()
        print("Velocities scaled.")

    def normalize_velocities(self):
        """Normalize MIDI velocities to the median value."""
        self.velocity_normalizer.run()
        print("Velocities normalized to median.")

    def invert_pitch(self):
        """Invert the pitch of MIDI notes around a central pitch."""
        self.pitch_inverter.run()
        print("Pitch inverted.")

    def make_legato(self):
        """Make MIDI notes legato by overlapping them slightly."""
        self.legato_maker.run()
        print("Notes made legato.")

class MidiOperationBase:
    def __init__(self):
        with reapy.inside_reaper():
            self.project = reapy.Project()

    def get_active_take(self):
        with reapy.inside_reaper():
            item = self.project.get_selected_item(0)
            if not item:
                print("No selected item.")
                return None

            take = item.active_take
            if not take:
                print("No active take.")
                return None

            return take

class MidiVelocityAdjuster(MidiOperationBase):
    def run(self, velocity_change):
        self.select_all_midi_items()
        self.adjust_midi_velocities(velocity_change)

    def select_all_midi_items(self):
        RPR.Main_OnCommand(RPR.NamedCommandLookup("_BR_SEL_ALL_ITEMS_MIDI"), 0)
        print("Selected all MIDI items.")

    def adjust_midi_velocities(self, velocity_change):
        selected_items = self.project.selected_items
        for item in selected_items:
            self._process_item(item, velocity_change)

    def _process_item(self, item, velocity_change):
        for take in item.takes:
            if take.is_midi:
                self._adjust_take_velocities(take, velocity_change)

    def _adjust_take_velocities(self, take, velocity_change):
        notes = take.notes
        for note in notes:
            self._adjust_note_velocity(note, take, velocity_change)
        RPR.MIDI_Sort(take.id)
        print(f"Sorted MIDI events for take ID: {take.id}.")

    def _adjust_note_velocity(self, note, take, velocity_change):
        new_velocity = min(max(note.velocity + velocity_change, 0), 127)
        retval, *other_values = RPR.MIDI_GetNote(
            take.id, note.index, 0, 0, 0, 0, 0, 0, 0
        )
        muted, start, end, channel, original_pitch, _ = other_values[-6:]
        RPR.MIDI_SetNote(
            take.id,
            note.index,
            note.selected,
            muted,
            start,
            end,
            channel,
            note.pitch,
            new_velocity,
            False
        )
        print(f"Updated note (Pitch: {note.pitch}) to new velocity: {new_velocity}.")

class MidiPitchTransposer(MidiOperationBase):
    def run(self, interval):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Transposing {len(notes)} notes by {interval} semitones.")
        self.transpose_midi_notes(take, notes, interval)

    def transpose_midi_notes(self, take, notes, interval):
        note_infos = [note.infos for note in notes]

        # Start a transaction
        RPR.Undo_BeginBlock2(take.id)

        # Remove original notes
        for note in notes:
            RPR.MIDI_DeleteNote(
                take.id,
                note.index
            )

        # Add transposed notes
        for note_info in note_infos:
            start_ppq = take.time_to_ppq(note_info["start"])
            end_ppq = take.time_to_ppq(note_info["end"])
            new_pitch = note_info["pitch"] + interval
            take.add_note(
                start=start_ppq,
                end=end_ppq,
                pitch=new_pitch,
                velocity=note_info["velocity"],
                channel=note_info["channel"],
                selected=note_info["selected"],
                muted=note_info["muted"],
                unit="ppq",
                sort=True
            )

        # End the transaction
        RPR.Undo_EndBlock2(take.id, "Transpose MIDI Notes", -1)
        print("MIDI notes transposed.")

class MidiVelocityRandomizer(MidiOperationBase):
    def run(self):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Randomizing velocities for {len(notes)} notes.")
        self.randomize_midi_velocities(take, notes)

    def randomize_midi_velocities(self, take, notes):
        for note in notes:
            new_velocity = random.randint(0, 127)
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0
            )
            muted, start, end, channel, original_pitch, _ = other_values[-6:]
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                muted,
                start,
                end,
                channel,
                note.pitch,
                new_velocity,
                False
            )
            print(f"Updated note (Pitch: {note.pitch}) to new velocity: {new_velocity}.")

class MidiNoteQuantizer(MidiOperationBase):
    def run(self):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Quantizing {len(notes)} notes.")
        self.quantize_midi_notes(take, notes)

    def quantize_midi_notes(self, take, notes):
        for note in notes:
            start_ppq = take.time_to_ppq(note.start)
            quantized_start_ppq = round(start_ppq / 120) * 120  # Example quantization to nearest 1/8 note
            end_ppq = take.time_to_ppq(note.end)
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                note.muted,
                quantized_start_ppq,
                end_ppq,
                note.channel,
                note.pitch,
                note.velocity,
                False
            )
            print(f"Quantized note (Pitch: {note.pitch}) to start at PPQ: {quantized_start_ppq}.")

class MidiTimingHumanizer(MidiOperationBase):
    def run(self):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Humanizing timing for {len(notes)} notes.")
        self.humanize_midi_timing(take, notes)

    def humanize_midi_timing(self, take, notes):
        for note in notes:
            start_ppq = take.time_to_ppq(note.start)
            humanized_start_ppq = start_ppq + random.randint(-10, 10)  # Random shift within 10 PPQ
            end_ppq = take.time_to_ppq(note.end)
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                note.muted,
                humanized_start_ppq,
                end_ppq,
                note.channel,
                note.pitch,
                note.velocity,
                False
            )
            print(f"Humanized note (Pitch: {note.pitch}) to start at PPQ: {humanized_start_ppq}.")

class MidiVelocityScaler(MidiOperationBase):
    def run(self):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Scaling velocities for {len(notes)} notes.")
        self.scale_midi_velocities(take, notes)

    def scale_midi_velocities(self, take, notes):
        scale_factor = 1.2  # Example scale factor
        for note in notes:
            new_velocity = min(max(int(note.velocity * scale_factor), 0), 127)
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0
            )
            muted, start, end, channel, original_pitch, _ = other_values[-6:]
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                muted,
                start,
                end,
                channel,
                note.pitch,
                new_velocity,
                False
            )
            print(f"Scaled note (Pitch: {note.pitch}) to new velocity: {new_velocity}.")

class MidiVelocityNormalizer(MidiOperationBase):
    def run(self):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Normalizing velocities for {len(notes)} notes.")
        self.normalize_midi_velocities(take, notes)

    def normalize_midi_velocities(self, take, notes):
        velocities = [note.velocity for note in notes]
        median_velocity = statistics.median(velocities)
        for note in notes:
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0
            )
            muted, start, end, channel, original_pitch, _ = other_values[-6:]
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                muted,
                int(start),  # Ensure start is an integer
                int(end),    # Ensure end is an integer
                channel,
                note.pitch,
                int(median_velocity),  # Ensure velocity is an integer
                False
            )
            print(f"Normalized note (Pitch: {note.pitch}) to median velocity: {median_velocity}.")

class MidiPitchInverter(MidiOperationBase):
    def run(self):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Inverting pitch for {len(notes)} notes.")
        self.invert_midi_pitch(take, notes)

    def invert_midi_pitch(self, take, notes):
        central_pitch = 60  # Example central pitch (Middle C)
        for note in notes:
            inverted_pitch = central_pitch - (note.pitch - central_pitch)
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0
            )
            muted, start, end, channel, original_pitch, _ = other_values[-6:]
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                muted,
                start,
                end,
                channel,
                inverted_pitch,
                note.velocity,
                False
            )
            print(f"Inverted note (Original Pitch: {note.pitch}) to pitch: {inverted_pitch}.")

class MidiLegatoMaker(MidiOperationBase):
    def run(self):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        # Filter only selected notes
        selected_notes = [note for note in notes if note.selected]
        print(f"Making {len(selected_notes)} selected notes legato.")
        self.make_midi_legato(take, selected_notes)

    def make_midi_legato(self, take, notes):
        for i in range(len(notes) - 1):
            current_note = notes[i]
            next_note = notes[i + 1]
            new_end = take.time_to_ppq(next_note.start) - 10  # Overlap by 10 PPQ
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, current_note.index, 0, 0, 0, 0, 0, 0, 0
            )
            muted, start, end, channel, original_pitch, _ = other_values[-6:]
            RPR.MIDI_SetNote(
                take.id,
                current_note.index,
                current_note.selected,
                muted,
                start,
                new_end,
                channel,
                current_note.pitch,
                current_note.velocity,
                False
            )
            print(f"Adjusted note (Pitch: {current_note.pitch}) to end at PPQ: {new_end}.")

def main():
    app = QApplication(sys.argv)
    window = MidiSuite()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 