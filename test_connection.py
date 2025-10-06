"""
Test Paradex API connection and configuration
Run this before starting the bot to verify everything is set up correctly
"""

import asyncio
import json
import sys
from paradex_market_maker import ParadexAPI


async def test_connection():
    """Test connection to Paradex API"""
    print("="*60)
    print("PARADEX CONNECTION TEST")
    print("="*60)
    print()
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✓ Config file loaded")
    except FileNotFoundError:
        print("✗ config.json not found!")
        return False
    except json.JSONDecodeError:
        print("✗ Invalid JSON in config.json!")
        return False
    
    # Check required fields
    required_fields = ['api_key', 'api_secret', 'market']
    missing_fields = [f for f in required_fields if f not in config or not config[f] or config[f].startswith('YOUR_')]
    
    if missing_fields:
        print(f"✗ Missing or invalid fields: {', '.join(missing_fields)}")
        print("  Please update config.json with your API credentials")
        return False
    
    print("✓ Required fields present")
    print()
    
    # Test API connection
    api = ParadexAPI(
        api_key=config['api_key'],
        api_secret=config['api_secret'],
        testnet=config.get('testnet', False)
    )
    
    environment = "TESTNET" if config.get('testnet', False) else "MAINNET"
    print(f"Environment: {environment}")
    print(f"Market: {config['market']}")
    print()
    
    async with api:
        # Test 1: Get ticker
        print("Test 1: Fetching market ticker...")
        try:
            ticker = await api.get_ticker(config['market'])
            print(f"✓ Ticker received")
            print(f"  Last Price: ${ticker.get('last_price', 'N/A')}")
            print(f"  24h Volume: ${ticker.get('volume_24h', 'N/A')}")
        except Exception as e:
            print(f"✗ Failed to get ticker: {e}")
            return False
        
        print()
        
        # Test 2: Get orderbook
        print("Test 2: Fetching orderbook...")
        try:
            orderbook = await api.get_orderbook(config['market'])
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            if bids and asks:
                print(f"✓ Orderbook received")
                print(f"  Best Bid: ${bids[0].get('price', 'N/A')}")
                print(f"  Best Ask: ${asks[0].get('price', 'N/A')}")
                
                best_bid = float(bids[0]['price'])
                best_ask = float(asks[0]['price'])
                spread = ((best_ask - best_bid) / best_bid) * 100
                print(f"  Spread: {spread:.4f}%")
            else:
                print("✗ Empty orderbook")
        except Exception as e:
            print(f"✗ Failed to get orderbook: {e}")
            return False
        
        print()
        
        # Test 3: Get account (requires authentication)
        print("Test 3: Fetching account info...")
        try:
            account = await api.get_account_summary()
            print(f"✓ Account connected")
            
            # Display balances
            balances = account.get('balances', [])
            if balances:
                print("  Balances:")
                for balance in balances:
                    currency = balance.get('currency', 'N/A')
                    available = balance.get('available', 'N/A')
                    print(f"    {currency}: {available}")
            
            # Display positions
            positions = account.get('positions', [])
            if positions:
                print("  Positions:")
                for position in positions:
                    market = position.get('market', 'N/A')
                    size = position.get('size', 'N/A')
                    print(f"    {market}: {size}")
            else:
                print("  No open positions")
                
        except Exception as e:
            print(f"✗ Failed to get account: {e}")
            print("  Check your API key and secret")
            return False
        
        print()
    
    print("="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)
    print()
    print("You can now start the bot:")
    print("  python paradex_market_maker.py")
    print()
    
    return True


async def validate_config():
    """Validate configuration parameters"""
    print("Configuration Validation")
    print("-"*60)
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except:
        return False
    
    # Check spread
    base_spread = config.get('base_spread', 0)
    if base_spread < 0.0005:
        print("⚠ Warning: base_spread < 0.05% - might lose money on fees")
    elif base_spread > 0.01:
        print("⚠ Warning: base_spread > 1% - might not compete well")
    else:
        print(f"✓ Spread: {base_spread*100:.3f}%")
    
    # Check order size
    order_size = config.get('order_size_usd', 0)
    if order_size < 10:
        print("⚠ Warning: order_size_usd < $10 - might be too small")
    elif order_size > 500:
        print("⚠ Warning: order_size_usd > $500 - high risk for $5k capital")
    else:
        print(f"✓ Order Size: ${order_size}")
    
    # Check max position
    max_position = config.get('max_position_usd', 0)
    capital = 5000  # Assumed
    if max_position > capital * 0.8:
        print(f"⚠ Warning: max_position_usd > 80% of capital - high risk")
    else:
        print(f"✓ Max Position: ${max_position}")
    
    # Check refresh interval
    refresh = config.get('refresh_interval', 0)
    if refresh < 10:
        print("⚠ Warning: refresh_interval < 10s - might hit rate limits")
    elif refresh > 120:
        print("⚠ Warning: refresh_interval > 2min - might miss opportunities")
    else:
        print(f"✓ Refresh Interval: {refresh}s")
    
    print("-"*60)
    print()
    
    return True


if __name__ == "__main__":
    print()
    result = asyncio.run(validate_config())
    result = asyncio.run(test_connection())
    
    sys.exit(0 if result else 1)
