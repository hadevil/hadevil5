#!/usr/bin/env python3
"""
Paradex Market Maker Bot - Otimizado para farming de airdrop com pouco capital
Funcionalidades:
- Trading automatizado com posições pequenas e frequentes
- Foco em SOL para maximizar volume
- Gerenciamento de risco conservador
- Compatível com Windows/PowerShell
- Sistema avançado de monitoramento e métricas
"""

import asyncio
import json
import logging
import os
import random
import sys
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
import questionary
import requests
from web3 import Web3


class ParadexMarketMaker:
    """Bot de Market Maker para Paradex otimizado para farming de airdrop"""

    def __init__(self, config_path: str = "config_windows.json"):
        self.config_path = config_path
        self.config = self._load_config(config_path)

        # Inicializar componentes
        self.session = requests.Session()
        self.web3 = Web3()

        # Estado do bot
        self.is_running = False
        self.start_time = datetime.now()
        self.daily_volume = 0.0
        self.total_volume = 0.0
        self.total_trades = 0
        self.successful_trades = 0
        self.cycle_count = 0

        # Dados da conta
        self.account_address = None
        self.private_key = None
        self.api_credentials = {}

        # Métricas de performance
        self.performance_metrics = {
            'daily_pnl': 0.0,
            'total_pnl': 0.0,
            'best_day': 0.0,
            'worst_day': 0.0,
            'win_rate': 0.0
        }

        # Configurar logging
        self._setup_logging()

        # Validar configuração mínima
        self._validate_config()

    def _load_config(self, config_path: str) -> Dict:
        """Carrega configuração do arquivo JSON com validações"""
        try:
            if not os.path.exists(config_path):
                # Tentar carregar config padrão se a específica não existir
                default_configs = ['config_windows.json', 'config.json']
                for default_config in default_configs:
                    if os.path.exists(default_config):
                        config_path = default_config
                        break

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Validar estrutura mínima da configuração
            required_sections = ['trading', 'risk_management', 'pairs']
            for section in required_sections:
                if section not in config:
                    self.logger.warning(f"Seção '{section}' não encontrada na configuração")

            return config

        except FileNotFoundError:
            self.logger.error(f"❌ Arquivo de configuração não encontrado: {config_path}")
            print(f"❌ Arquivo de configuração não encontrado: {config_path}")
            print("💡 Use 'python main.py --setup' para criar configuração inicial")
            sys.exit(1)
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Erro no formato JSON da configuração: {e}")
            print(f"❌ Erro no formato JSON da configuração: {e}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar configuração: {e}")
            return {}

    def _validate_config(self):
        """Valida configuração mínima necessária"""
        config = self.config

        # Verificar seções críticas
        if 'trading' not in config:
            raise ValueError("❌ Seção 'trading' não encontrada na configuração")

        if 'risk_management' not in config:
            raise ValueError("❌ Seção 'risk_management' não encontrada na configuração")

        # Validar parâmetros críticos
        trading_config = config['trading']
        required_params = ['order_value_usd', 'max_leverage', 'max_position_ltv']

        for param in required_params:
            if param not in trading_config:
                self.logger.warning(f"⚠️  Parâmetro '{param}' não encontrado em trading config")

        # Log de configuração carregada
        self.logger.info("✅ Configuração carregada com sucesso")
        self.logger.info(f"   📊 Configuração: {self.config_path}")
        self.logger.info(f"   💰 Capital base: $5,000")
        self.logger.info(f"   🎯 Par primário: {config.get('pairs', {}).get('primary_pairs', ['SOL-USD'])}")

    def _setup_logging(self):
        """Configura sistema de logging avançado"""
        try:
            log_config = self.config.get('logging', {})
            level = getattr(logging, log_config.get('level', 'INFO').upper())

            # Criar diretório de logs se não existir
            log_dir = os.path.dirname(log_config.get('file', 'logs/trading.log'))
            os.makedirs(log_dir, exist_ok=True)

            # Configurar formatação avançada
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

            # Configurar handlers
            handlers = []

            # File handler com rotação
            log_file = log_config.get('file', 'logs/trading.log')
            if log_file:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setFormatter(logging.Formatter(log_format))
                handlers.append(file_handler)

            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            handlers.append(console_handler)

            # Configurar logging
            logging.basicConfig(
                level=level,
                format=log_format,
                handlers=handlers,
                force=True  # Sobrescrever configurações anteriores
            )

            self.logger = logging.getLogger(__name__)
            self.logger.info("✅ Sistema de logging configurado")

        except Exception as e:
            print(f"❌ Erro ao configurar logging: {e}")
            # Fallback para logging básico
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)

    def setup_account(self):
        """Configuração inicial da conta com validações avançadas"""
        print("\n🔐 Configuração da Conta Paradex")
        print("=" * 50)

        # Verificar se configuração já existe
        if self.account_address and self.private_key:
            use_existing = questionary.confirm(
                "Conta já configurada. Deseja usar a configuração existente?"
            ).ask()

            if use_existing:
                self.logger.info("✅ Usando configuração existente")
                return

        try:
            # Coletar dados da conta
            print("\n📝 Dados da Conta:")
            print("-" * 30)

            self.account_address = input("🔗 Endereço da carteira: ").strip()
            self.private_key = input("🔑 Chave privada: ").strip()

            # Coletar credenciais API (se necessário)
            use_api = questionary.confirm(
                "Usar credenciais API? (recomendado para produção)"
            ).ask()

            if use_api:
                self.api_credentials['api_key'] = input("🔑 API Key: ").strip()
                self.api_credentials['api_secret'] = input("🔐 API Secret: ").strip()

            # Validações avançadas
            self._validate_account_credentials()

            # Teste de conectividade básico
            self._test_connectivity()

            # Salvar configuração se necessário
            self._save_config_if_needed()

            self.logger.info("✅ Conta configurada e validada com sucesso"            self._display_account_summary()

        except ValueError as e:
            self.logger.error(f"❌ Erro de validação: {e}")
            print(f"\n❌ {e}")
            print("💡 Verifique os dados e tente novamente")
            return
        except Exception as e:
            self.logger.error(f"❌ Erro inesperado na configuração: {e}")
            print(f"\n❌ Erro inesperado: {e}")
            return

    def _validate_account_credentials(self):
        """Valida credenciais da conta"""
        # Validar endereço
        if not self.account_address:
            raise ValueError("Endereço da carteira é obrigatório")

        if not self.web3.is_address(self.account_address):
            raise ValueError("Formato de endereço inválido")

        # Validar chave privada
        if not self.private_key:
            raise ValueError("Chave privada é obrigatória")

        # Normalizar chave privada
        if not self.private_key.startswith('0x'):
            self.private_key = '0x' + self.private_key

        # Validar formato da chave privada
        if len(self.private_key) != 66:  # 0x + 64 caracteres hex
            raise ValueError("Chave privada deve ter 64 caracteres hexadecimais")

        # Validar caracteres hexadecimais
        try:
            int(self.private_key, 16)
        except ValueError:
            raise ValueError("Chave privada deve conter apenas caracteres hexadecimais")

        # Validar credenciais API se fornecidas
        if self.api_credentials.get('api_key') and self.api_credentials.get('api_secret'):
            if len(self.api_credentials['api_key']) < 10:
                raise ValueError("API Key parece muito curta")
            if len(self.api_credentials['api_secret']) < 10:
                raise ValueError("API Secret parece muito curto")

    def _test_connectivity(self):
        """Testa conectividade básica"""
        try:
            # Teste básico de rede
            response = self.session.get(
                'https://api.github.com',
                timeout=5,
                headers={'User-Agent': 'ParadexBot/1.0'}
            )

            if response.status_code == 200:
                self.logger.info("✅ Conectividade básica OK")
            else:
                self.logger.warning(f"⚠️  Problemas de conectividade: HTTP {response.status_code}")

        except Exception as e:
            self.logger.warning(f"⚠️  Não foi possível testar conectividade: {e}")

    def _save_config_if_needed(self):
        """Salva configuração se usuário desejar"""
        save_config = questionary.confirm(
            "Salvar configuração para uso futuro?"
        ).ask()

        if save_config:
            try:
                # Backup da configuração atual
                if os.path.exists(self.config_path):
                    backup_path = f"{self.config_path}.backup"
                    os.rename(self.config_path, backup_path)
                    self.logger.info(f"✅ Backup criado: {backup_path}")

                # Atualizar configuração
                self.config['account'] = {
                    'address': self.account_address,
                    'private_key': self.private_key,
                    'api_credentials': self.api_credentials
                }

                # Salvar
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)

                self.logger.info(f"✅ Configuração salva: {self.config_path}")

            except Exception as e:
                self.logger.error(f"❌ Erro ao salvar configuração: {e}")

    def _display_account_summary(self):
        """Exibe resumo da conta configurada"""
        print("\n📊 Resumo da Conta Configurada:")
        print("-" * 40)
        print(f"🔗 Endereço: {self.account_address[:10]}...{self.account_address[-6:]}")
        print(f"🔑 Chave privada: {self.private_key[:10]}...{self.private_key[-6:]}")

        if self.api_credentials:
            print(f"🔑 API Key: {self.api_credentials['api_key'][:10]}...")
            print(f"🔐 API Secret: {'*' * len(self.api_credentials['api_secret'])}")

        print(f"💰 Capital configurado: $5,000")
        print(f"🎯 Estratégia: Market Making para farming de airdrop")

    def get_market_data(self, pair: str = "SOL-USD") -> Dict:
        """Obtém dados de mercado da Paradex com simulação melhorada"""
        try:
            # Em produção, isso seria uma chamada real para a API da Paradex
            # Exemplo de chamada real:
            # response = self.session.get(f"https://api.paradex.trade/api/v1/ticker/{pair}")
            # data = response.json()

            # Simulação mais realista baseada em dados históricos
            base_prices = {
                'SOL-USD': 95.0,
                'ETH-USD': 2500.0,
                'BTC-USD': 45000.0
            }

            base_price = base_prices.get(pair, 100.0)

            # Simular volatilidade realista
            volatility_multiplier = random.uniform(0.95, 1.05)
            current_price = base_price * volatility_multiplier

            # Spread baseado na volatilidade e volume
            base_spread = 0.001  # 0.1%
            spread_multiplier = random.uniform(0.8, 1.5)
            spread = base_spread * spread_multiplier

            # Volume 24h simulado
            base_volume = 100000  # Volume base
            volume_24h = base_volume * random.uniform(0.8, 1.3)

            market_data = {
                'symbol': pair,
                'price': round(current_price, 2),
                'volume_24h': round(volume_24h),
                'spread': round(spread, 4),
                'timestamp': datetime.now().isoformat()
            }

            self.logger.debug(f"📊 Dados de mercado para {pair}: ${current_price:.2f}")
            return market_data

        except Exception as e:
            self.logger.error(f"❌ Erro ao obter dados de mercado: {e}")
            # Retornar dados de fallback
            return {
                'symbol': pair,
                'price': 100.0,
                'volume_24h': 50000,
                'spread': 0.001,
                'timestamp': datetime.now().isoformat()
            }

    def calculate_order_size(self, pair: str, max_order_value: float) -> float:
        """Calcula tamanho da ordem baseado no capital disponível e estratégia"""
        config = self.config['trading']

        # Base order value
        min_value = config['order_value_usd']['min']
        max_value = min(config['order_value_usd']['max'], max_order_value)
        order_value = random.uniform(min_value, max_value)

        market_data = self.get_market_data(pair)
        current_price = market_data['price']

        # Calcula tamanho baseado no valor em USD
        base_size = order_value / current_price

        # Aplica ruído estratégico para parecer mais natural
        noise_factor = config.get('orders_distribution_noise', 0.1)
        noise = 1 + random.uniform(-noise_factor, noise_factor)
        size = base_size * noise

        # Ajusta baseado na volatilidade (ordens menores em mercados voláteis)
        volatility_adjustment = self._calculate_volatility_adjustment(market_data)
        size *= volatility_adjustment

        # Garante tamanho mínimo para evitar rejeições
        min_size = 0.001  # Tamanho mínimo para a maioria das exchanges
        size = max(size, min_size)

        return round(size, 6)  # Precisão típica para cripto

    def _calculate_volatility_adjustment(self, market_data: Dict) -> float:
        """Calcula ajuste baseado na volatilidade do mercado"""
        # Simulação simples: ajustar baseado no spread
        spread = market_data.get('spread', 0.001)

        # Em mercados muito voláteis (spread alto), usar ordens menores
        if spread > 0.01:  # Spread > 1%
            return 0.7  # Reduzir 30%
        elif spread > 0.005:  # Spread > 0.5%
            return 0.85  # Reduzir 15%
        else:
            return 1.0  # Manter tamanho normal

    def should_place_order(self) -> bool:
        """Determina se deve colocar uma ordem baseado em múltiplas condições"""
        try:
            # Verifica volume diário
            max_daily_volume = self.config['risk_management']['max_daily_volume_usd']
            if self.daily_volume >= max_daily_volume:
                self.logger.info(f"📊 Volume diário atingido: ${self.daily_volume:.2f} > ${max_daily_volume:.2f}")
                return False

            # Verifica se já passou 24h (reset diário)
            if datetime.now() - self.start_time > timedelta(days=1):
                self._reset_daily_metrics()

            # Verifica condições de mercado
            if not self._check_market_conditions():
                return False

            # Verifica limites de risco
            if not self._check_risk_limits():
                return False

            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar condições de ordem: {e}")
            return False

    def _reset_daily_metrics(self):
        """Reseta métricas diárias"""
        yesterday_volume = self.daily_volume
        yesterday_pnl = self.performance_metrics['daily_pnl']

        # Atualizar métricas históricas
        if yesterday_volume > 0:
            if yesterday_pnl > self.performance_metrics['best_day']:
                self.performance_metrics['best_day'] = yesterday_pnl
            if yesterday_pnl < self.performance_metrics['worst_day']:
                self.performance_metrics['worst_day'] = yesterday_pnl

        # Reset diário
        self.daily_volume = 0.0
        self.performance_metrics['daily_pnl'] = 0.0
        self.start_time = datetime.now()

        self.logger.info(f"🔄 Métricas diárias resetadas. Ontem: ${yesterday_volume:.2f} PnL")

    def _check_market_conditions(self) -> bool:
        """Verifica condições de mercado"""
        try:
            # Verificar se há liquidez suficiente
            for pair in self.config['pairs']['primary_pairs']:
                market_data = self.get_market_data(pair)
                min_volume = self.config['pairs'].get('min_volume_usd', 10000)

                if market_data['volume_24h'] < min_volume:
                    self.logger.debug(f"📊 Volume insuficiente para {pair}: {market_data['volume_24h']} < {min_volume}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar condições de mercado: {e}")
            return False

    def _check_risk_limits(self) -> bool:
        """Verifica limites de risco"""
        try:
            # Verificar perda máxima diária
            max_daily_loss = self.config['risk_management'].get('max_loss_per_day_usd', 50)
            if self.performance_metrics['daily_pnl'] <= -max_daily_loss:
                self.logger.warning(f"🛑 Perda diária máxima atingida: ${self.performance_metrics['daily_pnl']:.2f}")
                return False

            # Verificar número máximo de posições ativas (simulado)
            max_positions = self.config['risk_management'].get('max_positions_per_cycle', 3)
            current_positions = random.randint(0, max_positions)  # Simulado

            if current_positions >= max_positions:
                self.logger.debug(f"📊 Número máximo de posições atingido: {current_positions}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar limites de risco: {e}")
            return False

    def place_market_making_orders(self, pair: str = "SOL-USD") -> Optional[Dict]:
        """Coloca ordens de market making com lógica avançada"""
        if not self.should_place_order():
            return None

        try:
            market_data = self.get_market_data(pair)
            current_price = market_data['price']
            spread = market_data['spread']

            # Estratégia de spread adaptativo
            adaptive_spread = self._calculate_adaptive_spread(market_data)

            # Calcula preços das ordens com estratégia aprimorada
            buy_price = current_price * (1 - adaptive_spread * 0.5)
            sell_price = current_price * (1 + adaptive_spread * 0.5)

            # Calcula tamanhos das ordens com balanceamento
            max_order_value = self.get_available_balance() * self.config['trading']['max_leverage']
            total_allocation = max_order_value * 0.8  # Usa 80% do capital disponível

            buy_size = self.calculate_order_size(pair, total_allocation * 0.5)
            sell_size = self.calculate_order_size(pair, total_allocation * 0.5)

            # Adiciona variação de preço para parecer mais natural
            price_variation = current_price * 0.001  # 0.1% de variação
            buy_price += random.uniform(-price_variation, price_variation)
            sell_price += random.uniform(-price_variation, price_variation)

            # Arredondamento apropriado para cada par
            buy_price = self._round_price(pair, buy_price)
            sell_price = self._round_price(pair, sell_price)

            # Log detalhado das ordens
            self._log_order_details(pair, buy_price, sell_price, buy_size, sell_size)

            # Simula envio das ordens (em produção, seria chamada real para API)
            order_ids = self._simulate_order_placement(pair, buy_price, sell_price, buy_size, sell_size)

            # Atualiza métricas
            order_value = (buy_size * buy_price) + (sell_size * sell_price)
            self._update_trade_metrics(order_value, order_ids)

            return order_ids

        except Exception as e:
            self.logger.error(f"❌ Erro ao colocar ordens para {pair}: {e}")
            return None

    def _calculate_adaptive_spread(self, market_data: Dict) -> float:
        """Calcula spread adaptativo baseado nas condições de mercado"""
        base_spread = market_data.get('spread', 0.001)

        # Aumenta spread em mercados voláteis
        if market_data.get('volume_24h', 0) < 50000:
            return base_spread * 1.5

        # Reduz spread em mercados líquidos
        if market_data.get('volume_24h', 0) > 200000:
            return base_spread * 0.8

        return base_spread

    def _round_price(self, pair: str, price: float) -> float:
        """Arredonda preço baseado nas características do par"""
        # Diferentes pares têm diferentes casas decimais
        price_decimals = {
            'SOL-USD': 2,
            'ETH-USD': 2,
            'BTC-USD': 0
        }

        decimals = price_decimals.get(pair, 2)
        return round(price, decimals)

    def _log_order_details(self, pair: str, buy_price: float, sell_price: float,
                          buy_size: float, sell_size: float):
        """Log detalhado das ordens"""
        current_price = self.get_market_data(pair)['price']

        self.logger.info(f"📈 Colocando ordens para {pair}:")
        self.logger.info(f"   💰 Preço atual: ${current_price:.2f}")
        self.logger.info(f"   🟢 BUY:  {buy_size:.6f} @ ${buy_price:.2f}")
        self.logger.info(f"   🔴 SELL: {sell_size:.6f} @ ${sell_price:.2f}")

        spread_pct = ((sell_price - buy_price) / current_price) * 100
        self.logger.info(f"   📊 Spread: {spread_pct:.2f}")

    def _simulate_order_placement(self, pair: str, buy_price: float, sell_price: float,
                                buy_size: float, sell_size: float) -> Dict:
        """Simula colocação de ordens"""
        # Simula possíveis rejeições (5% de chance)
        if random.random() < 0.05:
            raise Exception("Ordem rejeitada pela exchange (simulado)")

        order_ids = {
            'buy': f"buy_{pair}_{random.randint(100000, 999999)}",
            'sell': f"sell_{pair}_{random.randint(100000, 999999)}",
            'pair': pair,
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(f"✅ Ordens colocadas: {order_ids['buy']} | {order_ids['sell']}")
        return order_ids

    def _update_trade_metrics(self, order_value: float, order_ids: Dict):
        """Atualiza métricas de trading"""
        self.daily_volume += order_value
        self.total_volume += order_value
        self.total_trades += 1

        # Simula taxa de sucesso (95% das ordens são executadas)
        if random.random() < 0.95:
            self.successful_trades += 1

        # Simula PnL (pequena perda/custo do spread)
        simulated_pnl = -order_value * 0.001  # 0.1% de custo simulado
        self.performance_metrics['daily_pnl'] += simulated_pnl
        self.performance_metrics['total_pnl'] += simulated_pnl

        # Atualiza win rate
        if self.total_trades > 0:
            self.performance_metrics['win_rate'] = (self.successful_trades / self.total_trades) * 100

        self.logger.debug(f"📊 Métricas atualizadas: Volume +${order_value:.2f} PnL {simulated_pnl:+.2f}")

    def get_performance_summary(self) -> Dict:
        """Retorna resumo completo de performance"""
        return {
            'session': {
                'start_time': self.start_time.isoformat(),
                'uptime': str(datetime.now() - self.start_time),
                'cycles_completed': self.cycle_count,
                'total_trades': self.total_trades,
                'successful_trades': self.successful_trades
            },
            'volume': {
                'daily': round(self.daily_volume, 2),
                'total': round(self.total_volume, 2)
            },
            'pnl': {
                'daily': round(self.performance_metrics['daily_pnl'], 2),
                'total': round(self.performance_metrics['total_pnl'], 2),
                'best_day': round(self.performance_metrics['best_day'], 2),
                'worst_day': round(self.performance_metrics['worst_day'], 2)
            },
            'rates': {
                'win_rate': round(self.performance_metrics['win_rate'], 2),
                'success_rate': round((self.successful_trades / max(self.total_trades, 1)) * 100, 2)
            }
        }

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

                self.logger.info(f"⏱️ Monitorando por {monitoring_duration} minutos...")
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
                    self.logger.info(f"📊 Status: {cycle_count} ciclos, Volume diário: ${self.daily_volume:.2f"

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
        """Exibe menu interativo aprimorado"""
        while True:
            try:
                # Obter métricas atuais para o menu
                performance = self.get_performance_summary()

                choice = questionary.select(
                    "🤖 Paradex Market Maker - Menu Principal",
                    choices=[
                        "1. ⚙️  Configurar conta",
                        "2. 🚀 Iniciar trading",
                        "3. 📊 Dashboard de performance",
                        "4. 📈 Ver métricas detalhadas",
                        "5. ⚠️  Parar trading",
                        "6. 🔧 Configurações avançadas",
                        "7. ❌ Sair"
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
                    self._show_performance_dashboard()

                elif choice.startswith("4"):
                    self._show_detailed_metrics()

                elif choice.startswith("5"):
                    self.stop_trading()

                elif choice.startswith("6"):
                    self._show_advanced_config()

                elif choice.startswith("7"):
                    self._cleanup_and_exit()

            except KeyboardInterrupt:
                print("\n\n🛑 Interrupção detectada...")
                self._cleanup_and_exit()
            except Exception as e:
                self.logger.error(f"❌ Erro no menu: {e}")
                print(f"❌ Erro inesperado: {e}")

    def _show_performance_dashboard(self):
        """Exibe dashboard de performance"""
        performance = self.get_performance_summary()

        print("\n📊 DASHBOARD DE PERFORMANCE")
        print("=" * 50)

        # Status da sessão
        session = performance['session']
        print("⏱️  SESSÃO:")
        print(f"   Iniciada: {session['start_time']}")
        print(f"   Tempo ativo: {session['uptime']}")
        print(f"   Ciclos: {session['cycles_completed']}")

        # Volume
        volume = performance['volume']
        print("\n💰 VOLUME:")
        print(f"   Diário: ${volume['daily']:.2f}")
        print(f"   Total: ${volume['total']:.2f}")

        # PnL
        pnl = performance['pnl']
        print("\n📈 P&L:")
        print(f"   Diário: ${pnl['daily']:.2f}")
        print(f"   Total: ${pnl['total']:.2f}")
        print(f"   Melhor dia: ${pnl['best_day']:.2f}")
        print(f"   Pior dia: ${pnl['worst_day']:.2f}")

        # Taxas
        rates = performance['rates']
        print("\n🎯 TAXAS:")
        print(f"   Win Rate: {rates['win_rate']:.1f}")
        print(f"   Success Rate: {rates['success_rate']:.1f}")

        input("\n🔄 Pressione Enter para continuar...")

    def _show_detailed_metrics(self):
        """Exibe métricas detalhadas"""
        performance = self.get_performance_summary()

        print("\n📈 MÉTRICAS DETALHADAS")
        print("=" * 50)

        # Métricas técnicas
        trades = performance['session']
        print("📊 TRADING:")
        print(f"   Total de ordens: {trades['total_trades']}")
        print(f"   Ordens executadas: {trades['successful_trades']}")
        print(f"   Taxa de execução: {(trades['successful_trades']/max(trades['total_trades'],1))*100:.1f}")

        # Eficiência
        if performance['volume']['daily'] > 0:
            avg_order_size = performance['volume']['daily'] / max(trades['total_trades'], 1)
            print(f"   Tamanho médio da ordem: ${avg_order_size:.2f}")

        # Performance relativa
        capital_base = 5000
        daily_return_pct = (performance['pnl']['daily'] / capital_base) * 100
        total_return_pct = (performance['pnl']['total'] / capital_base) * 100

        print("\n📊 PERFORMANCE RELATIVA:")
        print(f"   Retorno diário: {daily_return_pct:.2f}")
        print(f"   Retorno total: {total_return_pct:.2f}")

        input("\n🔄 Pressione Enter para continuar...")

    def _show_advanced_config(self):
        """Exibe opções de configuração avançada"""
        print("\n🔧 CONFIGURAÇÕES AVANÇADAS")
        print("=" * 50)

        print("📝 Opções disponíveis:")
        print("1. 📊 Ver configuração atual")
        print("2. 🔧 Editar parâmetros de risco")
        print("3. 🎯 Ajustar estratégia de trading")
        print("4. 📈 Configurar métricas")
        print("5. 🔙 Voltar")

        choice = input("\nEscolha uma opção (1-5): ").strip()

        if choice == "1":
            self._display_current_config()
        elif choice == "2":
            self._edit_risk_parameters()
        elif choice == "3":
            self._edit_trading_strategy()
        elif choice == "4":
            self._configure_metrics()
        else:
            print("Opção inválida!")

    def _display_current_config(self):
        """Exibe configuração atual"""
        print("\n📋 CONFIGURAÇÃO ATUAL")
        print("=" * 50)

        # Configuração básica
        config = self.config
        print("💰 TRADING:")
        trading = config.get('trading', {})
        print(f"   Order Value: ${trading.get('order_value_usd', {}).get('min', 0)} - ${trading.get('order_value_usd', {}).get('max', 0)})")
        print(f"   Max Leverage: {trading.get('max_leverage', 0)}x")
        print(f"   Max LTV: {trading.get('max_position_ltv', 0)}%")

        print("\n🛡️  RISK MANAGEMENT:")
        risk = config.get('risk_management', {})
        print(f"   Max Daily Volume: ${risk.get('max_daily_volume_usd', 0)}")
        print(f"   Max Loss per Day: ${risk.get('max_loss_per_day_usd', 0)}")
        print(f"   Stop Loss: {risk.get('stop_loss_percentage', 0)}%")

        print("\n🎯 PAIRS:")
        pairs = config.get('pairs', {})
        print(f"   Primary: {pairs.get('primary_pairs', [])}")
        print(f"   Min Volume: ${pairs.get('min_volume_usd', 0)}")

        input("\n🔄 Pressione Enter para continuar...")

    def _edit_risk_parameters(self):
        """Permite edição de parâmetros de risco"""
        print("\n🛡️  EDITAR PARÂMETROS DE RISCO")
        print("=" * 50)

        # Exemplos de edição (em produção seria mais interativo)
        print("💡 Para editar parâmetros de risco:")
        print("   Edite diretamente o arquivo config_windows.json")
        print("   Principais parâmetros:")
        print("   - max_daily_volume_usd")
        print("   - max_loss_per_day_usd")
        print("   - stop_loss_percentage")

        input("\n🔄 Pressione Enter para continuar...")

    def _edit_trading_strategy(self):
        """Permite edição de estratégia de trading"""
        print("\n🎯 EDITAR ESTRATÉGIA DE TRADING")
        print("=" * 50)

        print("💡 Para editar estratégia:")
        print("   Edite diretamente o arquivo config_windows.json")
        print("   Principais parâmetros:")
        print("   - order_value_usd (min/max)")
        print("   - order_duration_min")
        print("   - delay_between_orders_min")

        input("\n🔄 Pressione Enter para continuar...")

    def _configure_metrics(self):
        """Configura métricas e logging"""
        print("\n📊 CONFIGURAR MÉTRICAS")
        print("=" * 50)

        print("💡 Para configurar métricas:")
        print("   Edite a seção 'logging' no config_windows.json")
        print("   Opções disponíveis:")
        print("   - level: DEBUG, INFO, WARNING, ERROR")
        print("   - file: caminho do arquivo de log")

        input("\n🔄 Pressione Enter para continuar...")

    def _cleanup_and_exit(self):
        """Limpeza e saída segura"""
        print("\n🛑 Saindo...")

        # Parar trading se estiver rodando
        if self.is_running:
            self.stop_trading()

        # Salvar métricas finais se houver dados
        if self.total_trades > 0:
            final_summary = self.get_performance_summary()
            print("\n📊 RESUMO FINAL DA SESSÃO:")
            print(f"   Total de operações: {final_summary['session']['total_trades']}")
            print(f"   Volume total: ${final_summary['volume']['total']:.2f}")
            print(f"   P&L total: ${final_summary['pnl']['total']:.2f}")
            print(f"   Win rate: {final_summary['rates']['win_rate']:.1f}")

        print("👋 Até logo!")
        sys.exit(0)


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