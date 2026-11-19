@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Bot de codigos
where python >nul 2>nul
if errorlevel 1 (
  echo Instalando Python...
  winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
  echo.
  echo Python instalado. CIERRA esta ventana y vuelve a abrir INICIAR.bat
  pause
  exit /b
)
if not exist ".listo" (
  echo Instalando lo necesario, solo la primera vez...
  python -m pip install --upgrade playwright pyperclip
  python -m playwright install chromium
  echo ok> .listo
)
python chat_bot.py rubius
pause
