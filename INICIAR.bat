@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Bot de codigos

set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY (
  python --version >nul 2>nul && set "PY=python"
)
if not defined PY (
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if not defined PY (
  echo Python no esta instalado. Instalando Python 3.12, espera...
  winget install -e --id Python.Python.3.12 --scope user --accept-source-agreements --accept-package-agreements
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  ) else (
    echo.
    echo No pude instalar Python solo. Instalalo desde https://www.python.org/downloads/
    echo marcando "Add python.exe to PATH", y vuelve a abrir INICIAR.bat
    pause
    exit /b
  )
)
echo Usando: %PY%

if not exist ".listo" (
  echo Instalando lo necesario, solo la primera vez...
  %PY% -m pip install --upgrade playwright pyperclip || goto error
  %PY% -m playwright install chromium || goto error
  echo ok> .listo
)
%PY% chat_bot.py rubius
pause
exit /b

:error
echo.
echo Algo fallo en la instalacion. Sacale una captura a esta ventana y mandamela.
pause
