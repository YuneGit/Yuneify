from PySide6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont
import reapy
from reapy import reascript_api as RPR
from modules.styles import apply_dark_theme
from reapy.core.reaper.midi import get_active_editor as get_active_midi_editor
import statistics

class ContextToolsWindow(QWidget):
    """Context-sensitive tools window that follows mouse position"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Context Tools")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(200, 150)
        apply_dark_theme(self)
        
        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Tool buttons
        self.velocity_tools = QPushButton("Velocity Tools")
        self.cc_tools = QPushButton("CC Tools")
        self.quantize_btn = QPushButton("Quantize")
        self.humanize_btn = QPushButton("Humanize")
        
        layout.addWidget(self.velocity_tools)
        layout.addWidget(self.cc_tools)
        layout.addWidget(self.quantize_btn)
        layout.addWidget(self.humanize_btn)
        
        # Position tracking
        self.position_timer = QTimer(self)
        self.position_timer.timeout.connect(self.check_selection)
        self.position_timer.start(100)
        
    def follow_mouse(self):
        """Smart positioning relative to MIDI editor or selection"""
        try:
            # First try to position relative to MIDI editor
            editor = get_active_midi_editor()
            if editor:
                # Get MIDI editor window position
                _, editor_x, editor_y, editor_w, editor_h = RPR.JS_Window_GetRect(editor.get_hwnd())
                
                # Position at right side of MIDI editor
                new_x = editor_x + editor_w + 10
                new_y = editor_y + 40  # Below toolbar
                self.move(new_x, new_y)
                return
                
            # If no editor, try to find selected media item
            item = reapy.get_selected_item()
            if item:
                # Get item position in arrange view
                item_pos = item.position
                _, arrange_x, arrange_y, _, _ = RPR.JS_Window_GetRect(RPR.GetMainHwnd())
                
                # Convert item position to screen coordinates
                screen_x = arrange_x + item_pos * 100  # Simplified, would need pixel_per_second
                screen_y = arrange_y + 100  # Rough position below track
                
                self.move(int(screen_x), int(screen_y))
                return
                
        except Exception as e:
            print(f"Positioning error: {e}")

        # Fallback to mouse position if no MIDI editor/item found
        mouse_pos = self.parent().mapFromGlobal(QPoint())
        self.move(mouse_pos.x() + 20, mouse_pos.y() + 20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(30, 30, 30, 200)))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawRoundedRect(self.rect(), 8, 8)
        
    def __init__(self, parent=None):
        super().__init__(parent)
        # Add position cache variables
        self.last_editor_id = None
        self.last_scroll_pos = (0, 0)
        self.last_zoom = 0
        self.position_history = QPoint(0, 0)
        
    def check_selection(self):
        try:
            editor = get_active_midi_editor()
            if not editor:
                return
                
            # Cache editor state if changed
            if editor.id != self.last_editor_id:
                self.last_editor_id = editor.id
                self.last_scroll_pos = (
                    RPR.MIDIEditor_GetSetting_int(editor.id, "scroll_x"),
                    RPR.MIDIEditor_GetSetting_int(editor.id, "scroll_y")
                )
                self.last_zoom = RPR.MIDIEditor_GetSetting_int(editor.id, "zoom")
                
            take = editor.take
            if not take:
                return
                
            # Batch get all selected events
            selected_notes = take.get_selected_notes()
            selected_cc = take.get_selected_cc()
            
            if selected_notes:
                # Calculate using numpy for speed
                avg_pos = statistics.mean(n.start for n in selected_notes)
                avg_pitch = statistics.mean(n.pitch for n in selected_notes)
                
                # Convert using cached scroll/zoom
                x = int((avg_pos - self.last_scroll_pos[0]) * self.last_zoom)
                y = int((127 - avg_pitch - self.last_scroll_pos[1]) * self.last_zoom)
                
                new_pos = QPoint(
                    self.parent().x() + x + 50,
                    self.parent().y() + y
                )
                
            elif selected_cc:
                first_cc = selected_cc[0]
                x = int((first_cc.position - self.last_scroll_pos[0]) * self.last_zoom)
                y = int((127 - first_cc.value - self.last_scroll_pos[1]) * self.last_zoom)
                
                new_pos = QPoint(
                    self.parent().x() + x + 50,
                    self.parent().y() + y
                )
                
            else:
                return
                
            # Animate position changes smoothly
            if new_pos != self.position_history:
                anim = QPropertyAnimation(self, b"pos")
                anim.setDuration(100)
                anim.setStartValue(self.pos())
                anim.setEndValue(new_pos)
                anim.setEasingCurve(QEasingCurve.OutQuad)
                anim.start()
                self.position_history = new_pos
                
        except Exception as e:
            print(f"Positioning error: {e}")
            
    def update_tools(self, selection_type):
        if selection_type == self.last_selection_type:
            return
            
        # Clear existing tools
        while self.tools_layout.count():
            item = self.tools_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        # Add new tools based on selection
        if selection_type == "notes":
            self.add_note_tools()
        elif selection_type == "cc":
            self.add_cc_tools()
            
        self.last_selection_type = selection_type
        
    def add_note_tools(self):
        octave_btn = QPushButton("Octave +")
        octave_btn.clicked.connect(self.transpose_octave_up)
        self.tools_layout.addWidget(octave_btn)
        
        octave_btn = QPushButton("Octave -")
        octave_btn.clicked.connect(self.transpose_octave_down)
        self.tools_layout.addWidget(octave_btn)
        
    def add_cc_tools(self):
        inc_btn = QPushButton("CC +5")
        inc_btn.clicked.connect(lambda: self.adjust_cc_values(5))
        self.tools_layout.addWidget(inc_btn)
        
        dec_btn = QPushButton("CC -5")
        dec_btn.clicked.connect(lambda: self.adjust_cc_values(-5))
        self.tools_layout.addWidget(dec_btn)
        
    def transpose_octave_up(self):
        self.transpose_notes(12)
        
    def transpose_octave_down(self):
        self.transpose_notes(-12)
        
    def transpose_notes(self, semitones):
        try:
            editor = get_active_midi_editor()
            if editor:
                take = editor.take
                if take:
                    take.transpose_notes(semitones)
                    RPR.UpdateArrange()
        except Exception as e:
            print(f"Transpose error: {e}")
            
    def adjust_cc_values(self, delta):
        try:
            editor = get_active_midi_editor()
            if editor:
                take = editor.take
                if take and take.is_midi:
                    for cc in take.cc_events:
                        if cc.selected:
                            cc.value = max(0, min(127, cc.value + delta))
                    RPR.UpdateArrange()
        except Exception as e:
            print(f"CC adjust error: {e}")
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)
            
    def mouseReleaseEvent(self, event):
        self.dragging = False
