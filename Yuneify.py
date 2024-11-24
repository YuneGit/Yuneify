import reapy
import os
import sys
import subprocess
import json

CONFIG_FILE = "reaper_script_config.json"

def enable_api():
    """
    Configure REAPER for distant API connections.
    This replaces the deprecated enable_dist_api method.
    """
    try:
        reapy.config.configure_reaper()
        print("REAPER distant API enabled successfully.")
    except Exception as e:
        print(f"Failed to enable distant API: {e}")

def show_reaper_message(message, title="Information", box_type="ok"):
    """Show a message box in REAPER."""
    return reapy.core.reaper.reaper.show_message_box(text=message, title=title, type=box_type)

def load_config():
    """Load configuration from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            show_reaper_message(f"Failed to load config file: {e}", "Error", "ok")
    return {}

def save_config(config):
    """Save configuration to a JSON file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        show_reaper_message(f"Failed to save config file: {e}", "Error", "ok")

def prompt_for_folder(prompt_message):
    """Prompt the user to manually enter a folder path using REAPER's get_user_inputs."""
    try:
        result = reapy.core.reaper.reaper.get_user_inputs(
            "Folder Path Input",  # Title of the popup
            [prompt_message],  # Captions for the input fields
        )
        
        if not result:
            raise RuntimeError("User canceled the input prompt.")
        
        folder_path = result.get(prompt_message, "").strip()
        if os.path.exists(folder_path):
            return folder_path
        else:
            show_reaper_message("Invalid folder path. Please ensure it exists and try again.", "Error", "ok")
            sys.exit("Exiting: Folder not found.")
    
    except RuntimeError as e:
        show_reaper_message(str(e), "Input Canceled", "ok")
        sys.exit("Exiting: User canceled input.")

def locate_script_folder():
    """Locate the folder of this script, prompting if necessary."""
    config = load_config()
    if "script_folder" in config and os.path.exists(config["script_folder"]):
        return config["script_folder"]

    folder_path = prompt_for_folder(
        "Could not locate the script folder. Please enter the full path to this script's directory."
    )

    config["script_folder"] = folder_path
    save_config(config)

    return folder_path

def check_start_script(script_folder):
    """Ensure _start.py is in the specified folder."""
    start_script = os.path.join(script_folder, "_start.py")
    if not os.path.exists(start_script):
        show_reaper_message(
            f"The required '_start.py' script is missing in the folder:\n{script_folder}\n\n"
            "Please ensure '_start.py' is located in the same folder as this script.",
            "Missing Script",
            "ok",
        )
        sys.exit("Exiting: '_start.py' is missing.")
    return start_script

def locate_reaper_scripts_folder():
    """Locate the REAPER Scripts folder dynamically."""
    appdata = os.getenv("APPDATA")
    if appdata:
        print(appdata)
        reaper_folder = os.path.join(appdata, "REAPER", "Scripts")
        if os.path.exists(reaper_folder):
            return reaper_folder
    show_reaper_message("Could not locate REAPER Scripts folder. Please provide the path manually.", "Folder Not Found", "ok")
    return prompt_for_folder("Enter the full path to your REAPER Scripts folder")

def locate_vscode(default_path):
    """Locate Visual Studio Code or prompt the user for its path."""
    if os.path.exists(default_path):
        return default_path
    show_reaper_message("VS Code not found at the default location.", "VS Code Missing", "ok")
    return prompt_for_folder("Enter the full path to your VS Code executable (or press Enter to exit)")

def open_vscode(vscode_path, folder):
    """Open VS Code in the specified folder."""
    try:
        subprocess.Popen([vscode_path, folder])
        show_reaper_message(f"Visual Studio Code opened successfully in folder:\n{folder}", "VS Code Opened", "ok")
        return True
    except Exception as e:
        show_reaper_message(f"Could not open VS Code: {e}", "Error", "ok")
        return False

def run_script(script):
    """Run the specified Python script."""
    try:
        script_dir = os.path.dirname(script)
        subprocess.Popen(["python", script], cwd=script_dir, creationflags=subprocess.CREATE_NO_WINDOW)
        show_reaper_message(f"Running script: {os.path.basename(script)}", "Script Started", "ok")
    except Exception as e:
        show_reaper_message(f"Failed to run {os.path.basename(script)}: {e}", "Script Error", "ok")

def main():
    """Main execution."""
    enable_api()  # Call to configure REAPER

    script_folder = locate_script_folder()
    start_script = check_start_script(script_folder)
    reaper_scripts_folder = locate_reaper_scripts_folder()

    default_code_path = "C:\\Program Files\\Microsoft VS Code\\Code.exe"
    vscode_path = locate_vscode(default_code_path)

    if vscode_path and open_vscode(vscode_path, reaper_scripts_folder):
        run_script(start_script)
    else:
        sys.exit("Exiting: Failed to open VS Code or run script.")

if __name__ == "__main__":
    main()
