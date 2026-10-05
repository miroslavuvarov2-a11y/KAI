@echo off
cd /d "%~dp0"
where ollama >nul 2>nul
if errorlevel 1 (
 echo [ОШИБКА] Ollama не найден.
 echo Установи Ollama: https://ollama.com/download/windows
 pause
 exit /b 1
)
for /f "delims=" %%m in (config.txt) do set MODEL=%%m
echo Загружаю локальную модель %MODEL%...
ollama pull %MODEL%
if errorlevel 1 (
 echo Не удалось загрузить модель.
 pause
 exit /b 1
)
echo Устанавливаю Python-зависимости...
py -m pip install -r requirements.txt
if errorlevel 1 (
 echo Не удалось установить зависимости.
 pause
 exit /b 1
)
echo ГОТОВО. Теперь запускай start.bat
pause
