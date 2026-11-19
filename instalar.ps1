<#
  INSTALADOR DO REPERTÓRIO DE SKILLS + PASTA DE CORTES (Windows)

  O que faz:
    1. Instala o que falta: ffmpeg, Python 3.12, yt-dlp e streamlink (pelo winget).
    2. Copia as skills deste repositório para %USERPROFILE%\.claude\skills\ (o Claude Code acha sozinho).
    3. Prepara o sistema de cortes (.venv com faster-whisper e numpy, uma vez só).
    4. Cria a pasta de cortes com o COMO-USAR.txt, o nova-live.cmd e o modelo de streamers.

  Como rodar (PowerShell aberto na pasta do repositório):
    powershell -ExecutionPolicy Bypass -File .\instalar.ps1                    -> skills essenciais (recomendado)
    powershell -ExecutionPolicy Bypass -File .\instalar.ps1 -Todas             -> TODAS as skills (gasta mais token)
    powershell -ExecutionPolicy Bypass -File .\instalar.ps1 -Skills ffmpeg,tdd  -> essenciais + as que você escolher
    Opções: -PastaCortes D:\cortes   -SemProgramas   -SemPreparar

  Por que não instala todas por padrão: o Claude Code lê o nome e a descrição de TODA skill instalada
  em toda conversa. Com 500+ skills isso gasta muito token à toa (regra do LEIA-ME.md: só use skill
  quando precisar). As outras continuam no repositório; o índice fica em %USERPROFILE%\.claude\repertorio-de-skills\INDICE.md
  Rodar de novo é seguro: atualiza as skills e não apaga nada seu.
#>
param(
    [switch]$Todas,
    [string[]]$Skills = @(),
    [string]$PastaCortes = (Join-Path $HOME "cortes"),
    [switch]$SemProgramas,
    [switch]$SemPreparar
)

$ErrorActionPreference = "Stop"
$Repo = $PSScriptRoot
$DestinoSkills = Join-Path $HOME ".claude\skills"
$Essenciais = @("sistema-de-cortes", "editar-video-ffmpeg", "ffmpeg")
# Pastas que NÃO viram skill: versões repetidas, notas e cópias que já vêm dentro dos plugins.
$Ignorar = @(".git", "22-versoes-alternativas", "23-notas-e-guias-dos-repositorios", "25-plugins-prontos")

function Passo($texto) { Write-Host ""; Write-Host "==> $texto" -ForegroundColor Cyan }
function Tem($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function TemPython {
    if (Tem "py") { return $true }
    $p = Get-Command python -ErrorAction SilentlyContinue
    return [bool]($p -and $p.Source -notlike "*WindowsApps*")  # o "python" da Microsoft Store é só um atalho
}
function RecarregarPath {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

# ------------------------------------------------------------------ 1. programas
if (-not $SemProgramas) {
    Passo "1/4 Programas (ffmpeg, Python, yt-dlp, streamlink)"
    if (-not (Tem "winget")) {
        Write-Warning "winget não encontrado. Instale o 'Instalador de Aplicativo' pela Microsoft Store e rode de novo."
    } else {
        $programas = @(
            @{ Nome = "ffmpeg";     Id = "Gyan.FFmpeg";           Tem = { Tem "ffmpeg" } },
            @{ Nome = "Python 3.12"; Id = "Python.Python.3.12";   Tem = { TemPython } },
            @{ Nome = "yt-dlp";     Id = "yt-dlp.yt-dlp";         Tem = { Tem "yt-dlp" } },
            @{ Nome = "streamlink"; Id = "Streamlink.Streamlink"; Tem = { Tem "streamlink" } }
        )
        foreach ($p in $programas) {
            if (& $p.Tem) { Write-Host "  ok: $($p.Nome)"; continue }
            Write-Host "  instalando $($p.Nome)..."
            winget install --id $p.Id -e --silent --accept-source-agreements --accept-package-agreements | Out-Host
        }
        RecarregarPath  # o winget só atualiza o PATH em janela nova; aqui recarregamos na mão
    }
}

# ------------------------------------------------------------------ 2. skills
Passo "2/4 Skills"
$sep = [IO.Path]::DirectorySeparatorChar
$achadas = Get-ChildItem -Path $Repo -Recurse -Filter "SKILL.md" -File | Where-Object {
    $rel = $_.FullName.Substring($Repo.Length).TrimStart('\', '/')
    $Ignorar -notcontains ($rel -split '[\\/]')[0]
} | ForEach-Object { $_.Directory.FullName } | Sort-Object { $_.Length }

# Skill dentro de outra skill (ex.: video-use\skills\...) vai junto com a de fora, não sozinha.
$raizes = New-Object System.Collections.Generic.List[string]
foreach ($pasta in $achadas) {
    $dentro = $false
    foreach ($r in $raizes) { if ($pasta.StartsWith($r + $sep)) { $dentro = $true; break } }
    if (-not $dentro) { $raizes.Add($pasta) }
}
$porNome = @{}
foreach ($pasta in $raizes) {
    $nome = Split-Path $pasta -Leaf
    if ($porNome.ContainsKey($nome)) { Write-Warning "Nome repetido, fico com a primeira: $nome"; continue }
    $porNome[$nome] = $pasta
}

if ($Todas) {
    $escolhidas = @($porNome.Keys | Sort-Object)
    Write-Warning "Instalando TODAS ($($escolhidas.Count)). Cada conversa vai gastar mais token com a lista de skills."
} else {
    $escolhidas = @($Essenciais + $Skills | Select-Object -Unique)
}

New-Item -ItemType Directory -Force -Path $DestinoSkills | Out-Null
$instaladas = 0
foreach ($nome in $escolhidas) {
    if (-not $porNome.ContainsKey($nome)) { Write-Warning "Skill não encontrada no repositório: $nome"; continue }
    $alvo = Join-Path $DestinoSkills $nome
    # robocopy /E copia por cima (atualiza) sem apagar o que já existe lá, como o .venv do sistema de cortes
    robocopy $porNome[$nome] $alvo /E /XD __pycache__ .pytest_cache .venv /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { Write-Warning "Falhou ao copiar $nome (robocopy $LASTEXITCODE)"; continue }
    $instaladas++
}
Write-Host "  $instaladas skill(s) em $DestinoSkills"

$repertorio = Join-Path $HOME ".claude\repertorio-de-skills"
New-Item -ItemType Directory -Force -Path $repertorio | Out-Null
foreach ($arq in @("INDICE.md", "LEIA-ME.md", "ORIGENS.md")) {
    $origem = Join-Path $Repo $arq
    if (Test-Path $origem) { Copy-Item $origem $repertorio -Force }
}
Write-Host "  índice de todas as skills: $repertorio\INDICE.md"

# ------------------------------------------------------------------ 3. sistema de cortes
$skillCortes = Join-Path $DestinoSkills "sistema-de-cortes"
$atalho = Join-Path $skillCortes "cortes.cmd"
if ((Test-Path $atalho) -and -not $SemPreparar) {
    Passo "3/4 Preparando o sistema de cortes (baixa uns 200 MB na primeira vez)"
    & $atalho preparar
    if ($LASTEXITCODE -ne 0) { Write-Warning "O preparar falhou. Rode depois: `"$atalho`" preparar" }
    & $atalho diagnostico
} else {
    Passo "3/4 Sistema de cortes: pulado"
}

# ------------------------------------------------------------------ 4. pasta de cortes
Passo "4/4 Pasta de cortes"
$modelo = Join-Path $skillCortes "pasta-modelo"
New-Item -ItemType Directory -Force -Path $PastaCortes, (Join-Path $PastaCortes "ao-vivo") | Out-Null
if (Test-Path $modelo) {
    Copy-Item (Join-Path $modelo "COMO-USAR.txt") $PastaCortes -Force
    Copy-Item (Join-Path $modelo "nova-live.cmd") $PastaCortes -Force
    Copy-Item (Join-Path $modelo "COLAR LIVE OU USUARIO.cmd") $PastaCortes -Force
    Copy-Item (Join-Path $modelo "COLAR LIVE OU USUARIO.ps1") $PastaCortes -Force
    New-Item -ItemType Directory -Force -Path (Join-Path $PastaCortes "PERFIS") | Out-Null
    foreach ($velho in @("colar-link.cmd", "colar-link.ps1")) { Remove-Item (Join-Path $PastaCortes $velho) -ErrorAction SilentlyContinue }
    $exemplo = Join-Path $skillCortes "streamers.exemplo.json"
    if (Test-Path $exemplo) { Copy-Item $exemplo (Join-Path $PastaCortes "ao-vivo") -Force }
}
Write-Host "  $PastaCortes"

Write-Host ""
Write-Host "PRONTO." -ForegroundColor Green
Write-Host "1. Feche e abra o Claude Code (para ele achar as skills novas)."
Write-Host "2. Abra $PastaCortes\COMO-USAR.txt e siga o passo a passo."
Start-Process notepad.exe (Join-Path $PastaCortes "COMO-USAR.txt") -ErrorAction SilentlyContinue
