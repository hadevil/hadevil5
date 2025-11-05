# 🤖 O QUE O BOT FAZ - SEQUÊNCIA COMPLETA

## 📋 RESUMO RÁPIDO

O bot faz isso em LOOP INFINITO:

```
1. ABRE posições LONG + SHORT
2. MONITORA PnL a cada 15 segundos
3. FECHA quando:
   - PnL ≥ Take Profit ($200) ✅
   - PnL ≤ Stop Loss (-$100) ❌
   - Tempo ≥ 60 minutos ⏰
4. REPETE (volta pro passo 1)
```

---

## 🎬 SEQUÊNCIA DETALHADA

### 🟢 FASE 1: INICIALIZAÇÃO

```
┌─────────────────────────────────────┐
│ python3 main.py                     │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 1. Carrega config.txt               │
│    - API keys                       │
│    - Símbolos (BTC-USDT, ETH-USDT)  │
│    - Tamanho posição ($100)         │
│    - SL (-$100) / TP ($200)         │
│    - Tempo limite (60 min)          │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 2. Conecta na API Apex              │
│    - Testa conexão                  │
│    - Verifica saldo                 │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 3. Mostra na tela:                  │
│    💰 Balance: $2,442.60            │
│    📊 Pares: BTC-USDT, ETH-USDT     │
│    🎯 SL: -$100 | TP: $200          │
│    ⏰ Time Limit: 60 minutes        │
└─────────────────────────────────────┘
         │
         ▼
    [INICIA CICLO]
```

---

### 🔵 FASE 2: ABERTURA DE POSIÇÕES

```
┌─────────────────────────────────────┐
│ CYCLE 1 START                       │
│ Vou abrir 4 posições:               │
│ - BTC-USDT LONG                     │
│ - BTC-USDT SHORT                    │
│ - ETH-USDT LONG                     │
│ - ETH-USDT SHORT                    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Para CADA símbolo:                  │
│                                     │
│ 1. Busca preço atual                │
│    GET ticker_v3(symbol)            │
│    → BTC: $67,850.00                │
│                                     │
│ 2. Calcula tamanho                  │
│    size = $100 / $67,850            │
│    → 0.00147 BTC                    │
│                                     │
│ 3. Cria ordem LONG                  │
│    POST create_order_v3(            │
│      symbol="BTC-USDT",             │
│      side="BUY",                    │
│      type="MARKET",                 │
│      size="0.00147"                 │
│    )                                │
│    → ✅ Order ID: abc123            │
│                                     │
│ 4. Cria ordem SHORT                 │
│    POST create_order_v3(            │
│      symbol="BTC-USDT",             │
│      side="SELL",                   │
│      type="MARKET",                 │
│      size="0.00147"                 │
│    )                                │
│    → ✅ Order ID: def456            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Repete para ETH-USDT                │
│ → ✅ ETH LONG aberta                │
│ → ✅ ETH SHORT aberta               │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ ⏳ Aguarda 5 segundos               │
│    (deixa ordens executarem)        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ ⚠️  VERIFICA se posições abriram:   │
│                                     │
│ GET account_info_v3()               │
│ → positions.filter(size > 0)        │
│                                     │
│ SE size = 0:                        │
│   ❌ ERRO: Ordens não executaram!   │
│   → Aguarda mais 10s                │
│   → Verifica novamente              │
│   → Se ainda size=0: ABORTA CICLO   │
│                                     │
│ SE size > 0:                        │
│   ✅ Posições abertas com sucesso!  │
│   → Continua                        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 📊 Mostra resumo:                   │
│                                     │
│ Positions opened:                   │
│ • BTC-USDT LONG: 0.00147 BTC        │
│ • BTC-USDT SHORT: 0.00147 BTC       │
│ • ETH-USDT LONG: 0.027 ETH          │
│ • ETH-USDT SHORT: 0.027 ETH         │
└─────────────────────────────────────┘
         │
         ▼
    [INICIA MONITORAMENTO]
```

---

### 🟡 FASE 3: MONITORAMENTO (LOOP A CADA 15 SEGUNDOS)

```
┌─────────────────────────────────────────────────────────┐
│ MONITORING LOOP                                         │
│ (roda a cada 15 segundos até fechar posições)           │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Busca posições atuais                                │
│    GET account_info_v3()                                │
│    → Lista todas posições com size > 0                  │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Para CADA posição:                                   │
│                                                         │
│    A. Busca preço atual                                 │
│       GET ticker_v3(symbol)                             │
│       → BTC: $67,920.00 (subiu $70)                     │
│                                                         │
│    B. Calcula PnL                                       │
│       Se LONG:                                          │
│         pnl = (preço_atual - preço_entrada) × size      │
│         pnl = ($67,920 - $67,850) × 0.00147             │
│         pnl = $70 × 0.00147                             │
│         pnl = +$0.10                                    │
│                                                         │
│       Se SHORT:                                         │
│         pnl = (preço_entrada - preço_atual) × size      │
│         pnl = ($67,850 - $67,920) × 0.00147             │
│         pnl = -$70 × 0.00147                            │
│         pnl = -$0.10                                    │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Soma PnL total de todas posições                     │
│                                                         │
│    BTC LONG:   +$0.10                                   │
│    BTC SHORT:  -$0.10                                   │
│    ETH LONG:   +$2.50                                   │
│    ETH SHORT:  -$2.30                                   │
│    ─────────────────                                    │
│    TOTAL PnL:  +$0.20                                   │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Calcula tempo decorrido                              │
│    start_time = 14:30:00                                │
│    current_time = 14:32:15                              │
│    elapsed = 2.25 minutos                               │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 5. VERIFICA CONDIÇÕES DE SAÍDA                          │
│                                                         │
│    ✅ TAKE PROFIT?                                      │
│       total_pnl >= $200                                 │
│       $0.20 >= $200 → NÃO                               │
│                                                         │
│    ❌ STOP LOSS?                                        │
│       total_pnl <= -$100                                │
│       $0.20 <= -$100 → NÃO                              │
│                                                         │
│    ⏰ TIME LIMIT?                                       │
│       elapsed >= 60 minutos                             │
│       2.25 >= 60 → NÃO                                  │
│                                                         │
│    → NENHUMA atingida, continua monitorando             │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Mostra no console (A CADA 5 MINUTOS):               │
│                                                         │
│    💰 PnL: $+0.20 | Time: 2/60min                      │
│    Target: TP=$+200 SL=$-100                           │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 7. ⏳ Aguarda 15 segundos                               │
└─────────────────────────────────────────────────────────┘
         │
         ▼
    [VOLTA PARA PASSO 1 - LOOP]


    ... 15 segundos depois ...
    ... 15 segundos depois ...
    ... 15 segundos depois ...


┌─────────────────────────────────────────────────────────┐
│ Após 62 minutos:                                        │
│                                                         │
│ ⏰ TIME LIMIT ATINGIDO!                                 │
│    elapsed = 62 minutos >= 60 minutos                   │
│    PnL atual: +$12.50                                   │
│                                                         │
│ → Vai para FASE 4 (Fechamento)                         │
└─────────────────────────────────────────────────────────┘
```

---

### 🔴 FASE 4: FECHAMENTO DE POSIÇÕES

```
┌─────────────────────────────────────┐
│ 🚨 EXIT CONDITION HIT!              │
│ Reason: TIME_LIMIT                  │
│ Final PnL: +$12.50                  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Para CADA posição aberta:           │
│                                     │
│ 1. BTC-USDT LONG (size: 0.00147)    │
│    POST create_order_v3(            │
│      symbol="BTC-USDT",             │
│      side="SELL",   ← VENDE (fecha) │
│      type="MARKET",                 │
│      size="0.00147"                 │
│    )                                │
│    → ✅ Closed                      │
│                                     │
│ 2. BTC-USDT SHORT (size: 0.00147)   │
│    POST create_order_v3(            │
│      symbol="BTC-USDT",             │
│      side="BUY",    ← COMPRA (fecha)│
│      type="MARKET",                 │
│      size="0.00147"                 │
│    )                                │
│    → ✅ Closed                      │
│                                     │
│ 3. ETH-USDT LONG → ✅ Closed        │
│ 4. ETH-USDT SHORT → ✅ Closed       │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 📊 Salva no database:               │
│                                     │
│ INSERT INTO cycles:                 │
│   start_time: 14:30:00              │
│   end_time: 15:32:00                │
│   reason: TIME_LIMIT                │
│   final_pnl: +$12.50                │
│   symbols: BTC-USDT,ETH-USDT        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 📢 Mostra no console:               │
│                                     │
│ ✅ CYCLE COMPLETED                  │
│ Reason: TIME_LIMIT                  │
│ Duration: 62 minutes                │
│ Final PnL: +$12.50                  │
│ Positions closed: 4                 │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ ⏳ Aguarda 10 segundos              │
│    (cooldown entre ciclos)          │
└─────────────────────────────────────┘
         │
         ▼
    [VOLTA PARA FASE 2 - NOVO CICLO]
```

---

## 🔄 EXEMPLO COMPLETO DE UM CICLO

### Cenário 1: Fechamento por TAKE PROFIT

```
14:30:00  CYCLE 1 START
14:30:05  ✅ 4 positions opened
14:30:05  💰 PnL: $+0.00 | Time: 0/60min

... monitorando a cada 15s ...

14:35:00  💰 PnL: $+45.20 | Time: 5/60min
14:40:00  💰 PnL: $+98.50 | Time: 10/60min
14:45:00  💰 PnL: $+152.30 | Time: 15/60min
14:47:15  💰 PnL: $+201.80 | Time: 17/60min

14:47:15  🎉 TAKE PROFIT HIT! ($201.80 >= $200)
14:47:16  🚨 Closing all positions...
14:47:20  ✅ All positions closed
14:47:20  💰 Final PnL: +$201.80
14:47:30  CYCLE 1 END (reason: TAKE_PROFIT)

14:47:40  CYCLE 2 START
          ... repete ...
```

### Cenário 2: Fechamento por STOP LOSS

```
15:10:00  CYCLE 2 START
15:10:05  ✅ 4 positions opened
15:10:05  💰 PnL: $+0.00 | Time: 0/60min

... mercado cai forte ...

15:15:00  💰 PnL: $-32.50 | Time: 5/60min
15:20:00  💰 PnL: $-67.80 | Time: 10/60min
15:23:45  💰 PnL: $-101.20 | Time: 13/60min

15:23:45  ❌ STOP LOSS HIT! ($-101.20 <= $-100)
15:23:46  🚨 Closing all positions...
15:23:50  ✅ All positions closed
15:23:50  💰 Final PnL: -$101.20
15:24:00  CYCLE 2 END (reason: STOP_LOSS)

15:24:10  CYCLE 3 START
          ... repete ...
```

### Cenário 3: Fechamento por TIME LIMIT

```
16:00:00  CYCLE 3 START
16:00:05  ✅ 4 positions opened
16:00:05  💰 PnL: $+0.00 | Time: 0/60min

... mercado lateral, PnL oscila ...

16:05:00  💰 PnL: $+5.20 | Time: 5/60min
16:10:00  💰 PnL: $+2.80 | Time: 10/60min
16:20:00  💰 PnL: $-8.50 | Time: 20/60min
16:30:00  💰 PnL: $+12.30 | Time: 30/60min
16:50:00  💰 PnL: $+18.70 | Time: 50/60min

17:00:15  💰 PnL: $+22.40 | Time: 60/60min

17:00:15  ⏰ TIME LIMIT HIT! (60 min >= 60 min)
17:00:16  🚨 Closing all positions...
17:00:20  ✅ All positions closed
17:00:20  💰 Final PnL: +$22.40
17:00:30  CYCLE 3 END (reason: TIME_LIMIT)

17:00:40  CYCLE 4 START
          ... repete ...
```

---

## 🚨 CENÁRIOS ESPECIAIS

### Ctrl+C (Primeira vez)

```
User press: Ctrl+C

🛑 Shutdown signal received
🚨 Closing all positions...
   → BTC LONG closed
   → BTC SHORT closed
   → ETH LONG closed
   → ETH SHORT closed
✅ All positions closed safely
👋 Bot stopped

Press Ctrl+C again to force quit
```

### Ctrl+C (Segunda vez)

```
User press: Ctrl+C (segunda vez)

⚠️  FORCE QUIT!
⚠️  Positions may still be open!
💀 Bot terminated immediately
```

### Posição Fechada Manualmente

```
14:45:00  💰 PnL: $+85.20 | Time: 15/60min
          Positions: 4

... usuário fecha 1 posição na plataforma ...

14:45:15  🔄 Checking positions...
14:45:15  🚨 POSITION MANUALLY CLOSED DETECTED!
14:45:15  Expected: 4 positions
14:45:15  Found: 3 positions
14:45:15  ❌ CRITICAL ERROR: Manual intervention!
14:45:15  💀 BOT CRASHING TO PREVENT INCONSISTENT STATE
14:45:15  👉 Please check the platform!

CRASH (exit code 1)
```

---

## 📊 RESUMO VISUAL

```
┌──────────────────────────────────────────────────────────┐
│                    FLUXO COMPLETO                        │
└──────────────────────────────────────────────────────────┘

INIT → OPEN → MONITOR → CLOSE → [REPEAT]
 ▼      ▼       ▼         ▼
 
 1️⃣     2️⃣      3️⃣        4️⃣
 
 Carrega  Abre    Monitora  Fecha
 config   4 pos   PnL 15s   todas
          
          LONG    TP ≥ $200  Salva
          SHORT   SL ≤ -$100 DB
                  T  ≥ 60min
```

---

## ⏱️ TIMINGS

| Ação | Tempo |
|------|-------|
| Abrir posições | ~5-10s |
| Verificar se abriu | 5s + retry 10s |
| Monitorar PnL | A cada 15s |
| Mostrar PnL console | A cada 5min |
| Fechar posições | ~5-10s |
| Cooldown entre ciclos | 10s |
| Timeout ordem | 30s max |

---

## 📁 O QUE É SALVO

### Database (`trading_bot.db`)

```sql
cycles:
  - id
  - start_time
  - end_time
  - reason (TP/SL/TIME)
  - final_pnl
  - symbols
  - duration

positions:
  - cycle_id
  - symbol
  - side
  - size
  - entry_price
  - exit_price
  - pnl
```

### Logs (`bot.log`)

```
Tudo que acontece com timestamp:
- Ordens criadas
- PnL calculado
- Condições verificadas
- Posições fechadas
- Erros
```

---

## 🎯 EM RESUMO

O bot é um **loop infinito** que:

1. **Abre** posições long + short
2. **Monitora** PnL a cada 15s
3. **Fecha** quando TP/SL/Tempo
4. **Repete** indefinidamente

**Objetivo:** Lucrar com volatilidade, usando hedge (LONG+SHORT).

**Controle:** Você pode parar com Ctrl+C a qualquer momento.
