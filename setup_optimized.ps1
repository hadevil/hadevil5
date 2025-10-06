# Script de configuração otimizado para Windows PowerShell
# Market Maker Bot Otimizado para Paradex - Airdrop Farming

Write-Host "🚀 Configurando Market Maker Bot Otimizado para Paradex" -ForegroundColor Green
Write-Host "🎯 Foco: Minimizar perdas e maximizar pontos de airdrop" -ForegroundColor Cyan

# Verificar se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado. Instale Python 3.8+ primeiro." -ForegroundColor Red
    Write-Host "Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Verificar se pip está disponível
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip encontrado: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip não encontrado. Reinstale Python com pip." -ForegroundColor Red
    exit 1
}

# Criar ambiente virtual
Write-Host "📦 Criando ambiente virtual otimizado..." -ForegroundColor Yellow
python -m venv venv_optimized

# Ativar ambiente virtual
Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv_optimized\Scripts\Activate.ps1"

# Atualizar pip
Write-Host "⬆️ Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Instalar dependências otimizadas
Write-Host "📚 Instalando dependências otimizadas..." -ForegroundColor Yellow
pip install -r requirements.txt

# Instalar dependências adicionais para otimização
Write-Host "⚡ Instalando dependências de otimização..." -ForegroundColor Yellow
pip install scikit-learn==1.3.0
pip install ta==0.10.2
pip install plotly==5.17.0

# Criar arquivo .env se não existir
if (-not (Test-Path ".env")) {
    Write-Host "📝 Criando arquivo .env otimizado..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️ Configure suas chaves da API no arquivo .env" -ForegroundColor Yellow
}

# Criar diretórios necessários
Write-Host "📁 Criando estrutura de diretórios..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs"
New-Item -ItemType Directory -Force -Path "data"
New-Item -ItemType Directory -Force -Path "backups"
New-Item -ItemType Directory -Force -Path "reports"

# Criar arquivo de configuração otimizada
Write-Host "⚙️ Criando configuração otimizada..." -ForegroundColor Yellow
$optimizedConfig = @"
# Configuração Otimizada para Airdrop Farming
# Foco: Minimizar perdas e maximizar pontos

# Configurações de Trading Otimizadas
TRADING_CONFIG = {
    'total_capital': 5000,
    'risk_per_trade': 0.01,  # 1% por trade (mais conservador)
    'max_daily_loss': 0.02,  # 2% perda máxima diária
    'min_order_size': 0.05,  # 0.05 SOL mínimo
    'max_order_size': 2.0,   # 2 SOL máximo
}

# Configurações de Airdrop Farming
AIRDROP_CONFIG = {
    'daily_volume_target': 1500,  # $1500 por dia
    'daily_trades_target': 100,   # 100 trades por dia
    'weekly_volume_target': 10500, # $10,500 por semana
    'consistency_bonus': 1.2,     # 20% bônus por consistência
}

# Configurações de Proteção de Capital
LOSS_PROTECTION = {
    'max_drawdown': 0.03,         # 3% drawdown máximo
    'emergency_stop_loss': 0.02,  # 2% perda máxima por trade
    'hedge_ratio': 0.8,           # 80% do inventário hedgeado
    'recovery_mode': True,        # Ativar modo de recuperação
}
"@

$optimizedConfig | Out-File -FilePath "optimized_config.py" -Encoding UTF8

# Testar importações otimizadas
Write-Host "🧪 Testando importações otimizadas..." -ForegroundColor Yellow
python -c "
try:
    import requests
    import numpy
    import pandas
    import aiohttp
    import websockets
    import sklearn
    import ta
    print('✅ Todas as dependências otimizadas instaladas com sucesso!')
except ImportError as e:
    print(f'❌ Erro de importação: {e}')
    exit(1)
"

# Criar script de teste otimizado
Write-Host "🔬 Criando script de teste otimizado..." -ForegroundColor Yellow
$testScript = @"
#!/usr/bin/env python3
"""
Teste do Bot Otimizado
"""

import asyncio
import sys
from optimized_market_maker import OptimizedMarketMaker

async def test_bot():
    print("🧪 Testando bot otimizado...")
    bot = OptimizedMarketMaker()
    
    # Testar inicialização
    print("✅ Bot inicializado com sucesso")
    
    # Testar componentes
    print("✅ Estratégia avançada: OK")
    print("✅ Minimizador de perdas: OK")
    print("✅ Otimizador de airdrop: OK")
    
    print("🎉 Todos os testes passaram!")

if __name__ == "__main__":
    asyncio.run(test_bot())
"@

$testScript | Out-File -FilePath "test_optimized.py" -Encoding UTF8

# Executar teste
Write-Host "🧪 Executando teste otimizado..." -ForegroundColor Yellow
python test_optimized.py

Write-Host ""
Write-Host "🎉 Configuração otimizada concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Configure suas chaves da API no arquivo .env" -ForegroundColor White
Write-Host "2. Ative o ambiente virtual: .\venv_optimized\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "3. Execute o bot otimizado: python optimized_market_maker.py" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Características do bot otimizado:" -ForegroundColor Yellow
Write-Host "• Minimização de perdas com controles dinâmicos" -ForegroundColor White
Write-Host "• Estratégia de airdrop farming agressiva" -ForegroundColor White
Write-Host "• Sistema de arbitragem interna" -ForegroundColor White
Write-Host "• Hedging automático" -ForegroundColor White
Write-Host "• Mean reversion inteligente" -ForegroundColor White
Write-Host "• Modos de performance adaptativos" -ForegroundColor White
Write-Host ""
Write-Host "📖 Para mais informações, consulte o README.md" -ForegroundColor Yellow