# 🚀 Início Rápido - Scalping Bot

## ⚡ Instalação em 3 Passos

### 1️⃣ Instalar dependências

```bash
cd ~/scalping-bot
chmod +x install.sh
./install.sh
```

Ou manualmente:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Configurar credenciais

Edite `config.yaml`:

```bash
nano config.yaml
```

Adicione suas credenciais ApeX Omni na seção `apex:`:

```yaml
apex:
  api_key: "SUA_API_KEY_AQUI"
  api_secret: "SEU_SECRET_AQUI"
  api_passphrase: "SUA_PASSPHRASE_AQUI"
  zk_seeds: "SEUS_ZK_SEEDS_AQUI"
```

> ⚠️ **NUNCA** commite esse arquivo com credenciais!

### 3️⃣ Rodar o bot

**Paper Trading (simulado, sem risco):**

```bash
python main.py --symbol BTCUSDT --strategy C2 --mode paper --data_source csv
```

**Live Trading (CUIDADO - usa dinheiro real!):**

```bash
python main.py --symbol BTCUSDT --strategy C2 --mode live --data_source live --order_value_usd 500
```

---

## 📊 Testar Setup

```bash
python test_setup.py
```

Se tudo passar ✅, está pronto para usar!

---

## 🎮 Exemplos de Uso

### C1 - Breakout Falso (BTC, 15m)
```bash
python main.py \
  --symbol BTCUSDT \
  --strategy C1 \
  --timeframe 15m \
  --order_value_usd 1000 \
  --mode paper
```

### C2 - Candle de Expansão (ETH, 1h)
```bash
python main.py \
  --symbol ETHUSDT \
  --strategy C2 \
  --timeframe 1h \
  --order_value_usd 1500 \
  --mode paper
```

### C4 - Pullback (SOL, apenas long)
```bash
python main.py \
  --symbol SOLUSDT \
  --strategy C4 \
  --use_long true \
  --use_short false \
  --mode paper
```

### Override TP/SL
```bash
python main.py \
  --symbol BTCUSDT \
  --strategy C2 \
  --tp_atr 2.0 \
  --sl_atr 0.5
```

---

## 📁 Onde Encontrar os Logs

- **Trades**: `./logs/trades.csv`
- **Estado**: `./state/position_state.json`
- **Console**: Veja em tempo real no terminal

---

## ❓ Troubleshooting

### "No CSV file found"
Coloque arquivos CSV em `./data/`:
- Formato: `BTCUSDT_15m.csv`
- Colunas: `timestamp,open,high,low,close,volume`

### "Insufficient data"
Aguarde mais candles ou use limite menor (`--limit 100`)

### "apex_client required"
Configure credenciais em `config.yaml` seção `apex:`

### Bot não abre posição
- Verifique filtros da estratégia (`rsi_min`, `rsi_max`, etc)
- Aumente faixa de RSI ou desabilite filtros

---

## 📚 Documentação Completa

- **README.md**: Guia completo de instalação e uso
- **STRATEGIES.md**: Detalhes das 3 estratégias (C1, C2, C4)
- **config.yaml**: Todos os parâmetros comentados

---

## 🆘 Precisa de Ajuda?

1. Leia `README.md` - tem tudo explicado
2. Veja `STRATEGIES.md` - entenda cada estratégia
3. Rode `python test_setup.py` - verifica se está tudo OK

---

**Bons trades! 📈🚀**
