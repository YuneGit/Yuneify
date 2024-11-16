import os

# Define the blacklist of folder names (in lowercase)
BLACKLIST = [
    "blocks base",
    "blocks primes",
    "butch vig drums library",
    "cloud supply library",
    "community drive",
    "community drive 2021",
    "decoded forms",
    "deep matter",
    "drive",
    "expansions selection",
    "elastic thump",
    "form",
    "halcyon sky",
    "hypha",
    "india",
    "indigo dust",
    "kinetic metal",
    "kinetic treats",
    "lilac glare",
    "lo-fi glow library",
    "london grit",
    "lucid mission",
    "mechanix",
    "mikro prism",
    "modular icons library",
    "moebius",
    "molten veil",
    "monark",
    "neon drive",
    "nocturnal state",
    "polyplex",
    "previews",
    "prism",
    "pulse",
    "queensbridge story",
    "rising crescent",
    "rounds",
    "rush",
    "scene",
    "solar breeze",
    "velvet lounge",
    "spark",
    "spectrum quake",
    "stadium flex",
    "the finger",
    "true school"
    "trk-01",
    "trk-01 bass",
    "trk-01 kick",
    "scarbee a-200",
    "scarbee clavinet pianet",
    "scarbee mark i library",
    "scarbee mm-bass",
    "scarbee rickenbacker bass",
]

def get_folder_names(library_path):
    # Get a list of all folders in the specified path
    try:
        # List all directories and filter out the blacklisted names
        return [
            name for name in os.listdir(library_path) 
            if os.path.isdir(os.path.join(library_path, name)) and name.lower().strip() not in BLACKLIST
        ]
    except Exception as e:
        print(f"Error accessing {library_path}: {e}")
        return []

# This block allows the script to be run directly or imported without executing the code below
if __name__ == "__main__":
    kontakt_library_path = "D:\\SynthContent"
    folders = get_folder_names(kontakt_library_path)
    print(folders)
