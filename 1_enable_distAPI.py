# Import the reapy library, which provides a way to interact with the REAPER DAW using Python.
import reapy

# Enable the REAPER distant API. 
# This allows Python to communicate with a running instance of REAPER.
# It is necessary when scripting from outside of REAPER.
reapy.config.enable_dist_api()

# Import the os module, which allows us to interact with the operating system.
import os

# Define the path to the Visual Studio Code executable. 
# You should modify this path if your VS Code is installed in a different location.
code_path = "C:\\Program Files\\Microsoft VS Code\\Code.exe"

# Open Visual Studio Code using the os.startfile() function.
# This will launch VS Code when the script is executed.
os.startfile(code_path)
