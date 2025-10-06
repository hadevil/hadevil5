"""
Estratégia Avançada de Market Making para Airdrop Farming
Focada em minimizar perdas e maximizar pontos de airdrop
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from config import MARKET_MAKING_CONFIG, STRATEGY_CONFIG, TRADING_CONFIG

@dataclass
class AirdropMetrics:
    """Métricas específicas para airdrop farming"""
    daily_volume: float = 0.0
    daily_trades: int = 0
    active_days: int = 0
    total_volume: float = 0.0
    total_trades: int = 0
    volume_score: float = 0.0
    consistency_score: float = 0.0

class AdvancedMarketMakingStrategy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Dados de mercado
        self.price_history = []
        self.volume_history = []
        self.trade_history = []
        self.orderbook_history = []
        
        # Métricas de airdrop
        self.airdrop_metrics = AirdropMetrics()
        self.daily_start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Estratégias específicas
        self.mean_reversion_factor = 0.3
        self.arbitrage_threshold = 0.0005  # 0.05% para arbitragem
        self.hedge_ratio = 0.8  # 80% do inventário é hedgeado
        
        # Controle de risco aprimorado
        self.max_inventory_imbalance = 0.1  # 10% do capital
        self.emergency_stop_loss = 0.02  # 2% de perda máxima por trade
        
    def update_airdrop_metrics(self, trade_data: Dict):
        """Atualiza métricas específicas para airdrop"""
        current_time = datetime.now()
        
        # Reset diário se necessário
        if current_time.date() != self.daily_start_time.date():
            self.daily_start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            self.airdrop_metrics.daily_volume = 0.0
            self.airdrop_metrics.daily_trades = 0
        
        # Atualizar métricas diárias
        self.airdrop_metrics.daily_volume += trade_data.get('volume', 0.0)
        self.airdrop_metrics.daily_trades += 1
        
        # Atualizar métricas totais
        self.airdrop_metrics.total_volume += trade_data.get('volume', 0.0)
        self.airdrop_metrics.total_trades += 1
        
        # Calcular scores
        self._calculate_airdrop_scores()
    
    def _calculate_airdrop_scores(self):
        """Calcula scores para airdrop farming"""
        # Score de volume (baseado em volume diário consistente)
        target_daily_volume = TRADING_CONFIG['total_capital'] * 0.3  # 30% do capital por dia
        volume_ratio = self.airdrop_metrics.daily_volume / target_daily_volume
        self.airdrop_metrics.volume_score = min(1.0, volume_ratio)
        
        # Score de consistência (baseado em trades diários)
        target_daily_trades = 100  # Meta de 100 trades por dia
        trades_ratio = self.airdrop_metrics.daily_trades / target_daily_trades
        self.airdrop_metrics.consistency_score = min(1.0, trades_ratio)
    
    def calculate_optimal_spread(self, current_price: float, volatility: float, 
                               volume_profile: Dict, inventory_skew: float) -> Tuple[float, float]:
        """Calcula spread ótimo para maximizar pontos de airdrop"""
        
        # Spread base mais agressivo para airdrop
        base_spread = 0.0003  # 0.03% - mais agressivo que o padrão
        
        # Ajuste baseado em volatilidade (menor spread em alta volatilidade para mais trades)
        volatility_adjustment = -volatility * 0.5  # Reduz spread quando volátil
        
        # Ajuste baseado em volume (mais agressivo quando volume baixo)
        volume_adjustment = -volume_profile.get('volume_trend', 0) * 0.0001
        
        # Ajuste baseado em inventário (mais agressivo para rebalancear)
        inventory_adjustment = -abs(inventory_skew) * 0.0002
        
        # Ajuste para maximizar trades (spread menor = mais execuções)
        airdrop_adjustment = -0.0001 if self.airdrop_metrics.volume_score < 0.8 else 0.0
        
        # Spread final
        total_spread = base_spread + volatility_adjustment + volume_adjustment + inventory_adjustment + airdrop_adjustment
        
        # Limites mais apertados para airdrop
        min_spread = 0.0001  # 0.01% mínimo
        max_spread = 0.001   # 0.1% máximo
        
        total_spread = np.clip(total_spread, min_spread, max_spread)
        
        # Calcular preços
        half_spread = total_spread / 2
        bid_price = current_price * (1 - half_spread)
        ask_price = current_price * (1 + half_spread)
        
        return bid_price, ask_price
    
    def calculate_order_sizes_airdrop(self, current_price: float, available_capital: float) -> Tuple[float, float]:
        """Calcula tamanhos de ordem otimizados para airdrop farming"""
        
        # Tamanho base menor para mais trades
        base_size = (available_capital * 0.005) / current_price  # 0.5% do capital por trade
        
        # Ajustar baseado no progresso do airdrop
        if self.airdrop_metrics.volume_score < 0.5:
            # Se volume baixo, aumentar tamanho
            size_multiplier = 1.5
        elif self.airdrop_metrics.consistency_score < 0.5:
            # Se poucos trades, aumentar tamanho
            size_multiplier = 1.2
        else:
            # Manter tamanho normal
            size_multiplier = 1.0
        
        adjusted_size = base_size * size_multiplier
        
        # Limites
        min_size = 0.05  # Mínimo 0.05 SOL
        max_size = min(2.0, available_capital * 0.02 / current_price)  # Máximo 2% do capital
        
        adjusted_size = np.clip(adjusted_size, min_size, max_size)
        
        return adjusted_size, adjusted_size
    
    def generate_airdrop_orders(self, current_price: float, orderbook, 
                               available_capital: float) -> List[Dict]:
        """Gera ordens otimizadas para airdrop farming"""
        orders = []
        
        # Calcular métricas de mercado
        volatility = self._calculate_volatility()
        volume_profile = self._calculate_volume_profile()
        inventory_skew = self._calculate_inventory_skew()
        
        # Calcular preços e tamanhos
        bid_price, ask_price = self.calculate_optimal_spread(
            current_price, volatility, volume_profile, inventory_skew
        )
        bid_size, ask_size = self.calculate_order_sizes_airdrop(current_price, available_capital)
        
        # Gerar múltiplas ordens por lado para maximizar execuções
        num_orders_per_side = 5  # Mais ordens para mais execuções
        
        # Ordens bid (compra) - escalonadas
        for i in range(num_orders_per_side):
            order_price = bid_price * (1 - i * 0.0001)  # Reduz preço gradualmente
            order_size = bid_size * (0.8 ** i)  # Reduz tamanho gradualmente
            
            if order_price > 0 and order_size >= 0.01:
                orders.append({
                    'side': 'buy',
                    'price': order_price,
                    'quantity': order_size,
                    'type': 'limit',
                    'time_in_force': 'GTC',
                    'priority': 'airdrop'  # Marca para prioridade
                })
        
        # Ordens ask (venda) - escalonadas
        for i in range(num_orders_per_side):
            order_price = ask_price * (1 + i * 0.0001)  # Aumenta preço gradualmente
            order_size = ask_size * (0.8 ** i)  # Reduz tamanho gradualmente
            
            if order_price > 0 and order_size >= 0.01:
                orders.append({
                    'side': 'sell',
                    'price': order_price,
                    'quantity': order_size,
                    'type': 'limit',
                    'time_in_force': 'GTC',
                    'priority': 'airdrop'
                })
        
        return orders
    
    def detect_arbitrage_opportunities(self, orderbook) -> List[Dict]:
        """Detecta oportunidades de arbitragem interna"""
        opportunities = []
        
        if not orderbook.bids or not orderbook.asks:
            return opportunities
        
        best_bid = orderbook.bids[0][0]
        best_ask = orderbook.asks[0][0]
        
        # Calcular spread interno
        internal_spread = (best_ask - best_bid) / best_bid
        
        if internal_spread > self.arbitrage_threshold:
            # Oportunidade de arbitragem detectada
            mid_price = (best_bid + best_ask) / 2
            
            # Ordem de compra no melhor bid
            opportunities.append({
                'side': 'buy',
                'price': best_bid,
                'quantity': min(1.0, orderbook.bids[0][1] * 0.5),
                'type': 'limit',
                'time_in_force': 'IOC',
                'priority': 'arbitrage'
            })
            
            # Ordem de venda no melhor ask
            opportunities.append({
                'side': 'sell',
                'price': best_ask,
                'quantity': min(1.0, orderbook.asks[0][1] * 0.5),
                'type': 'limit',
                'time_in_force': 'IOC',
                'priority': 'arbitrage'
            })
        
        return opportunities
    
    def calculate_mean_reversion_orders(self, current_price: float, 
                                      price_history: List[float]) -> List[Dict]:
        """Calcula ordens baseadas em mean reversion"""
        if len(price_history) < 20:
            return []
        
        # Calcular média móvel
        recent_prices = price_history[-20:]
        mean_price = np.mean(recent_prices)
        
        # Calcular desvio da média
        deviation = (current_price - mean_price) / mean_price
        
        orders = []
        
        # Se preço muito acima da média, vender
        if deviation > 0.002:  # 0.2% acima da média
            orders.append({
                'side': 'sell',
                'price': current_price * 0.999,  # Ligeiramente abaixo do preço atual
                'quantity': min(1.0, abs(deviation) * 10),  # Tamanho baseado no desvio
                'type': 'limit',
                'time_in_force': 'GTC',
                'priority': 'mean_reversion'
            })
        
        # Se preço muito abaixo da média, comprar
        elif deviation < -0.002:  # 0.2% abaixo da média
            orders.append({
                'side': 'buy',
                'price': current_price * 1.001,  # Ligeiramente acima do preço atual
                'quantity': min(1.0, abs(deviation) * 10),
                'type': 'limit',
                'time_in_force': 'GTC',
                'priority': 'mean_reversion'
            })
        
        return orders
    
    def calculate_hedge_orders(self, current_inventory: float, 
                              current_price: float) -> List[Dict]:
        """Calcula ordens de hedge para proteger inventário"""
        if abs(current_inventory) < 0.1:  # Inventário pequeno, não precisa hedge
            return []
        
        orders = []
        
        # Se inventário muito positivo, vender para hedge
        if current_inventory > self.max_inventory_imbalance:
            hedge_quantity = current_inventory * self.hedge_ratio
            orders.append({
                'side': 'sell',
                'price': current_price * 0.998,  # Preço ligeiramente abaixo
                'quantity': hedge_quantity,
                'type': 'limit',
                'time_in_force': 'GTC',
                'priority': 'hedge'
            })
        
        # Se inventário muito negativo, comprar para hedge
        elif current_inventory < -self.max_inventory_imbalance:
            hedge_quantity = abs(current_inventory) * self.hedge_ratio
            orders.append({
                'side': 'buy',
                'price': current_price * 1.002,  # Preço ligeiramente acima
                'quantity': hedge_quantity,
                'type': 'limit',
                'time_in_force': 'GTC',
                'priority': 'hedge'
            })
        
        return orders
    
    def _calculate_volatility(self) -> float:
        """Calcula volatilidade dos preços"""
        if len(self.price_history) < 10:
            return 0.02  # Volatilidade padrão
        
        prices = np.array(self.price_history[-50:])  # Últimos 50 preços
        returns = np.diff(np.log(prices))
        return np.std(returns) * np.sqrt(24 * 60)  # Volatilidade anualizada
    
    def _calculate_volume_profile(self) -> Dict:
        """Calcula perfil de volume"""
        if not self.volume_history:
            return {'avg_volume': 1000, 'volume_trend': 0.0}
        
        volumes = np.array(self.volume_history[-20:])  # Últimos 20 períodos
        avg_volume = np.mean(volumes)
        
        if len(volumes) >= 2:
            volume_trend = (volumes[-1] - volumes[0]) / volumes[0]
        else:
            volume_trend = 0.0
        
        return {
            'avg_volume': avg_volume,
            'volume_trend': volume_trend
        }
    
    def _calculate_inventory_skew(self) -> float:
        """Calcula skew do inventário"""
        # Simplificado - em implementação real, calcularia baseado no inventário atual
        return 0.0
    
    def get_airdrop_progress(self) -> Dict:
        """Retorna progresso detalhado para airdrop"""
        return {
            'daily_volume': self.airdrop_metrics.daily_volume,
            'daily_trades': self.airdrop_metrics.daily_trades,
            'total_volume': self.airdrop_metrics.total_volume,
            'total_trades': self.airdrop_metrics.total_trades,
            'volume_score': self.airdrop_metrics.volume_score,
            'consistency_score': self.airdrop_metrics.consistency_score,
            'overall_score': (self.airdrop_metrics.volume_score + self.airdrop_metrics.consistency_score) / 2,
            'target_volume_daily': TRADING_CONFIG['total_capital'] * 0.3,
            'target_trades_daily': 100,
            'is_on_track': self.airdrop_metrics.volume_score >= 0.8 and self.airdrop_metrics.consistency_score >= 0.8
        }
    
    def should_increase_aggressiveness(self) -> bool:
        """Determina se deve aumentar agressividade para airdrop"""
        return (
            self.airdrop_metrics.volume_score < 0.7 or 
            self.airdrop_metrics.consistency_score < 0.7
        )