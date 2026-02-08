import streamlit as st
from google import genai
from google.genai import types
import requests
import os

# --- KONFIGURACIJA (Vnesi svoje podatke ali uporabi secrets) ---
# Če imaš te podatke v drugi datoteki, jih uvozi, sicer jih prilepi sem:
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
HA_TOKEN = st.secrets["HA_TOKEN"]
HA_URL = st.secrets["HA_URL"]

st.set_page_config(page_title="Gemini Home Manager", page_icon="🏠", layout="wide")
st.title("🏠 Gemini Smart Home Manager")

# --- 1. FUNKCIJA ZA BRANJE STANJA (GET) ---
def get_ha_states():
    url = f"{HA_URL}/api/states"
    headers = {"Authorization": f"Bearer {HA_TOKEN}", "content-type": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            lines = []
            blocked = ["Voltage", "Current", "Energy", "Power", "SSID", "IP", "update"]
            
            for entity in data:
                eid = entity['entity_id']
                state = entity['state']
                name = entity.get('attributes', {}).get('friendly_name', eid)
                
                if state in ["unavailable", "unknown"]: continue
                if any(b in name for b in blocked): continue
                
                # Filtriramo samo pomembne naprave
                if any(x in eid for x in ['light.', 'switch.', 'cover.', 'climate.', 'lock.']):
                    lines.append(f"- {name} (ID: {eid}) is {state}")
            return "\n".join(lines)
        return "Error reading HA."
    except Exception as e:
        return f"Connection Error: {e}"

# --- 2. FUNKCIJA ZA UKAZOVANJE (POST) - "ROKE" ---
def call_ha_service(service_call, entity_id):
    """Izvede akcijo, npr. ugasne luč."""
    # service_call pride v formatu "light.turn_off"
    domain, service = service_call.split(".")
    url = f"{HA_URL}/api/services/{domain}/{service}"
    headers = {"Authorization": f"Bearer {HA_TOKEN}", "content-type": "application/json"}
    payload = {"entity_id": entity_id}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

# --- 3. GEMINI CLIENT ---
@st.cache_resource
def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)

client = get_client()

# --- 4. ZGODOVINA POGOVORA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Prikaži zgodovino
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. LOGIKA AGENTA ---
if prompt := st.chat_input("Npr: Ugasni luč v garaži"):
    
    # 1. Prikaži uporabnikovo sporočilo
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Pridobi sveže stanje hiše
    house_data = get_ha_states()

    # 3. Sistemska navodila (Navodila za možgane)
    # TUKAJ JE TRIK: Naučimo ga, da izpiše poseben ukaz, če želi nekaj narediti.
    system_instruction = f"""
    You are a Smart Home Manager. 
    Current House State:
    {house_data}

    YOUR RULES:
    1. If the user asks a question, answer briefly based on the state above.
    2. IF THE USER WANTS TO CHANGE SOMETHING (turn on/off, open/close):
       DO NOT ask "Do you want me to?". Just DO IT.
       To do it, output a command in this EXACT format:
       ### ACTION: domain.service | entity_id
       
       Examples:
       User: "Turn off garage light" -> Output: ### ACTION: light.turn_off | light.garaza_main
       User: "Open blinds" -> Output: ### ACTION: cover.open_cover | cover.bedroom_blinds
    
    3. If you output an action, add a short confirmation text after it.
    """

    # 4. Sestavimo celoten kontekst (Zgodovina + Novo stanje)
    # Da ne pozabi, o čem sva govorila, mu pošljemo prejšnja sporočila
    full_conversation = system_instruction + "\n\nChat History:\n"
    for msg in st.session_state.messages[-5:]: # Zadnjih 5 sporočil za kontekst
        full_conversation += f"{msg['role'].upper()}: {msg['content']}\n"
    
    full_conversation += f"USER: {prompt}\nASSISTANT:"

    # 5. Klic AI
    with st.spinner("Thinking..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_conversation
            )
            reply_text = response.text
            
            # 6. DETEKTIV ZA UKAZE (Ali je Gemini poslal ukaz?)
            if "### ACTION:" in reply_text:
                # Razčleni ukaz
                parts = reply_text.split("### ACTION:")[1].strip().split("|")
                service_call = parts[0].strip() # npr. light.turn_off
                entity_id = parts[1].strip().split()[0] # npr. light.garaza
                
                # Izvedi ukaz v Home Assistantu
                success = call_ha_service(service_call, entity_id)
                
                if success:
                    final_reply = f"✅ Opravljeno! ({service_call} -> {entity_id})"
                else:
                    final_reply = f"❌ Napaka pri klicanju Home Assistanta."
                
                # Odstrani tehnični ukaz iz odgovora, da bo lepše izgledalo
                clean_reply = reply_text.split("### ACTION:")[0] + "\n" + final_reply
            else:
                clean_reply = reply_text

            # 7. Izpiši odgovor
            with st.chat_message("assistant"):
                st.markdown(clean_reply)
            st.session_state.messages.append({"role": "assistant", "content": clean_reply})

        except Exception as e:
            st.error(f"Error: {e}")