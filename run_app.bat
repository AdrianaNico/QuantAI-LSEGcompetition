@echo off
REM Ruleaza interfata grafica Streamlit cu Python-ul corect
python -m pip install -r "%~dp0requirements.txt"
python -m streamlit run "%~dp0app.py"
pause
