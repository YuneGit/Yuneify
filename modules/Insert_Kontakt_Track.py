import os
import json
import reapy
from reapy import reascript_api as RPR
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QMessageBox, QTreeWidget, QTreeWidgetItem, QLabel, 
    QInputDialog, QComboBox, QApplication, QMainWindow, QGridLayout
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor, QPainter, QColor, QPen, QPainterPath
from modules.styles import apply_dark_theme

import os
import json
import reapy
from reapy import reascript_api as RPR
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, QTreeWidget, 
    QTreeWidgetItem, QLabel, QInputDialog, QComboBox, 
    QApplication, QMainWindow, QFrame
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor, QPainter, QColor, QPen, QPainterPath, QFont

class ModernButton(QPushButton):
    def __init__(self, text, parent=None, is_icon=False):
        super().__init__(text, parent)
        size = 36 if is_icon else 120
        self.setFixedHeight(36)
        self.setMinimumWidth(size)
        self.setFont(QFont("Inter", 10))
        self.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
            }
            QPushButton:pressed {
                background-color: #1D1D1D;
            }
        """)

class VSTPresetManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setFixedSize(480, 640)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.presets_dir = os.path.join(os.path.dirname(__file__), ".yuneify_presets")
        self.current_fx = None
        self.preset_structure = {}
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header section
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        title = QLabel("VST Preset Manager")
        title.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 600;")
        header_layout.addWidget(title)
        
        # FX Selection section
        fx_frame = QFrame()
        fx_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 12px;
                padding: 12px;
            }
        """)
        fx_layout = QVBoxLayout(fx_frame)
        fx_layout.setContentsMargins(16, 16, 16, 16)
        fx_layout.setSpacing(12)
        
        fx_label = QLabel("Selected FX")
        fx_label.setStyleSheet("color: #888888; font-size: 12px; font-weight: 500;")
        
        self.fx_combo = QComboBox()
        self.fx_combo.setStyleSheet("""
            QComboBox {
                background-color: #363636;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                min-height: 36px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #363636;
                color: #FFFFFF;
                selection-background-color: #4D4D4D;
                border: none;
                outline: none;
                padding: 4px;
            }
        """)
        
        fx_actions = QWidget()
        fx_actions_layout = QHBoxLayout(fx_actions)
        fx_actions_layout.setContentsMargins(0, 0, 0, 0)
        fx_actions_layout.setSpacing(8)
        
        self.refresh_fx_button = ModernButton("Refresh", is_icon=True)
        self.close_button = ModernButton("✕", is_icon=True)
        
        fx_actions_layout.addWidget(self.refresh_fx_button)
        fx_actions_layout.addWidget(self.close_button)
        fx_actions_layout.addStretch()
        
        fx_layout.addWidget(fx_label)
        fx_layout.addWidget(self.fx_combo)
        fx_layout.addWidget(fx_actions)
        
        # Preset Browser
        self.preset_tree = QTreeWidget()
        self.preset_tree.setHeaderHidden(True)
        self.preset_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                padding: 12px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-radius: 6px;
            }
            QTreeWidget::item:selected {
                background-color: #3D3D3D;
            }
            QTreeWidget::branch {
                background: transparent;
            }
        """)
        
        # Preset Actions
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(12)
        
        self.save_button = ModernButton("Save Preset")
        self.load_button = ModernButton("Load Preset")
        
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.load_button)
        
        # Add all sections to main layout
        layout.addWidget(header)
        layout.addWidget(fx_frame)
        layout.addWidget(self.preset_tree, 1)
        layout.addWidget(actions)
        
        # Connect signals
        self.refresh_fx_button.clicked.connect(self.refresh_kontakt_instances)
        self.close_button.clicked.connect(self.close)
        self.save_button.clicked.connect(self.save_preset)
        self.load_button.clicked.connect(self.load_preset)
        
        # Initial setup
        self.ensure_presets_dir()
        self.refresh_kontakt_instances()
        self.scan_presets()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create main window background
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        
        # Draw shadow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 40))
        painter.drawPath(path.translated(0, 2))
        
        # Draw main background
        painter.setBrush(QColor(26, 26, 26, 245))
        painter.drawPath(path)


    # Keep all other methods the same as they handle the functionality
    def ensure_presets_dir(self):
        os.makedirs(self.presets_dir, exist_ok=True)

    def refresh_kontakt_instances(self):
        """Find all tracks, including those without FX, and list them in the combo box"""
        self.fx_combo.clear()
        project = reapy.Project()
        
        for track in project.tracks:
            # Add the track itself, even if it has no FX
            self.fx_combo.addItem(
                f"{track.name} (No FX)", 
                userData=(track.id, -1)  # Use -1 to indicate no FX
            )
            
            # Add FX instances on the track
            for fx_index, fx in enumerate(track.fxs):
                if "Kontakt" in fx.name:
                    self.fx_combo.addItem(
                        f"{track.name} - {fx.name}", 
                        userData=(track.id, fx_index)
                    )

    def get_current_fx(self):
        index = self.fx_combo.currentIndex()
        if index < 0:
            return None
        return self.fx_combo.itemData(index)

    def sanitize_name(self, name):
        words = name.split()
        if not words:
            return "unnamed"
        category = "".join(c if c.isalnum() else "_" for c in words[0].lower())
        preset_part = "_".join(
            "".join(c if c.isalnum() else "_" for c in word.lower())
            for word in words[1:]
        )
        return f"{category}_{preset_part}" if preset_part else category

    def save_preset(self):
        fx_data = self.get_current_fx()
        if not fx_data:
            QMessageBox.warning(self, "Error", "No FX selected!")
            return

        track_id, fx_index = fx_data
        
        try:
            (_, _, _, _, fx_name, _) = RPR.TrackFX_GetNamedConfigParm(
                track_id, fx_index, "fx_name", "", 256
            )
            
            preset_name, ok = QInputDialog.getText(
                self, "Preset Name", "Enter preset name:"
            )
            if not ok or not preset_name:
                return

            (retval, _, _, _, chunk_b64, _) = RPR.TrackFX_GetNamedConfigParm(
                track_id, fx_index, "vst_chunk", "", 1024 * 1024
            )
            
            if not retval or not chunk_b64:
                raise Exception("Failed to retrieve VST chunk data")

            preset_data = {
                "fx_name": fx_name.strip(),
                "chunk": chunk_b64,
                "original_name": preset_name
            }

            filename = self.sanitize_name(preset_name) + ".yuneify_preset"
            file_path = os.path.join(self.presets_dir, filename)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(preset_data, f)
            
            self.scan_presets()
            QMessageBox.information(self, "Success", f"Preset saved to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save preset:\n{str(e)}")

    def load_preset(self):
        selected = self.preset_tree.currentItem()
        if not selected or selected.childCount() > 0:
            QMessageBox.warning(self, "Error", "Select a specific preset!")
            return

        try:
            filename = selected.data(0, Qt.UserRole)
            file_path = os.path.join(self.presets_dir, filename)
            
            with open(file_path, "r", encoding="utf-8") as f:
                preset_data = json.load(f)
            
            selected_fx = self.get_current_fx()
            target_fx = None
            track_id = None
            fx_index = -1

            if selected_fx:
                track_id, fx_index = selected_fx

            if track_id is None:
                project = reapy.Project()
                track = project.tracks[0]
                track_id = track.id

            if fx_index == -1:
                target_fx = self.create_compatible_fx(preset_data["fx_name"], track_id)
            else:
                (_, _, _, _, current_fx_name, _) = RPR.TrackFX_GetNamedConfigParm(
                    track_id, fx_index, "fx_name", "", 256
                )
                
                if current_fx_name.strip() != preset_data["fx_name"]:
                    target_fx = self.find_compatible_fx_on_track(
                        track_id, preset_data["fx_name"]
                    )
                
                if not target_fx:
                    target_fx = self.create_compatible_fx(
                        preset_data["fx_name"], track_id
                    )

            retval = RPR.TrackFX_SetNamedConfigParm(
                target_fx[0], target_fx[1], "vst_chunk", preset_data["chunk"]
            )
            
            if not retval:
                raise Exception("Failed to apply VST chunk")
            
            QMessageBox.information(self, "Success", 
                f"Loaded {preset_data['original_name']} into {preset_data['fx_name']}")
        
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Error", f"Failed to load preset:\n{str(e)}")

    def find_compatible_fx_on_track(self, track_id, required_fx_name):
        track = reapy.Track(track_id)
        for fx_index, fx in enumerate(track.fxs):
            (_, _, _, _, fx_name, _) = RPR.TrackFX_GetNamedConfigParm(
                track.id, fx_index, "fx_name", "", 256
            )
            if fx_name.strip() == required_fx_name:
                return (track.id, fx_index)
        return None

    def create_compatible_fx(self, fx_name, track_id):
        track = reapy.Track(track_id)
        fx = track.add_fx(fx_name)
        return (track.id, fx.index)

    def scan_presets(self):
        self.preset_tree.clear()
        self.preset_structure = {}
        
        for filename in os.listdir(self.presets_dir):
            if filename.endswith(".yuneify_preset"):
                base_name = os.path.splitext(filename)[0]
                parts = base_name.split('_', 1)
                category = parts[0].capitalize() if parts else "Uncategorized"
                preset_name = parts[1] if len(parts) > 1 else base_name
                
                if category not in self.preset_structure:
                    self.preset_structure[category] = []
                self.preset_structure[category].append((preset_name, filename))
        
        for category, presets in self.preset_structure.items():
            category_item = QTreeWidgetItem(self.preset_tree, [category])
            for preset in presets:
                preset_name, filename = preset
                item = QTreeWidgetItem(category_item, [preset_name])
                item.setData(0, Qt.UserRole, filename)

def create_vst_preset_manager():
    print("Creating VST Preset Manager...")
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            
        manager = VSTPresetManager()
        cursor_pos = QCursor.pos()
        manager.move(cursor_pos.x() - manager.width() // 2, cursor_pos.y() - manager.height() // 2)
        manager.show()
        
        app._vst_manager = manager
        
        print("VST Preset Manager created successfully")
        return manager
    except Exception as e:
        print(f"Error creating VST Preset Manager: {e}")
        return None