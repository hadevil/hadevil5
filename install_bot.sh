#!/bin/bash
# Script de instalação automática do Apex Omni Trading Bot
# Execute com: bash install_bot.sh

set -e

echo "🚀 Instalando Apex Omni Trading Bot..."
echo ""

# 1. Clone o repositório
echo "📥 Clonando repositório..."
git clone https://github.com/hadevil/hadevil5.git apex-bot
cd apex-bot

# 2. Checkout do branch correto
echo "🔄 Mudando para o branch do bot..."
git checkout cursor/bot-de-trading-autom-tico-para-perp-dex-c105

# 3. Instalar Python e pip se necessário
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python3 não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# 4. Instalar dependências
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

# 5. Criar arquivo de configuração
echo "📝 Criando arquivo de configuração..."
cp config.example.txt config.txt

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. Edite o arquivo de configuração:"
echo "   nano config.txt"
echo ""
echo "2. Adicione suas credenciais da Apex Omni"
echo ""
echo "3. Teste a conexão:"
echo "   python3 test_connection.py"
echo ""
echo "4. Inicie o bot:"
echo "   python3 main.py"
echo ""
