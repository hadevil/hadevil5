"""
Estratégia de Market Making Adaptativa para Paradex
Otimizada para SOL com capital limitado e foco em airdrop farming
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from config import MARKET_MAKING_CONFIG, STRATEGY_CONFIG, TRADING_CONFIG

@dataclass
class OrderBook:
    """Estrutura para dados do livro de ordens"""
    bids: List[Tuple[float, float]]  # [(price, quantity), ...]
    asks: List[Tuple[float, float]]
    timestamp: datetime

@dataclass
class MarketData:
    """Estrutura para dados de mercado"""
    price: float
    volume: float
    volatility: float
    trend: float
    timestamp: datetime

class AdaptiveMarketMakingStrategy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.price_history = []
        self.volume_history = []
        self.order_history = []
        self.current_inventory = 0.0
        self.target_inventory = 0.0
        self.last_prices = []
        self.volatility_window = STRATEGY_CONFIG['volatility_lookback']
        self.volume_window = STRATEGY_CONFIG['volume_lookback']
        self.trend_window = STRATEGY_CONFIG['trend_lookback']
        
    def update_market_data(self, market_data: MarketData):
        """Atualiza dados de mercado e calcula métricas"""
        self.price_history.append(market_data.price)
        self.volume_history.append(market_data.volume)
        
        # Manter apenas dados necessários
        if len(self.price_history) > self.volatility_window:
            self.price_history = self.price_history[-self.volatility_window:]
        if len(self.volume_history) > self.volume_window:
            self.volume_history = self.volume_history[-self.volume_window:]
    
    def calculate_volatility(self) -> float:
        """Calcula volatilidade baseada no histórico de preços"""
        if len(self.price_history) < 2:
            return 0.0
        
        prices = np.array(self.price_history)
        returns = np.diff(np.log(prices))
        return np.std(returns) * np.sqrt(24 * 60)  # Volatilidade anualizada
    
    def calculate_volume_profile(self) -> Dict[str, float]:
        """Calcula perfil de volume"""
        if not self.volume_history:
            return {'avg_volume': 0.0, 'volume_trend': 0.0}
        
        volumes = np.array(self.volume_history)
        avg_volume = np.mean(volumes)
        
        # Calcular tendência de volume
        if len(volumes) >= 2:
            volume_trend = (volumes[-1] - volumes[0]) / volumes[0]
        else:
            volume_trend = 0.0
        
        return {
            'avg_volume': avg_volume,
            'volume_trend': volume_trend
        }
    
    def calculate_trend(self) -> float:
        """Calcula tendência de preço usando regressão linear simples"""
        if len(self.price_history) < self.trend_window:
            return 0.0
        
        prices = np.array(self.price_history[-self.trend_window:])
        x = np.arange(len(prices))
        
        # Regressão linear simples
        slope = np.polyfit(x, prices, 1)[0]
        return slope / prices[0]  # Normalizar pela média dos preços
    
    def calculate_inventory_skew(self) -> float:
        """Calcula skew do inventário para ajustar spread"""
        if self.target_inventory == 0:
            return 0.0
        
        skew_ratio = self.current_inventory / self.target_inventory
        return np.clip(skew_ratio, -1.0, 1.0)
    
    def calculate_adaptive_spread(self, base_price: float) -> Tuple[float, float]:
        """Calcula spread adaptativo baseado em múltiplos fatores"""
        # Spread base
        base_spread = MARKET_MAKING_CONFIG['spread_percentage']
        
        # Ajustes baseados em volatilidade
        volatility = self.calculate_volatility()
        volatility_adjustment = min(volatility * 2, 0.01)  # Máximo 1%
        
        # Ajustes baseados em volume
        volume_profile = self.calculate_volume_profile()
        volume_adjustment = -volume_profile['volume_trend'] * 0.001  # Reduz spread se volume aumentando
        
        # Ajustes baseados em tendência
        trend = self.calculate_trend()
        trend_adjustment = abs(trend) * 0.002  # Aumenta spread se tendência forte
        
        # Ajustes baseados em inventário
        inventory_skew = self.calculate_inventory_skew()
        inventory_adjustment = inventory_skew * 0.001
        
        # Spread final
        total_spread = base_spread + volatility_adjustment + volume_adjustment + trend_adjustment + inventory_adjustment
        
        # Aplicar limites
        total_spread = np.clip(
            total_spread, 
            MARKET_MAKING_CONFIG['min_spread'], 
            MARKET_MAKING_CONFIG['max_spread']
        )
        
        # Calcular preços bid e ask
        half_spread = total_spread / 2
        bid_price = base_price * (1 - half_spread)
        ask_price = base_price * (1 + half_spread)
        
        return bid_price, ask_price
    
    def calculate_order_sizes(self, base_price: float, available_capital: float) -> Tuple[float, float]:
        """Calcula tamanhos de ordem baseados no capital disponível e volatilidade"""
        # Tamanho base baseado no capital
        base_size = (available_capital * TRADING_CONFIG['risk_per_trade']) / base_price
        
        # Ajustar baseado na volatilidade
        volatility = self.calculate_volatility()
        volatility_multiplier = max(0.5, 1 - volatility * 10)  # Reduz tamanho se alta volatilidade
        
        # Ajustar baseado no inventário
        inventory_skew = self.calculate_inventory_skew()
        inventory_multiplier = 1 - abs(inventory_skew) * 0.5  # Reduz tamanho se inventário desbalanceado
        
        # Tamanho final
        adjusted_size = base_size * volatility_multiplier * inventory_multiplier
        
        # Aplicar limites
        adjusted_size = np.clip(
            adjusted_size,
            TRADING_CONFIG['min_order_size'],
            min(TRADING_CONFIG['max_order_size'], available_capital / base_price)
        )
        
        return adjusted_size, adjusted_size
    
    def generate_orders(self, current_price: float, orderbook: OrderBook, 
                       available_capital: float) -> List[Dict]:
        """Gera lista de ordens para market making"""
        orders = []
        
        # Atualizar dados de mercado
        market_data = MarketData(
            price=current_price,
            volume=sum([qty for _, qty in orderbook.bids + orderbook.asks]),
            volatility=self.calculate_volatility(),
            trend=self.calculate_trend(),
            timestamp=datetime.now()
        )
        self.update_market_data(market_data)
        
        # Calcular preços e tamanhos
        bid_price, ask_price = self.calculate_adaptive_spread(current_price)
        bid_size, ask_size = self.calculate_order_sizes(current_price, available_capital)
        
        # Gerar ordens bid (compra)
        for i in range(MARKET_MAKING_CONFIG['max_orders_per_side']):
            order_price = bid_price * (1 - i * 0.0005)  # Reduz preço para ordens subsequentes
            order_size = bid_size * (MARKET_MAKING_CONFIG['order_size_multiplier'] ** i)
            
            if order_price > 0 and order_size >= TRADING_CONFIG['min_order_size']:
                orders.append({
                    'side': 'buy',
                    'price': order_price,
                    'quantity': order_size,
                    'type': 'limit',
                    'time_in_force': 'GTC'
                })
        
        # Gerar ordens ask (venda)
        for i in range(MARKET_MAKING_CONFIG['max_orders_per_side']):
            order_price = ask_price * (1 + i * 0.0005)  # Aumenta preço para ordens subsequentes
            order_size = ask_size * (MARKET_MAKING_CONFIG['order_size_multiplier'] ** i)
            
            if order_price > 0 and order_size >= TRADING_CONFIG['min_order_size']:
                orders.append({
                    'side': 'sell',
                    'price': order_price,
                    'quantity': order_size,
                    'type': 'limit',
                    'time_in_force': 'GTC'
                })
        
        return orders
    
    def should_adjust_inventory(self) -> bool:
        """Determina se deve ajustar inventário"""
        inventory_ratio = abs(self.current_inventory) / self.target_inventory if self.target_inventory > 0 else 0
        return inventory_ratio > MARKET_MAKING_CONFIG['inventory_skew_threshold']
    
    def get_inventory_adjustment_orders(self, current_price: float) -> List[Dict]:
        """Gera ordens para ajustar inventário"""
        if not self.should_adjust_inventory():
            return []
        
        orders = []
        inventory_skew = self.calculate_inventory_skew()
        
        # Se inventário muito positivo, vender mais agressivamente
        if inventory_skew > 0.5:
            # Ordem de venda com preço mais baixo
            sell_price = current_price * 0.999
            sell_size = abs(self.current_inventory) * 0.5
            orders.append({
                'side': 'sell',
                'price': sell_price,
                'quantity': sell_size,
                'type': 'limit',
                'time_in_force': 'IOC'  # Immediate or Cancel
            })
        
        # Se inventário muito negativo, comprar mais agressivamente
        elif inventory_skew < -0.5:
            # Ordem de compra com preço mais alto
            buy_price = current_price * 1.001
            buy_size = abs(self.current_inventory) * 0.5
            orders.append({
                'side': 'buy',
                'price': buy_price,
                'quantity': buy_size,
                'type': 'limit',
                'time_in_force': 'IOC'
            })
        
        return orders
    
    def update_inventory(self, filled_orders: List[Dict]):
        """Atualiza inventário baseado em ordens executadas"""
        for order in filled_orders:
            if order['side'] == 'buy':
                self.current_inventory += order['quantity']
            else:
                self.current_inventory -= order['quantity']
    
    def get_performance_metrics(self) -> Dict:
        """Retorna métricas de performance da estratégia"""
        if not self.price_history:
            return {}
        
        # Calcular retornos
        prices = np.array(self.price_history)
        returns = np.diff(np.log(prices))
        
        # Métricas básicas
        total_return = (prices[-1] - prices[0]) / prices[0] if len(prices) > 1 else 0
        volatility = np.std(returns) * np.sqrt(24 * 60) if len(returns) > 0 else 0
        sharpe_ratio = total_return / volatility if volatility > 0 else 0
        
        # Métricas de volume
        volume_profile = self.calculate_volume_profile()
        
        return {
            'total_return': total_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'avg_volume': volume_profile['avg_volume'],
            'volume_trend': volume_profile['volume_trend'],
            'current_inventory': self.current_inventory,
            'inventory_skew': self.calculate_inventory_skew(),
            'data_points': len(self.price_history)
        }