#!/usr/bin/env python3
"""
Debug script to check balance API response
"""

import json
from dotenv import load_dotenv
import os

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

config = load_config()

# Import after loading config
from apexomni.http_private_sign import HttpPrivateSign

print("="*60)
print("🔍 DEBUGGING BALANCE API")
print("="*60)
print()

# Initialize client
client = HttpPrivateSign(
    api_key=config['API_KEY'],
    api_secret=config['API_SECRET'],
    passphrase=config['API_PASSPHRASE'],
    zk_seeds=config['ZK_SEEDS'],
    zk_l2key=config.get('ZK_L2KEY', '')
)

print("1️⃣  Testing get_account_v3()...")
try:
    account = client.get_account_v3()
    print(json.dumps(account, indent=2))
    print()
    
    if 'account' in account.get('data', {}):
        acc_data = account['data']['account']
        print(f"   Balance: {acc_data.get('equity', 'N/A')}")
        print(f"   Available: {acc_data.get('availableBalance', 'N/A')}")
        print(f"   Total Value: {acc_data.get('totalValue', 'N/A')}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("="*60)
print("2️⃣  Testing get_account_balance_v3()...")
try:
    balance_data = client.get_account_balance_v3()
    print(json.dumps(balance_data, indent=2))
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("="*60)
