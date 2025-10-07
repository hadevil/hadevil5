"""
Módulo de gerenciamento de risco para o bot de market maker
Otimizado para cenários de pouco capital e farming de airdrop
"""

import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class Position:
    """Representa uma posição de trading"""
    symbol: str
    side: str  # 'BUY' ou 'SELL'
    size: float
    entry_price: float
    timestamp: datetime
    order_id: str

    @property
    def value_usd(self) -> float:
        return self.size * self.entry_price


@dataclass
class RiskMetrics:
    """Métricas de risco calculadas"""
    total_exposure: float
    ltv_percentage: float
    unrealized_pnl: float
    max_drawdown: float
    daily_volume: float


class RiskManager:
    """Gerenciador de risco avançado"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.positions: List[Position] = []
        self.daily_volume = 0.0
        self.peak_balance = 0.0
        self.start_time = datetime.now()

    def can_open_position(self, symbol: str, size: float, price: float) -> bool:
        """Verifica se pode abrir uma nova posição baseado nos limites de risco"""

        # Verifica exposição máxima
        current_exposure = sum(pos.value_usd for pos in self.positions)
        new_exposure = size * price
        max_exposure = self.config['trading']['max_leverage'] * 5000  # Base capital

        if current_exposure + new_exposure > max_exposure:
            self.logger.warning(f"❌ Exposição máxima atingida: ${current_exposure + new_exposure".2f"} > ${max_exposure:.".2f")
            return False

        # Verifica número máximo de posições
        max_positions = self.config['risk_management']['max_positions_per_cycle']
        if len(self.positions) >= max_positions:
            self.logger.warning(f"❌ Número máximo de posições atingido: {len(self.positions)} >= {max_positions}")
            return False

        # Verifica volume diário
        if self.daily_volume >= self.config['risk_management']['max_daily_volume_usd']:
            self.logger.warning(f"❌ Volume diário máximo atingido: ${self.daily_volume".2f"}")
            return False

        return True

    def add_position(self, position: Position):
        """Adiciona uma nova posição"""
        self.positions.append(position)
        self.logger.info(f"📈 Posição adicionada: {position.side} {position.size} {position.symbol} @ ${position.entry_price}")

    def close_position(self, order_id: str) -> Optional[Position]:
        """Fecha uma posição específica"""
        for i, pos in enumerate(self.positions):
            if pos.order_id == order_id:
                closed_position = self.positions.pop(i)
                pnl = self._calculate_pnl(closed_position)
                self.logger.info(f"🔒 Posição fechada: {closed_position.symbol} | PnL: ${pnl".2f"}")
                return closed_position
        return None

    def _calculate_pnl(self, position: Position, current_price: Optional[float] = None) -> float:
        """Calcula PnL de uma posição"""
        # Em produção, isso usaria o preço atual real
        current_price = current_price or (position.entry_price * (1 + random.uniform(-0.02, 0.02)))

        if position.side == 'BUY':
            return (current_price - position.entry_price) * position.size
        else:  # SELL
            return (position.entry_price - current_price) * position.size

    def check_stop_loss_take_profit(self) -> List[str]:
        """Verifica se alguma posição deve ser fechada por stop loss ou take profit"""
        positions_to_close = []
        stop_loss_pct = self.config['risk_management']['stop_loss_percentage'] / 100
        take_profit_pct = self.config['risk_management']['take_profit_percentage'] / 100

        for position in self.positions:
            # Simula preço atual (em produção seria preço real)
            current_price = position.entry_price * (1 + random.uniform(-0.05, 0.05))

            if position.side == 'BUY':
                pnl_pct = (current_price - position.entry_price) / position.entry_price
            else:
                pnl_pct = (position.entry_price - current_price) / position.entry_price

            if pnl_pct <= -stop_loss_pct:
                positions_to_close.append(position.order_id)
                self.logger.warning(f"🛑 Stop Loss ativado: {position.symbol} {pnl_pct*100".1f"}%")
            elif pnl_pct >= take_profit_pct:
                positions_to_close.append(position.order_id)
                self.logger.info(f"💰 Take Profit ativado: {position.symbol} {pnl_pct*100:.".1f"")

        return positions_to_close

    def get_risk_metrics(self) -> RiskMetrics:
        """Calcula métricas de risco atuais"""
        total_exposure = sum(pos.value_usd for pos in self.positions)

        # Calcula LTV (simplificado)
        base_capital = 5000
        ltv_percentage = (total_exposure / base_capital) * 100 if base_capital > 0 else 0

        # Calcula PnL não realizado
        unrealized_pnl = sum(self._calculate_pnl(pos) for pos in self.positions)

        # Calcula drawdown máximo (simplificado)
        current_balance = base_capital + unrealized_pnl
        self.peak_balance = max(self.peak_balance, current_balance)
        max_drawdown = ((self.peak_balance - current_balance) / self.peak_balance) * 100 if self.peak_balance > 0 else 0

        return RiskMetrics(
            total_exposure=total_exposure,
            ltv_percentage=ltv_percentage,
            unrealized_pnl=unrealized_pnl,
            max_drawdown=max_drawdown,
            daily_volume=self.daily_volume
        )

    def reset_daily_volume(self):
        """Reseta volume diário se passou 24h"""
        if datetime.now() - self.start_time > timedelta(days=1):
            self.daily_volume = 0.0
            self.start_time = datetime.now()
            self.logger.info("🔄 Volume diário resetado")

    def get_portfolio_summary(self) -> Dict:
        """Retorna resumo do portfólio"""
        metrics = self.get_risk_metrics()

        return {
            'total_positions': len(self.positions),
            'total_exposure_usd': metrics.total_exposure,
            'ltv_percentage': metrics.ltv_percentage,
            'unrealized_pnl_usd': metrics.unrealized_pnl,
            'daily_volume_usd': metrics.daily_volume,
            'max_drawdown_pct': metrics.max_drawdown,
            'positions': [
                {
                    'symbol': pos.symbol,
                    'side': pos.side,
                    'size': pos.size,
                    'entry_price': pos.entry_price,
                    'value_usd': pos.value_usd,
                    'age_minutes': (datetime.now() - pos.timestamp).total_seconds() / 60
                }
                for pos in self.positions
            ]
        }