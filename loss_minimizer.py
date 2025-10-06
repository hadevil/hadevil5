"""
Sistema Avançado de Minimização de Perdas
Foco em proteger capital e maximizar eficiência
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

@dataclass
class LossMetrics:
    """Métricas de perda e proteção"""
    max_loss_per_trade: float = 0.0
    max_daily_loss: float = 0.0
    current_drawdown: float = 0.0
    consecutive_losses: int = 0
    recovery_factor: float = 1.0
    capital_efficiency: float = 1.0

class LossMinimizer:
    def __init__(self, initial_capital: float = 5000):
        self.initial_capital = initial_capital
        self.logger = logging.getLogger(__name__)
        
        # Limites de perda
        self.max_loss_per_trade = initial_capital * 0.005  # 0.5% por trade
        self.max_daily_loss = initial_capital * 0.02      # 2% por dia
        self.max_weekly_loss = initial_capital * 0.05     # 5% por semana
        
        # Estado atual
        self.current_capital = initial_capital
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.peak_capital = initial_capital
        self.trade_count = 0
        self.loss_count = 0
        
        # Histórico de perdas
        self.loss_history = []
        self.recovery_history = []
        
        # Controles dinâmicos
        self.position_size_multiplier = 1.0
        self.spread_multiplier = 1.0
        self.trading_frequency_multiplier = 1.0
        
    def update_trade_result(self, trade_data: Dict):
        """Atualiza resultado de uma trade"""
        pnl = trade_data.get('pnl', 0.0)
        volume = trade_data.get('volume', 0.0)
        
        # Atualizar capital
        self.current_capital += pnl
        self.daily_pnl += pnl
        self.weekly_pnl += pnl
        
        # Atualizar contadores
        self.trade_count += 1
        if pnl < 0:
            self.loss_count += 1
            self.loss_history.append({
                'timestamp': datetime.now(),
                'pnl': pnl,
                'volume': volume,
                'capital_after': self.current_capital
            })
        else:
            # Reset consecutive losses
            self.consecutive_losses = 0
        
        # Atualizar peak capital
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
        
        # Calcular drawdown
        self.current_drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        
        # Ajustar controles dinâmicos
        self._adjust_controls()
        
        self.logger.debug(f"Trade atualizada: PnL={pnl:.4f}, Capital={self.current_capital:.2f}")
    
    def _adjust_controls(self):
        """Ajusta controles dinâmicos baseado no desempenho"""
        # Ajustar tamanho de posição baseado no drawdown
        if self.current_drawdown > 0.01:  # 1% de drawdown
            self.position_size_multiplier = max(0.3, 1 - self.current_drawdown * 2)
        else:
            self.position_size_multiplier = min(1.0, 1 + (0.01 - self.current_drawdown) * 0.5)
        
        # Ajustar spread baseado em perdas consecutivas
        if self.consecutive_losses > 2:
            self.spread_multiplier = min(2.0, 1 + self.consecutive_losses * 0.2)
        else:
            self.spread_multiplier = max(0.8, 1 - self.consecutive_losses * 0.1)
        
        # Ajustar frequência baseado no PnL diário
        daily_loss_ratio = abs(self.daily_pnl) / self.max_daily_loss
        if daily_loss_ratio > 0.5:
            self.trading_frequency_multiplier = max(0.5, 1 - daily_loss_ratio)
        else:
            self.trading_frequency_multiplier = min(1.2, 1 + (0.5 - daily_loss_ratio) * 0.4)
    
    def calculate_safe_position_size(self, base_size: float, current_price: float) -> float:
        """Calcula tamanho seguro de posição"""
        # Tamanho base ajustado pelos controles
        adjusted_size = base_size * self.position_size_multiplier
        
        # Limite baseado no capital atual
        max_size_by_capital = (self.current_capital * 0.01) / current_price  # 1% do capital
        
        # Limite baseado no drawdown
        if self.current_drawdown > 0.02:  # 2% de drawdown
            max_size_by_drawdown = (self.current_capital * 0.005) / current_price  # 0.5% do capital
        else:
            max_size_by_drawdown = (self.current_capital * 0.02) / current_price  # 2% do capital
        
        # Usar o menor limite
        max_safe_size = min(max_size_by_capital, max_size_by_drawdown)
        
        return min(adjusted_size, max_safe_size)
    
    def calculate_safe_spread(self, base_spread: float) -> float:
        """Calcula spread seguro"""
        return base_spread * self.spread_multiplier
    
    def should_place_order(self, order_data: Dict) -> bool:
        """Determina se uma ordem deve ser colocada"""
        # Verificar limites de perda diária
        if self.daily_pnl < -self.max_daily_loss:
            self.logger.warning("Limite de perda diária atingido")
            return False
        
        # Verificar limites de perda semanal
        if self.weekly_pnl < -self.max_weekly_loss:
            self.logger.warning("Limite de perda semanal atingido")
            return False
        
        # Verificar drawdown máximo
        if self.current_drawdown > 0.05:  # 5% de drawdown máximo
            self.logger.warning("Drawdown máximo atingido")
            return False
        
        # Verificar perdas consecutivas
        if self.consecutive_losses > 5:
            self.logger.warning("Muitas perdas consecutivas")
            return False
        
        # Verificar frequência de trading
        if self.trading_frequency_multiplier < 0.3:
            self.logger.warning("Frequência de trading muito baixa")
            return False
        
        return True
    
    def calculate_emergency_exit_orders(self, current_price: float, 
                                      current_inventory: float) -> List[Dict]:
        """Calcula ordens de saída de emergência"""
        if abs(current_inventory) < 0.01:
            return []
        
        orders = []
        
        # Se inventário positivo, vender imediatamente
        if current_inventory > 0:
            orders.append({
                'side': 'sell',
                'price': current_price * 0.995,  # 0.5% abaixo do preço atual
                'quantity': current_inventory,
                'type': 'market',
                'time_in_force': 'IOC',
                'priority': 'emergency_exit'
            })
        
        # Se inventário negativo, comprar imediatamente
        elif current_inventory < 0:
            orders.append({
                'side': 'buy',
                'price': current_price * 1.005,  # 0.5% acima do preço atual
                'quantity': abs(current_inventory),
                'type': 'market',
                'time_in_force': 'IOC',
                'priority': 'emergency_exit'
            })
        
        return orders
    
    def calculate_hedge_orders(self, current_price: float, 
                              current_inventory: float) -> List[Dict]:
        """Calcula ordens de hedge para proteger posições"""
        if abs(current_inventory) < 0.1:
            return []
        
        orders = []
        hedge_ratio = 0.7  # Hedge 70% do inventário
        
        # Hedge para inventário positivo
        if current_inventory > 0:
            hedge_quantity = current_inventory * hedge_ratio
            orders.append({
                'side': 'sell',
                'price': current_price * 0.999,  # Ligeiramente abaixo
                'quantity': hedge_quantity,
                'type': 'limit',
                'time_in_force': 'GTC',
                'priority': 'hedge'
            })
        
        # Hedge para inventário negativo
        elif current_inventory < 0:
            hedge_quantity = abs(current_inventory) * hedge_ratio
            orders.append({
                'side': 'buy',
                'price': current_price * 1.001,  # Ligeiramente acima
                'quantity': hedge_quantity,
                'type': 'limit',
                'time_in_force': 'GTC',
                'priority': 'hedge'
            })
        
        return orders
    
    def calculate_recovery_strategy(self) -> Dict:
        """Calcula estratégia de recuperação após perdas"""
        if self.current_drawdown < 0.01:  # Menos de 1% de drawdown
            return {'action': 'normal', 'multiplier': 1.0}
        
        # Estratégia conservadora para recuperação
        if self.current_drawdown < 0.03:  # 1-3% de drawdown
            return {
                'action': 'conservative',
                'multiplier': 0.7,
                'spread_increase': 1.2,
                'position_reduction': 0.8
            }
        
        # Estratégia muito conservadora para recuperação
        elif self.current_drawdown < 0.05:  # 3-5% de drawdown
            return {
                'action': 'very_conservative',
                'multiplier': 0.5,
                'spread_increase': 1.5,
                'position_reduction': 0.6
            }
        
        # Estratégia de emergência
        else:
            return {
                'action': 'emergency',
                'multiplier': 0.2,
                'spread_increase': 2.0,
                'position_reduction': 0.3
            }
    
    def get_loss_metrics(self) -> LossMetrics:
        """Retorna métricas de perda atuais"""
        return LossMetrics(
            max_loss_per_trade=self.max_loss_per_trade,
            max_daily_loss=self.max_daily_loss,
            current_drawdown=self.current_drawdown,
            consecutive_losses=self.consecutive_losses,
            recovery_factor=self.position_size_multiplier,
            capital_efficiency=self.current_capital / self.initial_capital
        )
    
    def should_stop_trading(self) -> bool:
        """Determina se deve parar de fazer trading"""
        return (
            self.daily_pnl < -self.max_daily_loss or
            self.weekly_pnl < -self.max_weekly_loss or
            self.current_drawdown > 0.05 or
            self.consecutive_losses > 7
        )
    
    def get_recommended_actions(self) -> List[str]:
        """Retorna ações recomendadas baseadas no estado atual"""
        actions = []
        
        if self.current_drawdown > 0.03:
            actions.append("Reduzir tamanho das posições em 50%")
        
        if self.consecutive_losses > 3:
            actions.append("Aumentar spread em 20%")
        
        if self.daily_pnl < -self.max_daily_loss * 0.5:
            actions.append("Pausar trading por 1 hora")
        
        if self.current_drawdown > 0.02:
            actions.append("Ativar ordens de hedge")
        
        if self.trading_frequency_multiplier < 0.5:
            actions.append("Reduzir frequência de trading")
        
        if not actions:
            actions.append("Continuar trading normal")
        
        return actions
    
    def reset_daily_metrics(self):
        """Reseta métricas diárias"""
        self.daily_pnl = 0.0
        self.trade_count = 0
        self.loss_count = 0
    
    def reset_weekly_metrics(self):
        """Reseta métricas semanais"""
        self.weekly_pnl = 0.0