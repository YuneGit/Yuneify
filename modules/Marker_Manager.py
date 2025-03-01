import sys
import reapy
from reapy import reascript_api as RPR
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
                               QTableWidgetItem, QPushButton, QVBoxLayout,
                               QWidget, QHeaderView, QLabel, QHBoxLayout,
                               QSpinBox, QComboBox)
from PySide6.QtCore import Qt, QTimer
import time
import numpy as np

class MarkerAdjustWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project = reapy.Project()
        self.sorted_markers = []
        # Get initial time signature from project settings
        self.initial_num, self.initial_denom = self.get_project_time_signature()
        self.time_sig_beats = self.initial_num
        self.timer = QTimer()
        self.tap_times = []
        # Add debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(100)
        self.debounce_timer.timeout.connect(self.process_pending_changes)
        self.pending_changes = []
        self.init_ui()
        self.load_markers()
        
    def init_ui(self):
        self.setWindowTitle("Marker Beat Alignment")
        self.setGeometry(100, 100, 800, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Marker", "Time", "Measure", "Beat", "BPM", "Time Sig", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.viewport().installEventFilter(self)
        layout.addWidget(self.table)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Apply button
        self.apply_btn = QPushButton("Apply to REAPER")
        self.apply_btn.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_btn)
        
        # Undo button
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_changes)
        self.undo_btn.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.undo_btn)
        
        # Tap button
        self.tap_button = QPushButton("Tap Tempo")
        self.tap_button.clicked.connect(self.handle_tap_tempo)
        button_layout.addWidget(self.tap_button)
        
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
        
        # Set up refresh timer
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(2000)  # Check every 2 seconds
        
    def load_markers(self):
        # Use list comprehension for faster marker processing
        markers = sorted(self.project.markers, key=lambda m: m.position)
        marker_count = len(markers)
        self.apply_btn.setEnabled(marker_count >= 2)

        # Pre-allocate list size for better memory management
        self.sorted_markers = [None] * marker_count
        for idx, m in enumerate(markers):
            self.sorted_markers[idx] = {
                'time': m.position,
                'measure': idx + 1,
                'beat': 1.0,
                'bpm': 0.0,
                'numerator': 4,
                'denominator': 4
            }
        
        self.calculate_bpms()
        self.populate_table()
        self.undo_btn.setEnabled(self.project.can_undo)
        
    def populate_table(self):
        # Disable sorting during updates
        self.table.setSortingEnabled(False)
        self.table.blockSignals(True)
        
        row_count = len(self.sorted_markers)
        self.table.setRowCount(row_count)
        
        # Pre-create all items first
        for row, marker in enumerate(self.sorted_markers):
            # Create all items first
            items = [
                QTableWidgetItem(f"Marker {row + 1}"),
                self.create_time_item(marker['time']),
                QTableWidgetItem(str(marker['measure'])),
                QTableWidgetItem(f"{marker['beat']:.1f}"),
                self.create_bpm_item(marker['bpm'], row),
                QTableWidgetItem(str(marker['numerator'])),
                self.create_denominator_combo(marker['denominator'], row)
            ]
            
            for col, item in enumerate(items):
                if col == 6:
                    self.table.setCellWidget(row, col, item)
                else:
                    self.table.setItem(row, col, item)
        
        self.table.blockSignals(False)
        self.table.setSortingEnabled(True)
        
    def create_time_item(self, time_val):
        item = QTableWidgetItem(f"{time_val:.3f}")
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        return item

    def create_bpm_item(self, bpm, row):
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, f"{bpm:.2f}" if row > 0 and bpm > 0 else "N/A")
        return item

    def create_denominator_combo(self, denominator, row):
        combo = QComboBox()
        combo.addItems(["2", "4", "8", "16"])
        combo.setCurrentText(str(denominator))
        combo.currentTextChanged.connect(lambda text, r=row: self.handle_ts_change(r, text))
        return combo

    def get_total_beats(self, measure, beat, numerator):
        return ((measure - 1) * numerator) + beat
        
    def handle_cell_change(self, row, column):
        # Debounce rapid changes
        self.pending_changes.append((row, column))
        if not self.debounce_timer.isActive():
            self.debounce_timer.start()

    def process_pending_changes(self):
        # Process all queued changes at once
        unique_changes = set(self.pending_changes)
        self.pending_changes.clear()
        
        for row, column in unique_changes:
            if column in [2, 3]:  # Existing measure/beat handling
                try:
                    measure = int(self.table.item(row, 2).text())
                    beat = float(self.table.item(row, 3).text())
                    
                    if beat < 0.1 or beat > self.time_sig_beats + 0.99:
                        return
                        
                    if measure < 1:
                        return
                    
                    self.sorted_markers[row]['measure'] = measure
                    self.sorted_markers[row]['beat'] = beat
                    self.calculate_bpms()
                    self.update_bpm_display()
                    
                except ValueError:
                    pass
            elif column == 4 and row > 0:  # New BPM editing handling
                try:
                    new_bpm = float(self.table.item(row, 4).text())
                    prev_marker = self.sorted_markers[row-1]
                    current_marker = self.sorted_markers[row]
                    
                    time_diff = current_marker['time'] - prev_marker['time']
                    if time_diff <= 0:
                        return
                        
                    beat_diff = (new_bpm * time_diff) / 60
                    prev_total = self.get_total_beats(prev_marker['measure'], prev_marker['beat'], prev_marker['numerator'])
                    new_total = prev_total + beat_diff
                    
                    measure = int((new_total - 1) // self.time_sig_beats + 1)
                    beat = (new_total - 1) % self.time_sig_beats + 1
                    
                    self.sorted_markers[row]['measure'] = measure
                    self.sorted_markers[row]['beat'] = beat
                    self.sorted_markers[row]['bpm'] = new_bpm
                    
                    self.safe_cell_update(row, 2, measure)
                    self.safe_cell_update(row, 3, beat)
                    self.update_bpm_display()
                    
                except ValueError:
                    pass
            elif column in [5, 6]:  # Time signature columns
                try:
                    numerator = int(self.table.item(row, 5).text())
                    denominator = int(self.table.cellWidget(row, 6).currentText())
                    
                    if numerator < 1:
                        return
                    if denominator not in {2,4,8,16}:
                        return
                        
                    self.sorted_markers[row]['numerator'] = numerator
                    self.sorted_markers[row]['denominator'] = denominator
                    self.calculate_bpms()
                    self.update_bpm_display()
                    
                except ValueError:
                    pass

    def calculate_bpms(self):
        markers = self.sorted_markers
        if len(markers) < 2:
            return

        # Use NumPy arrays for vectorized calculations
        times = np.array([m['time'] for m in markers])
        numerators = np.array([m['numerator'] for m in markers])
        denominators = np.array([m['denominator'] for m in markers])
        measures = np.array([m['measure'] for m in markers])
        beats = np.array([m['beat'] for m in markers])

        time_diffs = times[1:] - times[:-1]
        total_beats_prev = (measures[:-1] - 1) * numerators[:-1] + beats[:-1]
        total_beats_curr = (measures[1:] - 1) * numerators[:-1] + beats[1:]
        beat_diffs = total_beats_curr - total_beats_prev
        
        denominator_factors = denominators[:-1] / 4.0
        beat_diff_quarters = beat_diffs * denominator_factors
        
        valid = (time_diffs > 0) & (beat_diff_quarters > 0)
        bpms = np.zeros_like(time_diffs)
        bpms[valid] = (beat_diff_quarters[valid] * 60) / time_diffs[valid]
        
        # Update BPM values in bulk
        for i in range(1, len(markers)):
            markers[i]['bpm'] = bpms[i-1]

    def update_bpm_display(self):
        for row in range(1, len(self.sorted_markers)):
            bpm = self.sorted_markers[row]['bpm']
            item = self.table.item(row, 4)
            item.setText(f"{bpm:.2f}" if bpm > 0 else "Invalid")
            
    def apply_changes(self):
        with reapy.undo_block('Adjust Marker Beat Alignment'):
            project_id = self.project.id
            
            # Batch delete tempo markers
            num_tempo = RPR.CountTempoTimeSigMarkers(project_id)
            for i in reversed(range(num_tempo)):
                RPR.DeleteTempoTimeSigMarker(project_id, i)
            
            # Batch delete regular markers
            for marker in self.project.markers:
                marker.delete()
            
            # Batch create new tempo markers
            valid_markers = [
                (prev, current) for prev, current in 
                zip(self.sorted_markers[:-1], self.sorted_markers[1:])
                if current['bpm'] > 0
            ]
            
            for prev, current in valid_markers:
                total_beats = ((prev['measure'] - 1) * prev['numerator']) + prev['beat']
                RPR.SetTempoTimeSigMarker(
                    project_id, -1,
                    prev['time'],
                    -1,
                    total_beats,
                    current['bpm'],
                    prev['numerator'], prev['denominator'],
                    current.get('linear', False)
                )
            
            # Batch recreate markers
            add_marker = self.project.add_marker
            for marker in self.sorted_markers:
                add_marker(marker['time'])
        
        self.info_label.setText("Changes applied successfully!")
        self.undo_btn.setEnabled(self.project.can_undo)
        
    def undo_changes(self):
        if self.project.can_undo:
            self.project.undo()
            self.info_label.setText("Changes undone")
            self.load_markers()  # Reload markers to reflect the undo
            self.undo_btn.setEnabled(self.project.can_undo)

    def eventFilter(self, source, event):
        """Handle mouse wheel events on editable columns"""
        if event.type() == event.Type.Wheel and source is self.table.viewport():
            pos = event.position()
            index = self.table.indexAt(pos.toPoint())
            if index.isValid() and index.column() in [2, 3, 4]:
                self.handle_wheel_adjustment(index, event)
                return True
        return super().eventFilter(source, event)

    def handle_wheel_adjustment(self, index, event):
        """Route wheel adjustments to appropriate handler"""
        row, col = index.row(), index.column()
        if col == 4 and row > 0:
            self.adjust_bpm(row, event)
        elif col in [2, 3]:
            self.adjust_measure_beat(row, col, event)

    def adjust_measure_beat(self, row, col, event):
        """Handle measure/beat adjustments with wheel"""
        try:
            item = self.table.item(row, col)
            current = float(item.text())
            step = self.get_step_size(col, event.modifiers())
            
            new_value = current + (1 if event.angleDelta().y() > 0 else -1) * step
            new_value = self.clamp_value(col, new_value)
            
            self.safe_cell_update(row, col, new_value)
            self.handle_cell_change(row, col)
            
        except ValueError:
            pass

    def adjust_bpm(self, row, event):
        """Adjust BPM through measure/beat relationship"""
        prev_marker = self.sorted_markers[row-1]
        current_marker = self.sorted_markers[row]
        
        if (time_diff := current_marker['time'] - prev_marker['time']) <= 0:
            return

        step = 0.1 if event.modifiers() & Qt.ShiftModifier else 1.0
        current_bpm = current_marker['bpm'] + (step if event.angleDelta().y() > 0 else -step)
        
        # Update the BPM cell directly instead of through measure/beat
        self.safe_cell_update(row, 4, current_bpm)
        self.handle_cell_change(row, 4)  # Trigger the new BPM handling

    # Helper methods
    def get_step_size(self, column, modifiers):
        return 0.1 if (column == 3 and modifiers & Qt.ShiftModifier) else 1.0

    def clamp_value(self, column, value):
        if column == 2: return max(1, int(value))
        if column == 3: return max(0.1, min(self.time_sig_beats + 0.99, value))
        return value

    def safe_cell_update(self, row, col, value):
        """Update cell value without triggering signals"""
        with reapy.prevent_ui_refresh():
            self.table.blockSignals(True)
            item = self.table.item(row, col)
            fmt = ".1f" if col == 3 else ".0f" if col == 2 else ""
            item.setText(f"{value:{fmt}}".rstrip('0').rstrip('.') if fmt else str(value))
            self.table.blockSignals(False)

    def check_for_updates(self):
        """Check for external marker changes and refresh UI"""
        current_markers = sorted(self.project.markers, key=lambda m: m.position)
        current_positions = [m.position for m in current_markers]
        stored_positions = [m['time'] for m in self.sorted_markers]
        
        if current_positions != stored_positions:
            self.load_markers()
            self.info_label.setText("Detected marker changes - UI updated")

    def closeEvent(self, event):
        """Stop timer when window closes"""
        self.timer.stop()
        super().closeEvent(event)

    def handle_tap_tempo(self):
        now = time.time()
        if len(self.tap_times) > 0 and (now - self.tap_times[-1] > 2):
            self.tap_times = []
        self.tap_times.append(now)
        if len(self.tap_times) > 1:
            avg_bpm = 60 / (np.mean(np.diff(self.tap_times)))
            self.apply_tapped_bpm(avg_bpm)

    def apply_tapped_bpm(self, bpm):
        current_row = self.table.currentRow()
        if current_row > 0:
            self.safe_cell_update(current_row, 4, round(bpm, 1))
            self.handle_cell_change(current_row, 4)

    def handle_ts_change(self, row, denominator):
        """Handle time signature denominator changes"""
        try:
            denominator = int(denominator)
            numerator = int(self.table.item(row, 5).text())
            
            if numerator < 1:
                return
            if denominator not in {2,4,8,16}:
                return
                
            self.sorted_markers[row]['numerator'] = numerator
            self.sorted_markers[row]['denominator'] = denominator
            self.calculate_bpms()
            self.update_bpm_display()
            
        except ValueError:
            pass

    def get_project_time_signature(self):
        """Get both numerator and denominator from project settings"""
        ts = self.project.time_signature  # Returns tuple (bpm, bpi)
        return ts[1], 4  # ts[1] is the BPI (numerator)

def show_ui():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MarkerAdjustWindow()
    window.show()
    app.exec()

# Remove this auto-run call
# show_ui()