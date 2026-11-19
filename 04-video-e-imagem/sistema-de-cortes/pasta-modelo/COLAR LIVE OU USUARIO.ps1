# COLAR LIVE OU USUARIO
#  - link de LIVE ou VÍDEO (ao vivo ou já acabou): corta essa live (uma vez).
#  - link de PERFIL ou só o NOME do usuário: acompanha esse streamer SEMPRE (grava toda live dele).
# O trabalho pesado roda aqui, sem o Claude. O Claude só entra no fim (títulos, aprovar e cortar).
$ErrorActionPreference = "Stop"
$Skill = Join-Path $HOME ".claude\skills\sistema-de-cortes"
$Python = Join-Path $Skill ".venv\Scripts\python.exe"
$Perfis = Join-Path $PSScriptRoot "PERFIS"
$Memoria = Join-Path $PSScriptRoot "ultimas-respostas.json"
$env:PYTHONPATH = $Skill
$env:PYTHONIOENCODING = "utf-8"
function Sistema { & $Python -m sistema_cortes @args }  # Python direto: o "&" dos links do YouTube não quebra
function Fechar($codigo) { Read-Host "Enter para fechar"; exit $codigo }

Write-Host ""
Write-Host "  COLAR LIVE OU USUARIO" -ForegroundColor Cyan
Write-Host "  - link de uma live (ao vivo ou que já acabou)  -> corta essa live"
Write-Host "  - link do perfil ou só o nome do usuário        -> acompanha SEMPRE (grava toda live dele)"
Write-Host ""
if (-not (Test-Path $Python)) {
    Write-Host "O sistema ainda não está preparado. Rode o instalar.ps1 de novo." -ForegroundColor Red
    Fechar 1
}

$entrada = (Read-Host "Cole aqui").Trim()
if (-not $entrada) { exit }
$info = Sistema entender $entrada | ConvertFrom-Json
if ($info.precisa_plataforma) {
    $p = Read-Host "Esse usuário é de onde? 1 = Twitch, 2 = Kick, 3 = YouTube"
    $plat = @{ "1" = "twitch"; "2" = "kick"; "3" = "youtube" }[$p.Trim()]
    if (-not $plat) { Write-Host "Opção inválida." -ForegroundColor Red; Fechar 1 }
    $info = Sistema entender $entrada --plataforma $plat | ConvertFrom-Json
}
if (-not $info.url) { Write-Host "Não entendi o que foi colado." -ForegroundColor Red; Fechar 1 }
$url = $info.url

# Lembra a permissão, o @ e a quantidade da última vez (Enter = repetir)
$ultimo = @{ permissao = ""; arroba = ""; quantos = "5" }
if (Test-Path $Memoria) {
    $j = Get-Content $Memoria -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($k in @("permissao", "arroba", "quantos")) { if ($j.$k) { $ultimo[$k] = [string]$j.$k } }
}
function Perguntar($texto, $padrao) {
    $dica = if ($padrao) { " [Enter = $padrao]" } else { "" }
    $r = (Read-Host "$texto$dica").Trim()
    if ($r) { return $r } else { return $padrao }
}
$permissao = Perguntar "Onde está a permissão do streamer (programa de cortes, print...)" $ultimo.permissao
if (-not $permissao -or $permissao.Length -lt 5) {
    Write-Host "Sem permissão do streamer não dá para cortar (o canal toma strike)." -ForegroundColor Red
    Fechar 1
}
$padraoArroba = if ($info.tipo -eq "perfil") { "@" + $info.canal } else { $ultimo.arroba }
$arroba = Perguntar "@ do streamer para o crédito" $padraoArroba

# ------------------------------------------------------------------ PERFIL: acompanhar sempre
if ($info.tipo -eq "perfil") {
    @{ permissao = $permissao; arroba = $arroba; quantos = $ultimo.quantos } | ConvertTo-Json | Set-Content $Memoria -Encoding UTF8
    New-Item -ItemType Directory -Force -Path $Perfis | Out-Null
    Sistema --pasta $Perfis perfil adicionar $url --permissao $permissao --arroba $arroba
    if ($LASTEXITCODE -ne 0) { Fechar 1 }
    $batimento = Join-Path $Perfis ".acompanhando"
    $aberta = (Test-Path $batimento) -and ((Get-Date) - (Get-Item $batimento).LastWriteTime).TotalSeconds -lt 120
    if ($aberta) {
        Write-Host "Pronto. A janela que acompanha os perfis já está aberta e pega este em até 30 s." -ForegroundColor Green
        Fechar 0
    }
    Write-Host ""
    Write-Host "Acompanhando os perfis da pasta PERFIS. Quando um deles entrar ao vivo, grava e acha os momentos." -ForegroundColor Green
    Write-Host "DEIXE ESTA JANELA ABERTA (pode minimizar) e o PC ligado. Para parar, feche a janela." -ForegroundColor Yellow
    Write-Host "Os momentos vão para PERFIS\pendentes. Para revisar, abra o Claude Code na pasta PERFIS e escreva:"
    Write-Host "   continue o sistema de cortes nesta pasta" -ForegroundColor Cyan
    Write-Host ""
    Sistema --pasta $Perfis ao-vivo tudo
    Fechar $LASTEXITCODE
}

# ------------------------------------------------------------------ LIVE / VÍDEO: uma vez
$quantos = Perguntar "Quantos cortes" $ultimo.quantos
@{ permissao = $permissao; arroba = $arroba; quantos = $quantos } | ConvertTo-Json | Set-Content $Memoria -Encoding UTF8

# É o VOD de uma live que já acompanhamos ao vivo? Então usa a MESMA pasta (completa só o começo).
$pasta = $null
$anteriores = @(Get-ChildItem $PSScriptRoot -Directory | Where-Object { Test-Path (Join-Path $_.FullName "live.json") } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 5)
if ($anteriores.Count -gt 0) {
    Write-Host ""
    Write-Host "Lives que você já acompanhou ao vivo:"
    for ($i = 0; $i -lt $anteriores.Count; $i++) { Write-Host "  $($i + 1). $($anteriores[$i].Name)" }
    $n = Read-Host "Esse link é o VOD de uma delas? Digite o número (Enter = não, é live nova)"
    if ($n -match '^\d+$' -and [int]$n -ge 1 -and [int]$n -le $anteriores.Count) {
        $pasta = $anteriores[[int]$n - 1].FullName
        Write-Host "Vou completar o começo dessa live." -ForegroundColor Green
    }
}
if (-not $pasta) {
    $pasta = Join-Path $PSScriptRoot ("live-" + $info.canal + "-" + (Get-Date -Format "yyyy-MM-dd_HH-mm"))
    New-Item -ItemType Directory -Force -Path $pasta | Out-Null
}
Write-Host ""
Write-Host "Pasta: $pasta"
Write-Host "Pode minimizar esta janela, mas NÃO feche e deixe o PC ligado." -ForegroundColor Yellow
Write-Host ""
$argumentos = @("--pasta", $pasta, "link", $url, "--permissao", $permissao, "--quantos", $quantos)
if ($arroba) { $argumentos += @("--arroba", $arroba) }
Sistema @argumentos
$codigo = $LASTEXITCODE
Write-Host ""
if ($codigo -eq 0) {
    Write-Host "TERMINEI A PARTE PESADA." -ForegroundColor Green
    Write-Host "Agora abra o Claude Code nesta pasta e escreva:"
    Write-Host "   continue o sistema de cortes nesta pasta" -ForegroundColor Cyan
    Write-Host "(ele escreve os títulos, te mostra a lista para aprovar e corta)"
} else {
    Write-Host "Parou com aviso ou erro (veja acima). Abra o Claude Code nesta pasta e mande um print." -ForegroundColor Red
}
Start-Process explorer.exe $pasta
Fechar $codigo
