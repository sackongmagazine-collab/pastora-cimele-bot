@echo off
cd /d "D:\pastora_cimele_bot"

for /f "tokens=2" %%p in ('wmic process where "name='pythonw.exe' or name='python.exe'" get ProcessId^,CommandLine /format:csv ^| findstr /i "pastora_cimele_bot\\main.py"') do taskkill /F /PID %%p >nul 2>&1

timeout /t 3 /nobreak >nul
start "" /MIN python main.py >> bot_run.log 2>&1
echo Bot iniciado.
timeout /t 2 >nul