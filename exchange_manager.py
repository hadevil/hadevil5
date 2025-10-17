"""
Gerenciador de exchange para execução de ordens
"""
import ccxt
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from config import config

logger = logging.getLogger(__name__)

class ExchangeManager:
    """Gerenciador de operações na exchange"""
    
    def __init__(self):
        self.exchange = None
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Inicializa a conexão com a exchange"""
        try:
            exchange_class = getattr(ccxt, config.exchange_name)
            self.exchange = exchange_class({
                'apiKey': config.api_key,
                'secret': config.api_secret,
                'sandbox': config.sandbox,
                'enableRateLimit': True,
            })
            
            # Testar conexão
            self.exchange.load_markets()
            logger.info(f"Exchange {config.exchange_name} inicializada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar exchange: {e}")
            raise
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Obtém preço atual do ativo"""
        try:
            ticker = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.fetch_ticker, symbol
            )
            return ticker
        except Exception as e:
            logger.error(f"Erro ao obter ticker para {symbol}: {e}")
            raise
    
    async def place_market_order(self, symbol: str, side: str, amount: float) -> Dict:
        """Coloca ordem a mercado"""
        try:
            order = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.exchange.create_market_order,
                symbol, side, amount
            )
            logger.info(f"Ordem {side} executada para {symbol}: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Erro ao executar ordem {side} para {symbol}: {e}")
            raise
    
    async def place_stop_loss_order(self, symbol: str, side: str, amount: float, 
                                  stop_price: float) -> Dict:
        """Coloca ordem de stop loss"""
        try:
            order = await asyncio.get_event_loop().run_in_executor(
                None,
                self.exchange.create_order,
                symbol, 'stop_market', side, amount, None, stop_price
            )
            logger.info(f"Stop Loss {side} colocado para {symbol}: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Erro ao colocar stop loss para {symbol}: {e}")
            raise
    
    async def place_take_profit_order(self, symbol: str, side: str, amount: float,
                                    limit_price: float) -> Dict:
        """Coloca ordem de take profit"""
        try:
            order = await asyncio.get_event_loop().run_in_executor(
                None,
                self.exchange.create_limit_order,
                symbol, side, amount, limit_price
            )
            logger.info(f"Take Profit {side} colocado para {symbol}: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Erro ao colocar take profit para {symbol}: {e}")
            raise
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancela uma ordem"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.cancel_order, order_id, symbol
            )
            logger.info(f"Ordem {order_id} cancelada")
            return result
        except Exception as e:
            logger.error(f"Erro ao cancelar ordem {order_id}: {e}")
            return False
    
    async def get_open_orders(self, symbol: str) -> List[Dict]:
        """Obtém ordens abertas para um símbolo"""
        try:
            orders = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.fetch_open_orders, symbol
            )
            return orders
        except Exception as e:
            logger.error(f"Erro ao obter ordens abertas para {symbol}: {e}")
            return []
    
    async def get_balance(self) -> Dict:
        """Obtém saldo da conta"""
        try:
            balance = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.fetch_balance
            )
            return balance
        except Exception as e:
            logger.error(f"Erro ao obter saldo: {e}")
            return {}
    
    def calculate_position_size(self, symbol: str, price: float, 
                              risk_percentage: float = None) -> float:
        """Calcula tamanho da posição baseado no risco"""
        if risk_percentage is None:
            risk_percentage = config.risk_per_trade_percentage
        
        # Obter saldo disponível
        balance = self.exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        
        # Calcular valor da posição
        position_value = min(
            usdt_balance * (risk_percentage / 100),
            config.max_position_size_usdt
        )
        
        # Calcular quantidade
        amount = position_value / price
        return round(amount, 6)