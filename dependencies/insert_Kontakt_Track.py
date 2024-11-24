import reapy  # Import the reapy library to interact with REAPER
from reapy.core.reaper import reaper  # Import the reaper module for access to REAPER's functionalities

def add_track_with_kontakt(proj, track_name, index=0):
    """
    Add a new track to the project and insert the Kontakt plugin on it.
    
    Parameters:
    proj (reapy.Project): The REAPER project to which the track is added.
    track_name (str): The name of the track to create (typically used to identify the track).
    index (int, optional): The index at which to insert the track in the project (default is 0).
    
    Returns:
    reapy.Track: The newly created track with the Kontakt plugin inserted.
    """
    # Add a new track to the project at the specified index with the given name
    new_track = proj.add_track(index=index, name=track_name)
    
    # Specify the name of the Kontakt plugin to insert on the new track (ensure this matches the plugin name in REAPER)
    kontakt_plugin_name = "Kontakt 7"  # The name must exactly match how the plugin is listed in REAPER
    new_track.add_fx(kontakt_plugin_name)  # Insert the Kontakt plugin on the new track
    
    # Return the newly created track
    return new_track

if __name__ == "__main__":
    """
    Main script execution. Initializes a REAPER project, adds a track with the Kontakt plugin,
    and inserts the plugin into the track.
    
    The track name can be dynamically set here or passed in from other parts of the script.
    """
    track_name = "Kontakt 7"  # Default track name, can be modified as needed (e.g., use a different name)
    proj = reapy.Project()  # Initialize a new REAPER project
    new_track = add_track_with_kontakt(proj, track_name)  # Add a new track with Kontakt inserted on it
