# 🔍 Investigação: PnL Zerado

## ❌ Problema Identificado

O PnL está sempre $0.00 porque **AS POSIÇÕES NÃO FORAM ABERTAS**.

### Evidência

Dos seus logs anteriores:
```
'symbol': 'BTC-USDT', 'side': 'LONG', 'size': '0.000', 'entryPrice': '0.00'
'symbol': 'ETH-USDT', 'side': 'SHORT', 'size': '0.00', 'entryPrice': '0.00'
```

**`size='0.000'` e `entryPrice='0.00'`** significa que as posições NÃO foram executadas!

---

## 🔍 Documentação da Apex Omni

Consultei https://api-docs.omni.apex.exchange/

### Endpoint: GET /v3/account

**Campos retornados nas positions:**
```json
{
  "positions": [
    {
      "symbol": "BTC-USDT",
      "status": "",
      "side": "LONG",
      "size": "0.000",
      "entryPrice": "0.00",
      "exitPrice": "",
      "createdAt": 1690366452416,
      "updatedTime": 1690366452416,
      "fee": "0.000000",
      "fundingFee": "0.000000",
      "lightNumbers": "",
      "customInitialMarginRate": "0"
    }
  ]
}
```

### ⚠️ Campos que NÃO EXISTEM:
- ❌ `unrealizedPnl`  
- ❌ `realizedPnl`  
- ❌ `markPrice`  

---

## ✅ Solução: Calcular PnL Manualmente

Como a API da Apex Omni NÃO retorna `unrealizedPnl`, preciso:

### 1. Obter preço atual via ticker
```python
ticker = self.public_client.ticker_v3(symbol=symbol)
current_price = float(ticker['data']['lastPrice'])
```

### 2. Calcular PnL
```python
if side == 'LONG':
    pnl = (current_price - entry_price) * size
else:  # SHORT
    pnl = (entry_price - current_price) * size
```

### 3. Multiplicar pelo valor USD
```python
pnl_usd = pnl * entry_price  # Aproximação
```

---

## 🚨 Por Que Suas Posições Não Foram Abertas?

Possíveis causas:

### 1. Ordens de Market Falharam
- O bot cria ordens MARKET com slippage protection
- Se o slippage for muito grande, a ordem pode não executar

### 2. Saldo Insuficiente (Mas isso já foi resolvido!)
- Você tinha $2,442.60 mas o bot mostrava $0.00
- Isso JÁ FOI CORRIGIDO com o update

### 3. Erro na Criação da Ordem
- A API pode ter rejeitado a ordem por algum motivo
- Preciso adicionar melhor logging

---

## 🔧 Correções Necessárias

### 1. ✅ Calcular PnL manualmente (SIM, é possível!)
- Buscar preço atual via `ticker_v3()`
- Calcular diferença vs entry_price
- Multiplicar pelo size

### 2. ✅ Melhorar logging de ordens
- Mostrar resposta completa da API
- Verificar se ordem foi FILLED ou REJECTED
- Adicionar retry com delay

### 3. ✅ Validar posições abertas
- Após criar ordem, verificar se size > 0
- Se size == 0, reportar erro e tentar novamente

---

## 📝 Próximos Passos

1. Implementar função `calculate_unrealized_pnl()` em apex_client.py
2. Adicionar melhor logging em `open_position()`
3. Verificar status da ordem após criação
4. Adicionar retry logic para ordens que falharem

---

## ⚠️ IMPORTANTE

**RODE O BOT NOVAMENTE DEPOIS DO UPDATE!**

Agora que o saldo está sendo detectado ($2,442.60), as ordens DEVEM ser criadas. 

Execute:
```bash
python3 main.py
```

E verifique se você vê:
```
✅ BTC-USDT LONG opened
✅ ETH-USDT SHORT opened
```

Se as posições foram abertas, o PnL vai ser calculado!
