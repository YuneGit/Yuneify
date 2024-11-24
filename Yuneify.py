import reapy
import os
import sys
import subprocess
import psutil  # Import psutil to check running processes

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

def locate_script_folder():
    """Locate the folder of this script."""
    return os.path.dirname(os.path.abspath(__file__))

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

def locate_vscode(default_path):
    """Locate Visual Studio Code or return None if it's not found."""
    if os.path.exists(default_path):
        return default_path
    return None  # Return None if VS Code is not found at the default path

def open_vscode(vscode_path, folder):
    """Open VS Code in the specified folder."""
    try:
        subprocess.Popen([vscode_path, folder])
        show_reaper_message(f"Visual Studio Code opened successfully in folder:\n{folder}", "VS Code Opened", "ok")
        return True
    except Exception as e:
        show_reaper_message(f"Could not open VS Code: {e}", "Error", "ok")
        return False

def is_vscode_running():
    """Check if VS Code is already running."""
    for proc in psutil.process_iter(attrs=['name']):
        try:
            if proc.info['name'] == "Code.exe":
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
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

    script_folder = locate_script_folder()  # Automatically determine the folder where the script resides
    start_script = check_start_script(script_folder)  # Verify that _start.py exists in the folder

    default_code_path = "C:\\Program Files\\Microsoft VS Code\\Code.exe"
    vscode_path = locate_vscode(default_code_path)

    # Check if VS Code is installed and not running already
    if vscode_path:
        if not is_vscode_running():  # Check if VS Code is not running
            if open_vscode(vscode_path, script_folder):  # Open VS Code in the script folder
                run_script(start_script)
            else:
                sys.exit("Exiting: Failed to open VS Code or run script.")
        else:
            show_reaper_message("Visual Studio Code is already running, skipping launch.", "VS Code Already Running", "ok")
            run_script(start_script)
    else:
        # If VS Code is not found, skip the opening process silently
        run_script(start_script)

if __name__ == "__main__":
    main()
