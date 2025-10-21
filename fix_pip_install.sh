#!/bin/bash
# Script para corrigir instalação do pip no WSL

echo "🔧 Corrigindo instalação do Python e pip..."
echo ""

# 1. Atualizar repositórios
echo "📦 Atualizando repositórios apt..."
sudo apt update

# 2. Instalar Python e pip
echo "🐍 Instalando Python3 e pip..."
sudo apt install -y python3 python3-pip python3-venv

# 3. Verificar instalação
echo ""
echo "✅ Verificando instalação:"
python3 --version
pip3 --version

echo ""
echo "✅ Pronto! Agora você pode instalar o bot."
