@echo off
REM Ruleaza scriptul cu Python-ul corect (cel care are ollama instalat)
python -m pip install -r "%~dp0requirements.txt"
python "%~dp0tool_financial_risk_scorer.py"
pause
