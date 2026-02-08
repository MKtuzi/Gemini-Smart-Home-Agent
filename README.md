# Gemini Smart Home Agent 🏡🤖

![Smart Home Interface](screenshot.png)

A simple, lightweight, and powerful Python client that connects **Google Gemini 2.0 Flash** directly to your **Home Assistant**.

This project allows you to chat with your smart home in natural language using a beautiful web interface (Streamlit) or a command-line tool. Unlike standard integrations, this agent uses the latest Gemini models via the `google-genai` SDK and intelligently filters sensor data to provide meaningful context without the noise.

## ✨ Features

- **🚀 Gemini 2.0 Flash:** Uses Google's latest, fastest model for near-instant responses.
- **🏠 Direct Home Assistant Connection:** Connects via API (Long-Lived Access Token). No complex add-ons or Docker containers required.
- **🧹 Smart Filtering:** Automatically ignores technical sensor data (Voltage, Amps, Signal Strength) to focus on what matters (Lights, Switches, Climate, Locks).
- **🖥️ Dual Interface:**
  - **Web App:** A modern chat interface built with Streamlit.
  - **CLI Agent:** A terminal-based version for quick testing.
- **🧠 Context Awareness:** Remembers your conversation history (stored locally).

## 🛠️ Prerequisites

Before you begin, ensure you have:

1.  **Python 3.10+** installed on your system.
2.  A **Google Gemini API Key** (Get it free at [Google AI Studio](https://aistudio.google.com/)).
3.  A **Home Assistant Long-Lived Access Token** (User Profile -> Security -> Create Token).

## 📦 Installation

1.  **Clone this repository** (or download the files):
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Gemini-Home-Agent.git](https://github.com/YOUR_USERNAME/Gemini-Home-Agent.git)
    cd Gemini-Home-Agent
    ```

2.  **Create a Virtual Environment (Optional but recommended):**
    ```bash
    # Windows
    # (or py for python)
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

**⚠️ IMPORTANT:** Never commit your actual API keys to GitHub!

1.  Open `app.py` in a text editor.
2.  Locate the configuration section at the top:
    ```python
    # ==========================================
    # CONFIGURATION
    # ==========================================
    HA_TOKEN = "INSERT_YOUR_LONG_LIVED_ACCESS_TOKEN_HERE"
    HA_URL = "[http://homeassistant.local:8123](http://homeassistant.local:8123)" # Or your local IP (e.g., [http://192.168.1.100:8123](http://192.168.1.100:8123))
    GEMINI_API_KEY = "INSERT_YOUR_GEMINI_API_KEY_HERE"
    # ==========================================
    ```
3.  Replace the placeholder text with your actual keys.
4.  Save the file.

*(Repeat these steps for `agent.py` if you plan to use the terminal version).*

## 🚀 How to Run

### Option 1: The Web App (Recommended)
Run the following command in your terminal:
```bash
streamlit run app.py

Or, if you are on Windows, simply double-click the included run_app.bat file.

Option 2: The Terminal Agent
If you prefer a text-based interface:

Bash
python agent.py
📂 Project Structure
app.py - The main application (Streamlit GUI).

agent.py - The command-line version of the agent.

requirements.txt - List of required Python libraries.

run_app.bat - Windows shortcut to launch the app.

chat_history.json - Automatically created file to store chat memory.

🤝 Contributing
Feel free to fork this project and submit pull requests. You can add more domains to the filter list or improve the system prompt in app.py.

📄 License
This project is open-source. Feel free to use it and modify it for your personal setup.

Built with ❤️ using Python, Streamlit, and Google Gemini.
