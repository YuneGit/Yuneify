# Track_insert.py

import reapy
from reapy.core.reaper import reaper

def add_track_with_plugin(proj, plugin_name, index=0):
    """Add a new track with the given plugin name"""
    new_track = proj.add_track(index=index, name=plugin_name)
    
    # Insert the specified plugin on the new track
    new_track.add_fx(plugin_name)
    
    return new_track

def main(plugin_name="BBC Symphony Orchestra"):
    """Main function to add a track with a specified plugin name"""
    proj = reapy.Project()
    new_track = add_track_with_plugin(proj, plugin_name)
    return new_track

if __name__ == "__main__":
    main()  # Default execution if run as a script
