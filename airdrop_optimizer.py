"""
Otimizador de Airdrop Farming para Paradex
Foco em maximizar pontos de airdrop com eficiência de capital
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

@dataclass
class AirdropTargets:
    """Metas específicas para airdrop farming"""
    daily_volume_target: float = 1500.0  # $1500 por dia
    daily_trades_target: int = 100       # 100 trades por dia
    weekly_volume_target: float = 10500.0  # $10,500 por semana
    monthly_volume_target: float = 45000.0  # $45,000 por mês
    min_active_days: int = 30            # 30 dias ativos
    consistency_bonus: float = 1.2       # 20% de bônus por consistência

class AirdropOptimizer:
    def __init__(self, initial_capital: float = 5000):
        self.initial_capital = initial_capital
        self.logger = logging.getLogger(__name__)
        
        # Metas de airdrop
        self.targets = AirdropTargets()
        
        # Estado atual
        self.daily_stats = {
            'volume': 0.0,
            'trades': 0,
            'start_time': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        }
        
        self.weekly_stats = {
            'volume': 0.0,
            'trades': 0,
            'start_time': datetime.now() - timedelta(days=datetime.now().weekday())
        }
        
        self.monthly_stats = {
            'volume': 0.0,
            'trades': 0,
            'start_time': datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        }
        
        # Histórico de performance
        self.performance_history = []
        
        # Estratégias de otimização
        self.volume_boost_active = False
        self.trade_frequency_boost = False
        self.consistency_bonus_active = False
        
    def update_trade(self, trade_data: Dict):
        """Atualiza estatísticas com nova trade"""
        volume = trade_data.get('volume', 0.0)
        current_time = datetime.now()
        
        # Reset diário se necessário
        if current_time.date() != self.daily_stats['start_time'].date():
            self._reset_daily_stats()
        
        # Reset semanal se necessário
        if current_time.weekday() == 0 and current_time.hour < 6:  # Segunda-feira de manhã
            self._reset_weekly_stats()
        
        # Reset mensal se necessário
        if current_time.day == 1 and current_time.hour < 6:  # Primeiro dia do mês
            self._reset_monthly_stats()
        
        # Atualizar estatísticas
        self.daily_stats['volume'] += volume
        self.daily_stats['trades'] += 1
        
        self.weekly_stats['volume'] += volume
        self.weekly_stats['trades'] += 1
        
        self.monthly_stats['volume'] += volume
        self.monthly_stats['trades'] += 1
        
        # Atualizar estratégias de otimização
        self._update_optimization_strategies()
        
        self.logger.debug(f"Trade atualizada: Volume={volume:.2f}, Trades diários={self.daily_stats['trades']}")
    
    def _reset_daily_stats(self):
        """Reseta estatísticas diárias"""
        self.daily_stats = {
            'volume': 0.0,
            'trades': 0,
            'start_time': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        }
    
    def _reset_weekly_stats(self):
        """Reseta estatísticas semanais"""
        self.weekly_stats = {
            'volume': 0.0,
            'trades': 0,
            'start_time': datetime.now() - timedelta(days=datetime.now().weekday())
        }
    
    def _reset_monthly_stats(self):
        """Reseta estatísticas mensais"""
        self.monthly_stats = {
            'volume': 0.0,
            'trades': 0,
            'start_time': datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        }
    
    def _update_optimization_strategies(self):
        """Atualiza estratégias de otimização baseadas no progresso"""
        # Volume boost - ativar se volume diário baixo
        daily_volume_ratio = self.daily_stats['volume'] / self.targets.daily_volume_target
        self.volume_boost_active = daily_volume_ratio < 0.7
        
        # Trade frequency boost - ativar se poucos trades
        daily_trades_ratio = self.daily_stats['trades'] / self.targets.daily_trades_target
        self.trade_frequency_boost = daily_trades_ratio < 0.7
        
        # Consistency bonus - ativar se performance consistente
        if len(self.performance_history) >= 7:  # Pelo menos uma semana de dados
            recent_performance = self.performance_history[-7:]
            consistency_score = np.std([p['volume_ratio'] for p in recent_performance])
            self.consistency_bonus_active = consistency_score < 0.2  # Baixa variância = consistente
    
    def calculate_optimal_order_size(self, base_size: float, current_price: float) -> float:
        """Calcula tamanho ótimo de ordem para airdrop farming"""
        # Tamanho base
        optimal_size = base_size
        
        # Ajustar baseado no progresso diário
        daily_volume_ratio = self.daily_stats['volume'] / self.targets.daily_volume_target
        daily_trades_ratio = self.daily_stats['trades'] / self.targets.daily_trades_target
        
        # Se volume baixo, aumentar tamanho
        if daily_volume_ratio < 0.5:
            optimal_size *= 1.5
        elif daily_volume_ratio < 0.8:
            optimal_size *= 1.2
        
        # Se poucos trades, aumentar tamanho
        if daily_trades_ratio < 0.5:
            optimal_size *= 1.3
        elif daily_trades_ratio < 0.8:
            optimal_size *= 1.1
        
        # Ajustar baseado no tempo do dia (mais agressivo no final do dia)
        current_hour = datetime.now().hour
        if current_hour >= 20:  # Após 20h
            time_multiplier = 1.2
        elif current_hour >= 16:  # Após 16h
            time_multiplier = 1.1
        else:
            time_multiplier = 1.0
        
        optimal_size *= time_multiplier
        
        # Limites de segurança
        max_size = (self.initial_capital * 0.05) / current_price  # Máximo 5% do capital
        min_size = 0.01  # Mínimo 0.01 SOL
        
        return np.clip(optimal_size, min_size, max_size)
    
    def calculate_optimal_spread(self, base_spread: float) -> float:
        """Calcula spread ótimo para maximizar execuções"""
        # Spread base
        optimal_spread = base_spread
        
        # Ajustar baseado no progresso
        daily_volume_ratio = self.daily_stats['volume'] / self.targets.daily_volume_target
        daily_trades_ratio = self.daily_stats['trades'] / self.targets.daily_trades_target
        
        # Se volume baixo, reduzir spread para mais execuções
        if daily_volume_ratio < 0.5:
            optimal_spread *= 0.7
        elif daily_volume_ratio < 0.8:
            optimal_spread *= 0.8
        
        # Se poucos trades, reduzir spread
        if daily_trades_ratio < 0.5:
            optimal_spread *= 0.6
        elif daily_trades_ratio < 0.8:
            optimal_spread *= 0.8
        
        # Ajustar baseado no tempo do dia
        current_hour = datetime.now().hour
        if current_hour >= 20:  # Após 20h, mais agressivo
            optimal_spread *= 0.8
        elif current_hour >= 16:  # Após 16h
            optimal_spread *= 0.9
        
        # Limites
        min_spread = 0.0001  # 0.01% mínimo
        max_spread = 0.002   # 0.2% máximo
        
        return np.clip(optimal_spread, min_spread, max_spread)
    
    def calculate_trading_frequency(self) -> float:
        """Calcula frequência ótima de trading"""
        base_frequency = 1.0
        
        # Ajustar baseado no progresso
        daily_volume_ratio = self.daily_stats['volume'] / self.targets.daily_volume_target
        daily_trades_ratio = self.daily_stats['trades'] / self.targets.daily_trades_target
        
        # Se volume baixo, aumentar frequência
        if daily_volume_ratio < 0.5:
            base_frequency *= 2.0
        elif daily_volume_ratio < 0.8:
            base_frequency *= 1.5
        
        # Se poucos trades, aumentar frequência
        if daily_trades_ratio < 0.5:
            base_frequency *= 1.8
        elif daily_trades_ratio < 0.8:
            base_frequency *= 1.3
        
        # Ajustar baseado no tempo do dia
        current_hour = datetime.now().hour
        if current_hour >= 20:  # Após 20h, mais frequente
            base_frequency *= 1.5
        elif current_hour >= 16:  # Após 16h
            base_frequency *= 1.2
        
        return base_frequency
    
    def generate_airdrop_orders(self, current_price: float, orderbook, 
                               available_capital: float) -> List[Dict]:
        """Gera ordens otimizadas para airdrop farming"""
        orders = []
        
        # Calcular parâmetros ótimos
        base_size = (available_capital * 0.01) / current_price  # 1% do capital
        optimal_size = self.calculate_optimal_order_size(base_size, current_price)
        optimal_spread = self.calculate_optimal_spread(0.0005)  # 0.05% base
        
        # Calcular preços
        half_spread = optimal_spread / 2
        bid_price = current_price * (1 - half_spread)
        ask_price = current_price * (1 + half_spread)
        
        # Gerar múltiplas ordens para maximizar execuções
        num_orders = min(8, max(3, int(self.daily_stats['trades'] / 10 + 3)))
        
        # Ordens bid (compra)
        for i in range(num_orders):
            order_price = bid_price * (1 - i * 0.00005)  # Reduz preço gradualmente
            order_size = optimal_size * (0.9 ** i)  # Reduz tamanho gradualmente
            
            if order_price > 0 and order_size >= 0.01:
                orders.append({
                    'side': 'buy',
                    'price': order_price,
                    'quantity': order_size,
                    'type': 'limit',
                    'time_in_force': 'GTC',
                    'priority': 'airdrop_optimization'
                })
        
        # Ordens ask (venda)
        for i in range(num_orders):
            order_price = ask_price * (1 + i * 0.00005)  # Aumenta preço gradualmente
            order_size = optimal_size * (0.9 ** i)  # Reduz tamanho gradualmente
            
            if order_price > 0 and order_size >= 0.01:
                orders.append({
                    'side': 'sell',
                    'price': order_price,
                    'quantity': order_size,
                    'type': 'limit',
                    'time_in_force': 'GTC',
                    'priority': 'airdrop_optimization'
                })
        
        return orders
    
    def calculate_airdrop_score(self) -> float:
        """Calcula score atual de airdrop farming"""
        # Score de volume diário
        daily_volume_score = min(1.0, self.daily_stats['volume'] / self.targets.daily_volume_target)
        
        # Score de trades diários
        daily_trades_score = min(1.0, self.daily_stats['trades'] / self.targets.daily_trades_target)
        
        # Score de consistência
        consistency_score = 1.0
        if len(self.performance_history) >= 7:
            recent_performance = self.performance_history[-7:]
            volume_ratios = [p['volume_ratio'] for p in recent_performance]
            consistency_score = 1.0 - np.std(volume_ratios)  # Menor variância = maior consistência
        
        # Score geral
        overall_score = (daily_volume_score * 0.4 + daily_trades_score * 0.4 + consistency_score * 0.2)
        
        # Bônus de consistência
        if self.consistency_bonus_active:
            overall_score *= self.targets.consistency_bonus
        
        return min(1.0, overall_score)
    
    def get_airdrop_progress(self) -> Dict:
        """Retorna progresso detalhado do airdrop farming"""
        daily_volume_ratio = self.daily_stats['volume'] / self.targets.daily_volume_target
        daily_trades_ratio = self.daily_stats['trades'] / self.targets.daily_trades_target
        
        weekly_volume_ratio = self.weekly_stats['volume'] / self.targets.weekly_volume_target
        monthly_volume_ratio = self.monthly_stats['volume'] / self.targets.monthly_volume_target
        
        return {
            'daily': {
                'volume': self.daily_stats['volume'],
                'trades': self.daily_stats['trades'],
                'volume_ratio': daily_volume_ratio,
                'trades_ratio': daily_trades_ratio,
                'target_volume': self.targets.daily_volume_target,
                'target_trades': self.targets.daily_trades_target
            },
            'weekly': {
                'volume': self.weekly_stats['volume'],
                'trades': self.weekly_stats['trades'],
                'volume_ratio': weekly_volume_ratio,
                'target_volume': self.targets.weekly_volume_target
            },
            'monthly': {
                'volume': self.monthly_stats['volume'],
                'trades': self.monthly_stats['trades'],
                'volume_ratio': monthly_volume_ratio,
                'target_volume': self.targets.monthly_volume_target
            },
            'score': self.calculate_airdrop_score(),
            'optimizations': {
                'volume_boost': self.volume_boost_active,
                'trade_frequency_boost': self.trade_frequency_boost,
                'consistency_bonus': self.consistency_bonus_active
            }
        }
    
    def should_increase_aggressiveness(self) -> bool:
        """Determina se deve aumentar agressividade"""
        daily_volume_ratio = self.daily_stats['volume'] / self.targets.daily_volume_target
        daily_trades_ratio = self.daily_stats['trades'] / self.targets.daily_trades_target
        
        return daily_volume_ratio < 0.7 or daily_trades_ratio < 0.7
    
    def get_recommended_actions(self) -> List[str]:
        """Retorna ações recomendadas para otimizar airdrop farming"""
        actions = []
        
        daily_volume_ratio = self.daily_stats['volume'] / self.targets.daily_volume_target
        daily_trades_ratio = self.daily_stats['trades'] / self.targets.daily_trades_target
        
        if daily_volume_ratio < 0.5:
            actions.append("Aumentar tamanho das ordens em 50%")
        
        if daily_trades_ratio < 0.5:
            actions.append("Reduzir spread em 30%")
        
        if daily_volume_ratio < 0.8:
            actions.append("Aumentar frequência de trading")
        
        if daily_trades_ratio < 0.8:
            actions.append("Adicionar mais ordens por lado")
        
        if not self.consistency_bonus_active:
            actions.append("Focar em consistência diária")
        
        if not actions:
            actions.append("Manter estratégia atual")
        
        return actions