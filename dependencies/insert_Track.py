# Track_insert.py

import reapy  # Import the reapy library for interacting with REAPER
from reapy.core.reaper import reaper  # Import the reaper module for accessing REAPER's functionality

def add_track_with_plugin(proj, plugin_name, index=0):
    """
    Add a new track to the project and insert a specified plugin on it.
    
    Parameters:
    proj (reapy.Project): The REAPER project to add the track to.
    plugin_name (str): The name of the plugin to insert on the new track.
    index (int, optional): The index at which to insert the track (default is 0).
    
    Returns:
    reapy.Track: The newly created track with the plugin inserted.
    """
    # Add a new track at the specified index with the name of the plugin
    new_track = proj.add_track(index=index, name=plugin_name)
    
    # Insert the specified plugin on the new track using its name
    new_track.add_fx(plugin_name)
    
    return new_track

def main(plugin_name="BBC Symphony Orchestra"):
    """
    Main function that initializes a new project and adds a track with the specified plugin.
    
    Parameters:
    plugin_name (str, optional): The name of the plugin to add to the track. Defaults to "BBC Symphony Orchestra".
    
    Returns:
    reapy.Track: The new track with the inserted plugin.
    """
    # Initialize a new REAPER project
    proj = reapy.Project()

    # Add the track with the specified plugin and return the track
    new_track = add_track_with_plugin(proj, plugin_name)
    
    return new_track

# This block ensures the script runs the main function if executed directly.
if __name__ == "__main__":
    main()  # Calls the main function with the default plugin name if the script is run as a standalone
