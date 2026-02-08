import streamlit as st
from google import genai
import requests
import os
import json

# ==========================================
# CONFIGURATION (Users must fill this in!)
# ==========================================
HA_TOKEN = "INSERT_YOUR_LONG_LIVED_ACCESS_TOKEN_HERE"
HA_URL = "http://homeassistant.local:8123" 
GEMINI_API_KEY = "INSERT_YOUR_GEMINI_API_KEY_HERE"
# ==========================================

HISTORY_FILE = "chat_history.json"

# --- Function to get Home Assistant States ---
def get_ha_states():
    """Fetches the current state of devices from Home Assistant."""
    url = f"{HA_URL}/api/states"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "content-type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            state_text = "CURRENT HOUSE STATE:\n"
            
            # Filter out technical noise to save tokens and confusion
            blocked_words = [
                "Voltage", "Current", "Power factor", "Frequency", "Energy", 
                "Apparent power", "CPU", "SSID", "IP", "Uptime", "Signal strength"
            ]
            
            count = 0
            for entity in data:
                entity_id = entity['entity_id']
                state = entity['state']
                friendly_name = entity.get('attributes', {}).get('friendly_name', entity_id)
                
                # Filter out unavailable devices
                if state in ["unavailable", "unknown"]: continue
                
                # Filter out technical sensors based on keywords
                if any(b in friendly_name for b in blocked_words): continue

                # Filter by domain (what we actually care about)
                if any(x in entity_id for x in ['light.', 'switch.', 'sensor.', 'climate.', 'weather.', 'person.', 'cover.', 'lock.', 'media_player.']):
                    state_text += f"- {friendly_name} ({entity_id}): {state}\n"
                    count += 1
            return True, state_text
        return False, "Error: Could not connect to Home Assistant."
    except Exception as e:
        return False, f"Connection Error: {e}"

# --- Memory Functions ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# --- MAIN APPLICATION ---
st.set_page_config(page_title="Gemini Smart Home", page_icon="🏡")

st.title("🏡 My Smart Home (AI Agent)")

# 1. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# 2. Sidebar Controls
with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Refresh House State"):
        st.cache_data.clear()
        st.success("State refreshed!")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        save_history([])
        st.rerun()

# 3. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Chat Input
if prompt := st.chat_input("Ask me about the house... (e.g., Are the lights on?)"):
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to session history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # --- GENERATE RESPONSE ---
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ *Checking house sensors...*")
        
        # A) Get fresh data
        success, house_state = get_ha_states()
        
        if not success:
             message_placeholder.error(house_state)
             st.stop()

        # B) Prepare prompt for Gemini
        full_prompt = (
            f"You are a helpful smart home assistant. The user asks: '{prompt}'.\n"
            f"Here is the LIVE STATUS of the house devices:\n{house_state}\n\n"
            "Rules:\n"
            "1. Answer based ONLY on the provided status.\n"
            "2. Be concise and friendly.\n"
            "3. If the user asks about something not in the list, say you don't know."
        )

        try:
            # C) Call Gemini 2.0 Flash
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            bot_response = response.text
            
            # D) Display response
            message_placeholder.markdown(bot_response)
            
            # E) Save to history
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            save_history(st.session_state.messages)
            
        except Exception as e:
            message_placeholder.error(f"Gemini API Error: {e}")