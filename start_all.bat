@echo off 
cd /d %~dp0 
set PYTHONPATH=. 
start cmd /k "uvicorn main:app --reload --host 127.0.0.1 --port 8000" 
start cmd /k "python worker.py" 
