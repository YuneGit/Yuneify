import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter
from PyQt5.QtCore import Qt
from MIDI_Visualizer import MidiVisualizer
from MIDI_AI import AIOrchestrationStyleSelector
from AI_composition_review import CompositionSuggestionApp

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MIDI Suite Application')
        self.setFixedSize(1000, 800)

        # Apply dark mode stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
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
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
                margin: 5px;
            }
            QSplitter::handle {
                background-color: #5A5A5A;
            }
        """)

        # Main widget and layout
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        # Use QSplitter to allow resizing between components
        vertical_splitter = QSplitter(Qt.Vertical)

        # Add MIDI Visualizer
        self.visualizer = MidiVisualizer()
        self.visualizer.setFixedSize(1000, 400)  # Set fixed size for visualizer
        vertical_splitter.addWidget(self.visualizer)

        # Horizontal splitter for AI Orchestration and Composition Suggestion
        horizontal_splitter = QSplitter(Qt.Horizontal)

        # Add AI Orchestration Style Selector
        self.orchestration_selector = AIOrchestrationStyleSelector()
        self.orchestration_selector.setFixedSize(500, 400)  # Set fixed size for orchestration selector
        horizontal_splitter.addWidget(self.orchestration_selector)

        # Add Composition Suggestion App
        self.composition_suggestion = CompositionSuggestionApp()
        self.composition_suggestion.setFixedSize(500, 400)  # Set fixed size for composition suggestion
        horizontal_splitter.addWidget(self.composition_suggestion)

        # Add horizontal splitter to the vertical splitter
        vertical_splitter.addWidget(horizontal_splitter)

        # Add vertical splitter to the main layout
        main_layout.addWidget(vertical_splitter)

        # Set the central widget
        self.setCentralWidget(main_widget)


    def fetch_ai_suggestions(self):
        # Example function to fetch AI suggestions
        print("Fetching AI suggestions...")
        # Here you can integrate logic to fetch suggestions and update the UI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.show()
    sys.exit(app.exec_()) 