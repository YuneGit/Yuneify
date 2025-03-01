import reapy
import json
import os
import time
from pydantic import BaseModel
from modules.ai_models import get_model_handler, AIModelError
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QScrollArea, QFileDialog, QTabWidget
from modules.styles import apply_dark_theme  # Import the stylesheet function

class MidiNote(BaseModel):
    start: float
    end: float
    pitch: int
    velocity: int
    channel: int
    selected: bool
    muted: bool

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
        self.tabs.addTab(self.createChordTab(), "Chord Development")
        self.tabs.addTab(self.createMelodyTab(), "Melody Development")
        self.tabs.addTab(self.createAnalysisTab(), "MIDI Analysis")
        self.tabs.addTab(self.createSimilarityTab(), "Similarity Check")
        layout.addWidget(self.tabs)

        # Create and add feedback labels
        self.chord_feedback_label = QLabel('', self)
        self.melody_feedback_label = QLabel('', self)
        self.analysis_feedback_label = QLabel('', self)
        self.similarity_feedback_label = QLabel('', self)
        
        for label in [self.chord_feedback_label, self.melody_feedback_label,
                     self.analysis_feedback_label, self.similarity_feedback_label]:
            label.setWordWrap(True)

        self.chord_tab.layout().addWidget(self.chord_feedback_label)
        self.melody_tab.layout().addWidget(self.melody_feedback_label)
        self.analysis_tab.layout().addWidget(self.analysis_feedback_label)
        self.similarity_tab.layout().addWidget(self.similarity_feedback_label)

        self.setLayout(layout)

    def createChordTab(self):
        self.chord_tab = QWidget()
        layout = QVBoxLayout()
        self.prompt_input_chord = QLineEdit("Enter chord context...")
        self.suggest_button_chord = QPushButton("Get Chord Suggestions")
        self.suggest_button_chord.clicked.connect(lambda: self.on_get_suggestions('chord'))
        layout.addWidget(QLabel("Chord Development Tools:"))
        layout.addWidget(self.prompt_input_chord)
        layout.addWidget(self.suggest_button_chord)
        self.chord_tab.setLayout(layout)
        return self.chord_tab

    def createMelodyTab(self):
        self.melody_tab = QWidget()
        layout = QVBoxLayout()
        self.prompt_input_melody = QLineEdit("Enter melody context...")
        self.suggest_button_melody = QPushButton("Get Melody Suggestions")
        self.suggest_button_melody.clicked.connect(lambda: self.on_get_suggestions('melody'))
        layout.addWidget(QLabel("Melody Development Tools:"))
        layout.addWidget(self.prompt_input_melody)
        layout.addWidget(self.suggest_button_melody)
        self.melody_tab.setLayout(layout)
        return self.melody_tab

    def createAnalysisTab(self):
        self.analysis_tab = QWidget()
        layout = QVBoxLayout()
        self.analyze_button = QPushButton("Analyze Composition")
        self.analyze_button.clicked.connect(lambda: self.on_get_suggestions('analysis'))
        layout.addWidget(QLabel("MIDI Analysis Tools:"))
        layout.addWidget(self.analyze_button)
        self.analysis_tab.setLayout(layout)
        return self.analysis_tab

    def createSimilarityTab(self):
        self.similarity_tab = QWidget()
        layout = QVBoxLayout()
        self.similarity_button = QPushButton("Check Similarity")
        self.similarity_button.clicked.connect(lambda: self.on_get_suggestions('similarity'))
        layout.addWidget(QLabel("Similarity Check Tools:"))
        layout.addWidget(self.similarity_button)
        self.similarity_tab.setLayout(layout)
        return self.similarity_tab

    def on_get_suggestions(self, mode):
        # Disable UI elements
        self.tabs.setEnabled(False)
        for btn in [self.suggest_button_chord, self.suggest_button_melody,
                   self.analyze_button, self.similarity_button]:
            btn.setEnabled(False)

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

        # Re-enable UI elements
        self.tabs.setEnabled(True)
        for btn in [self.suggest_button_chord, self.suggest_button_melody,
                   self.analyze_button, self.similarity_button]:
            btn.setEnabled(True)

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
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

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
                'system': "Music theory expert analyzing chord progressions",
                'user': "Suggest 3 chord progression options using Roman numerals and specific voicings."
            },
            'melody': {
                'system': "Music composition expert developing melodies",
                'user': "Suggest 3 melodic development options with interval relationships."
            },
            'analysis': {
                'system': "Music analyst examining structural elements",
                'user': "Analyze key/mode, chords, contour, and rhythm patterns."
            },
            'similarity': {
                'system': "Musicologist comparing to known works",
                'user': "Identify similarities in motifs, harmony, rhythm, and genre."
            }
        }

        try:
            response = self.model.generate_text(
                system_prompt=prompts[mode]['system'],
                user_prompt=f"{self.custom_context}\n{prompts[mode]['user']}",
                midi_data=midi_data,
                temperature=0.6,
                max_tokens=400
            )
            return f"```markdown\n{response}\n```"
        except AIModelError as e:
            return f"⚠️ AI Error: {str(e)}"
        except NotImplementedError as e:
            return f"⚠️ Model not supported: {str(e)}"

if __name__ == "__main__":
    app = QApplication([])
    apply_dark_theme(app)
    suggestion_app = CompositionSuggestionApp()
    suggestion_app.show()
    sys.exit(app.exec())
