from google import genai
import requests
import os

# ==========================================
# CONFIGURATION
# ==========================================
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmMzM5YzljNzcwNzA0MGJiYTZjY2E1MGJjZTI1NmRjZCIsImlhdCI6MTc3MDUxNzcxMSwiZXhwIjoyMDg1ODc3NzExfQ.nh9S1CQAgkP87ZwEoHclEr7jTHyKam74TWjvC7PTbzM"
HA_URL = "http://homeassistant.local:8123" 
GEMINI_API_KEY = "AIzaSyCeixrtiyoXUeAVzwJJC54QfvVia1Wp0EI"
# ==========================================

def get_ha_states():
    """Fetches device states from Home Assistant API."""
    url = f"{HA_URL}/api/states"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "content-type": "application/json",
    }

    # --- TUKAJ DODAJ SVOJE VZDEVKE (ALIASES) ---
    # Format: "entity_id": "Vzdevek"
    # Entity ID najdeš v Home Assistantu pod Settings -> Devices -> Entities
    CUSTOM_ALIASES = {
        "light.garage_main_light_minir2_esp_light": "Bubble",
        "light.dnevna_soba": "Big Light",
        "cover.blinds_bedroom": "Morning Blinds"
    }
    # -------------------------------------------

    try:
        print("🔌 Connecting to Home Assistant...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            state_text = "CURRENT HOUSE STATE:\n"
            count = 0
            
            blocked_words = [
                "Voltage", "Current", "Power factor", "Frequency", "Energy", 
                "Apparent power", "CPU usage", "SSID", "IP Address", "Uptime",
                "Signal strength", "BSSID"
            ]

            for entity in data:
                entity_id = entity['entity_id']
                state = entity['state']
                
                # Get the default friendly name from HA
                friendly_name = entity.get('attributes', {}).get('friendly_name', entity_id)
                
                # --- CHECK FOR ALIAS (PREVERI VZDEVEK) ---
                if entity_id in CUSTOM_ALIASES:
                    nickname = CUSTOM_ALIASES[entity_id]
                    # We modify the name so Gemini sees both
                    friendly_name = f"{friendly_name} (Alias: {nickname})"
                # -----------------------------------------
                
                if state in ["unavailable", "unknown"]: continue
                if any(word in friendly_name for word in blocked_words): continue

                # Filter for specific device types
                if any(x in entity_id for x in ['light.', 'switch.', 'sensor.', 'climate.', 'cover.', 'lock.']):
                    state_text += f"- {friendly_name} ({entity_id}): {state}\n"
                    count += 1
            
            print(f"✅ Success! Retrieved status of {count} devices.")
            return state_text
        else:
            return f"Error: Home Assistant returned code {response.status_code}"
    except Exception as e:
        return f"Connection Error: {e}"