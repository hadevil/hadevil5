#!/bin/bash
# Script conveniente para rodar o bot com venv

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment não encontrado!"
    echo "Execute primeiro: bash setup_venv.sh"
    exit 1
fi

# Ativar venv e rodar bot
source venv/bin/activate
python3 main.py
