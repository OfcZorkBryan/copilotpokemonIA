@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 app.py --open
) else (
  python app.py --open
)
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Nao foi possivel iniciar. Instale Python 3 e verifique sua configuracao.
  pause
)
