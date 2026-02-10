import streamlit as st
from streamlit_mic_recorder import speech_to_text
from google import genai
import requests
import os
import subprocess
import sys
import re

# --- AUTO-INSTALL FOR EDGE-TTS ---
# This ensures the voice library is installed without manual pip commands
try:
    subprocess.run(["edge-tts", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except:
    pass 

# --- CONFIGURATION (Load from secrets) ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    HA_TOKEN = st.secrets["HA_TOKEN"]
    HA_URL = st.secrets["HA_URL"]
except FileNotFoundError:
    st.error("Secrets not found! Please create .streamlit/secrets.toml")
    st.stop()

# --- APP SETUP ---
st.set_page_config(page_title="Gemini Smart Home", page_icon="🏠", layout="wide")
st.title("🏠 Gemini Smart Home Agent v5.0")

# --- 1. VOICE FUNCTION (Microsoft Edge TTS) ---
def speak_text(text):
    if not text: return
    # Clean text (remove markdown bolding, technical jargon)
    clean_text = re.sub(r'[^\w\s,.:?!šđčćžŠĐČĆŽ-]', '', text)
    clean_text = clean_text.replace("ACTION", "").strip()
    output_file = "response_voice.mp3"
    try:
        # Using Slovenian voice 'Petra'. Change to 'en-US-AriaNeural' for English.
        command = ["edge-tts", "--text", clean_text, "--write-media", output_file, "--voice", "sl-SI-PetraNeural"]
        subprocess.run(command, check=True)
        st.audio(output_file, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.warning(f"Voice Error (Edge TTS): {e}")

# --- 2. GET WEATHER FORECAST (Special Service Call) ---
def get_forecast_data(entity_id):
    """Fetches daily forecast data from Home Assistant if available."""
    url = f"{HA_URL}/api/services/weather/get_forecasts"
    headers = {"Authorization": f"Bearer {HA_TOKEN}", "content-type": "application/json"}
    payload = {"entity_id": entity_id, "type": "daily"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=3)
        if response.status_code == 200:
            data = response.json()
            forecast_list = data.get(entity_id, {}).get("forecast", [])
            summary = []
            for item in forecast_list[:3]: # Get today + next 2 days
                date = item.get('datetime', '')[:10]
                cond = item.get('condition', 'unknown')
                high = item.get('temperature', '?')
                low = item.get('templow', '?')
                summary.append(f"[{date}: {cond}, Max: {high}°C, Min: {low}°C]")
            return " | ".join(summary)
    except:
        return "Forecast not available via API."
    return ""

# --- 3. FETCH HOUSE STATE ---
def get_ha_states():
    url = f"{HA_URL}/api/states"
    headers = {"Authorization": f"Bearer {HA_TOKEN}", "content-type": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            lines = []
            
            # Filter out technical entities to save tokens and confusion
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
                
                # --- WEATHER LOGIC ---
                if domain == "weather":
                    temp = attrs.get('temperature', '?')
                    hum = attrs.get('humidity', '?')
                    # Try to fetch forecast
                    forecast_str = get_forecast_data(eid)
                    lines.append(f"WEATHER_ENTITY ({name}): Current='{state}', Temp={temp}°C, Hum={hum}%. FORECAST: {forecast_str}")
                    continue

                if any(bad in name for bad in ignore_words): continue
                
                if domain in ['light', 'switch', 'cover', 'climate', 'lock', 'media_player', 'sensor']:
                    # Only keep relevant sensors
                    if domain == 'sensor' and not any(x in eid for x in ['temp', 'humid', 'battery']):
                        continue 
                    lines.append(f"- {name} (ID: {eid}) is {state}")
            
            return "\n".join(lines)
        return "Error reading Home Assistant."
    except:
        return "Connection Error."

# --- 4. EXECUTE ACTIONS ---
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

# --- 5. AI CLIENT ---
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

# --- 7. INPUT AREA (Mic + Text) ---
if 'mic_key' not in st.session_state:
    st.session_state.mic_key = 0

with st.container():
    c1, c2 = st.columns([0.85, 0.15])
    with c1:
        text_input = st.chat_input("Ask about your home...")
    with c2:
        # Just_once=True helps preventing the mic from getting stuck
        audio_text = speech_to_text(
            language='sl-SI', # CHANGE LANGUAGE HERE IF NEEDED
            start_prompt="🎙️", 
            stop_prompt="🛑", 
            just_once=True, 
            key=f'STT_{st.session_state.mic_key}'
        )

prompt = audio_text if audio_text else text_input

# --- 8. MAIN AGENT LOGIC ---
if prompt:
    st.session_state.mic_key += 1 # Reset mic for next turn
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    house_data = get_ha_states()

    # --- SYSTEM PROMPT ---
    system_instruction = f"""
    You are an intelligent Smart Home Agent connected to Home Assistant.
    
    CURRENT HOME STATE:
    {house_data}

    YOUR RULES:
    1. **LANGUAGE:** Speak natural Slovenian (Slovenščina). Keep responses concise.
    2. **WEATHER:** If available, use the FORECAST data provided in the state. If user asks about tomorrow, look at the forecast string.
    3. **SLANG & DEVICE MATCHING:**
       - "Babel", "Bubl", "Buben" -> MATCH TO: light.bubble_minir2_esp_light
       - "Zapri/Close" light -> MATCH TO: Turn OFF
       - "Odpri/Open" light -> MATCH TO: Turn ON
    4. **ACTIONS:** If the user wants to control a device, output strictly:
       ### ACTION: domain.service | entity_id
    """

    full_conversation = system_instruction + "\n\nHistory:\n"
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
                        voice_reply = "Urejeno." # Short voice reply
                        clean_reply = f"✅ Urejeno: {entity_id}"
                    else:
                        voice_reply = "Napaka pri povezavi."
                        clean_reply = "❌ Napaka pri klicu HA."
                except:
                    pass

            # Output
            with st.chat_message("assistant"):
                st.markdown(clean_reply)
            st.session_state.messages.append({"role": "assistant", "content": clean_reply})
            
            # Text-to-Speech
            speak_text(voice_reply)
            
            # Rerun to reset mic state
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")
