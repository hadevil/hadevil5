#!/usr/bin/env python3
"""
Debug script para verificar o saldo da API da Apex
"""

import requests
import json
import time
from datetime import datetime

def debug_apex_balance():
    """Debug do saldo da API Apex"""
    
    print("=" * 80)
    print("🔍 APEX API BALANCE DEBUG")
    print("=" * 80)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configurações da API (você precisará ajustar estas)
    base_url = "https://pro.apex.exchange"
    
    # Headers necessários (você precisará adicionar suas credenciais)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ApexTradingBot/1.0"
    }
    
    print("📡 Testando conectividade com a API Apex...")
    
    try:
        # Teste de conectividade básica
        response = requests.get(f"{base_url}/v1/public/time", timeout=10)
        print(f"✅ Conectividade OK - Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                time_data = response.json()
                print(f"🕐 Server Time: {time_data}")
            except:
                print(f"🕐 Server Time (raw): {response.text}")
        
    except Exception as e:
        print(f"❌ Erro de conectividade: {e}")
        return
    
    print()
    print("🔑 Testando endpoints de conta...")
    
    # Lista de endpoints para testar
    endpoints = [
        "/v1/account",
        "/v1/account/balance", 
        "/v1/account/positions",
        "/v1/account/wallets"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n📊 Testando: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sucesso - Dados recebidos")
                
                # Análise específica do endpoint
                if "balance" in endpoint:
                    print("   💰 Análise de saldo:")
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if "balance" in key.lower() or "wallet" in key.lower():
                                print(f"      {key}: {value}")
                
                elif "account" in endpoint and "balance" not in endpoint:
                    print("   👤 Análise de conta:")
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if "id" in key.lower() or "address" in key.lower():
                                print(f"      {key}: {value}")
                
                elif "positions" in endpoint:
                    print("   📈 Análise de posições:")
                    if isinstance(data, list):
                        print(f"      Total de posições: {len(data)}")
                        for i, pos in enumerate(data[:3]):  # Mostra apenas as primeiras 3
                            print(f"      Posição {i+1}: {pos}")
                    elif isinstance(data, dict) and "positions" in data:
                        positions = data["positions"]
                        print(f"      Total de posições: {len(positions)}")
                        for i, pos in enumerate(positions[:3]):
                            print(f"      Posição {i+1}: {pos}")
                
                elif "wallets" in endpoint:
                    print("   💳 Análise de carteiras:")
                    if isinstance(data, list):
                        print(f"      Total de carteiras: {len(data)}")
                        for i, wallet in enumerate(data[:3]):
                            print(f"      Carteira {i+1}: {wallet}")
                    elif isinstance(data, dict) and "wallets" in data:
                        wallets = data["wallets"]
                        print(f"      Total de carteiras: {len(wallets)}")
                        for i, wallet in enumerate(wallets[:3]):
                            print(f"      Carteira {i+1}: {wallet}")
                
            elif response.status_code == 401:
                print("   🔒 Erro de autenticação - Verifique suas credenciais")
            elif response.status_code == 403:
                print("   🚫 Acesso negado - Verifique permissões")
            elif response.status_code == 404:
                print("   ❌ Endpoint não encontrado")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Erro: {error_data}")
                except:
                    print(f"   Resposta: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")
    
    print()
    print("=" * 80)
    print("📋 RESUMO DO DEBUG")
    print("=" * 80)
    print("1. ✅ Conectividade com API Apex funcionando")
    print("2. 🔑 Teste de endpoints de conta realizado")
    print("3. 💰 Verifique os dados de saldo acima")
    print("4. 🔧 Se necessário, ajuste as credenciais no código")
    print("=" * 80)

if __name__ == "__main__":
    debug_apex_balance()