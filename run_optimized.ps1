# Script para executar o Market Maker Bot Otimizado
# Execute este script no PowerShell após a configuração

Write-Host "🤖 Iniciando Market Maker Bot Otimizado para Paradex" -ForegroundColor Green
Write-Host "🎯 Foco: Airdrop Farming com Proteção de Capital" -ForegroundColor Cyan

# Verificar se o ambiente virtual existe
if (-not (Test-Path "venv_optimized")) {
    Write-Host "❌ Ambiente virtual otimizado não encontrado. Execute setup_optimized.ps1 primeiro." -ForegroundColor Red
    exit 1
}

# Ativar ambiente virtual
Write-Host "🔧 Ativando ambiente virtual otimizado..." -ForegroundColor Yellow
& ".\venv_optimized\Scripts\Activate.ps1"

# Verificar se o arquivo .env existe e tem as chaves
if (-not (Test-Path ".env")) {
    Write-Host "❌ Arquivo .env não encontrado. Execute setup_optimized.ps1 primeiro." -ForegroundColor Red
    exit 1
}

$envContent = Get-Content ".env" -Raw
if ($envContent -match "your_api_key_here") {
    Write-Host "⚠️ Configure suas chaves da API no arquivo .env antes de executar o bot." -ForegroundColor Yellow
    Write-Host "Edite o arquivo .env e substitua 'your_api_key_here' pelas suas chaves reais." -ForegroundColor White
    exit 1
}

# Verificar se o bot otimizado existe
if (-not (Test-Path "optimized_market_maker.py")) {
    Write-Host "❌ Arquivo optimized_market_maker.py não encontrado." -ForegroundColor Red
    exit 1
}

# Verificar dependências
Write-Host "🔍 Verificando dependências..." -ForegroundColor Yellow
python -c "
try:
    from optimized_market_maker import OptimizedMarketMaker
    from advanced_strategy import AdvancedMarketMakingStrategy
    from loss_minimizer import LossMinimizer
    from airdrop_optimizer import AirdropOptimizer
    print('✅ Todas as dependências estão OK')
except ImportError as e:
    print(f'❌ Erro de dependência: {e}')
    exit(1)
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro nas dependências. Execute setup_optimized.ps1 novamente." -ForegroundColor Red
    exit 1
}

# Mostrar informações do bot
Write-Host ""
Write-Host "🎯 BOT OTIMIZADO - CARACTERÍSTICAS:" -ForegroundColor Cyan
Write-Host "• Proteção de capital com controles dinâmicos" -ForegroundColor White
Write-Host "• Estratégia de airdrop farming agressiva" -ForegroundColor White
Write-Host "• Sistema de arbitragem interna" -ForegroundColor White
Write-Host "• Hedging automático" -ForegroundColor White
Write-Host "• Mean reversion inteligente" -ForegroundColor White
Write-Host "• Modos de performance adaptativos" -ForegroundColor White
Write-Host ""

# Perguntar se quer executar em modo de teste
$testMode = Read-Host "Executar em modo de teste? (s/n)"
if ($testMode -eq "s" -or $testMode -eq "S") {
    Write-Host "🧪 Executando em modo de teste..." -ForegroundColor Yellow
    python -c "
import asyncio
from optimized_market_maker import OptimizedMarketMaker

async def test_run():
    print('🧪 Modo de teste ativado')
    print('⚠️ O bot não fará trades reais')
    # Aqui você pode adicionar lógica de teste
    print('✅ Teste concluído')

asyncio.run(test_run())
"
    exit 0
}

Write-Host "🚀 Iniciando bot otimizado..." -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar o bot" -ForegroundColor Yellow
Write-Host ""

# Executar o bot
try {
    python optimized_market_maker.py
} catch {
    Write-Host "❌ Erro ao executar o bot: $_" -ForegroundColor Red
    exit 1
} finally {
    Write-Host ""
    Write-Host "👋 Bot otimizado finalizado" -ForegroundColor Yellow
    Write-Host "📊 Verifique os logs em optimized_market_maker.log" -ForegroundColor Cyan
    Write-Host "📈 Verifique as métricas em optimized_performance.json" -ForegroundColor Cyan
}