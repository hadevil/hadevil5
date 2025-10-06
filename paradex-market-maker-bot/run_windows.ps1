# Script de inicialização para Windows PowerShell
# Paradex Market Maker Bot - Otimizado para pouco capital

param(
    [switch]$Install,
    [switch]$Run,
    [switch]$Config,
    [string]$ConfigFile = "config_windows.json"
)

Write-Host "🚀 Paradex Market Maker Bot - Windows Edition" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Função para verificar se Python está instalado
function Test-Python {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python (\d+\.\d+)") {
            $version = [double]$matches[1]
            if ($version -ge 3.8) {
                Write-Host "✅ Python $version encontrado" -ForegroundColor Green
                return $true
            } else {
                Write-Host "❌ Python $version encontrado, mas precisa ser 3.8+" -ForegroundColor Red
                return $false
            }
        }
    } catch {
        Write-Host "❌ Python não encontrado" -ForegroundColor Red
        return $false
    }
    return $false
}

# Função para instalar dependências
function Install-Dependencies {
    Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow

    try {
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependências instaladas com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "❌ Erro na instalação das dependências" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Erro ao instalar dependências: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Função para executar o bot
function Start-Bot {
    param([string]$ConfigFile)

    Write-Host "🎯 Iniciando Paradex Market Maker Bot..." -ForegroundColor Cyan

    try {
        python main.py
    } catch {
        Write-Host "❌ Erro ao executar o bot: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "💡 Verifique se a configuração está correta e tente novamente" -ForegroundColor Yellow
        exit 1
    }
}

# Função para configurar o bot
function Set-Configuration {
    Write-Host "⚙️  Configuração do Bot" -ForegroundColor Yellow
    Write-Host "======================" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "📝 Editando configuração: $ConfigFile" -ForegroundColor Cyan

    # Abre o arquivo de configuração no bloco de notas
    notepad.exe $ConfigFile

    Write-Host ""
    Write-Host "✅ Arquivo de configuração aberto. Edite conforme necessário." -ForegroundColor Green
    Write-Host "💡 Principais configurações para pouco capital:" -ForegroundColor Yellow
    Write-Host "   - order_value_usd: min 8, max 25" -ForegroundColor Yellow
    Write-Host "   - max_leverage: 1.2" -ForegroundColor Yellow
    Write-Host "   - max_daily_volume_usd: 800" -ForegroundColor Yellow
    Write-Host "   - primary_pairs: ['SOL-USD']" -ForegroundColor Yellow
}

# Verificar Python
if (-not (Test-Python)) {
    Write-Host ""
    Write-Host "💡 Instale o Python 3.8+ de: https://python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   Certifique-se de marcar 'Add Python to PATH' durante a instalação" -ForegroundColor Yellow
    exit 1
}

# Verificar se está no diretório correto
$currentDir = Get-Location
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Arquivo requirements.txt não encontrado!" -ForegroundColor Red
    Write-Host "💡 Execute este script do diretório do bot:" -ForegroundColor Yellow
    Write-Host "   cd paradex-market-maker-bot" -ForegroundColor Yellow
    Write-Host "   .\run_windows.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Processar argumentos
if ($Install) {
    Install-Dependencies
    Write-Host ""
    Write-Host "🎉 Instalação concluída! Use -Run para iniciar o bot." -ForegroundColor Green
}

if ($Config) {
    Set-Configuration
}

if ($Run) {
    Write-Host "🔍 Verificando instalação..." -ForegroundColor Yellow

    # Verificar se dependências estão instaladas
    try {
        $output = python -c "import requests, pandas, web3" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Todas as dependências estão instaladas" -ForegroundColor Green
        } else {
            Write-Host "📦 Instalando dependências necessárias..." -ForegroundColor Yellow
            Install-Dependencies
        }
    } catch {
        Write-Host "📦 Instalando dependências necessárias..." -ForegroundColor Yellow
        Install-Dependencies
    }

    Write-Host ""
    Start-Bot -ConfigFile $ConfigFile
}

# Se nenhum argumento foi fornecido, mostrar menu
if (-not ($Install -or $Run -or $Config)) {
    Write-Host "📋 Menu de Opções:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   .\run_windows.ps1 -Install  → Instalar dependências" -ForegroundColor White
    Write-Host "   .\run_windows.ps1 -Config   → Editar configuração" -ForegroundColor White
    Write-Host "   .\run_windows.ps1 -Run      → Executar o bot" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Recomendação: Execute primeiro -Install, depois -Config, e finalmente -Run" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🎯 Para pouco capital (5k) e foco em SOL, use:" -ForegroundColor Green
    Write-Host "   .\run_windows.ps1 -Run -ConfigFile config_windows.json" -ForegroundColor Green
}