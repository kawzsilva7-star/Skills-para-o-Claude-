@echo off
rem Atalho do sistema de cortes: cortes.cmd <comando>  (ex.: cortes.cmd diagnostico)
setlocal
set "SKILL=%~dp0"
set "SKILL=%SKILL:~0,-1%"
set "PYTHONPATH=%SKILL%"
set "PYTHONIOENCODING=utf-8"
if exist "%SKILL%\.venv\Scripts\python.exe" (
  "%SKILL%\.venv\Scripts\python.exe" -m sistema_cortes %*
  exit /b %ERRORLEVEL%
)
rem Sem .venv ainda: usa o Python do sistema (serve para diagnostico e preparar)
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 -m sistema_cortes %*
) else (
  python -m sistema_cortes %*
)
exit /b %ERRORLEVEL%
