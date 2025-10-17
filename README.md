# Apex Omni Trading Bot

Automated long/short trading bot for Apex Omni perpetual DEX.

## 🌟 Features

- ✅ **Automated Trading**: Opens long and short positions simultaneously
- ✅ **Smart Exit**: Closes all positions when SL, TP, or time limit is reached
- ✅ **Auto Reentry**: Reopens positions after configurable delay
- ✅ **Risk Management**: Built-in stop loss and take profit
- ✅ **Recovery System**: Handles crashes and failed orders
- ✅ **24/7 Operation**: Runs continuously with monitoring
- ✅ **Real-time Notifications**: Status reports every 5 minutes

## 📋 Prerequisites

- Python 3.9 or higher
- Apex Omni account with API keys
- Linux/Ubuntu server (or local machine for testing)

## 🚀 Installation

### 1. Clone Repository

```bash
cd /workspace
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Configure Bot

Edit `config.txt` with your settings:

```txt
# API Credentials (from https://omni.apex.exchange/keyManagement)
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
API_PASSPHRASE=your_passphrase_here
ZK_SEEDS=0x...
ZK_L2KEY=

# Trading Parameters
POSITION_SIZE_USD=1000          # USD per position
STOP_LOSS_USD=-100              # Total loss to trigger close
TAKE_PROFIT_USD=200             # Total profit to trigger close
TIME_LIMIT_MINUTES=60           # Max time before close
LEVERAGE=20                     # Leverage (fixed at 20x)
REENTRY_DELAY_MINUTES=8         # Wait time before reopening

# Assets to Trade
LONG_SYMBOLS=BTC,ETH            # Comma-separated
SHORT_SYMBOLS=SOL               # Comma-separated
```

## 🎮 Usage

### Start Bot

```bash
python3 main.py
```

### Stop Bot

Press `Ctrl+C` to stop gracefully (will close open positions)

### Run in Background

```bash
nohup python3 main.py > bot_output.log 2>&1 &
```

### Check Logs

```bash
tail -f logs/bot_YYYYMMDD.log
```

## 📊 How It Works

### Trading Cycle

1. **Opening**: Bot opens all configured positions (long + short)
2. **Monitoring**: Checks PnL and time every 30 seconds
3. **Closing**: When SL/TP/Time is hit, closes ALL positions
4. **Waiting**: Waits 8 minutes (configurable)
5. **Repeat**: Opens new positions and starts over

### Exit Conditions

Bot closes ALL positions when:
- **Stop Loss**: Total PnL ≤ configured SL (e.g., -$100)
- **Take Profit**: Total PnL ≥ configured TP (e.g., +$200)
- **Time Limit**: Time elapsed ≥ configured limit (e.g., 60 min)

### PnL Calculation

- **Total PnL** = Sum of all position PnLs
- Example: BTC Long (+$50) + ETH Long (-$20) + SOL Short (+$80) = **+$110 total**

## ⚙️ Configuration Details

### Position Size

`POSITION_SIZE_USD=1000` means:
- Bot will use $1000 USD worth for each position
- With 20x leverage, you control $20,000 notional per position
- Size is automatically converted to contracts (e.g., 0.015 BTC)

### Stop Loss / Take Profit

Values are in **USD** and apply to **TOTAL** PnL:
- `STOP_LOSS_USD=-100`: Lose $100 total → close everything
- `TAKE_PROFIT_USD=200`: Gain $200 total → close everything

### Symbols

Format: Short name without suffix (bot adds `-USDT` automatically)

**Available symbols**: BTC, ETH, SOL, MATIC, DOGE, AVAX, LINK, UNI, AAVE, ADA, DOT, ATOM, LTC, XRP, TRX, FIL, NEAR, ALGO, SAND, MANA, etc.

## 🛡️ Safety Features

### Automatic Recovery

If bot crashes or connection lost:
- On restart, checks for open positions
- Closes all existing positions
- Starts fresh cycle

### Failed Order Handling

If any position fails to open:
- Closes all successfully opened positions
- Waits and retries in next cycle

If position fails to close:
- Opens opposite position (hedge)
- Keeps trying to close both

## 📝 Logs

Bot creates daily log files in `logs/` directory:
- `bot_YYYYMMDD.log`: Complete log with all operations
- Console output: Real-time status

## 🔒 Security

- **Never share** your API keys or ZK seeds
- **Don't commit** `config.txt` to git (already in .gitignore)
- **Use read/trade permissions only** (not withdraw)
- Consider **IP whitelisting** on Apex dashboard

## 📞 Support

For issues or questions:
- Check logs in `logs/` directory
- Review error messages in console
- Verify config.txt settings
- Ensure sufficient balance on Apex

## ⚠️ Disclaimer

This bot is for educational and personal use. Trading cryptocurrencies involves risk. Use at your own risk. Always test with small amounts first.

## 📄 License

MIT License - Use freely, modify as needed

---

**Made with ❤️ for Apex Omni traders**
