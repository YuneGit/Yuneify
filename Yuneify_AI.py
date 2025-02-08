import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter
from PySide6.QtCore import Qt
from modules.MIDI_Visualizer import MidiVisualizer
from modules.MIDI_AI import AIOrchestrationStyleSelector
from modules.AI_composition_review import CompositionSuggestionApp
from modules.styles import apply_dark_theme
from modules.utils import setup_logger

class MainApplication(QMainWindow):
   def __init__(self):
       try:
           super().__init__()
           self.logger = setup_logger('MainApplication', 'main_application.log')
           self.logger.info("MainApplication initialized.")
           self.setWindowTitle('MIDI Suite Application')
           self.setFixedSize(1000, 800)
           apply_dark_theme(self)
           self.logger.info("Dark theme applied.")
           
           main_widget = QWidget(self)
           main_layout = QVBoxLayout(main_widget)
           vertical_splitter = QSplitter(Qt.Vertical)
           
           self.logger.info("Initializing MidiVisualizer.")
           self.visualizer = MidiVisualizer()
           self.visualizer.setFixedSize(1000, 400)
           vertical_splitter.addWidget(self.visualizer)
           
           horizontal_splitter = QSplitter(Qt.Horizontal)
           
           self.logger.info("Initializing AIOrchestrationStyleSelector.")
           self.orchestration_selector = AIOrchestrationStyleSelector()
           self.orchestration_selector.setFixedSize(500, 400)
           horizontal_splitter.addWidget(self.orchestration_selector)
           
           self.logger.info("Initializing CompositionSuggestionApp.")
           self.composition_suggestion = CompositionSuggestionApp()
           self.composition_suggestion.setFixedSize(500, 400)
           horizontal_splitter.addWidget(self.composition_suggestion)
           
           vertical_splitter.addWidget(horizontal_splitter)
           main_layout.addWidget(vertical_splitter)
           self.setCentralWidget(main_widget)
           self.logger.info("MainApplication setup completed.")
       except Exception as e:
           self.logger.error("Error initializing MainApplication", exc_info=True)
           print(f"Error initializing MainApplication: {e}")
           raise
if __name__ == "__main__":
  try:
      # Check if a QApplication instance already exists
      app = QApplication.instance()
      if app is None:
          app = QApplication([])
      logger = setup_logger('MainApplication', 'main_application.log')
      logger.info("Starting application.")
      
      apply_dark_theme(app)
      logger.info("Dark theme applied to QApplication.")
      
      main_app = MainApplication()
      main_app.show()
      logger.info("MainApplication shown.")
      
      sys.exit(app.exec_())
  except Exception as e:
      print(f"Application failed to start: {e}")
      logger.error("Application failed to start", exc_info=True)