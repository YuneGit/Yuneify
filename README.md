Here’s the updated README reflecting that the code can now be run outside of REAPER and in your code IDE:

---

# REAPER MIDI and FX Control Scripts

This project includes a collection of Python scripts for **REAPER**, a popular digital audio workstation (DAW), that automates several tasks related to MIDI manipulation, plugin management, and track creation using REAPER's API and GPT-powered suggestions. 

These scripts are designed to be used with **REAPER's distant API**, which allows control of REAPER remotely from Python.

## Features

1. **Adjust MIDI Velocities**: Automatically increases the velocity of MIDI notes with velocities below 10, ensuring more consistent performances.
2. **Control Floating FX Windows**: Streamline your workflow by showing the floating FX window for the selected track via keyboard commands.
3. **Track Suggestions with GPT**: Generate and automatically create new tracks in REAPER based on AI-powered suggestions for Kontakt libraries and VST plugins.
4. **Orchestrating MIDI Notes with GPT**: Use AI to orchestrate and transpose MIDI notes, creating lush, wide voicings with open voicings in orchestration.

## Requirements

- **REAPER** installed on your system.
- **reapy** library for Python to interact with REAPER.
- **VS Code** (or any other IDE) is required for editing and customizing the scripts. It ensures compatibility with the REAPER API and allows for easy management of Python files.
- The **SWS/S&M extension** for REAPER to enable the action for floating FX window functionality.

## Installation

To install the required Python dependencies for this project, simply use the `requirements.txt` file included in the repository. This file lists all necessary packages for running the scripts.

### Step 1: Clone the repository
Clone the repository to your local machine:

```bash
git clone https://github.com/YuneGit/Reascript-Testing
cd reaper-midi-fx-control
```

### Step 2: Install dependencies using `requirements.txt`
Once you have the repository cloned, navigate to the project folder and install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install the necessary Python libraries, including `reapy`, `openai`, `pydantic`, and `keyboard`.

### How to Get an OpenAI API Key and Set It Using `setx`

To interact with OpenAI's API, you'll need an API key. Here's how to obtain and set it:

#### Step 1: Obtain the API Key
1. Visit [OpenAI's API page](https://platform.openai.com/signup) to sign up or log in.
2. Once logged in, go to the API section of your account and generate a new API key.
3. Copy the generated API key.

#### Step 2: Set the API Key in Your System
You can use the `setx` command to set the OpenAI API key as an environment variable in Windows:

1. Open **Command Prompt** (CMD) or **PowerShell**.
2. Run the following command, replacing `your_api_key_here` with the API key you copied:

   ```bash
   setx OPENAI_API_KEY "your_api_key_here"
   ```

This will set the `OPENAI_API_KEY` as an environment variable, allowing your scripts to access the key.

#### Step 3: Verify the API Key
To confirm that the API key was set correctly, you can open a new Command Prompt window and run:

```bash
echo %OPENAI_API_KEY%
```

It should display your API key. If the key is visible, you're all set!

#### Troubleshooting
If you encounter issues, make sure:
- The environment variable is set correctly and the new Command Prompt window is used.
- Your API key is valid and active by checking your OpenAI account.

Once the API key is set, your scripts will automatically use it to make requests to OpenAI's API.

## Scripts

### 1. **`AI_plugin_suggest.py`**
This script uses GPT to suggest new tracks in REAPER, based on the available VST plugins and Kontakt libraries you have. It takes a user-provided prompt (such as "Cinematic Masterpiece") and generates suggestions on which plugins to use in new tracks.

#### Key Features:
- Retrieves available Kontakt libraries and VST plugins from your system.
- Prompts you for a descriptive idea (e.g., "Cinematic Masterpiece") and a number of tracks to generate.
- Sends the prompt, Kontakt libraries, and VST plugins to **GPT** for track suggestions.
- Automatically creates new tracks in REAPER with the suggested plugins and Kontakt libraries.

#### How It Works:
- **Step 1**: The script collects available **Kontakt libraries** and **VST plugins**.
- **Step 2**: You input a **user prompt** and the number of tracks you want to create.
- **Step 3**: GPT generates track suggestions based on your input and available libraries.
- **Step 4**: The script creates tracks in REAPER with the suggested VST plugins or Kontakt libraries.

### 2. **`auto_midi_gpt.py`**
This script orchestrates MIDI notes in REAPER using GPT. It transposes and arranges your MIDI notes into wider voicings with a focus on open, lush arrangements.

#### Key Features:
- Transposes and orchestrates MIDI notes in REAPER based on ChatGPT's suggestions.
- Sends your MIDI notes to GPT for orchestration, and the AI returns a structured response for the notes' new arrangement.
- Imports the orchestrated notes back into REAPER automatically after receiving the response.

#### How It Works:
- **Step 1**: The script collects the MIDI notes from the selected item in REAPER.
- **Step 2**: Sends the MIDI notes to **GPT** for orchestration, providing a style guide to avoid close voicings and focus on wide octaves.
- **Step 3**: GPT processes the notes and provides a new orchestration.
- **Step 4**: The script then imports the orchestrated notes back into REAPER and places them in the active track.

### 3. **`auto_midi_vel+10.py`**
This script increases the velocity of all MIDI notes with velocities below 10 by +10. This is useful for creating more dynamic and consistent MIDI items by avoiding low-velocity notes.

### 4. **`auto_open_plugin.py`**
This script monitors the `Alt` key press and automatically opens the floating FX window for the selected track when the key is pressed, helping you manage your effects more efficiently.

## How to Use

### 1. **Set Up REAPER** 
- Install **REAPER** and the **SWS/S&M extension**.
- Open your REAPER project.

### 2. **Enable Distant API**
You can now run **`1_enable_distAPI.py`** directly in your code IDE (like VS Code) to enable the REAPER distant API and open a UI that lets you toggle the scripts on and off. Ensure you have all dependencies installed for this feature to work.

```bash
python 1_enable_distAPI.py
```

### 3. **Run Scripts**
- **Run `auto_midi_vel+10.py`** to adjust MIDI velocities automatically:
  ```bash
  python auto_midi_vel+10.py
  ```
- **Run `auto_open_plugin.py`** to open the floating FX window with the `Alt` key press:
  ```bash
  python auto_open_plugin.py
  ```
- **Run `AI_plugin_suggest.py`** to generate track suggestions using GPT based on your available plugins and libraries:
  ```bash
  python AI_plugin_suggest.py
  ```
- **Run `auto_midi_gpt.py`** to orchestrate MIDI notes with GPT:
  ```bash
  python auto_midi_gpt.py
  ```

### 4. **Customizing the Scripts**
Customization of the scripts is required to fit your specific needs. Open the scripts in **VS Code**, which is the recommended environment for editing, and modify parameters such as velocity thresholds, key bindings, or the number of tracks generated. You can easily open them in **VS Code** by running the following script using the "ReaScript: Run ReaScript" command in REAPER:

```bash
1_enable_distAPI.py
```

This will open the project folder in **VS Code**, allowing you to make any adjustments you need.

## License

This project is licensed under the **GNU General Public License**. See the [LICENSE](LICENSE) file for more details.
