# 🚀 Quick Start Guide

## ⚡ Fast Setup (5 minutes)

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Edit Configuration

The `config.txt` file is already created with your credentials. Just edit the trading parameters:

```bash
nano config.txt
```

**Change these values:**
- `POSITION_SIZE_USD=1000` → Your position size in USD
- `STOP_LOSS_USD=-100` → Your stop loss (negative value)
- `TAKE_PROFIT_USD=200` → Your take profit (positive value)
- `TIME_LIMIT_MINUTES=60` → Max time per cycle
- `LONG_SYMBOLS=BTC,ETH` → Assets for long positions
- `SHORT_SYMBOLS=SOL` → Assets for short positions

### 3. Test Connection

```bash
python3 test_connection.py
```

This will verify:
- ✅ Your API credentials work
- ✅ Your trading symbols are valid
- ✅ You have sufficient balance
- ✅ Everything is configured correctly

### 4. Start Bot

```bash
python3 main.py
```

**Or run in background:**

```bash
nohup python3 main.py > bot_output.log 2>&1 &
```

### 5. Monitor

**Watch logs:**
```bash
tail -f logs/bot_*.log
```

**Stop bot:**
```bash
# If running in foreground: Ctrl+C
# If running in background:
ps aux | grep main.py
kill <PID>
```

---

## 📊 What the Bot Does

1. **Opens positions** (all at once):
   - BTC-USDT LONG
   - ETH-USDT LONG  
   - SOL-USDT SHORT

2. **Monitors continuously**:
   - Checks PnL every 30 seconds
   - Shows status every 5 minutes

3. **Closes all when**:
   - Total PnL hits stop loss (e.g., -$100)
   - Total PnL hits take profit (e.g., +$200)
   - Time limit reached (e.g., 60 minutes)

4. **Waits 8 minutes**

5. **Repeats forever** (or until you stop it)

---

## ⚙️ Configuration Examples

### Conservative (Low Risk)
```txt
POSITION_SIZE_USD=500
STOP_LOSS_USD=-50
TAKE_PROFIT_USD=100
TIME_LIMIT_MINUTES=120
LONG_SYMBOLS=BTC
SHORT_SYMBOLS=ETH
```

### Moderate (Medium Risk)
```txt
POSITION_SIZE_USD=1000
STOP_LOSS_USD=-100
TAKE_PROFIT_USD=200
TIME_LIMIT_MINUTES=60
LONG_SYMBOLS=BTC,ETH
SHORT_SYMBOLS=SOL
```

### Aggressive (High Risk)
```txt
POSITION_SIZE_USD=5000
STOP_LOSS_USD=-500
TAKE_PROFIT_USD=1000
TIME_LIMIT_MINUTES=30
LONG_SYMBOLS=BTC,ETH,AVAX
SHORT_SYMBOLS=SOL,MATIC,DOGE
```

---

## 🆘 Troubleshooting

### Bot won't start
```bash
# Check Python version (need 3.9+)
python3 --version

# Reinstall dependencies
pip3 install --upgrade -r requirements.txt

# Check config
python3 test_connection.py
```

### "Invalid symbols" error
```bash
# List available symbols
python3 -c "from apexomni.http_public import HttpPublic; from apexomni.constants import APEX_OMNI_HTTP_MAIN; c = HttpPublic(APEX_OMNI_HTTP_MAIN); configs = c.configs_v3(); print([s['symbol'] for s in configs['data']['contractConfig']['perpetualContract'][:20]])"
```

### Bot keeps failing to open positions
- Check your balance on Apex Omni
- Reduce `POSITION_SIZE_USD` 
- Verify leverage is set correctly on Apex

### Can't see logs
```bash
# Check if logs directory exists
ls -la logs/

# If not, create it
mkdir -p logs
```

---

## 📞 Need Help?

1. Check `logs/bot_*.log` for detailed errors
2. Run `python3 test_connection.py` to diagnose issues
3. Verify your API keys are correct in `config.txt`
4. Make sure you have sufficient balance on Apex Omni

---

## ⚠️ Important Notes

- **Start with small amounts** to test
- **Monitor the first few cycles** to ensure it works
- **Keep sufficient balance** on Apex Omni
- **Don't change leverage** on Apex dashboard while bot is running
- **Backup your config.txt** (contains your credentials)

---

**Ready to trade! 🚀**
