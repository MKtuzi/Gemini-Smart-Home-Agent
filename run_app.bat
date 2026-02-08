@echo off
TITLE Gemini Smart Home
echo Starting Streamlit Application...
cd /d "%~dp0"
call venv\Scripts\activate
streamlit run app.py