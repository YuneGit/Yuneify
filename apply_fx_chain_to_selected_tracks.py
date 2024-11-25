
#UPDATE THIS TO ALLOW THE USER TO COMPILE PRESETS AND 

import reapy
from reapy.core import Project

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

if __name__ == "__main__":
    # Define the FX chain here. Replace these with the actual names of the effects you want to apply.
    fx_chain = [
        "ReaComp (Cockos)",
        "ReaEQ (Cockos)",
        "ReaVerb (Cockos)"
    ]
    apply_fx_chain_to_selected_tracks(fx_chain) 