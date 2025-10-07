# Script de inicialização para Windows PowerShell
# Paradex Market Maker Bot - Otimizado para pouco capital e farming de airdrop

param(
    [switch]$Install,
    [switch]$Run,
    [switch]$Config,
    [switch]$Update,
    [switch]$Test,
    [switch]$Diagnose,
    [switch]$Backup,
    [switch]$Restore,
    [string]$ConfigFile = "config_windows.json",
    [string]$LogLevel = "INFO"
)

# Configurações de cores para Windows
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$White = "White"

Write-Host "🤖 Paradex Market Maker Bot - Windows Edition" -ForegroundColor $Green
Write-Host "================================================" -ForegroundColor $Green
Write-Host "🚀 Otimizado para farming de airdrop com pouco capital" -ForegroundColor $Cyan
Write-Host ""

# Função para verificar se Python está instalado
function Test-Python {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python (\d+\.\d+)") {
            $version = [double]$matches[1]
            if ($version -ge 3.8) {
                Write-Host "✅ Python $version encontrado" -ForegroundColor $Green
                return $true
            } else {
                Write-Host "❌ Python $version encontrado, mas precisa ser 3.8+" -ForegroundColor $Red
                return $false
            }
        }
    } catch {
        Write-Host "❌ Python não encontrado" -ForegroundColor $Red
        return $false
    }
    return $false
}

# Função para diagnóstico completo do sistema
function Test-SystemRequirements {
    Write-Host "🔍 Diagnóstico do Sistema:" -ForegroundColor $Cyan
    Write-Host "-" * 40 -ForegroundColor $Cyan

    $requirements = @(
        @{Name = "Python 3.8+"; Test = { Test-Python }},
        @{Name = "PIP"; Test = { Test-Pip }},
        @{Name = "Git"; Test = { Test-Git }},
        @{Name = "Espaço em disco"; Test = { Test-DiskSpace }},
        @{Name = "Memória RAM"; Test = { Test-Memory }},
        @{Name = "Conectividade"; Test = { Test-Connectivity }}
    )

    $allPassed = $true
    foreach ($req in $requirements) {
        try {
            $result = & $req.Test
            if ($result) {
                Write-Host "✅ $($req.Name)" -ForegroundColor $Green
            } else {
                Write-Host "❌ $($req.Name)" -ForegroundColor $Red
                $allPassed = $false
            }
        } catch {
            Write-Host "❌ $($req.Name) - Erro: $($_.Exception.Message)" -ForegroundColor $Red
            $allPassed = $false
        }
    }

    Write-Host ""
    if ($allPassed) {
        Write-Host "🎉 Todos os requisitos atendidos!" -ForegroundColor $Green
    } else {
        Write-Host "⚠️  Alguns requisitos não foram atendidos" -ForegroundColor $Yellow
        Write-Host "💡 Execute '.\run_windows.ps1 -Diagnose' para mais detalhes" -ForegroundColor $Cyan
    }

    return $allPassed
}

# Função para testar PIP
function Test-Pip {
    try {
        $pipVersion = pip --version 2>$null
        return $pipVersion -ne $null
    } catch {
        return $false
    }
}

# Função para testar Git
function Test-Git {
    try {
        $gitVersion = git --version 2>$null
        return $gitVersion -ne $null
    } catch {
        return $false
    }
}

# Função para testar espaço em disco
function Test-DiskSpace {
    try {
        $disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
        $freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)
        return $freeSpaceGB -gt 1  # Pelo menos 1GB livre
    } catch {
        return $false
    }
}

# Função para testar memória
function Test-Memory {
    try {
        $memory = Get-WmiObject Win32_ComputerSystem
        $totalMemoryGB = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
        return $totalMemoryGB -gt 2  # Pelo menos 2GB RAM
    } catch {
        return $false
    }
}

# Função para testar conectividade
function Test-Connectivity {
    try {
        $test = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -WarningAction SilentlyContinue
        return $test.TcpTestSucceeded
    } catch {
        return $false
    }
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

if ($Diagnose) {
    Write-Host "🔍 Executando diagnóstico completo..." -ForegroundColor Cyan
    Write-Host ""
    Test-SystemRequirements
    Write-Host ""
    Write-Host "💡 Para instalar dependências: .\run_windows.ps1 -Install" -ForegroundColor Yellow
    Write-Host "💡 Para executar o bot: .\run_windows.ps1 -Run" -ForegroundColor Yellow
}

if ($Test) {
    Write-Host "🧪 Executando testes..." -ForegroundColor Cyan

    # Teste de importação
    Write-Host "📦 Testando importação de módulos..." -ForegroundColor Yellow
    try {
        $testImport = python -c "
import requests
import pandas as pd
import web3
import questionary
print('✅ Todos os módulos importados com sucesso!')
" 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Teste de importação passou" -ForegroundColor Green
        } else {
            Write-Host "❌ Teste de importação falhou" -ForegroundColor Red
            Write-Host $testImport -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Erro no teste de importação: $($_.Exception.Message)" -ForegroundColor Red
    }

    # Teste de configuração
    Write-Host "⚙️  Testando configuração..." -ForegroundColor Yellow
    if (Test-Path $ConfigFile) {
        try {
            $configTest = python -c "
import json
with open('$ConfigFile', 'r') as f:
    config = json.load(f)
print('✅ Configuração válida!')
print(f'📊 Par primário: {config.get('pairs', {}).get('primary_pairs', [])}')
" 2>&1

            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Teste de configuração passou" -ForegroundColor Green
            } else {
                Write-Host "❌ Teste de configuração falhou" -ForegroundColor Red
                Write-Host $configTest -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Erro no teste de configuração: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  Arquivo de configuração não encontrado" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "💡 Para executar o bot: .\run_windows.ps1 -Run" -ForegroundColor Cyan
}

if ($Backup) {
    Write-Host "💾 Criando backup..." -ForegroundColor Cyan

    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupDir = "backups"

    if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir | Out-Null
    }

    $backupPath = "$backupDir\backup_$timestamp"

    try {
        # Backup da configuração
        if (Test-Path $ConfigFile) {
            Copy-Item $ConfigFile "$backupPath.json"
        }

        # Backup dos logs
        if (Test-Path "logs") {
            Copy-Item "logs" $backupPath -Recurse
        }

        Write-Host "✅ Backup criado: $backupPath" -ForegroundColor Green

        # Limpeza de backups antigos (7 dias)
        Get-ChildItem "$backupDir\*" -Directory | Where-Object {
            $_.LastWriteTime -lt (Get-Date).AddDays(-7)
        } | Remove-Item -Recurse -Force

        Write-Host "🧹 Backups antigos removidos" -ForegroundColor Yellow

    } catch {
        Write-Host "❌ Erro ao criar backup: $($_.Exception.Message)" -ForegroundColor Red
    }
}

if ($Update) {
    Write-Host "🔄 Verificando atualizações..." -ForegroundColor Cyan

    # Em produção, isso verificaria por novas versões no GitHub
    Write-Host "💡 Funcionalidade de atualização automática em desenvolvimento" -ForegroundColor Yellow
    Write-Host "📅 Verifique o repositório GitHub para atualizações manuais" -ForegroundColor White
}

# Se nenhum argumento foi fornecido, mostrar menu
if (-not ($Install -or $Run -or $Config -or $Update -or $Test -or $Diagnose -or $Backup)) {
    Write-Host "📋 Menu de Opções:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎯 OPERAÇÕES PRINCIPAIS:" -ForegroundColor Green
    Write-Host "   .\run_windows.ps1 -Install  → Instalar dependências" -ForegroundColor White
    Write-Host "   .\run_windows.ps1 -Config   → Editar configuração" -ForegroundColor White
    Write-Host "   .\run_windows.ps1 -Run      → Executar o bot" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 FERRAMENTAS AVANÇADAS:" -ForegroundColor Green
    Write-Host "   .\run_windows.ps1 -Diagnose → Diagnóstico completo do sistema" -ForegroundColor White
    Write-Host "   .\run_windows.ps1 -Test     → Testar instalação e configuração" -ForegroundColor White
    Write-Host "   .\run_windows.ps1 -Backup   → Criar backup da configuração" -ForegroundColor White
    Write-Host "   .\run_windows.ps1 -Update   → Verificar atualizações" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Recomendação: Execute primeiro -Install, depois -Config, e finalmente -Run" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🎯 Para pouco capital (5k) e foco em SOL, use:" -ForegroundColor Green
    Write-Host "   .\run_windows.ps1 -Run -ConfigFile config_windows.json" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 EXEMPLOS DE USO:" -ForegroundColor Cyan
    Write-Host "   .\run_windows.ps1 -Install" -ForegroundColor White
    Write-Host "   .\run_windows.ps1 -Config" -ForegroundColor White
    Write-Host "   .\run_windows.ps1 -Run -LogLevel DEBUG" -ForegroundColor White
}