#!/usr/bin/env python3
"""
Paradex Market Maker Bot - Otimizado para farming de airdrop com pouco capital
Funcionalidades:
- Trading automatizado com posições pequenas e frequentes
- Foco em SOL para maximizar volume
- Gerenciamento de risco conservador
- Compatível com Windows/PowerShell
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import questionary
import requests
from web3 import Web3


class ParadexMarketMaker:
    """Bot de Market Maker para Paradex otimizado para farming de airdrop"""

    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.web3 = Web3()
        self.is_running = False
        self.daily_volume = 0
        self.start_time = datetime.now()

        # Configurar logging
        self._setup_logging()

        # Dados da conta (deve ser configurado pelo usuário)
        self.account_address = None
        self.private_key = None
        self.api_credentials = {}

    def _load_config(self, config_path: str) -> Dict:
        """Carrega configuração do arquivo JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Arquivo de configuração não encontrado: {config_path}")
            return {}

    def _setup_logging(self):
        """Configura sistema de logging"""
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO').upper())

        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'logs/trading.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_account(self):
        """Configuração inicial da conta"""
        print("\n🔐 Configuração da Conta Paradex")
        print("=" * 50)

        self.account_address = input("Digite seu endereço da Paradex: ").strip()
        self.private_key = input("Digite sua chave privada: ").strip()

        # Validação básica
        if not self.web3.is_address(self.account_address):
            raise ValueError("❌ Endereço inválido!")

        if not self.private_key.startswith('0x'):
            self.private_key = '0x' + self.private_key

        self.logger.info(f"✅ Conta configurada: {self.account_address[:10]}...")

    def get_market_data(self, pair: str = "SOL-USD") -> Dict:
        """Obtém dados de mercado da Paradex"""
        # Nota: Em produção, isso seria uma chamada real para a API da Paradex
        # Por agora, retornamos dados simulados
        return {
            'symbol': pair,
            'price': 100.0 + random.uniform(-5, 5),  # Preço simulado
            'volume_24h': 50000 + random.randint(0, 10000),
            'spread': 0.1 + random.uniform(0, 0.2)
        }

    def calculate_order_size(self, pair: str, max_order_value: float) -> float:
        """Calcula tamanho da ordem baseado no capital disponível"""
        config = self.config['trading']
        order_value = random.uniform(
            config['order_value_usd']['min'],
            min(config['order_value_usd']['max'], max_order_value)
        )

        market_data = self.get_market_data(pair)
        current_price = market_data['price']

        # Calcula tamanho baseado no valor em USD
        size = order_value / current_price

        # Aplica ruído para parecer mais natural
        noise = 1 + random.uniform(-config['orders_distribution_noise'],
                                   config['orders_distribution_noise'])
        size *= noise

        return round(size, 6)  # Precisão típica para cripto

    def should_place_order(self) -> bool:
        """Determina se deve colocar uma ordem baseado em condições de mercado"""
        # Verifica volume diário
        if self.daily_volume >= self.config['risk_management']['max_daily_volume_usd']:
            self.logger.info(f"📊 Volume diário atingido: ${self.daily_volume}")
            return False

        # Verifica se já passou 24h (reset diário)
        if datetime.now() - self.start_time > timedelta(days=1):
            self.daily_volume = 0
            self.start_time = datetime.now()

        return True

    def place_market_making_orders(self, pair: str = "SOL-USD"):
        """Coloca ordens de market making (buy e sell próximas do preço atual)"""
        if not self.should_place_order():
            return

        market_data = self.get_market_data(pair)
        current_price = market_data['price']
        spread = market_data['spread']

        # Calcula preços das ordens
        buy_price = current_price * (1 - spread * 0.5)
        sell_price = current_price * (1 + spread * 0.5)

        # Calcula tamanhos das ordens
        max_order_value = self.get_available_balance() * self.config['trading']['max_leverage']
        buy_size = self.calculate_order_size(pair, max_order_value * 0.5)
        sell_size = self.calculate_order_size(pair, max_order_value * 0.5)

        self.logger.info(f"📈 Colocando ordens para {pair}:")
        self.logger.info(f"   🟢 BUY:  {buy_size} @ ${buy_price:.2".2f"
        self.logger.info(f"   🔴 SELL: {sell_size} @ ${sell_price:.2".2f"

        # Simula envio das ordens (em produção, seria chamada real para API)
        order_ids = {
            'buy': f"buy_{random.randint(1000, 9999)}",
            'sell': f"sell_{random.randint(1000, 9999)}"
        }

        # Atualiza volume diário
        order_value = (buy_size * buy_price) + (sell_size * sell_price)
        self.daily_volume += order_value

        self.logger.info(f"✅ Ordens colocadas. Volume parcial: ${order_value:.2".2f"
        return order_ids

    def get_available_balance(self) -> float:
        """Obtém saldo disponível (simulado)"""
        # Em produção, isso seria uma chamada real para a API da Paradex
        base_balance = 5000  # Simulado com base no capital do usuário

        # Calcula baseado no LTV máximo permitido
        max_leverage = self.config['trading']['max_leverage']
        return base_balance * max_leverage

    def monitor_positions(self):
        """Monitora posições abertas e gerencia riscos"""
        # Em produção, isso verificaria posições reais na exchange
        self.logger.info("🔍 Monitorando posições...")

        # Verifica LTV das posições
        current_ltv = random.uniform(60, 85)  # Simulado

        if current_ltv > self.config['trading']['max_position_ltv']:
            self.logger.warning(f"⚠️  LTV alto detectado: {current_ltv}%")
            self.logger.info("🔒 Fechando posições por segurança...")
            return False

        return True

    def run_trading_cycle(self):
        """Executa um ciclo completo de trading"""
        try:
            pairs = self.config['pairs']['primary_pairs']

            for pair in pairs:
                if not self.is_running:
                    break

                # Coloca ordens de market making
                order_ids = self.place_market_making_orders(pair)

                # Monitora posições por algum tempo
                monitoring_duration = random.randint(
                    self.config['trading']['order_duration_min']['min'],
                    self.config['trading']['order_duration_min']['max']
                )

                self.logger.info(f"⏱️  Monitorando por {monitoring_duration} minutos...")
                time.sleep(monitoring_duration * 60)

                # Cancela ordens (em produção seria chamada real)
                self.logger.info(f"🔄 Cancelando ordens: {order_ids}")

            # Delay entre ciclos
            delay = random.randint(
                self.config['trading']['delay_between_orders_min']['min'],
                self.config['trading']['delay_between_orders_min']['max']
            )

            self.logger.info(f"😴 Aguardando {delay} minutos para próximo ciclo...")
            time.sleep(delay * 60)

        except Exception as e:
            self.logger.error(f"❌ Erro no ciclo de trading: {e}")

    def start_trading(self):
        """Inicia o bot de trading"""
        print("\n🚀 Iniciando Paradex Market Maker Bot")
        print("=" * 50)

        self.is_running = True

        try:
            cycle_count = 0
            while self.is_running:
                cycle_count += 1
                self.logger.info(f"🔄 Iniciando ciclo #{cycle_count}")

                if not self.monitor_positions():
                    self.logger.warning("🛑 Parando devido a risco alto")
                    break

                self.run_trading_cycle()

                # Verifica se deve continuar
                if cycle_count % 10 == 0:
                    self.logger.info(f"📊 Status: {cycle_count} ciclos, Volume diário: ${self.daily_volume:.2".2f"

        except KeyboardInterrupt:
            self.logger.info("🛑 Interrompido pelo usuário")
        finally:
            self.is_running = False
            self.logger.info("✅ Bot parado")

    def stop_trading(self):
        """Para o bot de trading"""
        self.logger.info("🛑 Parando bot...")
        self.is_running = False

    def show_menu(self):
        """Exibe menu interativo"""
        while True:
            choice = questionary.select(
                "📋 Menu Principal - Paradex Market Maker",
                choices=[
                    "1. ⚙️  Configurar conta",
                    "2. 🚀 Iniciar trading",
                    "3. 📊 Ver status",
                    "4. ⚠️  Parar trading",
                    "5. ❌ Sair"
                ]
            ).ask()

            if choice.startswith("1"):
                try:
                    self.setup_account()
                except Exception as e:
                    print(f"❌ Erro na configuração: {e}")

            elif choice.startswith("2"):
                if not self.account_address or not self.private_key:
                    print("❌ Configure a conta primeiro!")
                    continue
                self.start_trading()

            elif choice.startswith("3"):
                print(f"\n📊 Status do Bot:")
                print(f"   Conta: {self.account_address[:10]}...{self.account_address[-6:]}")
                print(f"   Executando: {'Sim' if self.is_running else 'Não'}")
                print(f"   Volume diário: ${self.daily_volume:.".2f")
                print(f"   Ciclos executados: {len([x for x in dir(self) if x.startswith('cycle_')])}")

            elif choice.startswith("4"):
                self.stop_trading()

            elif choice.startswith("5"):
                self.stop_trading()
                print("👋 Até logo!")
                break


def main():
    """Função principal"""
    import os

    # Cria diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)

    # Inicia o bot
    bot = ParadexMarketMaker()
    bot.show_menu()


if __name__ == "__main__":
    main()