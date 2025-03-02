import sys
from functools import partial
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                              QTabWidget, QLabel, QScrollArea, QProgressBar, QSizePolicy,
                              QSplitter, QGroupBox, QTextEdit, QStackedWidget, QPushButton,
                              QDockWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from modules.MIDI_Visualizer import MidiVisualizer
from modules.AI_func.MIDI_AI import AIOrchestrationStyleSelector
from modules.AI_func.AI_composition_review import CompositionSuggestionApp
from modules.AI_func.AI_orchestration import OrchestrationConfigurator
from modules.styles import apply_dark_theme
from modules.utils import setup_logger
import reapy

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
        """Initialize modern dashboard layout with collapsible sections"""
        # Left sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.addWidget(self.create_quick_action_group())
        sidebar_layout.addStretch()
        
        # Main content area with tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_orchestration_workspace(), "Orchestration")
        
        # Create dockable visualizer
        self.visualizer_dock = QDockWidget("MIDI Visualizer", self)
        self.visualizer_dock.setObjectName("MidiVisualizerDock")
        self.visualizer = MidiVisualizer()
        self.visualizer_dock.setWidget(self.visualizer)
        self.visualizer_dock.setMinimumWidth(400)
        self.visualizer_dock.setMinimumHeight(300)
        self.visualizer_dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )
        self.addDockWidget(Qt.RightDockWidgetArea, self.visualizer_dock)
        
        # Main content area
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(sidebar)
        main_splitter.addWidget(self.tabs)
        
        self.setCentralWidget(main_splitter)
        main_splitter.setSizes([200, 1000])  # Allocate more space to main content

    def create_orchestration_workspace(self):
        """Create the orchestration workspace as a separate widget"""
        workspace = QWidget()
        layout = QVBoxLayout(workspace)
        
        # Section 1: Style Selection
        style_group = QGroupBox("Orchestration Style")
        style_layout = QVBoxLayout()
        self.style_selector = AIOrchestrationStyleSelector()
        style_layout.addWidget(self.style_selector)
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # Section 2: Configuration
        config_group = QGroupBox("Orchestration Parameters")
        self.orchestration_config = OrchestrationConfigurator()
        config_layout = QVBoxLayout()
        config_layout.addWidget(self.orchestration_config)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Section 3: Suggestions
        suggestions_group = QGroupBox("AI Suggestions")
        self.composition_suggestion = CompositionSuggestionApp()
        suggestions_layout = QVBoxLayout()
        suggestions_layout.addWidget(self.composition_suggestion)
        suggestions_group.setLayout(suggestions_layout)
        layout.addWidget(suggestions_group)
        
        return workspace

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
        try:
            reapy.Project().create()
            self.show_status("New project created", 2000)
            self.logger.info("Created new project")
        except Exception as e:
            self.logger.error(f"Error creating project: {str(e)}")
            self.show_status("Project creation failed", 2000)
    
    def open_project(self):
        try:
            project = reapy.Project()
            project.open()
            self.show_status("Project opened", 2000)
            self.logger.info("Opened project")
        except Exception as e:
            self.logger.error(f"Error opening project: {str(e)}")
            self.show_status("Open failed", 2000)
    
    def save_project(self):
        try:
            project = reapy.Project()
            project.save()
            self.show_status("Project saved", 2000)
            self.logger.info("Saved project")
        except Exception as e:
            self.logger.error(f"Error saving project: {str(e)}")
            self.show_status("Save failed", 2000)
    
    def show_preferences(self):
        try:
            reapy.show_message_box("Preferences", "Open preferences window")
            self.show_status("Preferences opened", 1500)
            self.logger.info("Opened preferences")
        except Exception as e:
            self.logger.error(f"Error opening preferences: {str(e)}")
    
    def show_quickstart(self):
        try:
            reapy.show_message_box("Quick Start", "Opening quick start guide...")
            self.show_status("Quick start guide opened", 1500)
            self.logger.info("Opened quick start guide")
        except Exception as e:
            self.logger.error(f"Error opening guide: {str(e)}")
    
    def show_tutorial(self):
        try:
            reapy.show_message_box("Tutorial", "Starting interactive tutorial...")
            self.show_status("Tutorial started", 1500)
            self.logger.info("Started tutorial")
        except Exception as e:
            self.logger.error(f"Error starting tutorial: {str(e)}")
    
    def show_about(self):
        try:
            reapy.show_message_box("About Yuneify", 
                "Yuneify AI v1.0\n\nAdvanced MIDI Orchestration Toolkit")
            self.show_status("About information shown", 1500)
            self.logger.info("Displayed about info")
        except Exception as e:
            self.logger.error(f"Error showing about: {str(e)}")
    
    def show_status(self, message: str, timeout: int = 3000):
        """Update status bar with timed message"""
        self.status_label.setText(message)
        QTimer.singleShot(timeout, lambda: self.status_label.setText('Ready'))
    
    def closeEvent(self, event):
        """Handle window closure cleanup"""
        self.logger.info("Application closing")
        super().closeEvent(event)

    def create_quick_action_group(self):
        """Create sidebar quick action buttons"""
        group = QGroupBox("Quick Actions")
        layout = QVBoxLayout()
        
        actions = [
            ("New Project", self.new_project, "Ctrl+N"),
            ("Open Project", self.open_project, "Ctrl+O"),
            ("Save Project", self.save_project, "Ctrl+S"),
            ("Render", partial(self.show_status, "Rendering...", 2000), "Ctrl+R"),
            ("Undo", partial(self.show_status, "Undoing...", 1000), "Ctrl+Z"),
            ("Redo", partial(self.show_status, "Redoing...", 1000), "Ctrl+Shift+Z")
        ]
        
        for text, handler, shortcut in actions:
            btn = QPushButton(text)
            btn.setShortcut(shortcut)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
        
        layout.addStretch()
        group.setLayout(layout)
        return group

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
