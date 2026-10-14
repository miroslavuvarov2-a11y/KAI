@echo off
chcp 65001 >nul
title KAI Local Desktop
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
 echo Python не найден. Установи Python 3.10+: https://www.python.org/downloads/windows/
 echo При установке отметь Add Python to PATH.
 pause
 exit /b 1
)
where ollama >nul 2>nul
if errorlevel 1 (
 echo Ollama не найдена. Установи: https://ollama.com/download/windows
 pause
 exit /b 1
)
start "" ollama serve
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8790
python server.py
pause
