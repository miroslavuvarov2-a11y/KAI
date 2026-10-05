@echo off
cd /d "%~dp0"
for /f "delims=" %%m in (config.txt) do set KAI_MODEL=%%m
echo KAI Local Voice
echo Модель: %KAI_MODEL%
echo Открой: http://127.0.0.1:8790
py server.py
pause
