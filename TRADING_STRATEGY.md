# 📊 Estratégia de Market Making - Detalhes Técnicos

## Visão Geral da Estratégia

Este bot implementa uma estratégia de **market making passivo** com recursos avançados otimizados para farming de airdrop da Paradex.

## Componentes Principais

### 1. Placement de Ordens Multi-Nível

```
Lado SELL:
  Nível 5: $101.50 | 0.08 SOL  (spread +1.5%)
  Nível 4: $101.25 | 0.09 SOL  (spread +1.25%)
  Nível 3: $101.00 | 0.10 SOL  (spread +1.0%)
  Nível 2: $100.75 | 0.11 SOL  (spread +0.75%)
  Nível 1: $100.50 | 0.12 SOL  (spread +0.5%)

MID PRICE: $100.00

Lado BUY:
  Nível 1: $99.50  | 0.12 SOL  (spread -0.5%)
  Nível 2: $99.25  | 0.11 SOL  (spread -0.75%)
  Nível 3: $99.00  | 0.10 SOL  (spread -1.0%)
  Nível 4: $98.75  | 0.09 SOL  (spread -1.25%)
  Nível 5: $98.50  | 0.08 SOL  (spread -1.5%)
```

**Vantagens:**
- Captura movimento em múltiplos níveis de preço
- Tamanho maior nos níveis mais próximos (maior probabilidade de fill)
- Profundidade no book aumenta score de market maker

### 2. Dynamic Spread Adjustment

O spread se ajusta automaticamente baseado na volatilidade do mercado:

```python
spread_final = base_spread * (1 + volatilidade * 10)
```

**Exemplo:**
- Volatilidade baixa (0.5%): spread = 0.15% * 1.05 = **0.16%**
- Volatilidade média (1.5%): spread = 0.15% * 1.15 = **0.17%**
- Volatilidade alta (3.0%): spread = 0.15% * 1.30 = **0.20%**

**Benefícios:**
- Proteção em mercados voláteis
- Mais competitivo em mercados calmos
- Reduz risco de adverse selection

### 3. Inventory Skewing

Sistema que ajusta preços baseado na posição atual:

```
Se LONG (comprado demais):
  - Aumenta preços de venda (mais agressivo para vender)
  - Aumenta preços de compra (menos agressivo para comprar)

Se SHORT (vendido demais):
  - Diminui preços de compra (mais agressivo para comprar)
  - Diminui preços de venda (menos agressivo para vender)
```

**Cálculo:**
```python
inventory_skew = current_position / max_position
skew_adjustment = inventory_skew * 0.02%  # max 0.02%

bid_price = mid_price * (1 - spread - skew_adjustment)
ask_price = mid_price * (1 + spread + skew_adjustment)
```

**Exemplo com posição +50% do máximo:**
- Skew = +0.5
- Adjustment = +0.01%
- Bids ficam 0.01% mais caros (compra menos)
- Asks ficam 0.01% mais baratos (vende mais)

### 4. Order Size Scaling

Tamanho das ordens diminui com a distância do mid price:

```python
for i in range(order_levels):
    size_multiplier = 1.0 - i * 0.1
    order_size = base_size * size_multiplier
```

**Exemplo com base_size = 0.10 SOL:**
- Nível 1: 0.10 SOL * 1.0 = **0.10 SOL**
- Nível 2: 0.10 SOL * 0.9 = **0.09 SOL**
- Nível 3: 0.10 SOL * 0.8 = **0.08 SOL**
- Nível 4: 0.10 SOL * 0.7 = **0.07 SOL**
- Nível 5: 0.10 SOL * 0.6 = **0.06 SOL**

**Razão:** Níveis distantes têm menor probabilidade de fill, então usamos menos capital.

### 5. Volatility Estimation

Calcula volatilidade usando desvio padrão dos retornos:

```python
returns = log(price[t] / price[t-1])
volatility = std(returns[-20:])  # últimos 20 períodos
```

**Window de 20 períodos** = ~10 minutos de histórico (refresh 30s)

### 6. Risk Management

#### A. Position Limits
```python
max_position = $2,500  # 50% do capital de $5k
current_position_usd = position_size * current_price

if abs(current_position_usd) > max_position * 0.8:
    # Reduzir exposição
    increase_inventory_skewing()
```

#### B. Daily Loss Limit
```python
max_daily_loss = $100  # 2% do capital

if daily_pnl < -max_daily_loss:
    cancel_all_orders()
    wait_until_next_day()
```

#### C. Emergency Stop
```python
if critical_error or api_down:
    cancel_all_orders()
    close_positions()
    shutdown()
```

## Ciclo de Execução

### Cada Iteração (30 segundos):

```
1. Fetch Market Data
   ├─ Ticker (last price, volume)
   ├─ Orderbook (bids/asks)
   └─ Account (position, balance)

2. Update State
   ├─ Calculate mid price
   ├─ Update volatility estimate
   └─ Update position tracking

3. Calculate Optimal Quotes
   ├─ Base spread from config
   ├─ Adjust for volatility
   ├─ Apply inventory skewing
   └─ Scale order sizes

4. Order Management
   ├─ Check if quotes changed significantly
   ├─ Cancel old orders if needed
   └─ Place new orders

5. Monitoring
   ├─ Log status
   ├─ Update statistics
   └─ Check risk limits
```

## Otimização para Airdrop

### 1. Maximizar Número de Ordens
- 5 níveis por lado = 10 ordens simultâneas
- Refresh a cada 30s = até 2,880 refreshes/dia
- Potencial: 28,800 ordens colocadas/dia

### 2. Maximizar Volume
Com ordem média de $100:
- 70% fill rate
- 28,800 ordens * 0.7 = 20,160 fills/dia
- Volume diário: **$2,016,000**

### 3. Manter Uptime
- Error handling robusto
- Auto-reconnection
- Graceful shutdown
- Log completo para debug

### 4. Competitividade
- Spread de 0.15% é competitivo
- Multi-level fornece liquidez em range
- Dynamic adjustment mantém relevância
- Fast refresh (30s) mantém quotes atuais

## Métricas de Performance

### Para Airdrop:
1. **Volume Traded**: Maior = melhor score
2. **Uptime**: 24/7 = maior score
3. **Spread Tightness**: Mais próximo do best bid/ask
4. **Order Depth**: Mais níveis = melhor
5. **Consistency**: Presença constante no book

### Para Lucratividade:
1. **Spread Captured**: Meta 50-70% do spread teórico
2. **Fill Rate**: 60-80% é bom
3. **Inventory Turnover**: Não acumular posição grande
4. **Sharpe Ratio**: Retorno ajustado por risco
5. **Max Drawdown**: Manter abaixo de 5% do capital

## Cenários e Respostas

### Cenário 1: Mercado Calmo
```
Volatilidade: 0.5%
Ação: Spread diminui para 0.16%
Resultado: Mais competitivo, mais fills
```

### Cenário 2: Mercado Volátil
```
Volatilidade: 5%
Ação: Spread aumenta para 0.65%
Resultado: Menos fills, mas protegido de adverse selection
```

### Cenário 3: Posição Long Grande
```
Position: +$2,000 (80% do máximo)
Ação: Skew asks down 0.015%, bids up 0.015%
Resultado: Vende mais fácil, compra menos
```

### Cenário 4: Movimento Forte Unidirecional
```
Situação: Mercado sobe 3% rápido
Ação: 
  - Ordens de compra antigas canceladas
  - Novas ordens colocadas 3% acima
  - Possível posição short formada (vendeu caro)
  - Inventory skew ajusta para reverter
```

### Cenário 5: API Error
```
Situação: Paradex API down
Ação:
  - Log error
  - Aguarda 60s
  - Retry connection
  - Se persistir após 5 tentativas, shutdown graceful
```

## Configuração por Perfil

### Conservative ($5k capital)
```json
{
  "base_spread": 0.002,      // Mais proteção
  "order_levels": 3,         // Menos exposição
  "order_size_usd": 125,     // Ordens maiores, menos níveis
  "max_position": 2000,      // Apenas 40% do capital
  "refresh": 60              // Menos frequente
}

Resultado esperado:
- Volume/dia: $50k-$80k
- PnL/dia: $100-$160
- Risco: Baixo
- Score airdrop: Médio
```

### Balanced ($5k capital)
```json
{
  "base_spread": 0.0015,     // Balanceado
  "order_levels": 5,         // Boa profundidade
  "order_size_usd": 100,     // Moderado
  "max_position": 2500,      // 50% do capital
  "refresh": 30              // Razoável
}

Resultado esperado:
- Volume/dia: $100k-$150k
- PnL/dia: $150-$225
- Risco: Médio
- Score airdrop: Alto
```

### Aggressive ($5k capital)
```json
{
  "base_spread": 0.001,      // Spreads tight
  "order_levels": 7,         // Muita profundidade
  "order_size_usd": 80,      // Ordens menores, mais níveis
  "max_position": 3000,      // 60% do capital
  "refresh": 20              // Muito frequente
}

Resultado esperado:
- Volume/dia: $150k-$250k
- PnL/dia: $150-$250 (mas mais variância)
- Risco: Alto
- Score airdrop: Muito Alto
```

## Tips Avançados

### 1. Otimizar Spread por Horário
```python
# Menor spread em horários líquidos (8am-12pm UTC)
# Maior spread em horários ilíquidos (12am-4am UTC)
```

### 2. Ajustar por Order Book Imbalance
```python
bid_depth = sum(orderbook['bids'][:10])
ask_depth = sum(orderbook['asks'][:10])

if bid_depth > ask_depth * 1.5:
    # Muita demanda, mercado pode subir
    # Aumentar asks, diminuir bids
```

### 3. Monitor Competitor Spreads
```python
best_bid = orderbook['bids'][0]['price']
best_ask = orderbook['asks'][0]['price']
market_spread = (best_ask - best_bid) / best_bid

# Ajustar para ser competitivo mas lucrativo
target_spread = market_spread * 1.1  # 10% wider que melhor spread
```

### 4. Tamanho Adaptativo
```python
# Aumentar tamanho quando volatilidade baixa (mais seguro)
# Diminuir tamanho quando volatilidade alta (mais risco)

adjusted_size = base_size * (1 - volatility * 5)
```

## Monitoramento

### Métricas Chave para Acompanhar:

1. **Fill Rate**: Deve estar entre 60-80%
   - Muito baixo: Spread muito largo
   - Muito alto: Spread muito estreito (risco)

2. **Position**: Deve oscilar em torno de zero
   - Sempre long: Muito spread nos asks
   - Sempre short: Muito spread nos bids

3. **PnL**: Deve crescer steady
   - Muita variância: Spread muito estreito
   - Crescimento lento: Spread muito largo

4. **Uptime**: Deve ser 99%+
   - Baixo uptime: Perda de score de airdrop

5. **Orders/Day**: Maximizar
   - Meta: 1,000-3,000 ordens/dia

## Conclusão

Esta estratégia balanceia:
- ✅ Lucratividade (spread captured)
- ✅ Farming de airdrop (volume + uptime)
- ✅ Gestão de risco (limits + skewing)
- ✅ Competitividade (dynamic adjustments)

Com $5k e configuração **Balanced**, expectativa realista:
- 📊 $100k-$150k volume/dia
- 💰 $150-$225 PnL/dia (3-4.5% ROI diário)
- 🎯 Top 20-30% dos market makers
- 🌾 Boa posição para airdrop

**Lembre-se:** Resultados variam com condições de mercado!
