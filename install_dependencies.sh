#!/bin/bash
# Instalação manual com versões compatíveis

echo "🚀 Instalando dependências do bot (versões compatíveis)..."
echo ""

# Instalar cada pacote individualmente
pip3 install --user apexomni
pip3 install --user requests
pip3 install --user python-dotenv
pip3 install --user 'web3>=6.0.0,<7.0.0'
pip3 install --user 'eth-account>=0.8.0'
pip3 install --user 'eth-utils>=2.1.0'
pip3 install --user 'eth-typing>=3.0.0'
pip3 install --user 'rlp>=3.0.0'
pip3 install --user 'websockets>=10.0,<14.0'
pip3 install --user hexbytes

echo ""
echo "✅ Dependências instaladas!"
echo ""
echo "Teste agora: python3 test_connection.py"
