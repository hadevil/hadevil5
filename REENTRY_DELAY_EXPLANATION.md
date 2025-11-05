# ⏰ Delay Entre Ciclos (Reentry Delay)

## ✅ JÁ ESTÁ IMPLEMENTADO!

O bot **JÁ FAZ ISSO AUTOMATICAMENTE**:

Após fechar posições (TP/SL/Time), o bot:
1. ✅ Aguarda 8 minutos
2. ✅ Reabre posições com os mesmos parâmetros
3. ✅ Repete indefinidamente

---

## 📋 CONFIGURAÇÃO ATUAL

### No arquivo `config.txt`:

```bash
# Delay em minutos antes de reabrir posições
REENTRY_DELAY_MINUTES=8
```

**Valor padrão:** 8 minutos  
**Você pode mudar:** Para qualquer valor (1, 5, 10, 15, etc)

---

## 🎬 SEQUÊNCIA COMPLETA (COM DELAY)

```
14:30:00  CYCLE 1 START
14:30:10  ✅ 4 positions opened

... monitorando ...

14:47:15  🎉 TAKE PROFIT! (+$201.80)
14:47:20  ✅ All positions closed
14:47:20  CYCLE 1 END

14:47:20  ⏰ Waiting 8 minutes before reopening...
14:49:20  ⏳ Reopening in 6 minutes...
14:51:20  ⏳ Reopening in 4 minutes...
14:53:20  ⏳ Reopening in 2 minutes...

14:55:20  CYCLE 2 START
14:55:30  ✅ 4 positions opened

... repete infinitamente ...
```

---

## 🔧 CÓDIGO IMPLEMENTADO

### Em `bot.py` (linhas 544-554):

```python
# Wait before reopening
reentry_delay = int(self.config['REENTRY_DELAY_MINUTES'])
print_waiting_reentry(reentry_delay)

# Sleep with countdown
for remaining in range(reentry_delay, 0, -1):
    if not self.is_running:
        break
    if remaining % 2 == 0:  # Log every 2 minutes
        logger.info(f"⏳ Reopening in {remaining} minutes...")
    time.sleep(60)
```

**O que faz:**
- Lê `REENTRY_DELAY_MINUTES` do config
- Aguarda esse tempo (padrão: 8 minutos)
- Mostra contagem regressiva a cada 2 minutos
- Respeita Ctrl+C durante a espera
- Após o delay, abre novo ciclo automaticamente

---

## ⚙️ COMO MUDAR O DELAY

### 1. Edite `config.txt`:

```bash
# Mudar de 8 para 10 minutos
REENTRY_DELAY_MINUTES=10

# Ou mudar para 5 minutos
REENTRY_DELAY_MINUTES=5

# Ou 1 minuto (reabrir quase imediatamente)
REENTRY_DELAY_MINUTES=1
```

### 2. Reinicie o bot:

```bash
# Pare o bot (Ctrl+C)
# Inicie novamente
python3 main.py
```

**Pronto!** O novo delay será aplicado.

---

## 💡 POR QUE 8 MINUTOS?

### Vantagens do delay:

✅ **Evita overtrading** - Não abre posições sem parar  
✅ **Respeita volatilidade** - Deixa mercado "se acalmar"  
✅ **Reduz fees** - Menos ordens = menos taxas  
✅ **Evita ban** - API não será sobrecarregada  
✅ **Cooldown mental** - Você pode acompanhar melhor  

### Quando mudar:

| Delay | Quando usar |
|-------|-------------|
| 1-2 min | Mercado muito volátil, quer aproveitar movimentos rápidos |
| 5 min | Padrão moderado |
| 8 min | **RECOMENDADO** - Bom equilíbrio |
| 10-15 min | Trading mais conservador |
| 20+ min | Swing trading, posições mais longas |

---

## 📊 EXEMPLO REAL DE UM DIA

```
09:00  CYCLE 1 START → TP em 18min → Fecha 09:18
09:26  CYCLE 2 START (8min delay)
10:15  CYCLE 2 TP → Fecha 10:15
10:23  CYCLE 3 START (8min delay)
11:40  CYCLE 3 TIME → Fecha 11:40
11:48  CYCLE 4 START (8min delay)
12:02  CYCLE 4 SL → Fecha 12:02
12:10  CYCLE 5 START (8min delay)
...
```

**Com 8 min de delay:**
- Ciclos mais espaçados
- ~6-8 ciclos por dia (depende duração)
- Menos estresse, melhor controle

**Sem delay (ou 1 min):**
- Ciclos back-to-back
- 10-15+ ciclos por dia
- Mais fees, mais risco

---

## 🚨 DELAY vs CTRL+C

### Durante o delay, você pode:

✅ **Ctrl+C (1ª vez):** Para o bot gracefully  
✅ **Ctrl+C (2ª vez):** Force quit  

**O bot NÃO vai abrir nova posição se você apertar Ctrl+C durante o delay!**

```
14:47:20  ⏰ Waiting 8 minutes...
14:49:20  ⏳ Reopening in 6 minutes...

[Você aperta Ctrl+C]

14:50:00  🛑 Shutdown signal received
14:50:00  ⏹️  Reentry cancelled
14:50:00  👋 Bot stopped

[Não abre nova posição]
```

---

## 🎯 RESUMO

| Pergunta | Resposta |
|----------|----------|
| O bot espera entre ciclos? | ✅ **SIM** |
| Quanto tempo? | **8 minutos** (padrão) |
| Onde configurar? | `config.txt` → `REENTRY_DELAY_MINUTES` |
| Posso mudar? | ✅ Sim, qualquer valor |
| Funciona com TP/SL/Time? | ✅ Todos os 3 |
| Mostra countdown? | ✅ A cada 2 minutos |
| Posso cancelar durante delay? | ✅ Ctrl+C funciona |

---

## ✅ CONCLUSÃO

**Você não precisa fazer NADA!**

O bot já:
- ✅ Aguarda 8 minutos após fechar posições
- ✅ Reabre automaticamente com mesmos parâmetros
- ✅ Repete indefinidamente
- ✅ Permite ajustar o delay no config

**Tá pronto! Só rodar!** 🚀
