# 🚀 Guia Rápido - Paradex Market Maker Bot

## ⚡ Comandos Rápidos para Windows PowerShell

### 📦 Instalação Completa (3 comandos)
```powershell
# 1. Criar diretório e baixar arquivos
mkdir C:\paradex-bot
cd C:\paradex-bot
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/seu-repo/paradex-market-maker-bot/main/main.py" -OutFile "main.py"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/seu-repo/paradex-market-maker-bot/main/requirements.txt" -OutFile "requirements.txt"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/seu-repo/paradex-market-maker-bot/main/config_windows.json" -OutFile "config_windows.json"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/seu-repo/paradex-market-maker-bot/main/run_windows.ps1" -OutFile "run_windows.ps1"

# 2. Verificar sistema
.\run_windows.ps1 -Diagnose

# 3. Instalar dependências
.\run_windows.ps1 -Install
```

### ⚙️ Configuração Básica
```powershell
# Editar configuração
.\run_windows.ps1 -Config

# Testar instalação
.\run_windows.ps1 -Test

# Executar bot
.\run_windows.ps1 -Run
```

---

## 🎯 Configuração Mínima Necessária

### 📝 Editar `config_windows.json`:
```json
{
  "account": {
    "address": "0xSEU_ENDEREÇO_AQUI",
    "private_key": "0xSUA_PRIVATE_KEY_AQUI",
    "api_key": "SUA_API_KEY_AQUI",
    "api_secret": "SEU_API_SECRET_AQUI"
  }
}
```

### 🔑 Como obter credenciais:

1. **Endereço da carteira:**
   - MetaMask: Conta → Copy address
   - Formato: `0x1234567890abcdef...`

2. **Chave privada:**
   - MetaMask: Settings → Security → Export Private Key
   - ⚠️ Mantenha segura!

3. **API Keys (se necessário):**
   - Site da Paradex → Settings → API Keys

---

## 📊 Usando o Bot

### 🚀 Menu Principal:
```
🤖 Paradex Market Maker - Menu Principal

1. ⚙️  Configurar conta
2. 🚀 Iniciar trading
3. 📊 Dashboard de performance
4. 📈 Ver métricas detalhadas
5. ⚠️  Parar trading
6. 🔧 Configurações avançadas
7. ❌ Sair
```

### 💡 Dicas de Uso:

- **Primeira vez?** Escolha opção 1 primeiro
- **Para ver performance:** Opção 3
- **Configurações avançadas:** Opção 6
- **Para parar:** Opção 5 ou Ctrl+C

---

## 🔧 Comandos Avançados

### 📊 Diagnóstico e Testes:
```powershell
# Diagnóstico completo
.\run_windows.ps1 -Diagnose

# Testar instalação
.\run_windows.ps1 -Test

# Backup automático
.\run_windows.ps1 -Backup

# Logs detalhados
.\run_windows.ps1 -Run -LogLevel DEBUG
```

### 🎛️ Configurações Específicas:

```powershell
# Para $5k (recomendado)
# Edite config_windows.json:
{
  "trading": {
    "order_value_usd": {"min": 8, "max": 25},
    "max_leverage": 1.2,
    "max_daily_volume_usd": 800
  }
}

# Para capital maior ($10k+)
{
  "trading": {
    "order_value_usd": {"min": 15, "max": 50},
    "max_leverage": 1.5,
    "max_daily_volume_usd": 1500
  }
}
```

---

## 📈 Estratégia Recomendada

### 🎯 Para Farming de Airdrop com $5k:

1. **Foque em SOL-USD** (par principal)
2. **Ordens pequenas** ($8-$25)
3. **Volume diário:** $500-$800
4. **Monitore constantemente**
5. **Ajuste baseado no desempenho**

### ⏱️ Tempo Estimado para Airdrop:
- **Volume mensal alvo:** $15,000-$25,000
- **Período mínimo:** 30-60 dias
- **Frequência:** Operações consistentes diariamente

---

## 🛠️ Solução de Problemas Rápida

### ❌ Erro Comum 1: "Python não encontrado"
```powershell
# Reinstalar Python com PATH marcado
# https://python.org/downloads/
```

### ❌ Erro Comum 2: "Módulo não encontrado"
```powershell
.\run_windows.ps1 -Install
```

### ❌ Erro Comum 3: "Configuração inválida"
```powershell
.\run_windows.ps1 -Test
```

### ❌ Erro Comum 4: "Ordem rejeitada"
- Verifique fundos na conta Paradex
- Ajuste valores no config_windows.json

---

## 📊 Monitoramento

### 🔍 Logs em Tempo Real:
```powershell
# Ver últimas linhas do log
Get-Content logs/trading.log -Tail 20 -Wait

# Filtrar erros
Get-Content logs/trading.log | Select-String "ERROR|Exception"
```

### 📈 Métricas Importantes:
- **Volume diário:** $500-$800 (meta)
- **Taxa de execução:** >80%
- **P&L diário:** -$10 a +$10 (normal)
- **Win rate:** >60% (ideal)

---

## 🎉 Pronto para Começar!

1. ✅ **Instalou** o bot?
2. ✅ **Configurou** sua conta?
3. ✅ **Testou** a instalação?
4. 🚀 **Execute** e monitore!

**💡 Dica:** Comece com valores pequenos e aumente gradualmente conforme confiança.

**🎯 Meta:** Volume consistente para maximizar chances de airdrop!