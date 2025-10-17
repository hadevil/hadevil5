# 📊 Guia de Backtesting e Análise de Performance

## 🎯 Objetivo

Este guia mostra como usar o banco de dados SQLite para:
- Analisar performance de trades
- Encontrar melhores valores de SL e TP
- Otimizar parâmetros para cada par

---

## 📂 Arquivo do Banco de Dados

O bot cria automaticamente: **`trades.db`**

Localização: Mesma pasta onde o bot roda

---

## 🗄️ Estrutura das Tabelas

### **1. trades** (Histórico de Posições)
```sql
- cycle_id: ID do ciclo
- symbol: Par de trading (BTC-USDT, ETH-USDT, etc)
- side: LONG ou SHORT
- entry_time: Quando abriu
- exit_time: Quando fechou  
- entry_price: Preço de entrada
- exit_price: Preço de saída
- size: Tamanho da posição
- leverage: Alavancagem usada
- unrealized_pnl: PnL não realizado
- realized_pnl: PnL final realizado
- fees: Taxas pagas
- close_reason: STOP_LOSS, TAKE_PROFIT, TIME_LIMIT, MANUAL_CLOSE
- duration_minutes: Duração em minutos
- config_sl: SL usado neste trade
- config_tp: TP usado neste trade
- config_time_limit: Limite de tempo usado
- status: OPEN ou CLOSED
```

### **2. cycles** (Ciclos Completos)
```sql
- cycle_id: ID único do ciclo
- start_time: Início
- end_time: Fim
- total_pnl: PnL total do ciclo
- close_reason: Razão do fechamento
- duration_minutes: Duração
- num_positions: Número de posições no ciclo
- config_snapshot: JSON com configuração usada
```

### **3. performance_metrics** (Métricas Agregadas)
```sql
- date: Data
- total_trades: Total de trades
- winning_trades: Trades vencedores
- losing_trades: Trades perdedores
- total_pnl: PnL total
- win_rate: Taxa de acerto
- avg_win: Média de ganhos
- avg_loss: Média de perdas
- profit_factor: Fator de lucro
- max_drawdown: Drawdown máximo
```

---

## 📊 Queries Úteis para Análise

### **Ver Todos os Trades**
```sql
SELECT 
    symbol,
    side,
    entry_time,
    exit_time,
    realized_pnl,
    close_reason,
    duration_minutes
FROM trades
WHERE status = 'CLOSED'
ORDER BY entry_time DESC
LIMIT 100;
```

### **Performance por Símbolo**
```sql
SELECT 
    symbol,
    COUNT(*) as total_trades,
    SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN realized_pnl < 0 THEN 1 ELSE 0 END) as losses,
    ROUND(AVG(realized_pnl), 2) as avg_pnl,
    ROUND(SUM(realized_pnl), 2) as total_pnl,
    ROUND(100.0 * SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
FROM trades
WHERE status = 'CLOSED'
GROUP BY symbol
ORDER BY total_pnl DESC;
```

### **Melhor SL para Cada Símbolo**
```sql
SELECT 
    symbol,
    config_sl as stop_loss,
    COUNT(*) as trades,
    ROUND(AVG(realized_pnl), 2) as avg_pnl,
    ROUND(SUM(realized_pnl), 2) as total_pnl,
    ROUND(100.0 * SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
FROM trades
WHERE status = 'CLOSED' AND symbol = 'BTC-USDT'
GROUP BY config_sl
ORDER BY total_pnl DESC;
```

### **Melhor TP para Cada Símbolo**
```sql
SELECT 
    symbol,
    config_tp as take_profit,
    COUNT(*) as trades,
    ROUND(AVG(realized_pnl), 2) as avg_pnl,
    ROUND(SUM(realized_pnl), 2) as total_pnl,
    SUM(CASE WHEN close_reason = 'TAKE_PROFIT' THEN 1 ELSE 0 END) as tp_hits
FROM trades
WHERE status = 'CLOSED' AND symbol = 'BTC-USDT'
GROUP BY config_tp
ORDER BY total_pnl DESC;
```

### **Análise por Razão de Fechamento**
```sql
SELECT 
    close_reason,
    COUNT(*) as count,
    ROUND(AVG(realized_pnl), 2) as avg_pnl,
    ROUND(SUM(realized_pnl), 2) as total_pnl,
    ROUND(AVG(duration_minutes), 2) as avg_duration
FROM trades
WHERE status = 'CLOSED'
GROUP BY close_reason
ORDER BY count DESC;
```

### **Performance LONG vs SHORT**
```sql
SELECT 
    side,
    COUNT(*) as trades,
    ROUND(AVG(realized_pnl), 2) as avg_pnl,
    ROUND(SUM(realized_pnl), 2) as total_pnl,
    ROUND(100.0 * SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
FROM trades
WHERE status = 'CLOSED'
GROUP BY side;
```

### **Melhor Horário para Trading**
```sql
SELECT 
    strftime('%H', entry_time) as hour,
    COUNT(*) as trades,
    ROUND(AVG(realized_pnl), 2) as avg_pnl,
    ROUND(SUM(realized_pnl), 2) as total_pnl
FROM trades
WHERE status = 'CLOSED'
GROUP BY hour
ORDER BY total_pnl DESC;
```

---

## 🐍 Script Python para Análise

Salve como `analyze_trades.py`:

```python
#!/usr/bin/env python3
import sqlite3
import pandas as pd

# Conectar ao database
conn = sqlite3.connect('trades.db')

# Carregar todos os trades
trades_df = pd.read_sql_query("""
    SELECT * FROM trades WHERE status = 'CLOSED'
""", conn)

print("="*60)
print("📊 ANÁLISE DE PERFORMANCE")
print("="*60)
print(f"\nTotal de trades: {len(trades_df)}")
print(f"PnL total: ${trades_df['realized_pnl'].sum():.2f}")
print(f"Win rate: {(trades_df['realized_pnl'] > 0).sum() / len(trades_df) * 100:.2f}%")
print(f"Avg win: ${trades_df[trades_df['realized_pnl'] > 0]['realized_pnl'].mean():.2f}")
print(f"Avg loss: ${trades_df[trades_df['realized_pnl'] < 0]['realized_pnl'].mean():.2f}")

# Performance por símbolo
print("\n" + "="*60)
print("📈 PERFORMANCE POR SÍMBOLO")
print("="*60)
perf_by_symbol = trades_df.groupby('symbol').agg({
    'realized_pnl': ['count', 'sum', 'mean']
}).round(2)
print(perf_by_symbol)

# Melhor SL/TP para BTC-USDT
btc_trades = trades_df[trades_df['symbol'] == 'BTC-USDT']
if len(btc_trades) > 0:
    print("\n" + "="*60)
    print("🔍 OTIMIZAÇÃO SL/TP PARA BTC-USDT")
    print("="*60)
    
    sl_analysis = btc_trades.groupby('config_sl').agg({
        'realized_pnl': ['count', 'sum', 'mean']
    }).round(2)
    print("\nPor Stop Loss:")
    print(sl_analysis)
    
    tp_analysis = btc_trades.groupby('config_tp').agg({
        'realized_pnl': ['count', 'sum', 'mean']
    }).round(2)
    print("\nPor Take Profit:")
    print(tp_analysis)

conn.close()
```

Executar:
```bash
pip3 install pandas
python3 analyze_trades.py
```

---

## 🔬 Backtest de Diferentes SL/TP

Depois de coletar dados reais com diferentes configurações:

### **Experimento 1: Testar SL=-50, -100, -150**
```bash
# Rodar por 3 dias com SL=-50 (editar config.txt)
# Rodar por 3 dias com SL=-100
# Rodar por 3 dias com SL=-150
```

### **Experimento 2: Testar TP=100, 200, 300**
```bash
# Similar ao acima, mudando TP
```

### **Análise:**
```sql
-- Ver qual combinação performou melhor
SELECT 
    config_sl,
    config_tp,
    COUNT(*) as trades,
    ROUND(AVG(realized_pnl), 2) as avg_pnl,
    ROUND(SUM(realized_pnl), 2) as total_pnl,
    ROUND(100.0 * SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
FROM trades
WHERE status = 'CLOSED'
GROUP BY config_sl, config_tp
HAVING COUNT(*) >= 10
ORDER BY total_pnl DESC;
```

---

## 📱 Acessar Database

### **Via SQLite CLI:**
```bash
sqlite3 trades.db
```

```sql
.tables
.schema trades
SELECT * FROM trades LIMIT 10;
.quit
```

### **Via Python:**
```python
import sqlite3

conn = sqlite3.connect('trades.db')
cursor = conn.execute("SELECT * FROM trades WHERE status='CLOSED'")
for row in cursor:
    print(row)
conn.close()
```

### **Via DB Browser (GUI):**
1. Download: https://sqlitebrowser.org/
2. Abrir: `trades.db`
3. Navegar visualmente

---

## 🎯 Workflow Recomendado

1. **Fase 1: Coleta de Dados (1-2 semanas)**
   - Rodar bot com parâmetros iniciais
   - Deixar acumular trades
   - Não mudar configuração

2. **Fase 2: Análise**
   - Usar queries SQL acima
   - Identificar padrões
   - Ver qual SL/TP performa melhor

3. **Fase 3: Otimização**
   - Ajustar config.txt com melhores valores
   - Rodar por mais 1 semana
   - Comparar resultados

4. **Fase 4: Refinamento**
   - Repetir processo
   - Ajustes finos
   - Maximizar profit factor

---

## 📈 Métricas Importantes

- **Win Rate >50%**: Mais trades ganhos que perdidos
- **Profit Factor >1.5**: Ganhos médios > Perdas médias
- **Avg Win / Avg Loss >2**: Risk/Reward favorável
- **Max Drawdown <20%**: Controle de risco

---

## 💡 Dicas

- Quanto mais dados, melhor a análise
- Teste um parâmetro por vez
- Documente mudanças
- Compare períodos similares (mesma volatilidade)
- Considere funding fees

---

**Happy Backtesting! 📊**
