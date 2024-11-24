import os

# Blacklist to exclude specific folder names (user should fill this with their entries)
BLACKLIST = set()  # Example: {"example folder 1", "example folder 2"}

def get_folder_names(library_path):
    """
    Retrieves a list of folder names in the specified library path, 
    excluding those present in the blacklist.
    """
    try:
        # List all directories, filtering out blacklisted names
        return [
            name for name in os.listdir(library_path) 
            if os.path.isdir(os.path.join(library_path, name)) and name.lower().strip() not in BLACKLIST
        ]
    except Exception as e:
        print(f"Error accessing {library_path}: {e}")
        return []
