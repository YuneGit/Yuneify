# REAPER MIDI and FX Control

Yuneify is a project that improves and speeds up your workflow in **REAPER**. These scripts automate various tasks related to MIDI manipulation, plugin management, and track management using REAPER's API and GPT-powered suggestions. 

The scripts are designed to work with **REAPER's distant API**, enabling remote control of REAPER from Python. 
Running Yuneify.py will enable it and provides a UI to run the scripts.

Alternatively, to manually enable the **REAPER's distant API** you can also run the following command in your terminal (make sure your terminal is open in the project directory)
```bash
pip install -r requirements.txt
python -c "import reapy; reapy.configure_reaper()"
```

---

## Features

1. **Adjust MIDI Velocities**: Automatically increase MIDI note velocities below 10 for more consistent performances.
2. **Control Floating FX Windows**: Open the floating FX window for the selected track using keyboard commands.
3. **Track Suggestions with GPT**: Generate and create new tracks in REAPER based on AI-powered suggestions for Kontakt libraries and VST plugins.
4. **Orchestrate MIDI Notes with GPT**: Use AI to transpose and orchestrate MIDI notes, creating lush open voicings in orchestral arrangements.
5. **MIDI Suite**: Perform a variety of MIDI manipulations, including velocity adjustment, pitch transposition, randomization, quantization, and more.

---

## Requirements

- **REAPER** installed on your system.
- **`reapy`** Python library for interacting with REAPER. (included in requirements.txt)
- **VS Code** (or any IDE) for editing and customizing scripts.
- **SWS/S&M Extension** for REAPER to enable floating FX window functionality.

---

## Installation

Follow these steps to install the required Python dependencies and set up the environment:

### Step 1: Clone the Repository
Clone the repository to your local machine:

```bash
git clone https://github.com/YuneGit/Yuneify
cd Yuneify
```

### Step 2: Install Dependencies
Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install necessary Python libraries such as `reapy`, `openai`, `pydantic`, and `keyboard`.

---

## Setting Up the OpenAI API Key (Optional)

To use the AI-powered features, you'll need an OpenAI API key.

### Step 1: Obtain the API Key
1. Visit [OpenAI's API page](https://platform.openai.com/signup) to sign up or log in.
2. Go to the API section of your account and generate a new API key.
3. Copy the generated API key.

### Step 2: Set the API Key
Set the API key as an environment variable in Windows using the `setx` command:

```bash
setx OPENAI_API_KEY "your_api_key_here"
```

### Step 3: Verify the API Key
Open a new Command Prompt and verify the key:

```bash
echo %OPENAI_API_KEY%
```

If the key is displayed, the setup is complete.

---

## Scripts

### 1. **`Yuneify.py`**
Launches a user-friendly UI for running other scripts and opens **VS Code** in the project folder for easy customization.

---

### 2. **`Plugin Suggestion Suite.py`**
Generates track suggestions in REAPER based on available VST plugins and Kontakt libraries.

#### Key Features:
- Retrieves available Kontakt libraries and VST plugins.
- Prompts you for a descriptive idea (e.g., "Cinematic Masterpiece") and generates track suggestions using GPT.
- Automatically creates tracks in REAPER with the suggested plugins and libraries.

---

### 3. **`MIDI AI.py`**
Orchestrates and transposes MIDI notes using GPT for lush, open arrangements.

#### Key Features:
- Extracts MIDI notes from REAPER and sends them to GPT for orchestration.
- Imports orchestrated notes back into REAPER.

---

### 4. **`MIDI Suite.py`**
A comprehensive tool for MIDI manipulations, including:
- Velocity adjustment
- Pitch transposition
- Randomization
- Quantization
- More

---

### 5. **`Auto VST Window.py`**
Monitors the `Alt` key and automatically opens the floating FX window for the selected track.

---

## How to Use

### Prerequisite: Install Dependencies
Complete the steps in the **Installation** section.

---

### 1. Set Up REAPER
1. Install **REAPER** and the **SWS/S&M Extension**.
2. Enable Python in REAPER:
   - Go to Preferences → Plug-ins → ReaScript.
   - Check **Enable Python for use with ReaScript**.
   - Specify the Python DLL (e.g., `python312.dll`).

---

### 2. Run `Yuneify.py`
Run the following command to launch the main script:

```bash
python Yuneify.py
```

This script provides a UI for running other scripts and opens the Reaper Distance API so you can run scripts from your terminal.

---

### 3. Run Individual Scripts (Optional)

- **Run `MIDI Suite.py`** for MIDI manipulations:
  ```bash
  python MIDI Suite.py
  ```
- **Run `Auto VST Window.py`** to manage FX windows:
  ```bash
  python Auto VST Window.py
  ```
- **Run `Plugin Suggestion Suite.py`** for GPT-generated track suggestions:
  ```bash
  python Plugin Suggestion Suite.py
  ```
- **Run `MIDI AI.py`** to orchestrate MIDI notes:
  ```bash
  python MIDI AI.py
  ```

---

### 4. Customize Scripts
Open the project folder in **VS Code** (via `Yuneify.py`) to edit parameters like velocity thresholds, key bindings, and track generation settings.

---

## License

This project is licensed under the **MIT License** with a **Commons Clause**. See the [LICENSE](LICENSE) file for details.
```

This revision improves clarity, consistency, and formatting to make the markdown more user-friendly and professional.
