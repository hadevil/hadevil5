#!/bin/bash
# Script para corrigir pip e instalar dependências

set -e

echo "🔧 Corrigindo pip e instalando dependências..."
echo ""

# 1. Atualizar pip
echo "📦 Atualizando pip para versão mais recente..."
python3 -m pip install --upgrade pip setuptools wheel

# 2. Instalar dependências com versões compatíveis
echo ""
echo "📥 Instalando dependências do bot..."

# Tentar com requirements.txt original
if pip3 install -r requirements.txt 2>/dev/null; then
    echo "✅ Instalação bem-sucedida com requirements.txt"
else
    echo "⚠️  Tentando com versões compatíveis..."
    
    # Usar versões mais antigas compatíveis
    pip3 install apexomni requests python-dotenv
    pip3 install 'web3>=6.0.0,<7.0.0'
    pip3 install 'eth-account>=0.8.0,<0.12.0'
    pip3 install 'eth-utils>=2.1.0,<3.0.0'
    pip3 install 'eth-typing>=3.0.0,<4.0.0'
    pip3 install 'rlp>=3.0.0,<4.0.0'
    pip3 install 'websockets>=10.0,<14.0'
    pip3 install hexbytes
fi

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "   1. cp config.example.txt config.txt"
echo "   2. nano config.txt (configure suas credenciais)"
echo "   3. python3 test_connection.py"
echo ""
