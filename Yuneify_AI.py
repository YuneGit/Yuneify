import sys
from functools import partial
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                              QTabWidget, QLabel, QScrollArea, QProgressBar, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from modules.MIDI_Visualizer import MidiVisualizer
from modules.MIDI_AI import AIOrchestrationStyleSelector
from modules.AI_composition_review import CompositionSuggestionApp
from modules.AI_orchestration import OrchestrationConfigurator
from modules.styles import apply_dark_theme
from modules.utils import setup_logger

class MainApplication(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.logger = setup_logger('MainApplication', 'main_application.log')
            self.logger.info("MainApplication initialized.")
            self.setWindowTitle('Yuneify AI')
            self.setMinimumSize(1000, 800)
            self.resize(1200, 900)
            apply_dark_theme(self)
            
            # Initialize all UI components
            self.init_menubar()
            self.init_status_bar()
            self.init_tab_widget()
            self.init_keyboard_shortcuts()
            
            self.logger.info("MainApplication setup completed.")
        except Exception as e:
            self.logger.error("Initialization error", exc_info=True)
            raise

    def init_menubar(self):
        """Initialize menu bar with actions and shortcuts"""
        self.menubar = self.menuBar()
        
        # File menu
        file_menu = self.menubar.addMenu('&File')
        file_menu.addAction('New Project', self.new_project, "Ctrl+N")
        file_menu.addAction('Open Project...', self.open_project, "Ctrl+O")
        file_menu.addAction('Save Project', self.save_project, "Ctrl+S")
        file_menu.addSeparator()
        file_menu.addAction('Preferences...', self.show_preferences, "Ctrl+,")
        file_menu.addAction('Exit', self.close, "Ctrl+Q")

        # Help menu
        help_menu = self.menubar.addMenu('&Help')
        help_menu.addAction('Quick Start Guide', self.show_quickstart)
        help_menu.addAction('Interactive Tutorial', self.show_tutorial)
        help_menu.addSeparator()
        help_menu.addAction('About Yuneify', self.show_about)

    def init_status_bar(self):
        """Initialize status bar with dynamic updates"""
        self.status_bar = self.statusBar()
        self.status_label = QLabel('Ready')
        self.status_bar.addWidget(self.status_label)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)

    def init_tab_widget(self):
        """Initialize tabbed interface with scroll areas"""
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabBarAutoHide(False)
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Create tabs with scroll areas
        self.visualizer = self.create_scrollable_tab(MidiVisualizer(), "Visualizer")
        self.orchestration_config = self.create_scrollable_tab(OrchestrationConfigurator(), "Orchestration")
        self.orchestration_selector = self.create_scrollable_tab(AIOrchestrationStyleSelector(), "Styles")
        self.composition_suggestion = self.create_scrollable_tab(CompositionSuggestionApp(), "Suggestions")
        
        # Central widget layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def create_scrollable_tab(self, widget: QWidget, title: str) -> QScrollArea:
        """Wrap a widget in a scroll area for responsive sizing"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, title)
        return scroll

    def init_keyboard_shortcuts(self):
        """Set up global keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+1"), self, partial(self.tabs.setCurrentIndex, 0))
        QShortcut(QKeySequence("Ctrl+2"), self, partial(self.tabs.setCurrentIndex, 1))
        QShortcut(QKeySequence("Ctrl+3"), self, partial(self.tabs.setCurrentIndex, 2))
        QShortcut(QKeySequence("Ctrl+4"), self, partial(self.tabs.setCurrentIndex, 3))

    # Menu action handlers
    def new_project(self):
        self.show_status("Creating new project...", 2000)
    
    def open_project(self):
        self.show_status("Opening project...", 2000)
    
    def save_project(self):
        self.show_status("Saving project...", 2000)
    
    def show_preferences(self):
        self.show_status("Opening preferences...", 1500)
    
    def show_quickstart(self):
        self.show_status("Opening quick start guide...", 1500)
    
    def show_tutorial(self):
        self.show_status("Starting interactive tutorial...", 1500)
    
    def show_about(self):
        self.show_status("Showing about information...", 1500)
    
    def show_status(self, message: str, timeout: int = 3000):
        """Update status bar with timed message"""
        self.status_label.setText(message)
        QTimer.singleShot(timeout, lambda: self.status_label.setText('Ready'))
    
    def closeEvent(self, event):
        """Handle window closure cleanup"""
        self.logger.info("Application closing")
        super().closeEvent(event)

if __name__ == "__main__":
    try:
        app = QApplication.instance() or QApplication([])
        logger = setup_logger('MainApplication', 'main_application.log')
        apply_dark_theme(app)
        
        main_app = MainApplication()
        main_app.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.error("Application failed to start", exc_info=True)
        print(f"Application failed to start: {e}")
