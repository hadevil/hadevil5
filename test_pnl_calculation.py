#!/usr/bin/env python3
"""
Test PnL calculation with real position data
"""

import json
import sys
from apex_client import ApexClient

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

print("="*80)
print("🔍 TESTE DE CÁLCULO DE PNL")
print("="*80)
print()

try:
    config = load_config()
    print("✅ Config carregado")
    
    # Initialize Apex client
    apex = ApexClient(config)
    print("✅ Apex client inicializado")
    print()
    
    # Get account with positions
    print("📊 Buscando posições da conta...")
    account = apex.get_account()
    
    all_positions = account.get('positions', [])
    print(f"   Total de posições no account: {len(all_positions)}")
    print()
    
    # Filter active positions
    active = [p for p in all_positions if p.get('size') and float(p['size']) != 0]
    print(f"🎯 Posições ATIVAS (size > 0): {len(active)}")
    print()
    
    if not active:
        print("⚠️  NENHUMA POSIÇÃO ATIVA ENCONTRADA!")
        print()
        print("   Possíveis causas:")
        print("   1. As ordens ainda não foram executadas (filled)")
        print("   2. As posições foram fechadas")
        print("   3. Problema na abertura das ordens")
        print()
        print("📝 Mostrando primeiras 5 posições (incluindo zeradas):")
        for i, pos in enumerate(all_positions[:5]):
            print(f"\n   Posição {i+1}:")
            print(f"      Symbol: {pos.get('symbol')}")
            print(f"      Side: {pos.get('side')}")
            print(f"      Size: {pos.get('size')}")
            print(f"      Entry Price: {pos.get('entryPrice')}")
        sys.exit(0)
    
    print("="*80)
    print("📊 DETALHES DAS POSIÇÕES ATIVAS:")
    print("="*80)
    
    total_pnl = 0.0
    
    for i, pos in enumerate(active, 1):
        symbol = pos['symbol']
        side = pos['side']
        size = pos.get('size', '0')
        entry_price = pos.get('entryPrice', '0')
        
        print(f"\n🔍 Posição {i}: {symbol} {side}")
        print(f"   Size: {size}")
        print(f"   Entry Price: ${entry_price}")
        
        try:
            # Get current price
            ticker = apex.public_client.ticker_v3(symbol=symbol)
            ticker_data = ticker['data']
            if isinstance(ticker_data, list):
                ticker_data = ticker_data[0]
            current_price = float(ticker_data['lastPrice'])
            
            print(f"   Current Price: ${current_price:.2f}")
            
            # Calculate PnL
            size_float = float(size)
            entry_float = float(entry_price)
            
            if side == 'LONG':
                price_diff = current_price - entry_float
            else:  # SHORT
                price_diff = entry_float - current_price
            
            pnl = price_diff * size_float
            total_pnl += pnl
            
            print(f"   Price Diff: ${price_diff:+.2f}")
            print(f"   💰 PnL: ${pnl:+.2f}")
            
        except Exception as e:
            print(f"   ❌ Erro ao calcular PnL: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
    
    print()
    print("="*80)
    print(f"💵 TOTAL PNL: ${total_pnl:+.2f}")
    print("="*80)
    print()
    
    # Now test get_positions() with PnL calculation
    print("🧪 Testando get_positions() com cálculo automático...")
    positions_with_pnl = apex.get_positions()
    
    if positions_with_pnl:
        print(f"✅ Retornou {len(positions_with_pnl)} posições")
        
        for pos in positions_with_pnl:
            print(f"\n   {pos['symbol']} {pos['side']}:")
            print(f"      unrealizedPnl: ${pos.get('unrealizedPnl', 0):+.2f}")
            print(f"      markPrice: ${pos.get('markPrice', 0):.2f}")
    else:
        print("❌ get_positions() retornou lista vazia!")
    
    print()
    print("="*80)
    
except FileNotFoundError:
    print("❌ config.txt não encontrado!")
    print("   Execute este script do diretório ~/apex-trading-bot")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    print()
    print(traceback.format_exc())
