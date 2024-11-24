import os
import reapy
from reapy.core.reaper import reaper
from reapy.core.reaper.reaper import get_resource_path

def get_vst_plugins():
    """
    Extracts and lists VST plugins from REAPER's plugin files, 
    excluding any plugins present in the blacklist.
    """
    # Get REAPER's resource path
    resource_path = get_resource_path()

    # Paths to REAPER's VST plugin files
    vst_files = [
        os.path.join(resource_path, 'reaper-vstplugins64.ini'),
        os.path.join(resource_path, 'reaper-vstplugins.ini')
    ]
    
    # Blacklist to exclude specific plugins (user should fill this with their entries)
    blacklist = set()  # Example: {"Plugin1.Vst3", "Plugin2.Vst3"}

    # Collect plugins
    plugins = []  # To store tuples of (raw_name, processed_name)

    for vst_file in vst_files:
        if os.path.isfile(vst_file):
            with open(vst_file, 'r') as file:
                for line in file:
                    # Extract plugin name
                    plugin_name = line.split('=')[0].strip()

                    # Process plugin name for readability
                    processed_name = plugin_name.replace("_", " ").title()
                    proper_name = plugin_name.replace("___", " - ").replace("__64_Bit_", "").replace(".vst3", "").replace("_", " ").replace("  ", " ").replace("   ", " ")

                    # Exclude plugins in the blacklist
                    if processed_name not in blacklist:
                        plugins.append((proper_name, processed_name))

    return sorted(plugins, key=lambda x: x[1])  # Sort plugins by processed name

if __name__ == "__main__":
    plugins = get_vst_plugins()
    if plugins:
        # Format plugin list for display
        plugin_list = "\n".join(f"{raw} - {processed}" for raw, processed in plugins)
        reaper.show_console_message(f"Available VST Plugins:\n{plugin_list}")
    else:
        reaper.show_console_message("No VST plugins found.")
