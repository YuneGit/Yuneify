import reapy
from reapy.core.reaper import reaper

def add_track_with_kontakt(proj, track_name, index=0):
    """Add a new track with the given name"""
    new_track = proj.add_track(index=index, name=track_name)
    
    # Insert the Kontakt plugin on the new track
    kontakt_plugin_name = "Kontakt 7"  # Ensure this matches the plugin name in REAPER
    new_track.add_fx(kontakt_plugin_name)
    
    return new_track

if __name__ == "__main__":
    # Set the track name dynamically from here or from another script
    track_name = "Kontakt 7"  # Default track name; can be changed
    proj = reapy.Project()
    new_track = add_track_with_kontakt(proj, track_name)
