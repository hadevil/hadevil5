#!/usr/bin/env python3
"""
Check if you're running the latest code version
"""

import os
import sys

print("="*80)
print("🔍 VERIFICADOR DE VERSÃO DO CÓDIGO")
print("="*80)
print()

# Check if apex_client.py exists
if not os.path.exists('apex_client.py'):
    print("❌ ERRO: apex_client.py não encontrado!")
    print("   Você deve rodar este script do diretório ~/apex-trading-bot")
    sys.exit(1)

print("✅ Encontrado: apex_client.py")
print()

# Read the file
with open('apex_client.py', 'r') as f:
    content = f.read()

print("🔍 Verificando versão do código...")
print("-"*80)
print()

# Check for OLD code (should NOT exist)
old_markers = [
    ("Unexpected account response structure", "❌ CÓDIGO ANTIGO DETECTADO!"),
    ("logger.warning(f\"⚠️  Unexpected account", "❌ CÓDIGO ANTIGO DETECTADO!"),
]

# Check for NEW code (should exist)
new_markers = [
    ("# PATH 1: Check contractWallets (CORRECT for Apex Omni", "✅ CÓDIGO ATUALIZADO"),
    ("logger.debug(f\"✅ Found contractWallets with", "✅ CÓDIGO ATUALIZADO"),
    ("logger.info(f\"💰 Balance from contractWallets:", "✅ CÓDIGO ATUALIZADO"),
]

has_old_code = False
has_new_code = False

print("📝 Checando por código ANTIGO (não deveria existir):")
for marker, message in old_markers:
    if marker in content:
        print(f"   {message}")
        print(f"   Encontrado: '{marker[:50]}...'")
        has_old_code = True
print()

if not has_old_code:
    print("   ✅ Nenhum código antigo encontrado!")
print()

print("📝 Checando por código NOVO (deveria existir):")
for marker, message in new_markers:
    if marker in content:
        print(f"   {message}")
        has_new_code = True
print()

if not has_new_code:
    print("   ❌ Código atualizado NÃO encontrado!")
print()

print("="*80)
print("📊 DIAGNÓSTICO:")
print("="*80)
print()

if has_old_code and not has_new_code:
    print("❌ VOCÊ ESTÁ USANDO CÓDIGO ANTIGO!")
    print()
    print("   O seu código está DESATUALIZADO e não vai detectar o saldo corretamente.")
    print()
    print("   🔧 SOLUÇÃO:")
    print("   1. cd ~/apex-trading-bot")
    print("   2. git fetch origin")
    print("   3. git pull origin cursor/bot-de-trading-autom-tico-para-perp-dex-c105")
    print("   4. python3 check_code_version.py  # Verificar novamente")
    print()
    print("   Se o git pull não funcionar:")
    print("   git reset --hard origin/cursor/bot-de-trading-autom-tico-para-perp-dex-c105")
    print()
elif not has_old_code and has_new_code:
    print("✅ VOCÊ ESTÁ USANDO A VERSÃO MAIS RECENTE!")
    print()
    print("   O código está correto e deveria detectar o saldo de $2,442.60")
    print()
    print("   Se o bot ainda mostrar $0.00, execute:")
    print("   python3 debug_balance.py")
    print()
    print("   Isso vai mostrar exatamente onde está o problema.")
elif has_old_code and has_new_code:
    print("⚠️  CÓDIGO MESCLADO (VELHO + NOVO)")
    print()
    print("   Parece que você tem uma mistura de código antigo e novo.")
    print("   Isso pode acontecer se você fez modificações manuais.")
    print()
    print("   🔧 SOLUÇÃO:")
    print("   git reset --hard origin/cursor/bot-de-trading-autom-tico-para-perp-dex-c105")
else:
    print("❓ CÓDIGO NÃO RECONHECIDO")
    print()
    print("   Não foi possível identificar a versão do código.")
    print("   Faça o pull da última versão:")
    print()
    print("   git pull origin cursor/bot-de-trading-autom-tico-para-perp-dex-c105")

print("="*80)
print()

# Show git status
print("🔍 Status do Git:")
print("-"*80)
os.system("git log --oneline -1")
print()
os.system("git status | head -10")
print("="*80)
