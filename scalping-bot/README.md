# 📈 Scalping Bot - Bot Direcional de Trading

Bot de trading automático para operar estratégias de scalping direcional (long e short) na exchange ApeX.

## 🎯 Características

- **3 Estratégias Pré-definidas**: C1 (Breakout Falso), C2 (Candle de Expansão), C4 (Pullback na Tendência)
- **Direcional**: Opera tanto long quanto short
- **TP/SL Automático**: Baseado em múltiplos de ATR
- **Parametrização Flexível**: Configure indicadores, TP/SL via YAML ou CLI
- **Paper Trading**: Teste estratégias sem risco
- **Persistência de Estado**: Recupera posições após reinício
- **Logs Detalhados**: CSV com todos os trades

## 📋 Pré-requisitos

- **Sistema**: WSL/Ubuntu (ou qualquer Linux)
- **Python**: 3.10 ou superior
- **pip**: Gerenciador de pacotes Python

## 🚀 Instalação

### 1. Clone ou copie o projeto

```bash
cd ~
# Projeto já está em ./scalping-bot
cd scalping-bot
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure o bot

Edite o arquivo `config.yaml`:

```bash
nano config.yaml
```

**Configurações principais:**

```yaml
general:
  symbol: "BTCUSDT"           # Ativo a operar
  strategy: "C2"              # Estratégia: C1, C2 ou C4
  timeframe: "15m"            # 15m ou 1h
  order_value_usd: 1000       # Valor por operação (USD)
  mode: "paper"               # paper (simulado) ou live (real)
  data_source: "csv"          # csv (local) ou live (exchange)
```

**Para usar em LIVE (real)**, adicione suas credenciais da ApeX:

```yaml
apex:
  api_key: "SUA_API_KEY"
  api_secret: "SEU_SECRET"
  api_passphrase: "SUA_PASSPHRASE"
  zk_seeds: "SEUS_ZK_SEEDS"
```

## 📊 Preparar Dados (para CSV/Paper Trading)

Se usar `data_source: "csv"`, coloque arquivos CSV na pasta `./data/`:

**Formato esperado** (`BTCUSDT_15m.csv`):

```csv
timestamp,open,high,low,close,volume
2025-10-28T10:00:00,65000.50,65100.00,64900.00,65050.00,1234567.89
2025-10-28T10:15:00,65050.00,65200.00,65000.00,65150.00,1456789.12
...
```

- **timestamp**: ISO format (YYYY-MM-DDTHH:MM:SS) ou Unix timestamp
- **Nomenclatura**: `{SYMBOL}_{TIMEFRAME}.csv` (ex: `BTCUSDT_15m.csv`, `ETHUSDT_1h.csv`)

## 🎮 Como Usar

### Modo básico (usa config.yaml)

```bash
python main.py
```

### Com parâmetros via CLI

```bash
# Exemplo 1: BTC, estratégia C2, timeframe 15m, $1500 por operação
python main.py --symbol BTCUSDT --strategy C2 --timeframe 15m --order_value_usd 1500

# Exemplo 2: ETH, estratégia C1, timeframe 1h, ajustar TP/SL
python main.py --symbol ETHUSDT --strategy C1 --timeframe 1h --tp_atr 2.0 --sl_atr 1.0

# Exemplo 3: SOL, estratégia C4, apenas long
python main.py --symbol SOLUSDT --strategy C4 --use_long true --use_short false

# Exemplo 4: Paper trading com dados CSV
python main.py --symbol BTCUSDT --strategy C2 --mode paper --data_source csv
```

### Parâmetros CLI disponíveis

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `--config` | Arquivo de configuração | `--config config.yaml` |
| `--symbol` | Símbolo a operar | `--symbol BTCUSDT` |
| `--strategy` | Estratégia (C1, C2, C4) | `--strategy C2` |
| `--timeframe` | Timeframe (15m, 1h) | `--timeframe 15m` |
| `--order_value_usd` | Valor da ordem (USD) | `--order_value_usd 1500` |
| `--mode` | Modo (paper, live) | `--mode paper` |
| `--data_source` | Fonte de dados (csv, live) | `--data_source csv` |
| `--tp_atr` | TP múltiplo de ATR | `--tp_atr 1.6` |
| `--sl_atr` | SL múltiplo de ATR | `--sl_atr 0.6` |
| `--use_long` | Habilitar long | `--use_long true` |
| `--use_short` | Habilitar short | `--use_short false` |

## 📈 Estratégias

### C1 — Breakout Falso (Reversão curta)

**Parâmetros padrão:**
- EMAs: 20/50
- RSI: 40-65
- TP: 1.8× ATR | SL: 0.8× ATR
- Filtro volume: > 1.2× VolMA20

**Lógica Long:**
1. Detecta fakeout de mínima de range (12 barras)
2. EMA20 > EMA50 (tendência de alta)
3. RSI entre 40-65
4. Volume > 1.2× média

**Lógica Short:** Espelho (fakeout de máxima)

---

### C2 — Candle de Expansão (Momentum scalp)

**Parâmetros padrão:**
- EMAs: 9/21
- RSI: 45-60
- TP: 1.4× ATR | SL: 0.6× ATR
- Filtro ATR: > ATR MA(20)

**Lógica Long:**
1. Candle anterior = âncora (range > ATR, volume > 1.5× VolMA)
2. Close atual rompe máxima do âncora
3. EMA9 > EMA21
4. RSI entre 45-60
5. ATR > ATR MA

**Lógica Short:** Espelho (rompe mínima do âncora)

---

### C4 — Pullback na Tendência (Trend scalp)

**Parâmetros padrão:**
- EMAs: 13/34
- RSI: 47-57
- TP: 1.0× ATR | SL: 0.5× ATR

**Lógica Long:**
1. Tendência: EMA13 > EMA34
2. Pullback: close < EMA13
3. RSI entre 47-57

**Lógica Short:** Espelho (tendência de baixa, pullback acima)

## 📁 Estrutura do Projeto

```
scalping-bot/
├── main.py                    # Ponto de entrada (CLI + loop principal)
├── config.yaml                # Configuração padrão
├── config_override_example.yaml  # Exemplo de override
├── requirements.txt           # Dependências Python
├── README.md                  # Este arquivo
│
├── core/                      # Módulos principais
│   ├── __init__.py
│   ├── indicators.py          # EMA, RSI, ATR, VolMA
│   ├── strategies.py          # C1, C2, C4
│   ├── data_provider.py       # LiveProvider + CSVProvider
│   ├── execution.py           # PaperExecutor + ApexExecutor
│   ├── position_state.py      # Persistência JSON
│   └── utils.py               # Helpers
│
├── data/                      # Arquivos CSV (para backtest)
│   └── BTCUSDT_15m.csv
│
├── logs/                      # Logs de trades
│   └── trades.csv
│
├── state/                     # Estado de posições
│   └── position_state.json
│
├── apex_client.py             # Cliente ApeX (reutilizado)
├── resilience.py              # Resiliência de API
└── logger_config.py           # Configuração de logs
```

## 📊 Logs de Trades

Todos os trades são salvos em `./logs/trades.csv`:

```csv
timestamp,symbol,strategy,side,entry_price,exit_price,quantity,tp_price,sl_price,exit_reason,pnl_usd,fee_usd,net_pnl_usd,atr,rsi,ema_fast,ema_slow
2025-10-28T10:30:00,BTC-USDT,C2,LONG,65000.00,65700.00,0.015,65910.00,64610.00,TP,10.50,0.98,9.52,650.00,52.3,65100.00,64900.00
```

## 🔄 Recuperação de Estado

O bot salva o estado da posição em `./state/position_state.json`. Se o bot parar e reiniciar com posição aberta:

1. Carrega posição do arquivo
2. Continua monitorando TP/SL
3. Fecha quando atingir exit

## ⚠️ Avisos Importantes

1. **Paper Trading Primeiro**: Sempre teste com `mode: paper` antes de usar `mode: live`
2. **Credenciais**: NUNCA commite credenciais no git
3. **1 Instância = 1 Ativo + 1 Estratégia**: Para múltiplos ativos/estratégias, rode múltiplas instâncias
4. **Timeframe Real**: O bot verifica sinais a cada intervalo baseado no timeframe (15m → 60s, 1h → 180s)
5. **Dados CSV**: Para paper trading, use dados históricos reais (ex: baixe de Binance, ApeX, etc.)

## 🐛 Troubleshooting

### Erro: "No CSV file found"

Certifique-se de que o arquivo CSV está em `./data/` com nome correto:
- `BTCUSDT_15m.csv` (sem hífen)
- ou `BTC-USDT_15m.csv` (com hífen)

### Erro: "apex_client required for live"

Configure as credenciais da ApeX em `config.yaml` seção `apex:`.

### Erro: "Insufficient data"

O bot precisa de pelo menos 200 barras para calcular indicadores. Verifique seu CSV ou aguarde mais dados em live.

### Indicadores retornando NaN

Aguarde mais barras. Indicadores como EMA(50) precisam de ~200 barras para estabilizar.

## 📝 Exemplos de Uso

### 1. Testar C2 em BTC (paper, CSV)

```bash
python main.py --symbol BTCUSDT --strategy C2 --mode paper --data_source csv --timeframe 15m
```

### 2. Rodar C1 em ETH (live data, paper execution)

```bash
python main.py --symbol ETHUSDT --strategy C1 --mode paper --data_source live --timeframe 1h
```

### 3. Trading real na ApeX (C4, SOL)

```bash
# CUIDADO: Isso usa dinheiro real!
python main.py --symbol SOLUSDT --strategy C4 --mode live --data_source live --order_value_usd 500
```

### 4. Override de parâmetros

```bash
# C2 com TP mais alto e SL mais baixo
python main.py --symbol BTCUSDT --strategy C2 --tp_atr 2.0 --sl_atr 0.4
```

## 🎓 Próximos Passos

1. **Teste em Paper**: Rode por algumas horas/dias com dados CSV
2. **Analise Logs**: Veja `./logs/trades.csv` para performance
3. **Ajuste Parâmetros**: Mude TP/SL, EMAs conforme necessário
4. **Live Testnet**: Se ApeX tiver testnet, teste lá primeiro
5. **Live Real**: Com confiança, use `mode: live` com valores pequenos

## 📞 Suporte

Para dúvidas sobre:
- **Estratégias**: Revise a seção "Estratégias" acima
- **Parâmetros**: Veja `config.yaml` comentado
- **ApeX API**: Consulte https://api-docs.omni.apex.exchange/

## ⚖️ License

MIT License - Use por sua conta e risco. Trading envolve riscos financeiros.

---

**Boa sorte com seu scalping! 🚀📈**
