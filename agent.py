from google import genai
import requests
import os

# ==========================================
# CONFIGURATION
# ==========================================
HA_TOKEN = "INSERT_YOUR_LONG_LIVED_ACCESS_TOKEN_HERE"
HA_URL = "http://homeassistant.local:8123" 
GEMINI_API_KEY = "INSERT_YOUR_GEMINI_API_KEY_HERE"
# ==========================================

def get_ha_states():
    """Fetches device states from Home Assistant API."""
    url = f"{HA_URL}/api/states"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "content-type": "application/json",
    }

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
                friendly_name = entity.get('attributes', {}).get('friendly_name', entity_id)
                
                if state in ["unavailable", "unknown"]: continue
                if any(word in friendly_name for word in blocked_words): continue

                if any(x in entity_id for x in ['light.', 'switch.', 'sensor.', 'climate.', 'cover.', 'lock.']):
                    state_text += f"- {friendly_name} ({entity_id}): {state}\n"
                    count += 1
            
            print(f"✅ Success! Retrieved status of {count} devices.")
            return state_text
        else:
            return f"Error: Home Assistant returned code {response.status_code}"
    except Exception as e:
        return f"Connection Error: {e}"

def main():
    print("\n--- 🤖 GEMINI HOME AGENT (CLI v3.0) 🤖 ---\n")
    
    house_state = get_ha_states()
    
    if "Error" in house_state:
        print(house_state)
        return

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        MODEL_NAME = "gemini-2.0-flash" 

        print(f"🧠 Initializing model {MODEL_NAME}...")

        chat = client.chats.create(model=MODEL_NAME)
        
        system_instruction = (
            "You are a smart home assistant. Below is the current status of all devices.\n"
            "Your task: Answer questions about the house. Be brief and friendly.\n"
            f"{house_state}"
        )

        print("📤 Sending context to Gemini...")
        response = chat.send_message(system_instruction)
        
        print(f"\nGemini: {response.text}\n")
        print("💬 Agent ready! (Type 'exit' to quit)\n")

        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'stop']:
                break
            
            response = chat.send_message(user_input)
            print(f"Gemini: {response.text}")

    except Exception as e:
        print(f"\n❌ Gemini Error: {e}")

if __name__ == "__main__":
    main()