# 🔧 Guia de Solução de Problemas - Windows PowerShell

## 📋 PROBLEMAS COMUNS E SOLUÇÕES

### ❌ ERRO 1: "python não é reconhecido como comando interno"

**🔍 Diagnóstico:**
- Python não instalado ou não adicionado ao PATH

**✅ Solução:**
```powershell
# Passo 1: Verificar instalação
Get-Command python -ErrorAction SilentlyContinue

# Passo 2: Se não encontrar, baixar Python
# https://python.org/downloads/

# Passo 3: Durante instalação, MARQUE "Add Python to PATH"

# Passo 4: Reinicie PowerShell

# Passo 5: Verificar novamente
python --version
```

**🛠️ Solução alternativa (se PATH não funcionou):**
```powershell
# Adicionar manualmente ao PATH atual
$env:Path += ";C:\Python310;C:\Python310\Scripts"

# Testar
python --version
```

---

### ❌ ERRO 2: "pip não é reconhecido" ou "No module named pip"

**🔍 Diagnóstico:**
- pip não instalado ou corrompido

**✅ Solução:**
```powershell
# Reinstalar pip
python -m ensurepip --upgrade

# Ou instalar manualmente
curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
python get-pip.py

# Verificar
pip --version
```

---

### ❌ ERRO 3: "No module named 'requests'" (ou outros módulos)

**🔍 Diagnóstico:**
- Dependências não instaladas

**✅ Solução:**
```powershell
# Método 1: Instalação automática (recomendado)
.\run_windows.ps1 -Install

# Método 2: Instalação manual
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Método 3: Instalar um por um
python -m pip install requests pandas openpyxl web3 eth-account questionary python-dotenv

# Método 4: Se pip falhar
python -m pip install --user requests pandas openpyxl web3 eth-account questionary python-dotenv
```

---

### ❌ ERRO 4: "Access denied" ou "Erro de permissão"

**🔍 Diagnóstico:**
- PowerShell sem privilégios de administrador

**✅ Solução:**
```powershell
# Método 1: Executar como Administrador
# Win + X → "Windows PowerShell (Admin)"

# Método 2: Permitir execução de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Método 3: Se ainda falhar, usar:
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
```

---

### ❌ ERRO 5: "Erro ao conectar na Paradex" ou "Connection timeout"

**🔍 Diagnóstico:**
- Problemas de rede ou configuração

**✅ Solução:**
```powershell
# 1. Teste de conectividade básica
ping google.com

# 2. Teste conexão com Paradex
Test-NetConnection -ComputerName api.paradex.trade -Port 443

# 3. Teste com Python
python -c "
import requests
try:
    r = requests.get('https://api.paradex.trade/api/v1/ticker', timeout=10)
    print(f'✅ Status: {r.status_code}')
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

**🔧 Se conexão falhar:**
- Verifique sua conexão de internet
- Tente usar VPN
- Verifique firewall/antivírus

---

### ❌ ERRO 6: "Private key inválida" ou "Endereço inválido"

**🔍 Diagnóstico:**
- Credenciais mal formatadas

**✅ Solução:**
```powershell
# Verificar formato da chave privada
python -c "
pk = '0xSUA_PRIVATE_KEY_AQUI'
print('Comprimento:', len(pk))
print('Começa com 0x:', pk.startswith('0x'))
print('É hexadecimal:', all(c in '0123456789abcdefABCDEF' for c in pk[2:]))
"
```

**📋 Formatos corretos:**
- **Private Key:** `0x` + 64 caracteres hexadecimais
- **Address:** `0x` + 40 caracteres hexadecimais
- **API Key:** String alfanumérica (se necessário)

---

### ❌ ERRO 7: "Ordem rejeitada" ou "Insufficient funds"

**🔍 Diagnóstico:**
- Problemas com fundos ou configuração de trading

**✅ Solução:**
```powershell
# 1. Verificar saldo (se possível)
# Acesse https://paradex.trade/ e verifique sua conta

# 2. Ajustar configuração para valores menores
# Edite config_windows.json:
{
  'trading': {
    'order_value_usd': {'min': 5, 'max': 10}
  }
}

# 3. Verificar logs detalhados
Get-Content logs/trading.log -Tail 50 -Wait
```

---

### ❌ ERRO 8: "Script não pode ser carregado porque a execução de scripts está desabilitada"

**🔍 Diagnóstico:**
- PowerShell com execução restrita

**✅ Solução:**
```powershell
# Ver política atual
Get-ExecutionPolicy

# Permitir execução local
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Ou para scripts locais apenas
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

---

### ❌ ERRO 9: "Erro de codificação" ou caracteres estranhos

**🔍 Diagnóstico:**
- Problemas com encoding do Windows

**✅ Solução:**
```powershell
# Definir encoding UTF-8
$env:PYTHONIOENCODING = 'utf-8'

# Ou executar com encoding específico
python -X utf8 main.py
```

---

### ❌ ERRO 10: "Bot trava" ou "Não responde"

**🔍 Diagnóstico:**
- Loop infinito ou problema de threading

**✅ Solução:**
```powershell
# Ver processos Python
tasklist | findstr python

# Matar processos travados
taskkill /f /im python.exe

# Reiniciar PowerShell
# Fechar e abrir nova janela
```

---

## 🛠️ FERRAMENTAS DE DIAGNÓSTICO

### 📊 Script de Diagnóstico Completo:
```powershell
# Criar arquivo de diagnóstico
@"
# Diagnostic Script
Write-Host "=== DIAGNÓSTICO PARADX BOT ===" -ForegroundColor Green

# Python
try {
    $py = python --version 2>$null
    Write-Host "✅ Python: $py" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado" -ForegroundColor Red
}

# Pip
try {
    $pip = pip --version 2>$null
    Write-Host "✅ Pip: $pip" -ForegroundColor Green
} catch {
    Write-Host "❌ Pip não encontrado" -ForegroundColor Red
}

# Dependências
$deps = @('requests', 'pandas', 'web3')
foreach ($dep in $deps) {
    try {
        python -c "import $dep" 2>$null
        Write-Host "✅ $dep: OK" -ForegroundColor Green
    } catch {
        Write-Host "❌ $dep: FALTANDO" -ForegroundColor Red
    }
}

# Arquivos
$files = @('main.py', 'config_windows.json', 'requirements.txt')
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file: Encontrado" -ForegroundColor Green
    } else {
        Write-Host "❌ $file: NÃO ENCONTRADO" -ForegroundColor Red
    }
}

Write-Host "=== FIM DO DIAGNÓSTICO ===" -ForegroundColor Green
"@ | Out-File -FilePath "diagnose.ps1" -Encoding UTF8

# Executar diagnóstico
.\diagnose.ps1
```

### 🔍 Verificar Logs Detalhados:
```powershell
# Ver últimas linhas do log
Get-Content logs/trading.log -Tail 20

# Ver log em tempo real
Get-Content logs/trading.log -Tail 0 -Wait

# Filtrar erros
Get-Content logs/trading.log | Select-String "ERROR|Exception"
```

---

## 📞 PRECISANDO DE MAIS AJUDA?

### 1. **Verifique os passos básicos:**
```powershell
# Está no diretório correto?
pwd

# Tem todos os arquivos?
ls -la

# Conseguiu instalar Python?
python --version

# Conseguiu instalar dependências?
python -c "import requests; print('✅ OK')"
```

### 2. **Teste passo a passo:**
```powershell
# Passo 1: Python
python --version

# Passo 2: Dependências
python -m pip install requests

# Passo 3: Arquivo de configuração
Test-Path config_windows.json

# Passo 4: Teste do bot
python -c "print('Bot pode ser importado')"
```

### 3. **Se tudo falhar:**
- Reinstale Python completamente
- Delete a pasta do projeto e baixe novamente
- Execute em uma máquina virtual limpa
- Considere usar Docker (se confortável)

**🎯 Lembre-se: A maioria dos problemas é resolvida seguindo os passos na ordem correta!**