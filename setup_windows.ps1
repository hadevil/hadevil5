# Script de configuração para Windows PowerShell
# Market Maker Bot para Paradex

Write-Host "🚀 Configurando Market Maker Bot para Paradex" -ForegroundColor Green

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
Write-Host "📦 Criando ambiente virtual..." -ForegroundColor Yellow
python -m venv venv

# Ativar ambiente virtual
Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Atualizar pip
Write-Host "⬆️ Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Instalar dependências
Write-Host "📚 Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

# Criar arquivo .env se não existir
if (-not (Test-Path ".env")) {
    Write-Host "📝 Criando arquivo .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️ Configure suas chaves da API no arquivo .env" -ForegroundColor Yellow
}

# Criar diretórios necessários
Write-Host "📁 Criando diretórios..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs"
New-Item -ItemType Directory -Force -Path "data"

# Testar importações
Write-Host "🧪 Testando importações..." -ForegroundColor Yellow
python -c "
try:
    import requests
    import numpy
    import pandas
    import aiohttp
    print('✅ Todas as dependências instaladas com sucesso!')
except ImportError as e:
    print(f'❌ Erro de importação: {e}')
    exit(1)
"

Write-Host ""
Write-Host "🎉 Configuração concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Configure suas chaves da API no arquivo .env" -ForegroundColor White
Write-Host "2. Ative o ambiente virtual: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "3. Execute o bot: python market_maker_bot.py" -ForegroundColor White
Write-Host ""
Write-Host "📖 Para mais informações, consulte o README.md" -ForegroundColor Yellow