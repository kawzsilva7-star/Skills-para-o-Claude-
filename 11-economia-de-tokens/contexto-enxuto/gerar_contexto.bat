@echo off
setlocal

:: Gera um arquivo so com as skills escolhidas, para gastar menos token.
:: Procura primeiro skills\<nome>.txt e, se nao achar, a pasta <nome>\SKILL.md
:: dentro deste repositorio (a primeira que encontrar).

set "RAIZ=%~dp0..\.."
set "OUT=%CD%\contexto_enxuto.txt"

echo ^<regras_ativas^> > "%OUT%"
echo Execute APENAS as skills listadas. Ignore funcoes nao mencionadas. Combine-as se houver mais de uma. >> "%OUT%"

echo ========================================
echo GERADOR DE CONTEXTO OTIMIZADO
echo ========================================
echo Use o nome da pasta da skill (veja INDICE.md). Ex.: copywriting ffmpeg seo-audit
set /p "selecao=Digite as skills separadas por espaco: "

for %%s in (%selecao%) do call :adicionar "%%~s"

echo ^</regras_ativas^> >> "%OUT%"
echo.
echo Sucesso! Arquivo "%OUT%" gerado.
echo Envie este arquivo ao Claude ou aponte o MCP para ele.
pause
exit /b

:adicionar
set "ACHOU="
if exist "skills\%~1.txt" set "ACHOU=skills\%~1.txt"
if not defined ACHOU for /d /r "%RAIZ%" %%d in (*) do (
    if not defined ACHOU if /i "%%~nxd"=="%~1" if exist "%%d\SKILL.md" set "ACHOU=%%d\SKILL.md"
)
if not defined ACHOU (
    echo [AVISO] Skill "%~1" nao encontrada.
    exit /b
)
echo Adicionando: %~1
echo [Skill: %~1] >> "%OUT%"
type "%ACHOU%" >> "%OUT%"
echo. >> "%OUT%"
exit /b
