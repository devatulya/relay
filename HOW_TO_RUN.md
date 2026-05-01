# Influenze Relay - Setup & Run Guide

This guide is for the team members to easily download, setup, and run the Influenze Relay WhatsApp Automation tool on their local Windows computers.

## Method 1: The 1-Click Method (Recommended)

The easiest way to run this tool without any command line knowledge is to use the automated `start.bat` file.

1. **Download the Code:** Go to the GitHub repository, click the green **Code** button, and select **Download ZIP**.
2. **Extract:** Right-click the downloaded ZIP file and click "Extract All..." to extract the folder.
3. **Run:** Open the extracted folder and double-click the `start.bat` file.
4. **Wait:** A black Command Prompt window will open. It will automatically install everything it needs (this might take a minute on the first run).
5. **Open Dashboard:** Once you see `Starting Influenze Relay Backend...`, open your web browser (Chrome/Edge) and go to: `http://localhost:5000`

> [!WARNING]
> Do **NOT** close the black Command Prompt window while you are using the tool. Closing it will shut down the server.

---

## Method 2: Manual Command Prompt Method

If you prefer to manually run the commands yourself, follow these steps:

### 1. Prerequisites
You must have Python installed. 
- Download Python from [python.org](https://www.python.org/downloads/). 
- **CRITICAL:** When running the installer, you *must* check the box at the bottom that says **"Add Python.exe to PATH"** before clicking Install.

### 2. Setup (First Time Only)
Open the Command Prompt (press Windows key, type `cmd`, and hit Enter).
Navigate to the folder where you extracted the code. For example:
```cmd
cd C:\Users\YourName\Downloads\relay-main
```

Create a virtual environment to isolate the packages:
```cmd
python -m venv venv
```

Activate the virtual environment:
```cmd
venv\Scripts\activate
```

Install the required Python packages:
```cmd
pip install -r requirements.txt
```

Install the browser automation engine:
```cmd
playwright install chromium
```

### 3. Running the Tool (Every Time)
Whenever you want to use the tool, open Command Prompt, navigate to the folder, activate the environment, and run the app:

```cmd
cd C:\Users\YourName\Downloads\relay-main
venv\Scripts\activate
python run.py
```
Then, open your web browser and go to `http://localhost:5000`.

---

## Common Fixes & Troubleshooting

If you run into issues, check this list first:

> [!CAUTION]
> **Issue:** `'python' is not recognized as an internal or external command`
> **Fix:** Python is not installed properly. Re-download the Python installer. Run it, and make absolutely sure you check the box that says **"Add Python.exe to PATH"**.

> [!WARNING]
> **Issue:** WhatsApp Web refuses to load or says browser is unsupported.
> **Fix:** Run the command `playwright install chromium` inside your activated environment. This updates the hidden browser to the latest version.

> [!NOTE]
> **Issue:** The tool randomly crashed or stopped sending.
> **Fix:** Look at the black Command Prompt window. It logs exactly what caused the crash. You can safely close the window, double-click `start.bat` again, and resume from where you left off. The Google Sheet is automatically updated, so you won't double-message people.

> [!TIP]
> **Issue:** How do I safely stop a campaign?
> **Fix:** You can click the "Stop" button in the web dashboard. Alternatively, you can click on the black Command Prompt window and press `Ctrl + C`. This will safely kill the server.
