# 📦 Entrega - Bot de Scalping Direcional

## ✅ Projeto Completo - Pronto para Uso!

---

## 🎯 O que foi entregue

Bot de trading automático para **ApeX Omni** com:

✅ **3 Estratégias Pré-definidas** (C1, C2, C4)  
✅ **Operações direcionais** (long E short)  
✅ **TP/SL automático** (baseado em ATR)  
✅ **Paper trading** (simulado, sem risco)  
✅ **Live trading** (pronto para ApeX Omni)  
✅ **Parametrização flexível** (YAML + CLI)  
✅ **Persistência de estado** (recupera após reinício)  
✅ **Logs detalhados em CSV**  
✅ **Documentação completa em português**  

---

## 📁 Estrutura do Projeto

```
scalping-bot/
│
├── main.py                          # 🚀 Ponto de entrada (execute este!)
├── config.yaml                      # ⚙️ Configuração principal
├── config_override_example.yaml    # 📝 Exemplo de override
├── requirements.txt                 # 📦 Dependências Python
├── install.sh                       # 🔧 Script de instalação
│
├── README.md                        # 📚 Documentação completa
├── QUICK_START_PT.md               # ⚡ Início rápido
├── STRATEGIES.md                    # 📊 Detalhes das estratégias
├── ENTREGA.md                       # 📦 Este arquivo
│
├── core/                            # 🧠 Módulos principais
│   ├── indicators.py                # EMA, RSI, ATR, VolMA
│   ├── strategies.py                # C1, C2, C4
│   ├── data_provider.py             # Live + CSV data
│   ├── execution.py                 # Paper + Live execution
│   ├── position_state.py            # Persistência JSON
│   └── utils.py                     # Funções auxiliares
│
├── data/                            # 📊 Dados CSV (backtest)
│   └── BTCUSDT_15m_example.csv
│
├── logs/                            # 📝 Logs de trades
│   └── trades.csv (gerado)
│
├── state/                           # 💾 Estado de posições
│   └── position_state.json (gerado)
│
├── apex_client.py                   # 🔌 Cliente ApeX Omni
├── resilience.py                    # 🛡️ Resiliência de API
├── logger_config.py                 # 📋 Config de logs
└── test_setup.py                    # 🧪 Teste de instalação
```

---

## 🚀 Como Usar

### 1. Instalar

```bash
cd ~/scalping-bot
./install.sh
```

### 2. Configurar

```bash
nano config.yaml
```

Adicione suas credenciais ApeX Omni:

```yaml
apex:
  api_key: "SUA_API_KEY"
  api_secret: "SEU_SECRET"
  api_passphrase: "SUA_PASSPHRASE"
  zk_seeds: "SEUS_ZK_SEEDS"
```

### 3. Testar

```bash
python test_setup.py
```

### 4. Rodar

**Paper trading (simulado):**
```bash
python main.py --symbol BTCUSDT --strategy C2 --mode paper --data_source csv
```

**Live trading (real):**
```bash
python main.py --symbol BTCUSDT --strategy C2 --mode live --data_source live
```

---

## 📊 As 3 Estratégias

### C1 — Breakout Falso (Reversão)
- **Conceito**: Captura reversões após fakeouts de mínimas/máximas
- **TP/SL**: 1.8× ATR / 0.8× ATR
- **Risk/Reward**: 2.25:1
- **Melhor em**: Mercados laterais, ranges definidos

### C2 — Candle de Expansão (Momentum)
- **Conceito**: Entra após candles de alta expansão + breakout
- **TP/SL**: 1.4× ATR / 0.6× ATR
- **Risk/Reward**: 2.33:1
- **Melhor em**: Breakouts, início de tendências

### C4 — Pullback na Tendência (Trend Scalp)
- **Conceito**: Entra em pullbacks de tendências estabelecidas
- **TP/SL**: 1.0× ATR / 0.5× ATR
- **Risk/Reward**: 2.0:1
- **Melhor em**: Tendências fortes, gráficos 1h

---

## ⚙️ Parametrização Flexível

### Via config.yaml

```yaml
general:
  symbol: "BTCUSDT"
  strategy: "C2"
  timeframe: "15m"
  order_value_usd: 1000
  use_long: true
  use_short: true
  mode: "paper"

strategies:
  C2:
    ema_fast: 9
    ema_slow: 21
    rsi_min: 45
    rsi_max: 60
    tp_atr_mult: 1.4
    sl_atr_mult: 0.6
```

### Via CLI (override)

```bash
python main.py \
  --symbol BTCUSDT \
  --strategy C2 \
  --timeframe 15m \
  --order_value_usd 1500 \
  --tp_atr 2.0 \
  --sl_atr 0.5 \
  --use_long true \
  --use_short false
```

---

## 📝 Logs Detalhados

Todos os trades são salvos em `./logs/trades.csv`:

```csv
timestamp,symbol,strategy,side,entry_price,exit_price,quantity,tp_price,sl_price,exit_reason,pnl_usd,fee_usd,net_pnl_usd,atr,rsi,ema_fast,ema_slow
2025-10-28T10:30:00,BTC-USDT,C2,LONG,65000.00,65700.00,0.015,65910.00,64610.00,TP,10.50,0.98,9.52,650.00,52.3,65100.00,64900.00
```

### Análise de Performance

```python
import pandas as pd

df = pd.read_csv('./logs/trades.csv')

# PnL total
print(f"PnL Total: ${df['net_pnl_usd'].sum():.2f}")

# Win rate
win_rate = (df['net_pnl_usd'] > 0).mean() * 100
print(f"Win Rate: {win_rate:.1f}%")

# Por estratégia
df.groupby('strategy')['net_pnl_usd'].agg(['sum', 'mean', 'count'])
```

---

## 💾 Persistência de Estado

O bot salva o estado da posição em `./state/position_state.json`.

**Vantagens:**
- ✅ Se bot parar, retoma posição ao reiniciar
- ✅ Não perde TP/SL
- ✅ Continua monitorando automaticamente

---

## 🧪 Testes

```bash
# Testar instalação
python test_setup.py

# Paper trading com CSV
python main.py --symbol BTCUSDT --strategy C2 --mode paper --data_source csv

# Paper trading com dados live
python main.py --symbol BTCUSDT --strategy C2 --mode paper --data_source live
```

---

## 📚 Documentação

| Arquivo | Conteúdo |
|---------|----------|
| **README.md** | Documentação completa em português |
| **QUICK_START_PT.md** | Início rápido em 3 passos |
| **STRATEGIES.md** | Detalhes das 3 estratégias |
| **config.yaml** | Todos os parâmetros comentados |

---

## ⚠️ Avisos Importantes

1. ⚠️ **Sempre teste em PAPER primeiro** antes de usar LIVE
2. 🔐 **NUNCA commite credenciais** no git (use .gitignore)
3. 💰 **Comece com valores pequenos** em live
4. 📊 **1 instância = 1 ativo + 1 estratégia**
5. 🔄 **Para múltiplos ativos**, rode múltiplas instâncias do bot

---

## 🎓 Próximos Passos

### 1. Testar em Paper (1-2 dias)
```bash
python main.py --symbol BTCUSDT --strategy C2 --mode paper --data_source csv
```

### 2. Analisar Performance
```bash
# Veja logs/trades.csv
# Analise win rate, PnL médio, etc
```

### 3. Ajustar Parâmetros
```bash
# Teste diferentes TP/SL
python main.py --symbol BTCUSDT --strategy C2 --tp_atr 2.0 --sl_atr 0.5
```

### 4. Live com Valores Pequenos
```bash
# CUIDADO: dinheiro real!
python main.py --symbol BTCUSDT --strategy C2 --mode live --order_value_usd 100
```

---

## 🔧 Requisitos Técnicos

- **OS**: WSL/Ubuntu (ou qualquer Linux)
- **Python**: 3.10+
- **Conta**: ApeX Omni com API habilitada
- **Dependências**: Instaladas via `pip install -r requirements.txt`

---

## ✅ Checklist de Entrega

- [x] 3 Estratégias implementadas (C1, C2, C4)
- [x] Paper trading funcionando
- [x] Live trading pronto (ApeX Omni)
- [x] TP/SL automático via ATR
- [x] Parametrização flexível (YAML + CLI)
- [x] Persistência de estado (JSON)
- [x] Logs detalhados (CSV)
- [x] Cliente ApeX Omni integrado
- [x] Indicadores técnicos (EMA, RSI, ATR, VolMA)
- [x] Data provider (Live + CSV)
- [x] Executor (Paper + Live)
- [x] README completo em português
- [x] Script de instalação (install.sh)
- [x] Teste de setup (test_setup.py)
- [x] Exemplo de CSV
- [x] .gitignore configurado

---

## 🎯 Resultado Final

✅ **Bot 100% funcional e pronto para uso!**

**O que você pode fazer agora:**

1. ✅ Rodar em **paper mode** com dados CSV (sem risco)
2. ✅ Rodar em **paper mode** com dados live da ApeX (sem risco)
3. ✅ Rodar em **live mode** na ApeX Omni (trading real)
4. ✅ Testar as **3 estratégias** (C1, C2, C4)
5. ✅ Ajustar **parâmetros** via config ou CLI
6. ✅ Operar **long E short**
7. ✅ Monitorar **logs em tempo real**
8. ✅ Analisar **performance** via CSV

---

## 📞 Suporte

**Leia primeiro:**
- `README.md` - documentação completa
- `QUICK_START_PT.md` - início rápido
- `STRATEGIES.md` - detalhes das estratégias

**Rode o teste:**
```bash
python test_setup.py
```

**Se algo não funcionar**, verifique:
1. Python 3.10+ instalado
2. Dependências instaladas (`pip install -r requirements.txt`)
3. Credenciais ApeX configuradas em `config.yaml`
4. Arquivo CSV no formato correto (se usar `data_source: csv`)

---

## 🏆 Conclusão

Projeto entregue **completo e funcional**! 🎉

- ✅ Código limpo e modular
- ✅ Documentação em português
- ✅ Pronto para WSL/Ubuntu
- ✅ Paper + Live trading
- ✅ 3 estratégias testadas
- ✅ Parametrização total

**Bons trades! 📈🚀💰**

---

*Desenvolvido com base no bot de long/short da ApeX Omni*  
*Compatível com ApeX Omni API (https://api-docs.omni.apex.exchange/)*
