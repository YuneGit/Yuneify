import logging
import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QGroupBox, QVBoxLayout, QProgressBar

def setup_logger(name, log_file_prefix, level=logging.INFO):
   """Function to setup a logger."""
   # Determine the base path for logs
   if getattr(sys, 'frozen', False):
       # If running as a bundled executable
       base_path = sys._MEIPASS
   else:
       # If running as a script
       base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Ensure the yunify-log directory exists
   log_dir = os.path.join(base_path, 'yunify-log')
   os.makedirs(log_dir, exist_ok=True)
    # Append date and time to the log file name
   timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
   log_file = f"{log_file_prefix}_{timestamp}.log"
   log_path = os.path.join(log_dir, log_file)
   handler = logging.FileHandler(log_path)
   formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
   handler.setFormatter(formatter)
   logger = logging.getLogger(name)
   logger.setLevel(level)
   logger.addHandler(handler)
   def handle_exception(exc_type, exc_value, exc_traceback):
       if issubclass(exc_type, KeyboardInterrupt):
           sys.__excepthook__(exc_type, exc_value, exc_traceback)
           return
       logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
   sys.excepthook = handle_exception
   return logger

class BaseAIPanel(QWidget):
    """Base class for AI panels with standardized UI elements."""
    
    def __init__(self):
        super().__init__()
        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        self.progress_bar = QProgressBar()
        
    def create_input_group(self, title: str, widgets: list) -> QGroupBox:
        """Create standardized input group with title."""
        group = QGroupBox(title)
        layout = QVBoxLayout()
        for widget in widgets:
            layout.addWidget(widget)
        group.setLayout(layout)
        return group