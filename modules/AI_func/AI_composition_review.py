import reapy
import json
import os
import time
from pydantic import BaseModel
from modules.AI_func.ai_models import get_model_handler, AIModelError
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QScrollArea, QTabWidget, QHBoxLayout
from PySide6.QtGui import QAction
from modules.styles import apply_dark_theme  # Import the stylesheet function
from PySide6.QtCore import Qt, QTimer

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

class CompositionSuggestionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.composition_suggester = AICompositionSuggester()

    def initUI(self):
        self.setWindowTitle('Composition Suggestion')
        self.setFixedSize(400, 300)
        apply_dark_theme(self)

        layout = QVBoxLayout()
        self.tabs = QTabWidget(self)
        
        # Create and store tab references
        self.chord_tab = self.create_tab("Chord Development", "Chord Development Tools:", "Enter chord context...", "Get Chord Suggestions")
        self.melody_tab = self.create_tab("Melody Development", "Melody Development Tools:", "Enter melody context...", "Get Melody Suggestions")
        self.analysis_tab = self.create_tab("MIDI Analysis", "MIDI Analysis Tools:", "", "Analyze Composition")
        self.similarity_tab = self.create_tab("Similarity Check", "Similarity Check Tools:", "", "Check Similarity")
        
        self.tabs.addTab(self.chord_tab, "Chord Development")
        self.tabs.addTab(self.melody_tab, "Melody Development")
        self.tabs.addTab(self.analysis_tab, "MIDI Analysis")
        self.tabs.addTab(self.similarity_tab, "Similarity Check")
        
        layout.addWidget(self.tabs)

        # Replace all QLabel feedbacks with CopyableLabel
        self.chord_feedback_label = CopyableLabel()
        self.melody_feedback_label = CopyableLabel()
        self.analysis_feedback_label = CopyableLabel()
        self.similarity_feedback_label = CopyableLabel()
        
        for label in [self.chord_feedback_label, self.melody_feedback_label,
                     self.analysis_feedback_label, self.similarity_feedback_label]:
            label.label.setWordWrap(True)
        
        self.chord_tab.layout().addWidget(self.chord_feedback_label)
        self.melody_tab.layout().addWidget(self.melody_feedback_label)
        self.analysis_tab.layout().addWidget(self.analysis_feedback_label)
        self.similarity_tab.layout().addWidget(self.similarity_feedback_label)

        self.setLayout(layout)

    def create_tab(self, title, label_text, prompt_placeholder, button_text):
        tab = QWidget()
        layout = QVBoxLayout()
        prompt_input = QLineEdit(prompt_placeholder)
        button = QPushButton(button_text)
        layout.addWidget(QLabel(label_text))
        layout.addWidget(prompt_input)
        layout.addWidget(button)
        tab.setLayout(layout)
        return tab

    def async_operation(func):
        """Decorator to handle UI state during async operations."""
        def wrapper(self, *args, **kwargs):
            try:
                self.tabs.setEnabled(False)
                [btn.setEnabled(False) for btn in self.buttons]
                result = func(self, *args, **kwargs)
                return result
            finally:
                self.tabs.setEnabled(True)
                [btn.setEnabled(True) for btn in self.buttons]
        return wrapper

    @async_operation
    def on_get_suggestions(self, mode):
        # Set loading text
        feedback_labels = {
            'chord': self.chord_feedback_label,
            'melody': self.melody_feedback_label,
            'analysis': self.analysis_feedback_label,
            'similarity': self.similarity_feedback_label
        }
        feedback_labels[mode].setText("Generating suggestions...")

        # Get suggestions
        self.composition_suggester.custom_context = self.get_custom_context(mode)
        suggestions = self.composition_suggester.generate_suggestions(mode)
        feedback_labels[mode].setText(suggestions)

    def get_custom_context(self, mode):
        if mode == 'chord':
            return self.prompt_input_chord.text()
        elif mode == 'melody':
            return self.prompt_input_melody.text()
        return ''

class AICompositionSuggester:
    def __init__(self, custom_context='', model_name='openai'):
        self.project = reapy.Project()
        self.custom_context = custom_context
        self.model = get_model_handler(model_name)

    def generate_suggestions(self, mode):
        try:
            note_infos = self.get_midi_data()
            return self._generate_suggestion(mode, note_infos)
        except (AIModelError, ValueError) as e:  # Combine related exceptions
            return f"⚠️ Error: {str(e)}"
        except Exception as e:
            return f"⚠️ Unexpected Error: {str(e)}"

    def get_midi_data(self):
        item = self.project.get_selected_item(0)
        if not item:
            raise ValueError("No MIDI item selected")
        
        take = item.active_take
        if not take:
            raise ValueError("No active take")
        
        notes = take.notes
        if not notes:
            raise ValueError("No MIDI notes found")
        
        return [{
            "start": note.start,
            "end": note.end,
            "pitch": note.pitch,
            "velocity": note.velocity,
            "channel": note.channel,
            "selected": note.selected,
            "muted": note.muted
        } for note in notes]

    def _generate_suggestion(self, mode: str, midi_data: dict) -> str:
        prompts = {
            'chord': {
                'system': "Orchestration expert analyzing chord voicings",
                'user': "Suggest 3 orchestral chord voicing options with instrument combinations"
            },
            'melody': {
                'system': "Orchestrator developing melodic lines",
                'user': "Suggest 3 orchestral instrumentation options for this melody"
            },
            'analysis': {
                'system': "Orchestral analyst",
                'user': "Analyze orchestration balance, range coverage, and timbral variety"
            },
            'similarity': {
                'system': "Orchestral musicologist",
                'user': "Identify similarities to standard orchestral repertoire"
            }
        }

        try:
            response = self.model.generate_text(
                system_prompt=prompts[mode]['system'],
                user_prompt=f"{self.custom_context}\n{prompts[mode]['user']}\n"
                            "Respond with valid JSON in this format:\n"
                            "{\n  \"suggestions\": [\"suggestion1\", \"suggestion2\"]\n}",
                midi_data=midi_data,
                temperature=0.6,
                max_tokens=400
            )
            # Validate JSON structure
            json_data = json.loads(response)
            if 'suggestions' not in json_data:
                raise AIModelError("Response missing 'suggestions' key")
            
            return "\n".join(f"- {s}" for s in json_data['suggestions'])
        
        except json.JSONDecodeError:
            return "⚠️ Error: Invalid JSON format in AI response"

if __name__ == "__main__":
    app = QApplication([])
    apply_dark_theme(app)
    suggestion_app = CompositionSuggestionApp()
    suggestion_app.show()
    sys.exit(app.exec())
