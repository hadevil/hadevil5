#!/usr/bin/env python3
"""
Debug script específico para API Apex baseado no output do bot
"""

import requests
import json
import time
from datetime import datetime

def debug_apex_balance_detailed():
    """Debug detalhado do saldo da API Apex baseado no output do bot"""
    
    print("=" * 80)
    print("🔍 APEX API BALANCE DEBUG - DETALHADO")
    print("=" * 80)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Simulando a estrutura de dados que o bot recebeu
    print("📊 SIMULANDO RESPOSTA DA API APEX (baseado no output do bot):")
    print("-" * 60)
    
    # Dados simulados baseados no output que você mostrou
    mock_account_response = {
        'l2Key': '0xc9eca77aa9db233e56afb8fdcad4fe34e3aa932ca08bcd8eab913c3efafd5012',
        'ethereumAddress': '0x4fb0297ea31b84448a36ed8efc31ebbc0124dcb0',
        'id': '761373792180109360',
        'spotAccount': {
            'createdAt': 1759362457697,
            'status': 'NORMAL',
            'unrealizePnlPriceType': '',
            'ethAddress': '',
            'defaultSubAccountId': '0',
            'zkAccountId': '146416',
            'nonce': 1,
            'subAccounts': [{
                'subAccountId': '0',
                'l2Key': '0xc9eca77aa9db233e56afb8fdcad4fe34e3aa932ca08bcd8eab913c3efafd5012',
                'nonce': 10,
                'nonceVersion': 0,
                'changePubKeyStatus': 'FINISH'
            }],
            'updatedAt': 1760726220132
        },
        'spotWallets': [
            {
                'userId': '761373792180109360',
                'accountId': '761373792180109360',
                'subAccountId': '0',
                'tokenId': '140',
                'balance': '0.000000000000000000',
                'pendingDepositAmount': '0.000000000000000000',
                'pendingWithdrawAmount': '0.000000000000000000',
                'pendingTransferOutAmount': '0.000000000000000000',
                'pendingTransferInAmount': '0.000000000000000000',
                'createdAt': 1759946907159,
                'updatedAt': 1759947881100
            },
            {
                'userId': '2052075459193356288',
                'accountId': '761373792180109360',
                'subAccountId': '0',
                'tokenId': '141',
                'balance': '0.000745000000000001',
                'pendingDepositAmount': '0.000000000000000000',
                'pendingWithdrawAmount': '0.000000000000000000',
                'pendingTransferOutAmount': '0.000000000000000000',
                'pendingTransferInAmount': '0.000000000000000000',
                'createdAt': 1759362457988,
                'updatedAt': 1760726202700
            }
        ],
        'contractAccount': {
            'createdAt': 1759362469050,
            'takerFeeRate': '0.0005',
            'makerFeeRate': '0.0002',
            'minInitialMarginRate': '0',
            'status': 'NORMAL',
            'unrealizePnlPriceType': 'MARKET_PRICE',
            'vipTakerFeeRate': '0.00047500',
            'vipMakerFeeRate': '0.00019000'
        },
        'contractWallets': [
            {
                'userId': '2052075459193356288',
                'accountId': '761373792180109360',
                'balance': '2442.603212781542850814',
                'token': 'USDT',
                'pendingDepositAmount': '0.000000000000000000',
                'pendingWithdrawAmount': '0.000000000000000000',
                'pendingTransferOutAmount': '0.000000000000000000',
                'pendingTransferInAmount': '0.000000000000000000'
            },
            {
                'userId': '2052075459193356288',
                'accountId': '761373792180109360',
                'balance': '0.000000000000000000',
                'token': 'USDC',
                'pendingDepositAmount': '0.000000000000000000',
                'pendingWithdrawAmount': '0.000000000000000000',
                'pendingTransferOutAmount': '0',
                'pendingTransferInAmount': '0'
            }
        ],
        'omniSwapAccount': {
            'id': '',
            'l2Key': '',
            'status': '',
            'feeRate': ''
        },
        'omniSwapWallets': None,
        'positions': [
            {
                'token': '',
                'symbol': 'BTC-USDT',
                'status': '',
                'side': 'LONG',
                'size': '0.000',
                'entryPrice': '0.00',
                'exitPrice': '',
                'createdAt': 1759362930236,
                'updatedTime': 1760734126167,
                'fee': '0',
                'fundingFee': '0',
                'lightNumbers': '',
                'customInitialMarginRate': '0.01250'
            },
            {
                'token': '',
                'symbol': 'ETH-USDT',
                'status': '',
                'side': 'SHORT',
                'size': '0.00',
                'entryPrice': '0.00',
                'exitPrice': '',
                'createdAt': 1759949847992,
                'updatedTime': 1760734129612,
                'fee': '0',
                'fundingFee': '0',
                'lightNumbers': '',
                'customInitialMarginRate': '0'
            }
        ]
    }
    
    print("🔍 ANÁLISE DETALHADA DA RESPOSTA:")
    print()
    
    # Análise das carteiras de contrato (onde está o saldo real)
    print("💰 CONTRACT WALLETS (Saldo Principal):")
    print("-" * 40)
    for wallet in mock_account_response['contractWallets']:
        token = wallet['token']
        balance = float(wallet['balance'])
        print(f"   {token}: ${balance:,.2f}")
    
    print()
    
    # Análise das carteiras spot
    print("💳 SPOT WALLETS:")
    print("-" * 40)
    for wallet in mock_account_response['spotWallets']:
        token_id = wallet['tokenId']
        balance = float(wallet['balance'])
        print(f"   Token ID {token_id}: {balance}")
    
    print()
    
    # Análise das posições
    print("📈 POSIÇÕES ATIVAS:")
    print("-" * 40)
    active_positions = [pos for pos in mock_account_response['positions'] if float(pos['size']) > 0]
    if active_positions:
        for pos in active_positions:
            symbol = pos['symbol']
            side = pos['side']
            size = pos['size']
            entry_price = pos['entryPrice']
            print(f"   {symbol} {side}: {size} @ ${entry_price}")
    else:
        print("   Nenhuma posição ativa")
    
    print()
    
    # Cálculo do saldo total
    print("🧮 CÁLCULO DO SALDO TOTAL:")
    print("-" * 40)
    
    usdt_balance = 0.0
    usdc_balance = 0.0
    
    for wallet in mock_account_response['contractWallets']:
        if wallet['token'] == 'USDT':
            usdt_balance = float(wallet['balance'])
        elif wallet['token'] == 'USDC':
            usdc_balance = float(wallet['balance'])
    
    total_balance = usdt_balance + usdc_balance
    
    print(f"   USDT: ${usdt_balance:,.2f}")
    print(f"   USDC: ${usdc_balance:,.2f}")
    print(f"   TOTAL: ${total_balance:,.2f}")
    
    print()
    
    # Diagnóstico do problema
    print("🔍 DIAGNÓSTICO DO PROBLEMA:")
    print("-" * 40)
    print("❌ PROBLEMA IDENTIFICADO:")
    print("   O bot está retornando saldo $0.00, mas a API retorna $2,442.60")
    print()
    print("🔧 POSSÍVEIS CAUSAS:")
    print("   1. Parsing incorreto da resposta da API")
    print("   2. Busca no campo errado da resposta")
    print("   3. Conversão de string para float com erro")
    print("   4. Filtro aplicado incorretamente")
    print()
    print("💡 SOLUÇÃO SUGERIDA:")
    print("   O bot deve buscar em 'contractWallets' onde 'token' == 'USDT'")
    print(f"   Campo correto: contractWallets[0]['balance'] = '{usdt_balance}'")
    
    print()
    print("=" * 80)
    print("📋 RESUMO FINAL")
    print("=" * 80)
    print(f"✅ Saldo real na API: ${total_balance:,.2f}")
    print("❌ Saldo detectado pelo bot: $0.00")
    print("🔧 Ação necessária: Corrigir parsing da resposta da API")
    print("=" * 80)

if __name__ == "__main__":
    debug_apex_balance_detailed()