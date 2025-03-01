import reapy
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                              QLineEdit, QComboBox, QGroupBox, QSlider)
from PySide6.QtCore import Qt
from modules.ai_models import get_model_handler, AIModelError
from modules.styles import apply_dark_theme

class OrchestrationConfigurator(QWidget):
    def __init__(self):
        super().__init__()
        self.project = reapy.Project()
        self.model = get_model_handler('openai')
        self.init_ui()
        
    def init_ui(self):
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        
        # Section grouping
        self.param_group = QGroupBox("Orchestration Parameters")
        param_layout = QVBoxLayout()
        
        # Instrumentation controls
        self.instrumentation_label = QLabel("Target Ensemble Size:")
        self.ensemble_slider = QSlider(Qt.Horizontal)
        self.ensemble_slider.setRange(1, 12)
        self.ensemble_slider.setValue(4)
        
        # Complexity controls
        self.complexity_combo = QComboBox()
        self.complexity_combo.addItems(["Basic", "Intermediate", "Advanced", "Professional"])
        
        # Style controls
        self.style_input = QLineEdit("Enter musical style or era...")
        
        # Assemble parameter controls
        param_layout.addWidget(self.instrumentation_label)
        param_layout.addWidget(self.ensemble_slider)
        param_layout.addWidget(QLabel("Technical Complexity:"))
        param_layout.addWidget(self.complexity_combo)
        param_layout.addWidget(QLabel("Musical Style/Era:"))
        param_layout.addWidget(self.style_input)
        self.param_group.setLayout(param_layout)
        
        # Action buttons
        self.analyze_button = QPushButton("Analyze Current Orchestration")
        self.suggest_button = QPushButton("Generate Orchestration Plan")
        self.apply_button = QPushButton("Apply Suggestions")
        
        # Feedback area
        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        
        # Layout assembly
        layout.addWidget(self.param_group)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.suggest_button)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.feedback_label)
        
        self.setLayout(layout)
        apply_dark_theme(self)
        
        # Connect signals
        self.analyze_button.clicked.connect(self.analyze_orchestration)
        self.suggest_button.clicked.connect(self.generate_suggestions)
        self.apply_button.clicked.connect(self.apply_suggestions)

    def analyze_orchestration(self):
        try:
            midi_data = self.get_midi_data()
            analysis = self.model.generate_text(
                system_prompt="Orchestration analysis expert",
                user_prompt=f"Analyze current orchestration for:\n- Instrument balance\n- Range conflicts\n- Dynamic effectiveness\nStyle: {self.style_input.text()}",
                midi_data=midi_data,
                temperature=0.4,
                max_tokens=500
            )
            self.feedback_label.setText(f"```markdown\n{analysis}\n```")
        except Exception as e:
            self.feedback_label.setText(f"⚠️ Error: {str(e)}")

    def generate_suggestions(self):
        try:
            params = {
                'ensemble_size': self.ensemble_slider.value(),
                'complexity': self.complexity_combo.currentText().lower(),
                'style': self.style_input.text()
            }
            
            suggestions = self.model.generate_text(
                system_prompt="Orchestration AI generating configuration suggestions",
                user_prompt=f"Suggest orchestration adjustments for:\n- Ensemble size: {params['ensemble_size']}\n- Complexity: {params['complexity']}\n- Style: {params['style']}",
                midi_data=self.get_midi_data(),
                temperature=0.7,
                max_tokens=600
            )
            self.feedback_label.setText(f"```markdown\n{suggestions}\n```")
        except Exception as e:
            self.feedback_label.setText(f"⚠️ Error: {str(e)}")

    def apply_suggestions(self):
        self.feedback_label.setText("Applying orchestration suggestions...")
        # Implementation would go here to actually modify the project
        # This would interface with REAPER's API via reapy
        self.feedback_label.setText("Orchestration applied successfully!")

    def get_midi_data(self):
        item = self.project.get_selected_item(0)
        if not item:
            raise ValueError("No MIDI item selected")
        
        take = item.active_take
        if not take:
            raise ValueError("No active take")
        
        return [{
            "start": note.start,
            "end": note.end,
            "pitch": note.pitch,
            "velocity": note.velocity
        } for note in take.notes]

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    apply_dark_theme(app)
    window = OrchestrationConfigurator()
    window.show()
    app.exec()
