@echo off
rem Cria uma pasta nova para a live (com data e hora) e abre o Claude Code nela.
chcp 65001 >nul
for /f %%d in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm"') do set "DATA=%%d"
set "PASTA=%~dp0live-%DATA%"
mkdir "%PASTA%" 2>nul
echo Pasta criada: %PASTA%
start "" explorer "%PASTA%"
where claude >nul 2>nul
if %ERRORLEVEL%==0 (
  start "Claude Code" /D "%PASTA%" cmd /k claude
) else (
  echo Abra essa pasta no app do Claude Code e cole a mensagem do COMO-USAR.txt
  pause
)
