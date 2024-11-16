# Import necessary modules and dependencies
from openai import OpenAI  # Import OpenAI module for interacting with the GPT API
import reapy  # ReaScript API for interacting with the REAPER digital audio workstation
from dependencies.list_Kontakt_VST import get_folder_names  # Import function to get folder names for Kontakt libraries
from dependencies.list_VST import get_vst_plugins  # Import function to list VST plugins
from dependencies.insert_Kontakt_Track import add_track_with_kontakt  # Import function to add a Kontakt track
from dependencies import insert_Track  # Import script for adding a standard VST plugin track
import re  # Import Python's regular expression library

# Initialize the OpenAI client
client = OpenAI()

# Function to generate track suggestions using GPT based on user input and available plugins/libraries
def get_gpt_suggestions(user_prompt, vst_plugins, kontakt_folders, num_tracks=3):
    """
    Generate suggestions for new tracks using GPT based on a user prompt,
    a list of available VST plugins, and Kontakt libraries.

    Args:
        user_prompt (str): Description or theme for composing music.
        vst_plugins (list): List of available VST plugins.
        kontakt_folders (list): List of available Kontakt library folders.
        num_tracks (int): Number of track suggestions to generate.

    Returns:
        str: GPT-generated suggestions for new tracks.
    """
    
    # Construct a combined prompt with the user input and available libraries
    combined_prompt = (
        f"I am composing something about: {user_prompt}\n\n"
        f"Here are the Kontakt libraries I own:\n" +
        "\n".join(kontakt_folders) + 
        "\n\n"
        f"Here are the VST plugins I own:\n" +
        "\n".join([re.sub(r'\.vst3$', '', plugin[0]) for plugin in vst_plugins]) +  # Remove ".vst3" extension
        "\n\n"
        f"Please provide {num_tracks} suggestions for new tracks.\n"
        f"Please give one suggestion per track.\n"
        f"Repeat the same plugin multiple times to keep a consistent sound.\n"
        f"Respond in the following format:\n"
        f"VST Plugin: [Your VST Plugin]\n"
        f"or Kontakt Library: [Your Kontakt Library]"        
    )

    # Make a request to the OpenAI GPT model to get suggestions
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Specify the model to use
        messages=[
            {"role": "system", "content": "No markdown."},
            {"role": "user", "content": combined_prompt}
        ]
    )
    
    print(combined_prompt)  # Print the prompt for debugging
    return completion.choices[0].message.content.strip()  # Return the suggestions

# Function to create a new track with a Kontakt library
def create_new_kontakt_track(track_name=None, index=0):
    """
    Create a new track in REAPER using a Kontakt library.

    Args:
        track_name (str): Name of the Kontakt library to use.
        index (int): Index of the track in the REAPER project.
    """
    add_track_with_kontakt(reapy.Project(), track_name, index)

# Function to create a new track with a standard VST plugin
def create_new_track(plugin_name=None):
    """
    Create a new track in REAPER using a standard VST plugin.

    Args:
        plugin_name (str): Name of the VST plugin to use.
    """
    insert_Track.main(plugin_name)

# Main function to orchestrate the track creation workflow
def main():
    """
    Main function to:
    1. Retrieve available Kontakt libraries and VST plugins.
    2. Collect user input for composing new tracks.
    3. Generate and display track suggestions using GPT.
    4. Create tracks in REAPER based on the suggestions.
    """
    
    # Path to the Kontakt library folder
    kontakt_library_path = "D:\\SynthContent"

    # Get a list of Kontakt library folder names
    kontakt_folders = get_folder_names(kontakt_library_path)
    
    # Get a list of available VST plugins
    vst_plugins = get_vst_plugins()

    # Display available Kontakt libraries
    print("Kontakt Libraries:")
    for folder in kontakt_folders:
        print(folder)

    # Display available VST plugins
    print("\nVST Plugins:")
    for plugin in vst_plugins:
        print(f"{plugin[0]} - {plugin[1]}")  # Print formatted VST plugin list

    # Prompt user for the number of tracks and a descriptive prompt
    title = "Track Creation"
    captions = ["Number of Tracks", "User Prompt"]
    user_inputs = reapy.core.reaper.reaper.get_user_inputs(title, captions)

    # Extract the number of tracks to generate (default to 3 if not specified)
    num_tracks = int(user_inputs.get("Number of Tracks", 3))
    
    # Extract the user's descriptive prompt (default to "Cinematic Masterpiece." if not specified)
    user_prompt = user_inputs.get("User Prompt", "Cinematic Masterpiece.")

    # Get track suggestions from GPT
    suggestions = get_gpt_suggestions(user_prompt, vst_plugins, kontakt_folders, num_tracks=num_tracks)
    print("\nGPT Suggestions:")
    print(suggestions)

    # Parse GPT suggestions into individual track components
    lines = suggestions.splitlines()
    track_suggestions = []

    # Process each suggestion line-by-line
    for line in lines:
        line = line.strip()
        if "VST Plugin:" in line:
            plugin_name = line.split(": ")[1].strip()  # Extract the VST plugin name
            print(f"Assigned VST Plugin: {plugin_name}")  # Debugging output
        elif "Kontakt Library:" in line:
            kontakt_library = line.split(": ")[1].strip()  # Extract the Kontakt library name
            print(f"Assigned Kontakt Library: {kontakt_library}")  # Debugging output

            # Save the suggestion once both plugin and library names are assigned
            if 'plugin_name' in locals() and 'kontakt_library' in locals():
                track_suggestions.append({"plugin": plugin_name, "library": kontakt_library})

    # Create tracks in REAPER based on the suggestions
    for suggestion in track_suggestions:
        plugin_name = suggestion.get("plugin")
        kontakt_library = suggestion.get("library")
        
        print(f"\nCreating track:")
        print(f"VST Plugin: {plugin_name}")
        print(f"Kontakt Library: {kontakt_library}")

        if plugin_name and kontakt_library:
            create_new_kontakt_track(track_name=kontakt_library)  # Create a Kontakt track
            create_new_track(plugin_name=plugin_name)  # Create a VST plugin track
        else:
            print("Error: One of the required variables is not assigned. Please check the suggestions.")

# Entry point for the script
if __name__ == "__main__":
    main()
