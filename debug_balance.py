#!/usr/bin/env python3
"""
Debug script to check balance API response - NO CONFIG FILE NEEDED
Run this from the bot directory with your config.txt file
"""

import json
import sys
import os

print("="*80)
print("🔍 APEX OMNI - BALANCE DETECTION DEBUG TOOL")
print("="*80)
print()

# Check if config.txt exists
if not os.path.exists('config.txt'):
    print("❌ ERROR: config.txt not found!")
    print()
    print("   This script must be run from the bot directory where config.txt is located.")
    print("   Example: cd ~/apex-trading-bot && python3 debug_balance.py")
    print()
    sys.exit(1)

# Load config
def load_config():
    config = {}
    with open('config.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config

try:
    config = load_config()
    print("✅ Config loaded successfully")
    print()
except Exception as e:
    print(f"❌ Failed to load config: {e}")
    sys.exit(1)

# Import Apex SDK
try:
    from apexomni.http_private_sign import HttpPrivateSign
    from apexomni.constants import APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB
    print("✅ Apex SDK imported successfully")
    print()
except ImportError as e:
    print(f"❌ Failed to import Apex SDK: {e}")
    print()
    print("   Install it with: pip3 install apexpro")
    print()
    sys.exit(1)

# Initialize client
print("🔧 Initializing Apex client...")
try:
    client = HttpPrivateSign(
        APEX_OMNI_HTTP_MAIN,
        network_id=int(config.get('NETWORK_ID', NETWORKID_OMNI_MAIN_ARB)),
        zk_seeds=config['ZK_SEEDS'],
        zk_l2Key=config.get('ZK_L2KEY', ''),
        api_key_credentials={
            'key': config['API_KEY'],
            'secret': config['API_SECRET'],
            'passphrase': config['API_PASSPHRASE']
        }
    )
    print("✅ Client initialized")
    print()
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    sys.exit(1)

print("="*80)
print("📊 FETCHING ACCOUNT DATA...")
print("="*80)
print()

try:
    account = client.get_account_v3()
    
    # Save full response to file for inspection
    with open('debug_account_response.json', 'w') as f:
        json.dump(account, f, indent=2)
    print("💾 Full response saved to: debug_account_response.json")
    print()
    
    # Analyze structure
    print("🔍 RESPONSE STRUCTURE ANALYSIS:")
    print("-" * 80)
    print(f"   Top-level keys: {list(account.keys())}")
    print()
    
    # Check contractWallets (CORRECT LOCATION)
    if 'contractWallets' in account:
        print("✅ FOUND: contractWallets (perpetual trading balance)")
        print()
        for wallet in account['contractWallets']:
            token = wallet.get('token', 'UNKNOWN')
            balance = wallet.get('balance', '0')
            print(f"   💰 Token: {token}")
            print(f"      Balance: {balance}")
            print(f"      Balance (float): ${float(balance):.2f}")
            print(f"      Pending Deposit: {wallet.get('pendingDepositAmount', '0')}")
            print(f"      Pending Withdraw: {wallet.get('pendingWithdrawAmount', '0')}")
            print()
            
            if token == 'USDT':
                usdt_balance = float(balance)
                if usdt_balance > 0:
                    print(f"   ✅ SUCCESS! Your USDT balance is: ${usdt_balance:,.2f}")
                else:
                    print(f"   ⚠️  WARNING: USDT balance is $0.00")
                print()
    else:
        print("❌ contractWallets NOT FOUND in response")
        print()
    
    # Check data.account (OLD LOCATION - wrong for Apex Omni)
    if 'data' in account:
        print("📝 Found 'data' field (checking alternative structure):")
        if 'account' in account['data']:
            acc = account['data']['account']
            print(f"   Keys: {list(acc.keys())}")
            print(f"   Equity: {acc.get('equity', 'N/A')}")
            print(f"   Available: {acc.get('availableBalance', 'N/A')}")
            print(f"   Total Value: {acc.get('totalValue', 'N/A')}")
        else:
            print(f"   data keys: {list(account['data'].keys())}")
        print()
    
    # Check spotWallets
    if 'spotWallets' in account:
        print("📝 Found 'spotWallets' (spot trading balance):")
        for wallet in account['spotWallets']:
            token_id = wallet.get('tokenId', 'UNKNOWN')
            balance = wallet.get('balance', '0')
            if float(balance) > 0:
                print(f"   Token ID {token_id}: {balance}")
        print()
    
    print("="*80)
    print("💡 DIAGNOSIS:")
    print("="*80)
    print()
    
    if 'contractWallets' in account:
        usdt_wallets = [w for w in account['contractWallets'] if w.get('token') == 'USDT']
        if usdt_wallets:
            balance = float(usdt_wallets[0].get('balance', 0))
            if balance > 0:
                print(f"✅ YOUR BALANCE: ${balance:,.2f} USDT")
                print()
                print("   The bot code should read this from:")
                print("   → account['contractWallets'][i]['balance'] where token='USDT'")
                print()
                print("   ⚠️  If your bot is showing $0.00, you need to:")
                print("   1. Make sure you're using the LATEST code from git")
                print("   2. The fix is in commit: f08cb3d")
                print("   3. Run: git pull origin cursor/bot-de-trading-autom-tico-para-perp-dex-c105")
            else:
                print("⚠️  Your USDT balance is $0.00")
                print("   Please deposit funds to your Apex Omni account")
        else:
            print("❌ No USDT wallet found in contractWallets")
    else:
        print("❌ CRITICAL: contractWallets not found in API response")
        print("   This is unexpected. Please check:")
        print("   1. API credentials are correct")
        print("   2. Account is on the correct network (Arbitrum mainnet)")
        print("   3. Check debug_account_response.json for full structure")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    print()
    print(traceback.format_exc())

print()
print("="*80)
