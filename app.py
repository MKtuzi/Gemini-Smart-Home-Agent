import streamlit as st
from streamlit_mic_recorder import speech_to_text
from google import genai
import requests
import os
import subprocess
import sys
import re

# --- AUTO-INSTALL CHECK ---
# Ensures edge-tts is available for voice synthesis without manual system install
try:
    subprocess.run(["edge-tts", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except:
    pass 

# --- CONFIGURATION ---
# Load secrets from .streamlit/secrets.toml
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    HA_TOKEN = st.secrets["HA_TOKEN"]
    HA_URL = st.secrets["HA_URL"]
except FileNotFoundError:
    st.error("⚠️ Secrets not found! Please create a .streamlit/secrets.toml file.")
    st.stop()

# --- APP SETUP ---
st.set_page_config(page_title="Gemini Smart Home", page_icon="🏠", layout="wide")
st.title("🏠 Gemini Smart Home Agent v5.0")

# --- 1. VOICE SYNTHESIS (Edge TTS) ---
def speak_text(text):
    if not text: return
    # Clean text: remove markdown bolding/italics and technical jargon for better speech
    clean_text = re.sub(r'[^\w\s,.:?!šđčćžŠĐČĆŽ-]', '', text)
    clean_text = clean_text.replace("ACTION", "").strip()
    output_file = "response_voice.mp3"
    
    try:
        # VOICE SELECTION:
        # Slovenian: "sl-SI-PetraNeural" or "sl-SI-RokNeural"
        # English: "en-US-AriaNeural"
        command = ["edge-tts", "--text", clean_text, "--write-media", output_file, "--voice", "sl-SI-PetraNeural"]
        subprocess.run(command, check=True)
        st.audio(output_file, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.warning(f"Voice Error: {e}")

# --- 2. WEATHER FORECAST RETRIEVAL ---
def get_forecast_data(entity_id):
    """Fetches 5-day forecast data from Home Assistant using the 'get_forecasts' service."""
    url = f"{HA_URL}/api/services/weather/get_forecasts"
    headers = {"Authorization": f"Bearer {HA_TOKEN}", "content-type": "application/json"}
    payload = {"entity_id": entity_id, "type": "daily"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=3)
        if response.status_code == 200:
            data = response.json()
            # Parse the nested JSON response from HA
            forecast_list = data.get(entity_id, {}).get("forecast", [])
            summary = []
            # Get today + next 2 days to save token space
            for item in forecast_list[:3]: 
                date = item.get('datetime', '')[:10]
                cond = item.get('condition', 'unknown')
                high = item.get('temperature', '?')
                low = item.get('templow', '?')
                summary.append(f"[{date}: {cond}, Max: {high}°C, Min: {low}°C]")
            return " | ".join(summary)
    except:
        return "Forecast unavailable."
    return ""

# --- 3. FETCH HOME ASSISTANT STATE ---
def get_ha_states():
    url = f"{HA_URL}/api/states"
    headers = {"Authorization": f"Bearer {HA_TOKEN}", "content-type": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            lines = []
            
            # Filter out technical entities to reduce noise for the AI
            ignore_words = [
                "update", "prerelease", "authorization", "ble_integration", 
                "auto tracking", "siren", "record", "guard", "email", "ftp", 
                "push notif", "status led", "auto lock", "keypad", "button",
                "router", "wifi", "data fetching", "shelly3em", "energy", "voltage",
                "browser", "cast", "screen", "mute", "wake", "amplifier", "version"
            ]
            
            for entity in data:
                eid = entity['entity_id']
                state = entity['state']
                attrs = entity.get('attributes', {})
                name = attrs.get('friendly_name', eid).lower()
                domain = eid.split('.')[0]
                
                if state in ["unavailable", "unknown"]: continue
                
                # --- SPECIAL WEATHER HANDLING ---
                if domain == "weather":
                    temp = attrs.get('temperature', '?')
                    hum = attrs.get('humidity', '?')
                    # Fetch forecast for this entity
                    forecast_str = get_forecast_data(eid)
                    lines.append(f"WEATHER ({name}): Current='{state}', Temp={temp}°C, Hum={hum}%. FORECAST: {forecast_str}")
                    continue

                if any(bad in name for bad in ignore_words): continue
                
                # Filter useful domains
                if domain in ['light', 'switch', 'cover', 'climate', 'lock', 'media_player', 'sensor']:
                    # Only keep relevant sensors (temp/humidity)
                    if domain == 'sensor' and not any(x in eid for x in ['temp', 'humid', 'battery']):
                        continue 
                    lines.append(f"- {name} (ID: {eid}) is {state}")
            
            return "\n".join(lines)
        return "Error reading HA."
    except:
        return "Connection Error."

# --- 4. ACTION HANDLER ---
def call_ha_service(service_call, entity_id):
    domain, service = service_call.split(".")
    url = f"{HA_URL}/api/services/{domain}/{service}"
    headers = {"Authorization": f"Bearer {HA_TOKEN}", "content-type": "application/json"}
    payload = {"entity_id": entity_id}
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.status_code == 200
    except:
        return False

# --- 5. AI SETUP ---
@st.cache_resource
def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)
client = get_client()

# --- 6. CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 7. INPUT (Text + Microphone) ---
if 'mic_key' not in st.session_state:
    st.session_state.mic_key = 0

with st.container():
    c1, c2 = st.columns([0.85, 0.15])
    with c1:
        text_input = st.chat_input("Ask Nabu something...")
    with c2:
        # Key increment ensures the mic button resets after use
        audio_text = speech_to_text(
            language='sl-SI', 
            start_prompt="🎙️", 
            stop_prompt="🛑", 
            just_once=True, 
            key=f'STT_{st.session_state.mic_key}'
        )

prompt = audio_text if audio_text else text_input

# --- 8. CORE LOGIC ---
if prompt:
    st.session_state.mic_key += 1 # Reset mic state
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    house_data = get_ha_states()

    # --- SYSTEM PROMPT (The Brains) ---
    # Customize this section for your own home!
    system_instruction = f"""
    You are Nabu, an intelligent Smart Home Agent.
    
    CURRENT HOME STATE:
    {house_data}

    YOUR RULES:
    1. **LANGUAGE:** Speak natural Slovenian (Slovenščina). Be concise.
    2. **WEATHER:** Use the provided FORECAST data in the state to answer questions about tomorrow's weather.
    3. **SLANG & ALIASES:** - "Babel", "Bubl", "Buben" -> MATCH TO: light.bubble_minir2_esp_light
       - "Close/Zapri" light -> Turn OFF
       - "Open/Odpri" light -> Turn ON
    4. **ACTIONS:** If the user wants to control a device, output strictly:
       ### ACTION: domain.service | entity_id
    """

    full_conversation = system_instruction + "\n\nChat History:\n"
    for msg in st.session_state.messages[-5:]:
        full_conversation += f"{msg['role'].upper()}: {msg['content']}\n"
    full_conversation += f"USER: {prompt}\nASSISTANT:"

    with st.spinner("Processing..."):
        try:
            response = client.models.generate_content(model="gemini-2.0-flash", contents=full_conversation)
            reply_text = response.text
            clean_reply = reply_text
            voice_reply = reply_text
            
            # Action Parser
            if "### ACTION:" in reply_text:
                try:
                    parts = reply_text.split("### ACTION:")[1].strip().split("|")
                    service_call = parts[0].strip()
                    entity_id = parts[1].strip().split()[0]
                    
                    success = call_ha_service(service_call, entity_id)
                    
                    if success:
                        voice_reply = "Urejeno."
                        clean_reply = f"✅ Urejeno: {entity_id}"
                    else:
                        voice_reply = "Napaka pri povezavi."
                        clean_reply = "❌ Napaka pri klicu HA."
                except:
                    pass

            # Display Output
            with st.chat_message("assistant"):
                st.markdown(clean_reply)
            st.session_state.messages.append({"role": "assistant", "content": clean_reply})
            
            # Speak Output
            speak_text(voice_reply)
            
            # Rerun to reset mic
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")
