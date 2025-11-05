# 🔍 DEBUG: Por Que PnL Está $0.00?

## ✅ Você Confirmou: Posições ESTÃO ABERTAS

Você está vendo as posições na plataforma, então o problema **NÃO** é falha na abertura.

---

## 🎯 INVESTIGAÇÃO NECESSÁRIA

Execute este script de diagnóstico:

```bash
cd ~/apex-trading-bot
git pull origin cursor/bot-de-trading-autom-tico-para-perp-dex-c105
python3 test_pnl_calculation.py
```

### O Que Este Script Faz:

1. ✅ Busca todas as posições da sua conta
2. ✅ Mostra quais têm `size > 0` (abertas)
3. ✅ Para cada posição ativa:
   - Mostra symbol, side, size, entry_price
   - Busca preço atual do mercado
   - Calcula PnL manualmente
4. ✅ Testa a função `get_positions()` com cálculo automático

### Outputs Possíveis:

#### ✅ Caso 1: Posições Encontradas e PnL Calculado

```
🎯 Posições ATIVAS (size > 0): 2

🔍 Posição 1: BTC-USDT LONG
   Size: 0.015
   Entry Price: $67000.00
   Current Price: $67500.00
   Price Diff: $+500.00
   💰 PnL: $+7.50

💵 TOTAL PNL: $+7.50
```

**Se você vir isso:** O cálculo está funcionando! O bot vai mostrar o PnL.

#### ❌ Caso 2: Posições com Size = 0

```
🎯 Posições ATIVAS (size > 0): 0

⚠️  NENHUMA POSIÇÃO ATIVA ENCONTRADA!

📝 Mostrando primeiras 5 posições (incluindo zeradas):
   Posição 1:
      Symbol: BTC-USDT
      Side: LONG
      Size: 0.000
      Entry Price: 0.00
```

**Se você vir isso:** As posições **NÃO estão na API**, mesmo que você veja na plataforma!

---

## 🔧 Verificação da Lógica de TP/SL

### ✅ Stop Loss FUNCIONA Corretamente

```python
# Config: STOP_LOSS_USD=-100
if total_pnl <= -100:  # ✅ Correto
    return True, "STOP_LOSS"
```

**Exemplo:** Se PnL chegar em -$100.00 ou pior → Fecha tudo

### ✅ Take Profit FUNCIONA Corretamente

```python
# Config: TAKE_PROFIT_USD=200
if total_pnl >= 200:  # ✅ Correto
    return True, "TAKE_PROFIT"
```

**Exemplo:** Se PnL chegar em +$200.00 ou melhor → Fecha tudo

### ✅ Time Limit FUNCIONA Corretamente

```python
# Config: TIME_LIMIT_MINUTES=60
if elapsed >= 60:  # ✅ Correto
    return True, "TIME_LIMIT"
```

**Exemplo:** Após 60 minutos → Fecha tudo

---

## 🚨 POSSÍVEIS CAUSAS DO PNL $0.00

### 1. Delay na Sincronização da API

**Problema:** Você abriu as posições na plataforma, mas a API ainda não atualizou.

**Solução:** Aguarde 1-2 minutos e execute o script novamente.

### 2. Posições em Conta Diferente

**Problema:** As posições estão em uma sub-conta ou conta spot.

**Verificar:**
```bash
python3 debug_balance.py
```

Confirme que:
- `contractWallets` tem o saldo correto
- `positions` lista suas posições

### 3. Erro no Cálculo de PnL

**Problema:** Falha ao buscar ticker ou calcular.

**Verificar Logs:**
```bash
tail -50 logs/bot_$(date +%Y%m%d).log | grep -i "pnl\|calculate"
```

Procure por:
- ❌ "Failed to calculate PnL"
- ❌ "Failed to get ticker"

### 4. Posições Foram Fechadas e Reabertas

**Problema:** O bot fechou as posições antes de você verificar.

**Verificar:**
```bash
tail -100 logs/bot_$(date +%Y%m%d).log | grep -i "closed\|stop\|take profit"
```

---

## 🎯 PRÓXIMOS PASSOS

### 1️⃣ Execute o Script de Diagnóstico

```bash
cd ~/apex-trading-bot
git pull
python3 test_pnl_calculation.py
```

### 2️⃣ Me Mostre o Output Completo

Cole todo o output aqui para eu analisar.

### 3️⃣ Verifique os Logs do Bot

```bash
tail -100 logs/bot_$(date +%Y%m%d).log
```

---

## 📊 Dados Que Eu Preciso Ver

Para diagnosticar completamente, me mostre:

1. **Output de `test_pnl_calculation.py`**
2. **Output de `python3 debug_balance.py`** (seção de positions)
3. **Últimas 50 linhas do log:**
   ```bash
   tail -50 logs/bot_$(date +%Y%m%d).log
   ```

4. **Screenshot da plataforma mostrando:**
   - Posições abertas
   - Symbol, Side, Size, Entry Price
   - PnL atual (se mostrado)

---

## 🔍 O Que o Script Vai Revelar

| Cenário | Causa | Solução |
|---------|-------|---------|
| Posições encontradas, PnL calculado | Tudo OK! | Bot deve mostrar PnL agora |
| Posições com size=0 | API não atualizou | Aguarde ou reabra posições |
| Erro ao buscar ticker | Problema na API Apex | Retry ou aguarde |
| Erro ao calcular | Bug no código | Correção necessária |
| Nenhuma posição encontrada | Conta errada ou posições fechadas | Verificar conta/logs |

---

## ⚡ EXECUTE AGORA:

```bash
cd ~/apex-trading-bot && \
git pull origin cursor/bot-de-trading-autom-tico-para-perp-dex-c105 && \
python3 test_pnl_calculation.py
```

**Cole o output completo aqui!** 🔍
