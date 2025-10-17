#!/bin/bash

# Script para executar o Long&Short Bot
# Uso: ./run.sh [bot|dashboard|both]

MODE=${1:-both}

echo "Iniciando Long&Short Bot em modo: $MODE"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python3 não encontrado. Instalando..."
    apt-get update && apt-get install -y python3 python3-pip
fi

# Instalar dependências se necessário
if [ ! -f "venv/bin/activate" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "Arquivo .env não encontrado. Copiando exemplo..."
    cp .env.example .env
    echo "IMPORTANTE: Configure suas credenciais no arquivo .env antes de continuar!"
    echo "Edite o arquivo .env com suas chaves da exchange."
    exit 1
fi

# Executar o bot
echo "Executando Long&Short Bot..."
python main.py --mode $MODE