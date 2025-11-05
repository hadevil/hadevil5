#!/usr/bin/env python3
"""
Test script to verify Apex API connection and credentials
"""

import sys
from pathlib import Path

def test_connection():
    """Test API connection"""
    print("=" * 60)
    print("🧪 APEX OMNI API CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Test 1: Check config file
    print("1️⃣  Checking config.txt...")
    config_path = Path("config.txt")
    if not config_path.exists():
        print("   ❌ config.txt not found!")
        print("   💡 Copy config.example.txt to config.txt and fill in your credentials")
        return False
    print("   ✅ config.txt found")
    print()
    
    # Test 2: Import dependencies
    print("2️⃣  Checking dependencies...")
    try:
        from apexomni.http_public import HttpPublic
        from apexomni.http_private_sign import HttpPrivateSign
        from apexomni.constants import APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB
        print("   ✅ All dependencies installed")
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        print("   💡 Run: pip3 install -r requirements.txt")
        return False
    print()
    
    # Test 3: Load config
    print("3️⃣  Loading configuration...")
    try:
        from main import load_config
        config = load_config("config.txt")
        print("   ✅ Configuration loaded")
        print(f"   📊 Position Size: ${config['POSITION_SIZE_USD']}")
        print(f"   📈 Long: {config['LONG_SYMBOLS']}")
        print(f"   📉 Short: {config['SHORT_SYMBOLS']}")
    except Exception as e:
        print(f"   ❌ Error loading config: {e}")
        return False
    print()
    
    # Test 4: Test public API
    print("4️⃣  Testing public API (no auth)...")
    try:
        client = HttpPublic(APEX_OMNI_HTTP_MAIN)
        configs = client.configs_v3()
        symbols = configs['data']['contractConfig']['perpetualContract']
        print(f"   ✅ Public API working")
        print(f"   📊 Available symbols: {len(symbols)}")
    except Exception as e:
        print(f"   ❌ Public API failed: {e}")
        return False
    print()
    
    # Test 5: Test private API (with credentials)
    print("5️⃣  Testing private API (with your credentials)...")
    try:
        private_client = HttpPrivateSign(
            APEX_OMNI_HTTP_MAIN,
            network_id=NETWORKID_OMNI_MAIN_ARB,
            zk_seeds=config['ZK_SEEDS'],
            zk_l2Key=config.get('ZK_L2KEY', ''),
            api_key_credentials={
                'key': config['API_KEY'],
                'secret': config['API_SECRET'],
                'passphrase': config['API_PASSPHRASE']
            }
        )
        
        # Test account access
        account = private_client.get_account_v3()
        positions = account.get('positions', [])
        
        print("   ✅ Private API working")
        print(f"   👤 Account ID: {config.get('ACCOUNT_ID', 'N/A')}")
        print(f"   💼 Open positions: {len([p for p in positions if float(p.get('size', 0)) != 0])}")
        
        # Get balance
        balance_data = private_client.get_account_balance_v3()
        if balance_data and 'data' in balance_data:
            balances = balance_data['data'].get('balances', [])
            for bal in balances:
                if float(bal.get('availableBalance', 0)) > 0:
                    print(f"   💰 {bal['token']}: ${float(bal['availableBalance']):.2f} available")
        
    except Exception as e:
        print(f"   ❌ Private API failed: {e}")
        print("   💡 Check your API credentials in config.txt")
        return False
    print()
    
    # Test 6: Validate symbols
    print("6️⃣  Validating trading symbols...")
    try:
        from apex_client import ApexClient
        apex = ApexClient(config)
        
        all_symbols = []
        long_symbols = [s.strip() for s in config['LONG_SYMBOLS'].split(',') if s.strip()]
        short_symbols = [s.strip() for s in config['SHORT_SYMBOLS'].split(',') if s.strip()]
        
        for sym in long_symbols:
            full_sym = f"{sym}-USDT" if not sym.endswith('-USDT') else sym
            all_symbols.append(full_sym)
        
        for sym in short_symbols:
            full_sym = f"{sym}-USDT" if not sym.endswith('-USDT') else sym
            all_symbols.append(full_sym)
        
        invalid = []
        for sym in all_symbols:
            if not apex.validate_symbol(sym):
                invalid.append(sym)
        
        if invalid:
            print(f"   ❌ Invalid symbols: {invalid}")
            print(f"   💡 Available symbols: {', '.join(apex.get_available_symbols()[:20])}...")
            return False
        
        print("   ✅ All symbols valid")
        print(f"   📈 Long: {', '.join([s + '-USDT' if not s.endswith('-USDT') else s for s in long_symbols])}")
        print(f"   📉 Short: {', '.join([s + '-USDT' if not s.endswith('-USDT') else s for s in short_symbols])}")
        
    except Exception as e:
        print(f"   ❌ Symbol validation failed: {e}")
        return False
    print()
    
    # Success
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("🚀 You're ready to start the bot:")
    print("   python3 main.py")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
