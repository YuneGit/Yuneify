# Import the reapy library, which provides a way to interact with the REAPER DAW using Python.
import reapy

# Enable the REAPER distant API. 
# This allows Python to communicate with a running instance of REAPER.
# It is necessary when scripting from outside of REAPER.
reapy.config.enable_dist_api()

# Import the os module, which allows us to interact with the operating system.
import os
import sys
import subprocess

# Define the default path to the Visual Studio Code executable. 
# Modify this path if your VS Code is installed in a different location.
default_code_path = "C:\\Program Files\\Microsoft VS Code\\Code.exe"

# Function to show a message box in REAPER
def show_reaper_message(message, title="Information", box_type="ok"):
    return reapy.core.reaper.reaper.show_message_box(text=message, title=title, type=box_type)

# Track whether VS Code was opened already
vs_code_opened = False

# Check if the default path exists.
if os.path.exists(default_code_path):
    # If VS Code is found at the default path, open it.
    os.startfile(default_code_path)
    
    # Show the "found and opened" message only the first time
    if not vs_code_opened:
        show_reaper_message("Visual Studio Code found and opened successfully.", "VS Code Status", "ok")
        vs_code_opened = True  # Mark that VS Code has been opened

else:
    # If VS Code is not found, prompt the user to locate their VS Code installation.
    show_reaper_message("Visual Studio Code not found at the default location.", "VS Code Status", "ok-cancel")
    
    user_input = input("Do you have VS Code installed? (yes/no): ").lower()

    if user_input == "yes":
        # Prompt the user to locate the VS Code executable manually.
        code_path = input("Please enter the full path to your VS Code executable (e.g., C:\\path\\to\\Code.exe): ").strip()
        if os.path.exists(code_path):
            # If the provided path exists, open VS Code.
            os.startfile(code_path)
            
            # Show the "found and opened" message only the first time
            if not vs_code_opened:
                show_reaper_message(f"Visual Studio Code found at {code_path} and opened successfully.", "VS Code Status", "ok")
                vs_code_opened = True  # Mark that VS Code has been opened
        else:
            show_reaper_message("The provided path does not exist. Please ensure you enter the correct path.", "Error", "ok")
            sys.exit(1)
    elif user_input == "no":
        # Offer to install VS Code if it isn't found.
        show_reaper_message("You can download and install Visual Studio Code from: https://code.visualstudio.com/Download", "VS Code Not Installed", "ok")
        user_input = input("Would you like to continue working with REAPER without VS Code? (yes/no): ").lower()
        if user_input != "yes":
            sys.exit("Exiting because VS Code is not installed and not provided.")
    else:
        show_reaper_message("Invalid response. Please answer 'yes' or 'no'.", "Error", "ok")
        sys.exit(1)

# The script will continue to work with REAPER regardless of whether VS Code is opened or installed.
# You can proceed with other REAPER tasks here.
