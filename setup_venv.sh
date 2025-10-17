#!/bin/bash
# Script para criar ambiente virtual isolado para o bot

echo "========================================="
echo "🚀 SETUP APEX TRADING BOT"
echo "========================================="
echo ""

# Verificar se está no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ Erro: Execute este script de dentro do diretório apex-trading-bot"
    exit 1
fi

# Criar virtual environment
echo "📦 Criando virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Falha ao criar venv. Instalando python3-venv..."
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv venv
fi

# Ativar venv
echo "🔌 Ativando virtual environment..."
source venv/bin/activate

# Atualizar pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Verificar instalação
echo ""
echo "✅ Verificando instalação..."
python3 verify_implementation.py

echo ""
echo "========================================="
echo "✅ SETUP COMPLETO!"
echo "========================================="
echo ""
echo "Para usar o bot:"
echo ""
echo "  1. Ativar ambiente virtual:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Rodar o bot:"
echo "     python3 main.py"
echo ""
echo "  3. Desativar quando terminar:"
echo "     deactivate"
echo ""
echo "========================================="
