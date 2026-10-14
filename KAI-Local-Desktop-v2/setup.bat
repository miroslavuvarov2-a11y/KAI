@echo off
chcp 65001 >nul
title KAI Local Desktop - Setup
echo Подготовка KAI Local Desktop...
where ollama >nul 2>nul
if errorlevel 1 (
 echo Ollama не найдена. Установи: https://ollama.com/download/windows
 pause
 exit /b 1
)
ollama pull qwen3:4b
if errorlevel 1 (
 echo Не удалось загрузить модель. Проверь интернет и место на диске.
 pause
 exit /b 1
)
echo Готово! Теперь запусти start.bat
pause
