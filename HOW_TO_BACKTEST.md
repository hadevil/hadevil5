# 🔬 Como Fazer Backtest e Otimizar Parâmetros

## 🎯 O QUE É ISSO?

Depois de rodar o bot por alguns dias, você terá **dados reais** salvos no database (`trades.db`).

Com esses dados, você pode **simular** diferentes valores de SL/TP/Time para descobrir qual combinação teria dado **MAIS LUCRO**.

---

## 📋 PROCESSO COMPLETO

```
1. RODAR BOT (coletar dados reais)
   ↓
2. ANALISAR (ver como está performando)
   ↓
3. OTIMIZAR (testar diferentes SL/TP/Time)
   ↓
4. APLICAR (usar melhores parâmetros)
   ↓
5. REPETIR
```

---

## 🚀 PASSO A PASSO

### 1️⃣ COLETAR DADOS (Rode o bot)

```bash
# Inicie o bot normalmente
python3 main.py

# Deixe rodar por pelo menos 10-20 ciclos
# Pode levar 1-3 dias dependendo dos parâmetros
```

**O que o bot salva:**
- Cada trade (símbolo, preço entrada/saída, PnL)
- Cada ciclo (SL/TP/Time usado, motivo de fechamento)
- Timestamps de tudo

**Arquivo gerado:** `trades.db` (SQLite database)

---

### 2️⃣ ANALISAR PERFORMANCE

```bash
python3 analyze_performance.py
```

**O que mostra:**
- PnL total e por símbolo
- Win rate (% de trades ganhos)
- Profit factor
- Performance LONG vs SHORT
- Quantas vezes fechou por TP/SL/Time
- Se você tem dados suficientes para otimizar

**Exemplo de saída:**
```
📊 ANÁLISE DE PERFORMANCE DO BOT
================================================

🎯 RESUMO GERAL:
   Total de trades: 48
   Total de ciclos: 12
   PnL total: +$287.50
   Trades ganhos: 28 (58.3%)
   Trades perdidos: 20 (41.7%)
   Profit Factor: 1.85

📈 PERFORMANCE POR SÍMBOLO:
BTC-USDT:
   Trades: 24
   PnL: +$152.30
   Win Rate: 62.5%

ETH-USDT:
   Trades: 24
   PnL: +$135.20
   Win Rate: 54.2%

💡 RECOMENDAÇÕES:
✅ Você tem dados suficientes para otimização!
   Execute: python3 backtest_optimizer.py
```

---

### 3️⃣ OTIMIZAR PARÂMETROS

```bash
python3 backtest_optimizer.py
```

**O que faz:**
- Pega seus trades reais
- Simula TODOS eles com diferentes SL/TP/Time
- Calcula qual combinação teria dado melhor resultado
- Rankeia as melhores opções

**Exemplo de saída:**
```
🔬 BACKTEST OPTIMIZER
================================================

📊 Testando 180 combinações...
   SL: [-50, -75, -100, -125, -150, -200]
   TP: [100, 150, 200, 250, 300, 400]
   Time: [30, 45, 60, 90, 120]
   Ciclos: 12

🏆 TOP 10 MELHORES COMBINAÇÕES
================================================

#1
   SL: $-75 | TP: $250 | Time: 45min
   💰 Total PnL: $+342.80
   📊 Avg PnL: $+28.57
   🎯 Win Rate: 66.7% (8W / 4L)
   📈 Profit Factor: 2.15
   ⏱️  Avg Duration: 38 min
   🎲 Exits: TP=6 | SL=3 | Time=3

#2
   SL: $-100 | TP: $200 | Time: 60min
   💰 Total PnL: $+287.50
   📊 Avg PnL: $+23.96
   🎯 Win Rate: 58.3% (7W / 5L)
   📈 Profit Factor: 1.85
   ⏱️  Avg Duration: 42 min
   🎲 Exits: TP=5 | SL=4 | Time=3

...

🎯 MELHOR COMBINAÇÃO RECOMENDADA:
================================================

Edite seu config.txt:
   STOP_LOSS_USD=-75
   TAKE_PROFIT_USD=250
   TIME_LIMIT_MINUTES=45

Resultado esperado:
   💰 Avg PnL por ciclo: $+28.57
   🎯 Win Rate: 66.7%
   📈 Profit Factor: 2.15
```

**Arquivo gerado:** `backtest_results.csv` (todas as combinações testadas)

---

### 4️⃣ APLICAR MELHORES PARÂMETROS

```bash
# Edite config.txt com os valores recomendados
nano config.txt

# Ou use o script que já criei:
# (substitua pelos valores recomendados)
STOP_LOSS_USD=-75
TAKE_PROFIT_USD=250
TIME_LIMIT_MINUTES=45

# Reinicie o bot
python3 main.py
```

---

### 5️⃣ REPETIR CICLO

Após 1-2 semanas com novos parâmetros:
1. Rode `analyze_performance.py` novamente
2. Compare com resultados anteriores
3. Rode `backtest_optimizer.py` com novos dados
4. Refine parâmetros

---

## 📊 COMO FUNCIONA A SIMULAÇÃO?

### Dados Reais (exemplo):

```
Ciclo 1: Abriu posições às 14:30
- BTC LONG: entrada $67,850
- BTC SHORT: entrada $67,850
- Duração real: 45 minutos
- Fechou por: TIME_LIMIT
- PnL real: +$22.50
```

### Simulação:

O otimizador pega esses trades e **"rejoga"** com diferentes parâmetros:

```python
# Original: SL=-100, TP=200, Time=60min
# → Fechou aos 60min com +$22.50

# Simulação 1: SL=-50, TP=200, Time=60min
# → Teria fechado aos 15min (SL) com -$50

# Simulação 2: SL=-100, TP=150, Time=60min
# → Teria fechado aos 25min (TP) com +$150

# Simulação 3: SL=-100, TP=200, Time=30min
# → Teria fechado aos 30min (Time) com +$18
```

Faz isso para **TODOS os ciclos** e **TODAS as combinações**.

Depois soma os resultados e rankeia!

---

## 🎯 QUANTOS DADOS PRECISO?

| Ciclos | Status | Confiabilidade |
|--------|--------|----------------|
| 1-5 | ⚠️ Poucos dados | Não otimize ainda |
| 5-10 | 🟡 Mínimo aceitável | Resultados iniciais |
| 10-20 | ✅ Bom | Confiável |
| 20-50 | ✅ Muito bom | Muito confiável |
| 50+ | ✅ Excelente | Extremamente confiável |

**Recomendação:** Pelo menos 10 ciclos antes de otimizar.

---

## 💡 DICAS IMPORTANTES

### ✅ Faça:

- **Colete dados suficientes** (10+ ciclos)
- **Compare períodos similares** (mesma volatilidade)
- **Teste um parâmetro por vez** inicialmente
- **Documente mudanças** (anote o que mudou e quando)
- **Dê tempo** para novos parâmetros funcionarem (1-2 semanas)
- **Considere fees** (incluídas no PnL)

### ❌ Não faça:

- **Otimizar com poucos dados** (< 10 ciclos)
- **Mudar parâmetros todo dia** (não dá tempo de avaliar)
- **Ignorar contexto de mercado** (alta volatilidade vs lateral)
- **Confiar cegamente** (backtest não garante futuro)
- **Overfitting** (parâmetros muito específicos)

---

## 📈 ANÁLISE AVANÇADA

### Ver resultados em Excel/Sheets:

```bash
# Após rodar backtest_optimizer.py
# Abra o arquivo CSV gerado:
backtest_results.csv

# Importar no Google Sheets ou Excel
# Criar gráficos, filtros, etc
```

### Queries SQL diretas:

```bash
sqlite3 trades.db

# Ver últimos 10 trades
SELECT symbol, side, realized_pnl, close_reason 
FROM trades 
WHERE status='CLOSED' 
ORDER BY entry_time DESC 
LIMIT 10;

# Ver performance por hora do dia
SELECT strftime('%H', entry_time) as hour, 
       COUNT(*) as trades,
       AVG(realized_pnl) as avg_pnl
FROM trades 
WHERE status='CLOSED'
GROUP BY hour
ORDER BY avg_pnl DESC;
```

---

## 🔬 EXEMPLO REAL COMPLETO

### Dia 1-3: Coleta (config inicial)
```
STOP_LOSS_USD=-100
TAKE_PROFIT_USD=200
TIME_LIMIT_MINUTES=60

Resultado: 12 ciclos, +$287.50, 58% win rate
```

### Dia 3: Análise
```bash
python3 analyze_performance.py
# → Vejo que tenho 12 ciclos, dados suficientes
```

### Dia 3: Otimização
```bash
python3 backtest_optimizer.py
# → Recomenda: SL=-75, TP=250, Time=45
# → Esperado: +$342.80 (19% melhor!)
```

### Dia 3-10: Teste (config otimizado)
```
STOP_LOSS_USD=-75
TAKE_PROFIT_USD=250
TIME_LIMIT_MINUTES=45

Resultado: 15 ciclos, +$421.30, 64% win rate ✅
```

### Dia 10: Repetir ciclo
```bash
# Agora com 27 ciclos totais, muito mais dados!
python3 backtest_optimizer.py
# → Refinar ainda mais...
```

---

## 🎯 RESUMO

| Ferramenta | Quando usar | O que faz |
|------------|-------------|-----------|
| `main.py` | Sempre | Roda o bot, coleta dados |
| `analyze_performance.py` | A cada 1-3 dias | Ver como está indo |
| `backtest_optimizer.py` | Após 10+ ciclos | Encontrar melhores parâmetros |

**Fluxo ideal:**
```
1. Rodar bot 3-5 dias → 10-20 ciclos
2. analyze_performance.py → Ver performance atual
3. backtest_optimizer.py → Encontrar melhores parâmetros
4. Editar config.txt → Aplicar otimizações
5. Rodar bot 1-2 semanas → Validar melhorias
6. Repetir
```

---

## 🚀 COMEÇAR AGORA

```bash
# 1. Rode o bot
python3 main.py

# 2. Espere coletar dados (10+ ciclos)

# 3. Depois, analise:
python3 analyze_performance.py

# 4. E otimize:
python3 backtest_optimizer.py

# 5. Aplique os melhores parâmetros no config.txt

# 6. Profit! 💰
```

---

**Boa sorte! 🍀 Qualquer dúvida, me chame!**
