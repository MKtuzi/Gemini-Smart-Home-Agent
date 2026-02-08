# 🏠 Gemini Smart Home Agent (v4.0)

![App Screenshot](screenshot.png)

A personalized AI Agent powered by **Google Gemini 2.0 Flash** that connects directly to your **Home Assistant**. It doesn't just read data—it can control your home (lights, blinds, switches) using natural language!

## 🚀 Features (Kaj zna)
- **🧠 Natural Language Understanding:** Understands context, follow-up questions, and aliases (e.g., "Bubble" for garage light).
- **👀 Live House State:** Reads real-time status of lights, switches, covers, and sensors.
- **⚡ Active Control:** Can turn devices ON/OFF, open/close blinds, and unlock doors upon request.
- **🛡️ Secure:** Uses strict file handling (secrets are hidden in `.streamlit/secrets.toml`) and runs locally via Streamlit.

## 🛑 Limitations (Česa (še) ne zna)
- **No Dashboard Editing:** Cannot modify Lovelace dashboards or UI cards.
- **No Permanent Automations:** Can execute commands *now*, but cannot create background schedules in Home Assistant directly.

---

## 🛠️ Installation & Setup

Follow these steps to run the agent on your own computer (Windows).

### 1. Prerequisites
- Python 3.10 or newer.
- A **Home Assistant** instance (local IP).
- A **Gemini API Key** (from Google AI Studio).

### 2. Download the code
Clone this repository or download the ZIP file.

### 3. Set up the environment (Windows)
Open your terminal (PowerShell) in the project folder and run:

```powershell
# 1. Create a virtual environment
py -m venv venv

# 2. Activate the environment
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

4. Configure Secrets (Important!) 🔐
This agent uses a secure way to store passwords so they don't end up on GitHub.

Create a new folder named .streamlit inside your project folder.

Inside that folder, create a file named secrets.toml.

Paste your keys into secrets.toml:

GEMINI_API_KEY = "your_google_api_key_here"
HA_TOKEN = "your_home_assistant_token_here"
HA_URL = "[http://192.168.](http://192.168.)x.x:8123"

5. Run the App 🚀
Run this command in your terminal:

PowerShell
py -m streamlit run app.py
