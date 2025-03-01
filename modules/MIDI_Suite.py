import sys
import reapy
import time
import random
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSpinBox, QLabel, QComboBox, QGridLayout, QGroupBox, QScrollArea
from PySide6.QtCore import Qt, QTimer
from reapy import reascript_api as RPR
import statistics
from modules.styles import apply_dark_theme  # Import the stylesheet function


class MidiSuite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI Suite")
        self.setGeometry(100, 100, 400, 500)  # Increased window size
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
        
        # Add group boxes in a more organized way
        self.add_velocity_controls()
        self.add_transpose_controls()
        self.add_quick_tools()
        self.add_advanced_tools()
        
        # Initialize MIDI operation classes
        self.init_midi_operations()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._process_operations)
        self._pending_operations = []

    def add_velocity_controls(self):
        # Create a group box for velocity controls
        velocity_group = QGroupBox("Velocity Controls")
        velocity_layout = QGridLayout()
        
        # Add velocity adjustment controls
        self.velocity_label = QLabel("Adjustment Amount:", self)
        velocity_layout.addWidget(self.velocity_label, 0, 0)
        
        self.velocity_spinbox = QSpinBox(self)
        self.velocity_spinbox.setRange(-127, 127)
        self.velocity_spinbox.setValue(10)
        velocity_layout.addWidget(self.velocity_spinbox, 0, 1)
        
        # Add velocity range controls
        self.min_velocity_label = QLabel("Min Velocity:", self)
        velocity_layout.addWidget(self.min_velocity_label, 1, 0)
        
        self.min_velocity_spinbox = QSpinBox(self)
        self.min_velocity_spinbox.setRange(0, 127)
        self.min_velocity_spinbox.setValue(0)
        velocity_layout.addWidget(self.min_velocity_spinbox, 1, 1)
        
        self.max_velocity_label = QLabel("Max Velocity:", self)
        velocity_layout.addWidget(self.max_velocity_label, 2, 0)
        
        self.max_velocity_spinbox = QSpinBox(self)
        self.max_velocity_spinbox.setRange(0, 127)
        self.max_velocity_spinbox.setValue(127)
        velocity_layout.addWidget(self.max_velocity_spinbox, 2, 1)
        
        # Add apply button
        self.velocity_button = QPushButton("Adjust Velocities", self)
        self.velocity_button.clicked.connect(self.adjust_velocities)
        velocity_layout.addWidget(self.velocity_button, 3, 0, 1, 2)
        
        velocity_group.setLayout(velocity_layout)
        self.main_layout.addWidget(velocity_group)

    def add_transpose_controls(self):
        group = QGroupBox("Transposition")
        layout = QGridLayout()
        
        self.transpose_combobox = QComboBox()
        self.transpose_combobox.addItems(["Octave", "Major Third", "Minor Third", "Perfect Fifth"])
        layout.addWidget(self.transpose_combobox, 0, 0)
        
        transpose_btn = QPushButton("Transpose", clicked=self.transpose_notes)
        layout.addWidget(transpose_btn, 0, 1)
        
        group.setLayout(layout)
        self.main_layout.addWidget(group)

    def add_quick_tools(self):
        group = QGroupBox("Quick Tools")
        layout = QGridLayout()
        
        # First row
        layout.addWidget(QPushButton("Randomize", clicked=self.randomize_velocities), 0, 0)
        layout.addWidget(QPushButton("Quantize", clicked=self.quantize_notes), 0, 1)
        
        # Second row
        humanize_group = QGroupBox("Humanize")
        humanize_layout = QGridLayout()
        
        self.timing_amount = QSpinBox()
        self.timing_amount.setRange(0, 100)
        self.timing_amount.setValue(10)
        self.timing_amount.setSuffix(" ticks")
        humanize_layout.addWidget(QLabel("Timing:"), 0, 0)
        humanize_layout.addWidget(self.timing_amount, 0, 1)
        
        self.velocity_amount = QSpinBox()
        self.velocity_amount.setRange(0, 127)
        self.velocity_amount.setValue(10)
        humanize_layout.addWidget(QLabel("Velocity:"), 1, 0)
        humanize_layout.addWidget(self.velocity_amount, 1, 1)
        
        humanize_btn = QPushButton("Apply", clicked=self.humanize)
        humanize_layout.addWidget(humanize_btn, 2, 0, 1, 2)
        
        humanize_group.setLayout(humanize_layout)
        layout.addWidget(humanize_group, 1, 0, 1, 2)
        
        # Third row
        layout.addWidget(QPushButton("Normalize", clicked=self.normalize_velocities), 2, 0)
        layout.addWidget(QPushButton("Legato", clicked=self.make_legato), 2, 1)
        
        # Fourth row
        layout.addWidget(QPushButton("Reverse", clicked=self.reverse_notes), 3, 0)
        
        group.setLayout(layout)
        self.main_layout.addWidget(group)

    def add_advanced_tools(self):
        group = QGroupBox("Advanced Tools")
        layout = QGridLayout()
        
        # Chord generation controls
        self.chord_type = QComboBox()
        self.chord_type.addItems(["Major", "Minor", "7th", "Maj7", "Min7", "Sus2", "Sus4", "Dim", "Aug"])
        layout.addWidget(QLabel("Chord Type:"), 0, 0)
        layout.addWidget(self.chord_type, 0, 1)
        
        layout.addWidget(QPushButton("Compress", clicked=self.compress_velocities), 1, 0)
        layout.addWidget(QPushButton("Invert Pitch", clicked=self.invert_pitch), 1, 1)
        layout.addWidget(QPushButton("Generate Chords", clicked=self.generate_chords), 2, 0)
        
        group.setLayout(layout)
        self.main_layout.addWidget(group)


    def init_midi_operations(self):
        self.velocity_adjuster = MidiVelocityAdjuster()
        self.pitch_transposer = MidiPitchTransposer()
        self.velocity_randomizer = MidiVelocityRandomizer()
        self.note_quantizer = MidiNoteQuantizer()
        self.timing_humanizer = MidiTimingHumanizer()
        self.velocity_scaler = MidiVelocityScaler()
        self.velocity_normalizer = MidiVelocityNormalizer()
        self.velocity_compressor = MidiVelocityCompressor()
        self.pitch_inverter = MidiPitchInverter()
        self.legato_maker = MidiLegatoMaker()
        self.chord_generator = MidiChordGenerator()

    def adjust_velocities(self):
        """Adjust MIDI velocities using MidiVelocityAdjuster."""
        velocity_change = self.velocity_spinbox.value()
        self.velocity_adjuster.run(velocity_change)
        print(f"Velocities adjusted by {velocity_change}")

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

    def humanize(self):
        """Humanize MIDI timing and velocities"""
        timing_amount = self.timing_amount.value()
        velocity_amount = self.velocity_amount.value()
        self.timing_humanizer.run(timing_amount, velocity_amount)
        print(f"Humanized timing by ±{timing_amount} ticks and velocity by ±{velocity_amount}")

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

    def compress_velocities(self):
        """Compress MIDI velocities using threshold and ratio."""
        threshold = 64  # Example threshold value
        ratio = 2.0     # Example compression ratio
        self.velocity_compressor.run(threshold, ratio)
        print(f"Velocities compressed with {ratio}:1 ratio above {threshold}")

    def reverse_notes(self):
        """Reverse the order of MIDI notes in time."""
        self.note_reverser.run()
        print("MIDI notes reversed")

    def generate_chords(self):
        """Generate chords from selected notes"""
        chord_type = self.chord_type.currentText()
        self.chord_generator.run(chord_type)
        print(f"Generated {chord_type} chords from selected notes")


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
    def run(self, timing_amount, velocity_amount):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Humanizing timing and velocity for {len(notes)} notes.")
        self.humanize_midi(take, notes, timing_amount, velocity_amount)

    def humanize_midi(self, take, notes, timing_amount, velocity_amount):
        for note in notes:
            # Humanize timing
            start_ppq = take.time_to_ppq(note.start)
            timing_variation = random.randint(-timing_amount, timing_amount)
            humanized_start_ppq = start_ppq + timing_variation
            
            # Humanize velocity
            velocity_variation = random.randint(-velocity_amount, velocity_amount)
            new_velocity = min(max(note.velocity + velocity_variation, 0), 127)
            
            # Apply changes
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                note.muted,
                humanized_start_ppq,
                take.time_to_ppq(note.end),
                note.channel,
                note.pitch,
                new_velocity,
                False
            )
            print(f"Humanized note (Pitch: {note.pitch}) - Timing: ±{timing_amount}, Velocity: {new_velocity}")

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

class MidiVelocityCompressor(MidiOperationBase):
    def run(self, threshold, ratio):
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Compressing velocities for {len(notes)} notes with threshold {threshold} and ratio {ratio}:1.")
        self.compress_midi_velocities(take, notes, threshold, ratio)

    def compress_midi_velocities(self, take, notes, threshold, ratio):
        for note in notes:
            if note.velocity > threshold:
                # Calculate compressed velocity
                excess = note.velocity - threshold
                compressed_excess = excess / ratio
                new_velocity = threshold + compressed_excess
                
                # Clamp to valid range
                new_velocity = min(max(int(new_velocity), 0), 127)
                
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
                print(f"Compressed note (Pitch: {note.pitch}) from {note.velocity} to {new_velocity}.")

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



class MidiChordGenerator(MidiOperationBase):
    def run(self):
        take = self.get_active_take()
        if not take:
            return

        notes = [note for note in take.notes if note.selected]
        if not notes:
            print("No selected notes to generate chords from")
            return

        print(f"Generating chords for {len(notes)} selected notes")
        self.generate_midi_chords(take, notes)

    def generate_midi_chords(self, take, notes, chord_type):
        RPR.Undo_BeginBlock2(take.id, "Generate Chords", -1)
        
        # Define chord intervals for each type
        chord_intervals = {
            "Major": [4, 7],
            "Minor": [3, 7],
            "7th": [4, 7, 10],
            "Maj7": [4, 7, 11],
            "Min7": [3, 7, 10],
            "Sus2": [2, 7],
            "Sus4": [5, 7],
            "Dim": [3, 6],
            "Aug": [4, 8]
        }
        
        intervals = chord_intervals.get(chord_type, [4, 7])  # Default to major if invalid
        
        for note in notes:
            for interval in intervals:
                take.add_note(
                    start=take.time_to_ppq(note.start),
                    end=take.time_to_ppq(note.end),
                    pitch=note.pitch + interval,
                    velocity=note.velocity,
                    channel=note.channel,
                    selected=False,
                    muted=note.muted,
                    unit="ppq",
                    sort=False
                )
        
        RPR.MIDI_Sort(take.id)
        RPR.Undo_EndBlock2(take.id, "Generate Chords", -1)

def main():
    app = QApplication([])
    window = MidiSuite()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
