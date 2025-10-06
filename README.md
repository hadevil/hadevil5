# 🚀 Paradex Market Maker Bot - Advanced Airdrop Farming

Bot avançado de market making para Paradex otimizado para farming de airdrop com capital limitado ($5k).

> 🇧🇷 **Novo aqui? [COMECE_AQUI.md](COMECE_AQUI.md) - Guia rápido em português!**

## 🎯 Características Principais

### Estratégias Avançadas
- **Multi-Level Order Placement**: 5 níveis de ordens em cada lado do book
- **Dynamic Spread Adjustment**: Ajuste automático baseado em volatilidade
- **Inventory Management**: Sistema inteligente de skewing para gerenciar posição
- **Volatility-Based Sizing**: Ajuste de tamanho de ordem baseado em volatilidade
- **Risk Management**: Controles de risco integrados

### Otimizações para Airdrop
- **High Order Frequency**: Maximiza número de ordens para score de airdrop
- **Volume Optimization**: Otimiza volume traded vs capital disponível
- **Competitive Edge**: Algoritmos para competir com outros market makers
- **Capital Efficiency**: Uso eficiente de $5k para máximo retorno

## 📊 Estratégia de $5k

Com $5k de capital, o bot:
- Usa $100 por ordem (50 ordens simultâneas possíveis)
- 5 níveis buy + 5 níveis sell = 10 ordens ativas
- Mantém posição máxima de $2,500 (50% do capital)
- Spread base de 0.15% para capturar edge
- Rebalanceamento a cada 30 segundos

**Resultado esperado**: 
- ~1000-2000 ordens/dia
- $50k-100k volume diário
- Posicionamento competitivo no leaderboard de market makers

## 🛠️ Instalação (Windows/PowerShell)

### Instalação Automática (Recomendada)
```powershell
# Clone o repositório
git clone https://github.com/hadevil/hadevil5.git
cd hadevil5

# Execute o instalador automático
.\install.ps1
```

O script irá:
- ✅ Verificar Python
- ✅ Criar ambiente virtual
- ✅ Instalar dependências
- ✅ Gerar configurações otimizadas
- ✅ Criar arquivo .env

### Instalação Manual

#### 1. Instalar Python
```powershell
# Baixe Python 3.10+ de python.org
# Verifique a instalação:
python --version
```

#### 2. Clonar Repositório
```powershell
git clone https://github.com/hadevil/hadevil5.git
cd hadevil5
```

#### 3. Criar Ambiente Virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Se der erro de ExecutionPolicy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. Instalar Dependências
```powershell
pip install -r requirements.txt
```

### 5. Gerar Configurações Otimizadas

```powershell
# Gera 3 perfis: conservative, balanced, aggressive
python optimize_config.py

# Escolha um perfil (recomendado começar com conservative)
copy config_conservative.json config.json
```

### 6. Configurar API Keys

1. Acesse [Paradex](https://www.paradex.trade/)
2. Crie uma conta e gere API keys
3. Edite `config.json` e adicione suas credenciais:

```powershell
notepad config.json
```

Adicione suas API keys:
```json
{
  "api_key": "sua_api_key_aqui",
  "api_secret": "seu_api_secret_aqui",
  "testnet": true
}
```

### 7. Testar Conexão

```powershell
# Verifica configuração e conexão com Paradex
python test_connection.py
```

Se tudo estiver OK, você verá:
```
ALL TESTS PASSED! ✓
```

### 8. (Opcional) Executar Backtest

Antes de usar capital real, rode o backtest para entender o comportamento:

```powershell
# Simula 24h de trading com diferentes configurações
python backtest.py
# ou use o script:
.\run_backtest.ps1
```

### 9. Configurar Parâmetros (se necessário)

Se quiser ajustar manualmente, edite `config.json`:
```powershell
notepad config.json
```

Parâmetros importantes:
- `order_size_usd`: Tamanho de cada ordem ($100 recomendado)
- `max_position_usd`: Posição máxima ($2500 = 50% do capital)
- `base_spread`: Spread base (0.0015 = 0.15%)
- `order_levels`: Número de níveis (5 recomendado)
- `refresh_interval`: Intervalo de refresh em segundos (30s)

## 🚀 Executar o Bot

### Método 1: Usando Script (Mais Fácil)
```powershell
# Inicia o bot automaticamente
.\start_bot.ps1
```

### Método 2: Manual

#### Modo Testnet (Recomendado para testar)
```powershell
# Ative o ambiente virtual primeiro
.\venv\Scripts\Activate.ps1

# Execute o bot
python paradex_market_maker.py
```

#### Modo Produção
```powershell
# Edite config.json e mude "testnet": false
notepad config.json

# Execute o bot
python paradex_market_maker.py
```

### Executar em Background
```powershell
# Usando Start-Process
Start-Process python -ArgumentList "paradex_market_maker.py" -NoNewWindow -RedirectStandardOutput "bot_output.log"

# Ou use Windows Terminal com múltiplas abas
```

## 📊 Monitoramento

### Método 1: Usando Script
```powershell
# Em outra janela do PowerShell
.\start_monitor.ps1
```

### Método 2: Dashboard Manual
```powershell
# Ative o ambiente virtual
.\venv\Scripts\Activate.ps1

# Execute o monitor
python monitor.py
```

### Verificar Logs
```powershell
# Ver últimas linhas do log
Get-Content .\market_maker.log -Tail 50 -Wait

# Ou use o Notepad++, VSCode, etc
notepad market_maker.log
```

### Estatísticas
O bot loga automaticamente:
- Número de ordens colocadas/canceladas
- Volume total traded
- Posição atual
- PnL estimado
- Tempo de execução

## 📈 Otimização para Airdrop

### Maximizar Score de Airdrop
1. **Volume**: Bot coloca/cancela ordens frequentemente
2. **Spread Competitivo**: 0.15% é competitivo mas lucrativo
3. **Uptime**: Rode 24/7 para máximo score
4. **Consistência**: Evita paradas, mantém liquidez constante

### Ajustes Avançados

Para ser mais agressivo (mais volume, mais risco):
```json
{
  "base_spread": 0.001,        // Spread menor
  "order_levels": 7,            // Mais níveis
  "refresh_interval": 15,       // Refresh mais rápido
  "order_size_usd": 150         // Ordens maiores
}
```

Para ser mais conservador (menos risco):
```json
{
  "base_spread": 0.002,        // Spread maior
  "order_levels": 3,            // Menos níveis
  "refresh_interval": 60,       // Refresh mais lento
  "max_position_usd": 1500      // Posição menor
}
```

## 🛡️ Gestão de Risco

O bot inclui:
- **Max Position Limit**: Limita exposição máxima
- **Inventory Skewing**: Ajusta preços quando posicionado
- **Volatility Scaling**: Aumenta spread em alta volatilidade
- **Auto-shutdown**: Para em caso de erros críticos

### Monitorar Risco
```powershell
# Verifique posição regularmente
# O bot loga a cada iteração
Get-Content .\market_maker.log | Select-String "Position:"
```

## 🔧 Troubleshooting

### Erro de API
```
Error: API request failed
```
**Solução**: Verifique suas API keys no `.env`

### Erro de Saldo
```
Error: Insufficient balance
```
**Solução**: Deposite fundos na conta Paradex

### Erro de Rate Limit
```
Error: Rate limit exceeded
```
**Solução**: Aumente `refresh_interval` no config.json

### Bot Não Conecta
**Verificar**:
1. Internet estável
2. Paradex API está online
3. API keys corretas
4. Testnet vs Mainnet configurado corretamente

## 📊 Performance Esperada

Com $5k em SOL:

| Métrica | Valor Estimado |
|---------|---------------|
| Ordens/Dia | 1,500-2,500 |
| Volume/Dia | $75k-$150k |
| Spread Capturado | 0.10-0.15% |
| PnL Diário | $75-$225 |
| Fill Rate | 60-80% |

**Nota**: Performance varia com volatilidade e competição.

## 🎓 Conceitos de Market Making

### Como Funciona
1. Bot coloca ordens BUY abaixo do preço e SELL acima
2. Quando ordens são executadas, captura o spread
3. Gerencia inventário para não acumular muita posição
4. Ajusta preços continuamente com o mercado

### Inventory Skewing
- **Long (comprado demais)**: Aumenta preços de venda, diminui compra
- **Short (vendido demais)**: Diminui preços de venda, aumenta compra
- **Neutro**: Preços simétricos ao redor do mid

### Dynamic Spread
- **Alta Volatilidade**: Spread aumenta para proteção
- **Baixa Volatilidade**: Spread diminui para competir
- **Base Spread**: Sempre mantém edge mínimo (0.02%)

## 🔐 Segurança

### Melhores Práticas
1. **Nunca compartilhe** API keys
2. **Use permissões limitadas** (apenas trading, não withdrawal)
3. **Comece em testnet** antes de usar capital real
4. **Monitore regularmente** posições e PnL
5. **Defina limites** de perda máxima

### Backup
```powershell
# Backup de configuração
copy config.json config.backup.json
copy .env .env.backup
```

## 📞 Suporte

### Recursos
- [Documentação Paradex](https://docs.paradex.trade/)
- [API Reference](https://docs.paradex.trade/api)
- [Discord Paradex](https://discord.gg/paradex)

### Logs e Debug
```powershell
# Aumentar nível de logging
# Edite paradex_market_maker.py linha 24:
# level=logging.DEBUG
```

## 🚀 Próximos Passos

1. **Teste em Testnet**: Rode por 24h em testnet
2. **Analise Logs**: Verifique se está funcionando bem
3. **Ajuste Parâmetros**: Otimize para seu perfil de risco
4. **Deploy Mainnet**: Comece com capital pequeno
5. **Scale Up**: Aumente gradualmente à medida que ganha confiança

## 📝 Changelog

### v1.0.0 (2025-10-06)
- ✅ Multi-level order placement
- ✅ Dynamic spread adjustment
- ✅ Inventory management
- ✅ Volatility estimation
- ✅ Risk management
- ✅ Performance monitoring
- ✅ Windows/PowerShell support

## ⚖️ License

MIT License - Use at your own risk. Trading carries financial risk.

## ⚠️ Disclaimer

Este bot é fornecido "como está" sem garantias. Trading de derivativos envolve risco substancial de perda. Use apenas capital que você pode perder. O desenvolvedor não é responsável por perdas financeiras.

**ATENÇÃO**: 
- Sempre teste em testnet primeiro
- Comece com capital pequeno
- Monitore constantemente
- Entenda os riscos de market making
- Airdrops não são garantidos

---

**Boa sorte com o farming! 🌾💰**

Para dúvidas, abra uma issue no GitHub.
