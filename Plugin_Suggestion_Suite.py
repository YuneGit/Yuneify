import os
import json
import re
from openai import OpenAI
import reapy
from dependencies.list_Kontakt_VST import get_folder_names
from dependencies.list_VST import get_vst_plugins
from dependencies.insert_Kontakt_Track import add_track_with_kontakt
from dependencies import insert_Track
import tkinter as tk
from tkinter import messagebox
from PyQt5 import QtWidgets
import sys

# Initialize the OpenAI client
client = OpenAI()

CONFIG_FOLDER = "config_files"
KONTAKT_LIBRARY_FILE = os.path.join(CONFIG_FOLDER, "kontakt_library_path.json")

def load_kontakt_library_path():
    """Load the saved Kontakt library path from a file."""
    if os.path.exists(KONTAKT_LIBRARY_FILE):
        with open(KONTAKT_LIBRARY_FILE, 'r') as file:
            return json.load(file).get("kontakt_library_path", "")
    return ""

def save_kontakt_library_path(kontakt_library_path):
    """Save the Kontakt library path to a file in the config folder."""
    os.makedirs(CONFIG_FOLDER, exist_ok=True)
    with open(KONTAKT_LIBRARY_FILE, 'w') as file:
        json.dump({"kontakt_library_path": kontakt_library_path}, file)

def get_gpt_suggestions(user_prompt, vst_plugins, kontakt_folders, num_tracks=3):
    """Generate suggestions for new tracks using GPT based on user input and available plugins/libraries."""
    combined_prompt = (
        f"I am composing something about: {user_prompt}\n\n"
        f"Here are the Kontakt libraries I own:\n" +
        "\n".join(kontakt_folders) + 
        "\n\n"
        f"Here are the VST plugins I own:\n" +
        "\n".join([re.sub(r'\.vst3$', '', plugin[0]) for plugin in vst_plugins]) +
        "\n\n"
        f"Please provide {num_tracks} suggestions for new tracks.\n"
        f"Please give one suggestion per track.\n"
        f"Repeat the same plugin multiple times to keep a consistent sound.\n"
        f"Respond in the following format:\n"
        f"VST Plugin: [Your VST Plugin]\n"
        f"or Kontakt Library: [Your Kontakt Library]"
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "No markdown. Follow the exact prompt format."},
            {"role": "user", "content": combined_prompt}
        ]
    )
    
    print(combined_prompt)
    return completion.choices[0].message.content.strip()

def create_new_kontakt_track(track_name=None, index=0):
    """Create a new track in REAPER using a Kontakt library."""
    add_track_with_kontakt(reapy.Project(), track_name, index)

def create_new_track(plugin_name=None):
    """Create a new track in REAPER using a standard VST plugin."""
    insert_Track.main(plugin_name)

def show_suggestions_ui(track_suggestions):
    """Display a UI for the user to select which suggestions to use."""
    def on_submit():
        selected_suggestions = [
            suggestion for var, suggestion in zip(checkbox_vars, track_suggestions) if var.get()
        ]
        if not selected_suggestions:
            messagebox.showwarning("No Selection", "No suggestions selected. Exiting...")
            root.destroy()
            return
        root.destroy()
        create_tracks(selected_suggestions)

    root = tk.Tk()
    root.title("Select Track Suggestions")

    checkbox_vars = []
    for i, suggestion in enumerate(track_suggestions):
        var = tk.BooleanVar()
        checkbox_vars.append(var)
        plugin_name = suggestion.get("plugin")
        kontakt_library = suggestion.get("library")
        label_text = f"Suggestion {i+1}: VST Plugin: {plugin_name}, Kontakt Library: {kontakt_library}"
        tk.Checkbutton(root, text=label_text, variable=var).pack(anchor='w')

    tk.Button(root, text="Submit", command=on_submit).pack()
    root.mainloop()

def create_tracks(selected_suggestions):
    """Create tracks based on selected suggestions."""
    for suggestion in selected_suggestions:
        plugin_name = suggestion.get("plugin")
        kontakt_library = suggestion.get("library")
        
        print(f"\nCreating track:")
        print(f"VST Plugin: {plugin_name}")
        print(f"Kontakt Library: {kontakt_library}")

        if plugin_name and kontakt_library:
            create_new_kontakt_track(track_name=kontakt_library)
            create_new_track(plugin_name=plugin_name)
        else:
            print("Error: One of the required variables is not assigned. Please check the suggestions.")

class PluginSuggestionApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Plugin Suggestion Suite")
        
        # Create layout
        layout = QtWidgets.QVBoxLayout()

        # Create input fields
        self.prompt_input = QtWidgets.QLineEdit(self)
        self.prompt_input.setPlaceholderText("Enter your composition theme...")

        self.num_tracks_input = QtWidgets.QSpinBox(self)
        self.num_tracks_input.setRange(1, 10)
        self.num_tracks_input.setValue(3)

        # Create buttons
        self.submit_button = QtWidgets.QPushButton("Get Suggestions", self)
        self.submit_button.clicked.connect(self.get_suggestions)

        # Add widgets to layout
        layout.addWidget(QtWidgets.QLabel("User Prompt:"))
        layout.addWidget(self.prompt_input)
        layout.addWidget(QtWidgets.QLabel("Number of Tracks:"))
        layout.addWidget(self.num_tracks_input)
        layout.addWidget(self.submit_button)

        # Set layout
        self.setLayout(layout)

    def get_suggestions(self):
        user_prompt = self.prompt_input.text()
        num_tracks = self.num_tracks_input.value()
        
        # Call the existing function to get suggestions
        kontakt_folders = get_folder_names(load_kontakt_library_path())
        vst_plugins = get_vst_plugins()
        suggestions = get_gpt_suggestions(user_prompt, vst_plugins, kontakt_folders, num_tracks=num_tracks)
        
        # Display suggestions
        QtWidgets.QMessageBox.information(self, "Suggestions", suggestions)

def main():
    """Main function to orchestrate the track creation workflow."""
    app = QtWidgets.QApplication(sys.argv)
    window = PluginSuggestionApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
