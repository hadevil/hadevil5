# 📊 Estratégias Detalhadas

Este documento descreve as 3 estratégias implementadas no bot.

---

## C1 — Breakout Falso (Reversão Curta)

### 🎯 Conceito
Captura reversões após fakeouts (rompimentos falsos) de mínimas/máximas recentes.

### 📐 Parâmetros Padrão (Backtest)
```yaml
ema_fast: 20
ema_slow: 50
rsi_min: 40
rsi_max: 65
tp_atr_mult: 1.8
sl_atr_mult: 0.8
filter_volume: true
volume_ma_mult: 1.2
range_lookback: 12
```

### 🔍 Lógica LONG

**1. Identificar mínima do range**
- Calcular `range_min = min(low das últimas 12 barras)`

**2. Detectar fakeout**
- Close da barra anterior `< range_min` (rompeu para baixo)
- Close da barra atual `> range_min` (voltou para dentro)
- **Interpretação**: Vendedores foram rejeitados → reversão para cima

**3. Filtros de confirmação**
```
✓ EMA(20) > EMA(50)  → Tendência de alta
✓ 40 ≤ RSI ≤ 65      → Força moderada
✓ Volume > 1.2×MA    → Participação significativa
```

**4. Entrada**
- Entry: Close atual (imediato)
- TP: Entry + 1.8× ATR(10)
- SL: Entry - 0.8× ATR(10)

### 🔍 Lógica SHORT
Espelhado:
- `range_max = max(high das últimas 12 barras)`
- Close anterior `> range_max`, close atual `< range_max`
- EMA(20) < EMA(50)
- TP: Entry - 1.8× ATR
- SL: Entry + 0.8× ATR

### 💡 Quando usar C1
- Mercados com ranges definidos
- Após notícias (rejeição de extremos)
- Timeframes: 15m, 1h

---

## C2 — Candle de Expansão (Momentum Scalp)

### 🎯 Conceito
Captura momentum forte após candles de alta expansão (âncora).

### 📐 Parâmetros Padrão (Backtest)
```yaml
ema_fast: 9
ema_slow: 21
rsi_min: 45
rsi_max: 60
tp_atr_mult: 1.4
sl_atr_mult: 0.6
filter_atr: true
anchor_vol_mult: 1.5
```

### 🔍 Lógica LONG

**1. Identificar candle âncora (barra anterior)**
```
✓ Range > ATR(10)        → Alta volatilidade
✓ Volume > 1.5×VolMA20   → Forte participação
```
Se barra anterior NÃO atende → não há sinal.

**2. Detectar breakout**
- Close atual `> High do âncora`
- **Interpretação**: Momentum continua na direção da expansão

**3. Filtros de confirmação**
```
✓ EMA(9) > EMA(21)   → Tendência de alta
✓ 45 ≤ RSI ≤ 60      → Força moderada
✓ ATR(10) > ATR_MA   → Volatilidade acima da média
```

**4. Entrada**
- Entry: Close atual
- TP: Entry + 1.4× ATR(10)
- SL: Entry - 0.6× ATR(10)

### 🔍 Lógica SHORT
Espelhado:
- Âncora com range alto + volume alto
- Close atual `< Low do âncora`
- EMA(9) < EMA(21)

### 💡 Quando usar C2
- Breakouts de consolidações
- Início de tendências fortes
- Após releases econômicos
- Timeframes: 15m, 1h

---

## C4 — Pullback na Tendência (Trend Scalp)

### 🎯 Conceito
Captura pullbacks (retrações curtas) em tendências estabelecidas.

### 📐 Parâmetros Padrão (Backtest)
```yaml
ema_fast: 13
ema_slow: 34
rsi_min: 47
rsi_max: 57
tp_atr_mult: 1.0
sl_atr_mult: 0.5
filter_pullback: true
```

### 🔍 Lógica LONG

**1. Confirmar tendência de alta**
```
✓ EMA(13) > EMA(34)
```

**2. Detectar pullback**
```
✓ Close < EMA(13)  (se filter_pullback=true)
```
**Interpretação**: Preço recuou abaixo da EMA rápida → oportunidade de entrada

**3. Filtro RSI**
```
✓ 47 ≤ RSI ≤ 57  → Força balanceada
```

**4. Entrada**
- Entry: Close atual
- TP: Entry + 1.0× ATR(10)
- SL: Entry - 0.5× ATR(10)

### 🔍 Lógica SHORT
Espelhado:
- EMA(13) < EMA(34) → Tendência de baixa
- Close > EMA(13) → Pullback para cima
- 47 ≤ RSI ≤ 57

### 💡 Quando usar C4
- Tendências fortes já estabelecidas
- Pullbacks em gráficos 1h
- Menor risco (SL mais apertado)
- Alvo menor, maior taxa de acerto

---

## 🔄 Comparação das Estratégias

| Estratégia | TP/SL (ATR) | Tipo | Timeframe ideal | Risk/Reward |
|------------|-------------|------|-----------------|-------------|
| **C1** | 1.8/0.8 | Reversão | 15m, 1h | Alto (2.25) |
| **C2** | 1.4/0.6 | Momentum | 15m, 1h | Médio (2.33) |
| **C4** | 1.0/0.5 | Pullback | 1h | Baixo (2.0) |

---

## ⚙️ Personalizando Estratégias

### Via `config.yaml`:

```yaml
strategies:
  C2:
    # Mude EMAs para tendência mais lenta
    ema_fast: 13
    ema_slow: 34
    
    # Amplie faixa de RSI
    rsi_min: 40
    rsi_max: 65
    
    # Alvo mais agressivo
    tp_atr_mult: 2.0
    sl_atr_mult: 0.5
```

### Via CLI:

```bash
python main.py --symbol BTCUSDT --strategy C2 --tp_atr 2.0 --sl_atr 0.5
```

---

## 📈 Dicas de Uso

### C1 — Breakout Falso
✅ **Funciona bem em:**
- Mercados laterais com ranges definidos
- Após topos/fundos recentes testados
- Volumes altos nos extremos

❌ **Evite em:**
- Tendências muito fortes (poucos fakeouts)
- Baixa volatilidade

### C2 — Candle de Expansão
✅ **Funciona bem em:**
- Breakouts de consolidações
- Notícias/releases econômicos
- Início de tendências

❌ **Evite em:**
- Mercados muito laterais
- Candles pequenos sem momentum

### C4 — Pullback na Tendência
✅ **Funciona bem em:**
- Tendências fortes já estabelecidas
- Retrações curtas em gráficos 1h
- Mercados com EMAs bem espaçadas

❌ **Evite em:**
- Mercados laterais (EMAs se cruzam)
- Pullbacks muito profundos (perigo de reversão)

---

## 🧪 Testando Estratégias

### 1. Paper Trading com CSV

```bash
# Prepare dados históricos em ./data/BTCUSDT_15m.csv
python main.py --symbol BTCUSDT --strategy C2 --mode paper --data_source csv
```

### 2. Live Data + Paper Execution

```bash
# Usa dados reais, mas não executa ordens
python main.py --symbol BTCUSDT --strategy C1 --mode paper --data_source live
```

### 3. Comparar Estratégias

Rode 3 instâncias em paralelo:

```bash
# Terminal 1
python main.py --symbol BTCUSDT --strategy C1 --mode paper

# Terminal 2
python main.py --symbol BTCUSDT --strategy C2 --mode paper

# Terminal 3
python main.py --symbol BTCUSDT --strategy C4 --mode paper
```

Depois, compare `./logs/trades.csv` de cada.

---

## 📊 Análise de Performance

Após alguns trades, analise o CSV:

```python
import pandas as pd

df = pd.read_csv('./logs/trades.csv')

# PnL por estratégia
df.groupby('strategy')['net_pnl_usd'].agg(['sum', 'mean', 'count'])

# Win rate
df['win'] = df['net_pnl_usd'] > 0
df.groupby('strategy')['win'].mean() * 100  # %

# Best strategy
df.groupby('strategy')['net_pnl_usd'].sum().idxmax()
```

---

**Boa sorte com suas estratégias! 📈🚀**
