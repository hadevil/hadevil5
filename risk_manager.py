"""
Sistema de Gestão de Risco para Market Making
Otimizado para capital limitado e foco em airdrop farming
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np

from config import TRADING_CONFIG, SECURITY_CONFIG, MONITORING_CONFIG

@dataclass
class RiskMetrics:
    """Métricas de risco atuais"""
    current_pnl: float
    daily_pnl: float
    max_drawdown: float
    current_drawdown: float
    position_size: float
    exposure: float
    daily_volume: float
    trade_count: int
    win_rate: float
    avg_trade_size: float

class RiskManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.initial_capital = TRADING_CONFIG['total_capital']
        self.max_daily_loss = TRADING_CONFIG['max_daily_loss']
        self.risk_per_trade = TRADING_CONFIG['risk_per_trade']
        self.max_position_size = TRADING_CONFIG['max_position_size']
        
        # Estado do risco
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.peak_capital = self.initial_capital
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        self.daily_trades = 0
        self.daily_volume = 0.0
        self.winning_trades = 0
        self.total_trades = 0
        self.trade_history = []
        self.last_reset_date = datetime.now().date()
        
        # Circuit breaker
        self.consecutive_losses = 0
        self.circuit_breaker_active = False
        self.circuit_breaker_end_time = None
        
        # Alertas
        self.alert_thresholds = MONITORING_CONFIG['alert_thresholds']
        
    def reset_daily_metrics(self):
        """Reseta métricas diárias"""
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.daily_volume = 0.0
            self.last_reset_date = current_date
            self.logger.info("Métricas diárias resetadas")
    
    def update_trade(self, trade_data: Dict):
        """Atualiza métricas após uma trade"""
        self.reset_daily_metrics()
        
        # Atualizar PnL
        trade_pnl = trade_data.get('pnl', 0.0)
        self.daily_pnl += trade_pnl
        self.total_pnl += trade_pnl
        
        # Atualizar volume e contadores
        self.daily_volume += trade_data.get('volume', 0.0)
        self.daily_trades += 1
        self.total_trades += 1
        
        # Atualizar win rate
        if trade_pnl > 0:
            self.winning_trades += 1
        
        # Atualizar drawdown
        current_capital = self.initial_capital + self.total_pnl
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
            self.current_drawdown = 0.0
        else:
            self.current_drawdown = (self.peak_capital - current_capital) / self.peak_capital
            if self.current_drawdown > self.max_drawdown:
                self.max_drawdown = self.current_drawdown
        
        # Atualizar consecutive losses
        if trade_pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Adicionar ao histórico
        self.trade_history.append({
            'timestamp': datetime.now(),
            'pnl': trade_pnl,
            'volume': trade_data.get('volume', 0.0),
            'price': trade_data.get('price', 0.0),
            'quantity': trade_data.get('quantity', 0.0)
        })
        
        # Manter apenas últimos 1000 trades
        if len(self.trade_history) > 1000:
            self.trade_history = self.trade_history[-1000:]
        
        self.logger.debug(f"Trade atualizada: PnL={trade_pnl:.4f}, Total PnL={self.total_pnl:.4f}")
    
    def check_circuit_breaker(self) -> bool:
        """Verifica se circuit breaker deve ser ativado"""
        # Verificar consecutive losses
        if self.consecutive_losses >= SECURITY_CONFIG['circuit_breaker_threshold']:
            self.activate_circuit_breaker("Muitas perdas consecutivas")
            return True
        
        # Verificar drawdown máximo
        if self.current_drawdown > self.alert_thresholds['max_drawdown']:
            self.activate_circuit_breaker("Drawdown máximo excedido")
            return True
        
        # Verificar perda diária máxima
        if self.daily_pnl < -self.max_daily_loss * self.initial_capital:
            self.activate_circuit_breaker("Perda diária máxima excedida")
            return True
        
        return False
    
    def activate_circuit_breaker(self, reason: str):
        """Ativa circuit breaker"""
        self.circuit_breaker_active = True
        self.circuit_breaker_end_time = datetime.now() + timedelta(minutes=30)
        self.logger.warning(f"Circuit breaker ativado: {reason}")
    
    def check_circuit_breaker_reset(self) -> bool:
        """Verifica se circuit breaker deve ser resetado"""
        if self.circuit_breaker_active and self.circuit_breaker_end_time:
            if datetime.now() >= self.circuit_breaker_end_time:
                self.circuit_breaker_active = False
                self.circuit_breaker_end_time = None
                self.consecutive_losses = 0
                self.logger.info("Circuit breaker resetado")
                return True
        return False
    
    def calculate_position_size(self, current_price: float, volatility: float) -> float:
        """Calcula tamanho de posição baseado no risco"""
        if self.circuit_breaker_active:
            return 0.0
        
        # Tamanho base baseado no capital
        base_size = (self.initial_capital * self.risk_per_trade) / current_price
        
        # Ajustar baseado no drawdown atual
        drawdown_multiplier = max(0.1, 1 - self.current_drawdown * 2)
        
        # Ajustar baseado na volatilidade
        volatility_multiplier = max(0.2, 1 - volatility * 10)
        
        # Ajustar baseado no PnL diário
        daily_pnl_ratio = self.daily_pnl / (self.initial_capital * self.max_daily_loss)
        pnl_multiplier = max(0.1, 1 - abs(daily_pnl_ratio))
        
        # Tamanho final
        adjusted_size = base_size * drawdown_multiplier * volatility_multiplier * pnl_multiplier
        
        # Aplicar limites
        max_size = min(
            self.max_position_size,
            (self.initial_capital * 0.1) / current_price  # Máximo 10% do capital
        )
        
        return min(adjusted_size, max_size)
    
    def calculate_max_order_size(self, current_price: float) -> float:
        """Calcula tamanho máximo de ordem individual"""
        position_size = self.calculate_position_size(current_price, 0.02)  # Assumir 2% de volatilidade
        return min(position_size, TRADING_CONFIG['max_order_size'])
    
    def should_place_order(self, order_side: str, order_price: float, 
                          order_quantity: float, current_price: float) -> bool:
        """Determina se uma ordem deve ser colocada"""
        # Verificar circuit breaker
        if self.circuit_breaker_active:
            return False
        
        # Verificar limites de posição
        if order_side == 'buy':
            current_exposure = self.get_current_exposure()
            new_exposure = current_exposure + (order_price * order_quantity)
            max_exposure = self.initial_capital * 0.5  # Máximo 50% do capital em exposição
            if new_exposure > max_exposure:
                return False
        
        # Verificar tamanho mínimo
        if order_quantity < TRADING_CONFIG['min_order_size']:
            return False
        
        # Verificar se não excede perda diária máxima
        if self.daily_pnl < -self.max_daily_loss * self.initial_capital * 0.8:
            return False
        
        return True
    
    def get_current_exposure(self) -> float:
        """Calcula exposição atual"""
        # Simplificado - em implementação real, calcularia baseado nas posições abertas
        return abs(self.daily_pnl)
    
    def get_risk_metrics(self) -> RiskMetrics:
        """Retorna métricas de risco atuais"""
        win_rate = (self.winning_trades / self.total_trades) if self.total_trades > 0 else 0.0
        avg_trade_size = (self.daily_volume / self.daily_trades) if self.daily_trades > 0 else 0.0
        
        return RiskMetrics(
            current_pnl=self.total_pnl,
            daily_pnl=self.daily_pnl,
            max_drawdown=self.max_drawdown,
            current_drawdown=self.current_drawdown,
            position_size=self.get_current_exposure(),
            exposure=self.get_current_exposure(),
            daily_volume=self.daily_volume,
            trade_count=self.daily_trades,
            win_rate=win_rate,
            avg_trade_size=avg_trade_size
        )
    
    def get_risk_alerts(self) -> List[str]:
        """Retorna alertas de risco ativos"""
        alerts = []
        
        if self.circuit_breaker_active:
            alerts.append("Circuit breaker ativo")
        
        if self.current_drawdown > self.alert_thresholds['max_drawdown']:
            alerts.append(f"Drawdown alto: {self.current_drawdown:.2%}")
        
        if self.daily_pnl < -self.max_daily_loss * self.initial_capital * 0.5:
            alerts.append(f"Perda diária alta: {self.daily_pnl:.2f}")
        
        if self.consecutive_losses >= 3:
            alerts.append(f"Muitas perdas consecutivas: {self.consecutive_losses}")
        
        return alerts
    
    def get_airdrop_progress(self) -> Dict:
        """Retorna progresso para airdrop farming"""
        return {
            'daily_volume': self.daily_volume,
            'daily_trades': self.daily_trades,
            'target_volume': TRADING_CONFIG['total_capital'] * 0.2,  # 20% do capital por dia
            'target_trades': 50,
            'volume_progress': min(1.0, self.daily_volume / (TRADING_CONFIG['total_capital'] * 0.2)),
            'trades_progress': min(1.0, self.daily_trades / 50),
            'is_on_track': self.daily_volume >= TRADING_CONFIG['total_capital'] * 0.1 and self.daily_trades >= 25
        }
    
    def should_stop_trading(self) -> bool:
        """Determina se deve parar de fazer trading"""
        return (
            self.circuit_breaker_active or
            self.daily_pnl < -self.max_daily_loss * self.initial_capital or
            self.current_drawdown > self.alert_thresholds['max_drawdown']
        )
    
    def get_recommended_actions(self) -> List[str]:
        """Retorna ações recomendadas baseadas no estado atual"""
        actions = []
        
        if self.circuit_breaker_active:
            actions.append("Aguardar reset do circuit breaker")
        elif self.current_drawdown > 0.02:
            actions.append("Reduzir tamanho das posições")
        elif self.daily_pnl < -self.max_daily_loss * self.initial_capital * 0.5:
            actions.append("Aumentar spread para reduzir risco")
        elif self.consecutive_losses >= 2:
            actions.append("Pausar por alguns minutos")
        else:
            actions.append("Continuar trading normal")
        
        return actions