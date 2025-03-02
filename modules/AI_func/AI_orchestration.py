import reapy
import json
import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                              QLineEdit, QComboBox, QGroupBox, QSlider, QHBoxLayout,
                              QApplication)
from PySide6.QtCore import Qt
from modules.AI_func.ai_models import get_model_handler, AIModelError
from modules.styles import apply_dark_theme

class CopyableLabel(QWidget):
    """Reusable component with label and copy button"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.label = QLabel()
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setStyleSheet("background: #1E1E1E; padding: 5px;")
        
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(40, 25)
        self.copy_btn.clicked.connect(self.copy_text)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.copy_btn)
        self.setLayout(self.layout)
    
    def copy_text(self):
        QApplication.clipboard().setText(self.label.text())
    
    def setText(self, text):
        self.label.setText(text)

class OrchestrationConfigurator(QWidget):
    def __init__(self):
        super().__init__()
        self.project = reapy.Project()
        self.model = get_model_handler('openai')
        self.suggestions = ""  # Initialize empty suggestions attribute
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
        
        # Replace feedback label with CopyableLabel
        self.feedback_label = CopyableLabel()
        
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
            midi_data = self.get_midi_data()
            params = {
                'ensemble_size': self.ensemble_slider.value(),
                'complexity': self.complexity_combo.currentText().lower(),
                'style': self.style_input.text()
            }
            
            response = self.model.generate_text(
                system_prompt="Orchestration AI generating full score suggestions",
                user_prompt=(
                    f"Create orchestration for:\n"
                    f"- Ensemble size: {params['ensemble_size']}\n"
                    f"- Complexity: {params['complexity']}\n"
                    f"- Style: {params['style']}\n"
                    "Include instrument mapping and articulations."
                ),
                midi_data=midi_data,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Directly use the pre-validated JSON response
            self.suggestions = response
            try:
                parsed = json.loads(response)
                formatted_response = "\n".join(
                    f"- {k}: {v}" for k, v in parsed.items()
                )
                self.feedback_label.setText(f"```markdown\n{formatted_response}\n```")
            except json.JSONDecodeError:
                self.feedback_label.setText(f"⚠️ Error: Received valid JSON but failed to parse structure\n{response[:200]}...")
            
        except AIModelError as e:
            self.feedback_label.setText(f"⚠️ AI Error: {str(e)}")
        except Exception as e:
            self.feedback_label.setText(f"⚠️ Unexpected Error: {str(e)}")

    def apply_suggestions(self):
        try:
            self.feedback_label.setText("Applying orchestration suggestions...")
            
            json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', self.suggestions, re.DOTALL)
            if not json_blocks:
                json_blocks = re.findall(r'\{.*?\}', self.suggestions, re.DOTALL)
            
            if not json_blocks:
                raise ValueError("No valid JSON found in AI response")

            parsed_notes = []
            instrument_channels = {}  # Track instrument to channel mapping
            
            for json_str in json_blocks:
                try:
                    data = json.loads(json_str)
                    # Handle the orchestration object structure
                    if 'orchestration' in data:
                        orch_data = data['orchestration']
                        # Create instrument to channel mapping
                        instrument_channels = {
                            inst['name']: idx for idx, inst in enumerate(orch_data.get('instruments', []))
                        }
                        # Process notes with instrument mapping
                        for note in orch_data.get('notes', []):
                            if 'instrument' in note:
                                note['channel'] = instrument_channels.get(note['instrument'], 0)
                            parsed_notes.append(note)
                    elif 'midi_notes' in data:
                        parsed_notes.extend(data['midi_notes'])

                except json.JSONDecodeError as e:
                    error_context = f"JSON error at line {e.lineno}: {e.msg}\n{json_str[max(0,e.pos-50):e.pos+50]}"
                    self.feedback_label.setText(f"⚠️ JSON Error: {error_context}")
                    continue

            if not parsed_notes:
                raise ValueError("No valid MIDI notes found in any JSON blocks")

            item = self.project.get_selected_item(0)
            if not item:
                raise ValueError("No MIDI item selected")
            
            take = item.active_take
            if not take:
                raise ValueError("No active take")
            
            # Clear existing notes
            for note in take.notes:
                note.delete()
            
            # Add new notes with proper channel mapping
            for note in parsed_notes:
                take.add_note(
                    start=note['start'],
                    end=note['end'],
                    pitch=note['pitch'],
                    velocity=note.get('velocity', 64),  # Default velocity
                    channel=note.get('channel', 0),     # Default channel
                    selected=False,
                    muted=False
                )
            
            self.feedback_label.setText("Successfully applied orchestration suggestions!")
            
        except json.JSONDecodeError:
            self.feedback_label.setText("⚠️ Error: Invalid JSON format in AI response")
        except ValueError as e:
            self.feedback_label.setText(f"⚠️ Validation Error: {str(e)}")
        except Exception as e:
            self.feedback_label.setText(f"⚠️ Unexpected Error: {str(e)}")

    def get_midi_data(self):
        item = self.project.get_selected_item(0)
        if not item:
            raise ValueError("No MIDI item selected")
        
        take = item.active_take
        if not take:
            raise ValueError("No active take")
        
        # Get tempo and time signature from current project
        project = reapy.Project()  # Get current project
        tempo = project.bpm
        time_sig_num, time_sig_denom = project.time_signature
        
        return {
            "tempo": tempo,
            "time_signature": f"{int(time_sig_num)}/{int(time_sig_denom)}",
            "notes": [{
                "start": note.start,
                "end": note.end,
                "pitch": note.pitch,
                "velocity": note.velocity
            } for note in take.notes]
        }

    def handle_ai_response(self, response: str) -> dict:
        """Standardized JSON response parsing with multiple fallbacks."""
        json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL) or \
                      re.findall(r'\{.*?\}', response, re.DOTALL)
        
        for json_str in json_blocks:
            try:
                data = json.loads(json_str)
                if 'midi_notes' in data:
                    return data
            except json.JSONDecodeError:
                continue
        raise ValueError("No valid JSON found in AI response")

if __name__ == "__main__":
    app = QApplication([])
    apply_dark_theme(app)
    window = OrchestrationConfigurator()
    window.show()
    app.exec()
