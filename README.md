3. Install dependencies
Install the required Python libraries by running:

Bash
pip install -r requirements.txt
4. Configure Secrets (CRITICAL 🔐)
To keep your passwords safe, this app uses a specific file that is not shared on the internet.

Inside the Gemini-Smart-Home-Agent folder, create a new folder named .streamlit.

Inside that folder, create a new text file named secrets.toml.

File structure should look like this:

Plaintext
Gemini-Smart-Home-Agent/
├── .streamlit/
│   └── secrets.toml   <-- You create this file
├── app.py
├── requirements.txt
└── ...
Content of secrets.toml: Open the file with a text editor (like Notepad or VS Code) and paste this:

Ini, TOML
GEMINI_API_KEY = "YOUR_GOOGLE_API_KEY_HERE"
HA_TOKEN = "YOUR_LONG_LIVED_ACCESS_TOKEN_FROM_HA"
HA_URL = "[http://192.168.1.50:8123](http://192.168.1.50:8123)"
💡 How to get HA_TOKEN: Go to your Home Assistant Profile (click your icon at the bottom left) -> Scroll down to Long-Lived Access Tokens -> Click Create Token -> Name it "Gemini" -> Copy the long string.

5. Run the App 🚀
In your terminal, run:

Bash
streamlit run app.py
This will automatically open the app in your web browser.

⚙️ Customization
Open app.py in a code editor to tailor the agent to your home.

Change Language / Voice
Find the speak_text function in the code. Change "sl-SI-PetraNeural" to:

"en-US-AriaNeural" (English)

"de-DE-KatjaNeural" (German) (Any voice supported by Edge TTS)

Custom Aliases (Slang)
In the system_instruction variable (towards the bottom of the script), you can add your own rules so Gemini understands your specific nicknames.

Example inside the code:

Python
# Find this section inside system_instruction string:

"""
...
RULES:
1. If user says "Man Cave", they mean "light.basement_led".
2. If user says "Party Mode", activate "script.party_time".
...
"""
🤝 Contributing
Feel free to fork this project and submit pull requests!

Created by MKtuzi
