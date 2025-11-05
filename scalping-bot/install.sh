#!/bin/bash
# Script de instalação para o Scalping Bot
# WSL/Ubuntu

set -e

echo "========================================="
echo "  Scalping Bot - Instalação"
echo "========================================="
echo ""

# Check Python version
echo "🔍 Verificando versão do Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale com:"
    echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Create virtual environment
echo ""
echo "📦 Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "ℹ️  Ambiente virtual já existe"
fi

# Activate venv
echo ""
echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Instalando dependências..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "  ✅ Instalação concluída!"
echo "========================================="
echo ""
echo "Para usar o bot:"
echo "  1. Ative o ambiente: source venv/bin/activate"
echo "  2. Configure: nano config.yaml"
echo "  3. Execute: python main.py --symbol BTCUSDT --strategy C2"
echo ""
echo "Para mais informações, leia o README.md"
echo ""
