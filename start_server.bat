@echo off
echo Starting MYUBER Server...
cd server
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause

