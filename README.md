# 🏠 Gemini Smart Home Agent (v4.0)

![App Screenshot](screenshot.png)

A personalized AI Agent powered by **Google Gemini 2.0 Flash** that can talk to your **Home Assistant**. It doesn't just read data—it can control your home!

## 🚀 Features (Kaj zna)
- **🧠 Natural Language Understanding:** Understands context, follow-up questions, and aliases (e.g., "Bubble" for garage light).
- **👀 Live House State:** Reads real-time status of lights, switches, covers, and sensors.
- **⚡ Active Control:** Can turn devices ON/OFF, open/close blinds, and unlock doors upon request.
- **🛡️ Secure:** Uses strict file handling (secrets are hidden) and runs locally via Streamlit.

## 🛑 Limitations (Česa (še) ne zna)
- **No Dashboard Editing:** Cannot modify Lovelace dashboards or UI cards.
- **No Permanent Automations:** Can execute commands *now*, but cannot create background schedules or automations in Home Assistant directly.
- **No History Logs:** Does not read past history (e.g., "When was the light turned on yesterday?"), only current state.

## 🛠️ Setup
1. Clone the repo.
2. Create `.streamlit/secrets.toml` with your API keys.
3. Run `py -m streamlit run app.py`.

---
*Built with Python, Streamlit, and Gemini AI.*


