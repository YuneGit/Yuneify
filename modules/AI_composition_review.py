import reapy
import json
from openai import OpenAI
from pydantic import BaseModel
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QScrollArea, QFileDialog, QTabWidget
from modules.styles import apply_dark_theme  # Import the stylesheet function

# Define a Pydantic model to represent a MIDI note
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

        # Create labels for each tab to display suggestions
        self.chord_feedback_label = QLabel('', self)
        self.chord_feedback_label.setWordWrap(True)
        self.melody_feedback_label = QLabel('', self)
        self.melody_feedback_label.setWordWrap(True)
        self.analysis_feedback_label = QLabel('', self)
        self.analysis_feedback_label.setWordWrap(True)
        self.similarity_feedback_label = QLabel('', self)
        self.similarity_feedback_label.setWordWrap(True)

        # Add feedback labels to each tab
        self.chord_tab.layout().addWidget(self.chord_feedback_label)
        self.melody_tab.layout().addWidget(self.melody_feedback_label)
        self.analysis_tab.layout().addWidget(self.analysis_feedback_label)
        self.similarity_tab.layout().addWidget(self.similarity_feedback_label)

        self.setLayout(layout)

    def createChordTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.prompt_input_chord = QLineEdit(self)
        self.prompt_input_chord.setPlaceholderText('Enter context for chord development...')
        layout.addWidget(self.prompt_input_chord)

        self.suggest_button_chord = QPushButton('Get Chord Suggestions', self)
        self.suggest_button_chord.clicked.connect(lambda: self.on_get_suggestions('chord'))
        layout.addWidget(self.suggest_button_chord)

        tab.setLayout(layout)
        self.chord_tab = tab  # Store reference to the tab
        return tab

    def createMelodyTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.prompt_input_melody = QLineEdit(self)
        self.prompt_input_melody.setPlaceholderText('Enter context for melody development...')
        layout.addWidget(self.prompt_input_melody)

        self.suggest_button_melody = QPushButton('Get Melody Suggestions', self)
        self.suggest_button_melody.clicked.connect(lambda: self.on_get_suggestions('melody'))
        layout.addWidget(self.suggest_button_melody)

        tab.setLayout(layout)
        self.melody_tab = tab  # Store reference to the tab
        return tab

    def createAnalysisTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.analyze_button = QPushButton('Analyze MIDI', self)
        self.analyze_button.clicked.connect(lambda: self.on_get_suggestions('analysis'))
        layout.addWidget(self.analyze_button)

        tab.setLayout(layout)
        self.analysis_tab = tab  # Store reference to the tab
        return tab

    def createSimilarityTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.similarity_button = QPushButton('Check Similarity', self)
        self.similarity_button.clicked.connect(lambda: self.on_get_suggestions('similarity'))
        layout.addWidget(self.similarity_button)

        tab.setLayout(layout)
        self.similarity_tab = tab  # Store reference to the tab
        return tab

    def on_get_suggestions(self, mode):
        # Disable interaction
        self.tabs.setEnabled(False)
        self.suggest_button_chord.setEnabled(False)
        self.suggest_button_melody.setEnabled(False)
        self.analyze_button.setEnabled(False)
        self.similarity_button.setEnabled(False)

        if mode == 'chord':
            custom_context = self.prompt_input_chord.text()
            self.chord_feedback_label.setText("Generating suggestions...")
        elif mode == 'melody':
            custom_context = self.prompt_input_melody.text()
            self.melody_feedback_label.setText("Generating suggestions...")
        elif mode == 'analysis':
            custom_context = ''
            self.analysis_feedback_label.setText("Generating analysis...")
        elif mode == 'similarity':
            custom_context = ''
            self.similarity_feedback_label.setText("Checking similarity...")

        self.composition_suggester.custom_context = custom_context
        suggestions = self.composition_suggester.generate_suggestions(mode)

        if mode == 'chord':
            self.chord_feedback_label.setText(suggestions)
        elif mode == 'melody':
            self.melody_feedback_label.setText(suggestions)
        elif mode == 'analysis':
            self.analysis_feedback_label.setText(suggestions)
        elif mode == 'similarity':
            self.similarity_feedback_label.setText(suggestions)

        # Re-enable interaction
        self.tabs.setEnabled(True)
        self.suggest_button_chord.setEnabled(True)
        self.suggest_button_melody.setEnabled(True)
        self.analyze_button.setEnabled(True)
        self.similarity_button.setEnabled(True)

    def save_suggestions(self):
        suggestions = self.feedback_label.text()
        if suggestions:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Suggestions", "", "Text Files (*.txt);;All Files (*)", options=options)
            if file_name:
                with open(file_name, 'w') as file:
                    file.write(suggestions)

class AICompositionSuggester:
    def __init__(self, custom_context=''):
        self.project = reapy.Project()
        self.custom_context = custom_context

    def generate_suggestions(self, mode):
        item = self.project.get_selected_item(0)
        if not item:
            return "No selected item."

        take = item.active_take
        if not take:
            return "No active take."

        notes = take.notes
        if not notes:
            return "No MIDI notes."

        note_infos = [note.infos for note in notes]
        if mode == 'chord':
            return self.send_notes_to_chatgpt(note_infos, "chord")
        elif mode == 'melody':
            return self.send_notes_to_chatgpt(note_infos, "melody")
        elif mode == 'analysis':
            return self.analyze_midi(note_infos)
        elif mode == 'similarity':
            return self.check_similarity(note_infos)

    def send_notes_to_chatgpt(self, note_infos, mode):
        midi_data = json.dumps(note_infos, default=str)
        if mode == 'chord':
            prompt = (
                "Given the following MIDI notes, provide chord progression ideas. "
                "List specific chord sequences like 'Cmaj - Fmaj - Gmaj' that can be directly applied."
            )
        elif mode == 'melody':
            prompt = (
                "Given the following MIDI notes, provide direct suggestions to continue the melody. "
                "Use note names or concepts that can be directly applied."
            )
        
        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Provide practical suggestions without introductions."},
                {"role": "user", "content": f"{prompt}\n{midi_data}"},
            ],
            max_tokens=150  # Adjust this value to control the length of the response
        )

        return completion.choices[0].message.content.strip()

    def analyze_midi(self, note_infos):
        midi_data = json.dumps(note_infos, default=str)
        prompt = (
            "Analyze the following MIDI notes and provide a brief summary of the key musical elements. "
            "Focus on the main chords, melody, and rhythm patterns."
        )
        
        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Provide practical suggestions without introductions."},
                {"role": "user", "content": f"{prompt}\n{midi_data}"},
            ],
            max_tokens=150  # Adjust this value to control the length of the response
        )

        return completion.choices[0].message.content.strip()

    def check_similarity(self, note_infos):
        midi_data = json.dumps(note_infos, default=str)
        prompt = (
            "Given the following MIDI notes, identify any similarities to well-known songs or themes. "
            "Provide a list of songs or themes that are similar in melody, harmony, or rhythm."
        )
        
        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Provide practical suggestions without introductions."},
                {"role": "user", "content": f"{prompt}\n{midi_data}"},
            ],
            max_tokens=150  # Adjust this value to control the length of the response
        )

        return completion.choices[0].message.content.strip()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    suggestion_app = CompositionSuggestionApp()
    suggestion_app.show()
    sys.exit(app.exec_())