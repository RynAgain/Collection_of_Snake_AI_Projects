@echo off
:loop
start "" "http://localhost:8000/index.html"
python -m http.server 8000
timeout /t 600
taskkill /f /im python.exe
goto loop
