# 🏠 Gemini Smart Home Agent v5.0

A powerful, lightweight, and voice-enabled Smart Home Assistant powered by **Google Gemini 2.0 Flash**.
This Python application connects directly to your **Home Assistant** instance, allowing you to control your home using natural language (Voice or Text).

![Demo](demo_v2.png)

## 🚀 New in v5.0
- **🗣️ Natural Voice Output:** Uses Microsoft Edge TTS (Petra Neural) for high-quality Slovenian/English speech.
- **🌦️ Advanced Weather:** Reads 5-day forecasts directly from Home Assistant's `weather.get_forecasts` service.
- **🧠 Smart Context:** Understands slang (e.g., "Buben" = Bubble Light) and filters out system noise.
- **🎙️ Walkie-Talkie Mode:** Improved microphone handling for faster commands.

## 🛠️ Features
- **Control Devices:** Turn lights on/off, open blinds, lock doors.
- **Query State:** "Is the garage door open?", "What's the temperature in the living room?"
- **Future Cast:** "Will it rain tomorrow?" (Uses real forecast data).
- **Secure:** API keys are stored safely in `.streamlit/secrets.toml`.

---

## 📦 Installation & Setup

### 1. Prerequisites
- Python 3.10 or newer.
- A **Home Assistant** instance (accessible via LAN or Nabu Casa).
- A **Google Gemini API Key** (Get it free at [Google AI Studio](https://aistudio.google.com/)).

### 2. Clone the repository
```bash
git clone [https://github.com/MKtuzi/Gemini-Smart-Home-Agent.git](https://github.com/MKtuzi/Gemini-Smart-Home-Agent.git)
cd Gemini-Smart-Home-Agent
