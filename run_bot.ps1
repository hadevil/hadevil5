# Script para executar o Market Maker Bot
# Execute este script no PowerShell após a configuração

Write-Host "🤖 Iniciando Market Maker Bot para Paradex" -ForegroundColor Green

# Verificar se o ambiente virtual existe
if (-not (Test-Path "venv")) {
    Write-Host "❌ Ambiente virtual não encontrado. Execute setup_windows.ps1 primeiro." -ForegroundColor Red
    exit 1
}

# Ativar ambiente virtual
Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Verificar se o arquivo .env existe e tem as chaves
if (-not (Test-Path ".env")) {
    Write-Host "❌ Arquivo .env não encontrado. Execute setup_windows.ps1 primeiro." -ForegroundColor Red
    exit 1
}

$envContent = Get-Content ".env" -Raw
if ($envContent -match "your_api_key_here") {
    Write-Host "⚠️ Configure suas chaves da API no arquivo .env antes de executar o bot." -ForegroundColor Yellow
    Write-Host "Edite o arquivo .env e substitua 'your_api_key_here' pelas suas chaves reais." -ForegroundColor White
    exit 1
}

# Verificar se o bot existe
if (-not (Test-Path "market_maker_bot.py")) {
    Write-Host "❌ Arquivo market_maker_bot.py não encontrado." -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Iniciando bot..." -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar o bot" -ForegroundColor Yellow
Write-Host ""

# Executar o bot
try {
    python market_maker_bot.py
} catch {
    Write-Host "❌ Erro ao executar o bot: $_" -ForegroundColor Red
    exit 1
} finally {
    Write-Host ""
    Write-Host "👋 Bot finalizado" -ForegroundColor Yellow
}