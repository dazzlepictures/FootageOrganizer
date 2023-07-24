@echo off
cd /d %~dp0\.venv\Scripts
call activate
cd /d %~dp0
start python -m http.server
start http://localhost:8000/gallery.html
python app.py
pause
