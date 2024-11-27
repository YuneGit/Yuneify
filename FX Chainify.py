import reapy
from reapy.core import Project
from dependencies.list_VST import get_vst_plugins
import tkinter as tk
from tkinter import simpledialog, messagebox

def apply_fx_chain_to_selected_tracks(fx_chain):
    """
    Applies a chain of effects to all selected tracks in the current REAPER project.
    
    Parameters:
    fx_chain (list of str): A list of effect names to be applied in order.
    """
    project = Project()  # Get the current project
    selected_tracks = project.selected_tracks  # Get all selected tracks

    if not selected_tracks:
        print("No tracks selected. Please select tracks to apply the FX chain.")
        return

    for track in selected_tracks:
        for fx_name in fx_chain:
            track.add_fx(fx_name)
        print(f"Applied FX chain to '{track.name}'.")

def select_vst_plugins():
    """
    Opens a dialog for the user to select VST plugins from a list.
    
    Returns:
    list of str: A list of selected VST plugin names.
    """
    plugins = get_vst_plugins()
    if not plugins:
        messagebox.showinfo("Info", "No VST plugins found.")
        return []

    # Create a simple dialog to select plugins
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    selected_plugins = simpledialog.askstring(
        "Select VST Plugins",
        "Enter plugin numbers separated by commas:\n" +
        "\n".join(f"{i+1}. {name}" for i, (name, _) in enumerate(plugins))
    )

    if not selected_plugins:
        return []

    # Convert input to list of plugin names
    try:
        selected_indices = [int(i.strip()) - 1 for i in selected_plugins.split(",")]
        return [plugins[i][0] for i in selected_indices if 0 <= i < len(plugins)]
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter numbers separated by commas.")
        return []

if __name__ == "__main__":
    # Let the user select VST plugins
    fx_chain = select_vst_plugins()
    if fx_chain:
        apply_fx_chain_to_selected_tracks(fx_chain) 