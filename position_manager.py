"""
Position Manager
Manages trading positions, calculates PnL, and monitors exit conditions
"""

import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PositionManager:
    """Manages open positions and tracks PnL"""
    
    def __init__(self, config: Dict, apex_client):
        """
        Initialize position manager
        
        Args:
            config: Configuration dictionary
            apex_client: ApexClient instance
        """
        self.config = config
        self.apex_client = apex_client
        
        # Exit conditions
        self.stop_loss = float(config['STOP_LOSS_USD'])
        self.take_profit = float(config['TAKE_PROFIT_USD'])
        self.time_limit = int(config['TIME_LIMIT_MINUTES'])
        
        # Tracking
        self.cycle_start_time = None
        self.closed_positions = []  # Track recently closed positions
        
        logger.info(f"📊 Position Manager initialized")
        logger.info(f"   SL: ${self.stop_loss:.2f} | TP: ${self.take_profit:.2f} | Time: {self.time_limit}min")
    
    def start_new_cycle(self):
        """Mark the start of a new trading cycle"""
        self.cycle_start_time = datetime.now()
        self.closed_positions = []
        logger.info(f"🔄 New cycle started at {self.cycle_start_time.strftime('%H:%M:%S')}")
    
    def get_time_elapsed(self) -> int:
        """
        Get minutes elapsed since cycle start
        
        Returns:
            Minutes elapsed
        """
        if not self.cycle_start_time:
            return 0
        
        elapsed = datetime.now() - self.cycle_start_time
        return int(elapsed.total_seconds() / 60)
    
    def calculate_total_pnl(self, positions: List[Dict]) -> float:
        """
        Calculate total unrealized PnL from all positions
        
        Args:
            positions: List of position dictionaries
            
        Returns:
            Total PnL in USD
        """
        total_pnl = 0.0
        
        for pos in positions:
            unrealized_pnl = float(pos.get('unrealizedPnl', 0))
            total_pnl += unrealized_pnl
        
        return total_pnl
    
    def check_exit_conditions(self, positions: List[Dict]) -> tuple[bool, str]:
        """
        Check if exit conditions are met (SL, TP, or Time)
        
        Args:
            positions: List of open positions
            
        Returns:
            Tuple of (should_exit, reason)
        """
        # Check if no positions (shouldn't happen, but handle it)
        if not positions:
            return False, "No positions open"
        
        # Calculate total PnL
        total_pnl = self.calculate_total_pnl(positions)
        
        # Check Stop Loss
        if total_pnl <= self.stop_loss:
            logger.warning(f"🛑 STOP LOSS HIT: PnL ${total_pnl:.2f} <= ${self.stop_loss:.2f}")
            return True, "STOP_LOSS"
        
        # Check Take Profit
        if total_pnl >= self.take_profit:
            logger.info(f"🎯 TAKE PROFIT HIT: PnL ${total_pnl:.2f} >= ${self.take_profit:.2f}")
            return True, "TAKE_PROFIT"
        
        # Check Time Limit
        elapsed = self.get_time_elapsed()
        if elapsed >= self.time_limit:
            logger.info(f"⏰ TIME LIMIT HIT: {elapsed}min >= {self.time_limit}min")
            return True, "TIME_LIMIT"
        
        return False, "ACTIVE"
    
    def get_position_summary(self, positions: List[Dict]) -> Dict:
        """
        Get summary of all positions
        
        Args:
            positions: List of positions
            
        Returns:
            Dictionary with summary data
        """
        if not positions:
            return {
                'count': 0,
                'total_pnl': 0.0,
                'positions': []
            }
        
        summary = {
            'count': len(positions),
            'total_pnl': self.calculate_total_pnl(positions),
            'time_elapsed': self.get_time_elapsed(),
            'time_remaining': max(0, self.time_limit - self.get_time_elapsed()),
            'positions': []
        }
        
        for pos in positions:
            pos_info = {
                'symbol': pos['symbol'],
                'side': pos['side'],
                'size': pos['size'],
                'entry_price': float(pos.get('entryPrice', 0)),
                'mark_price': float(pos.get('markPrice', 0)),
                'unrealized_pnl': float(pos.get('unrealizedPnl', 0)),
                'realized_pnl': float(pos.get('realizedPnl', 0)),
            }
            summary['positions'].append(pos_info)
        
        return summary
    
    def add_closed_position(self, position: Dict, close_reason: str, final_pnl: float):
        """
        Track a closed position
        
        Args:
            position: Position that was closed
            close_reason: Reason for closing (SL, TP, TIME_LIMIT)
            final_pnl: Final PnL of the position
        """
        closed_info = {
            'symbol': position['symbol'],
            'side': position['side'],
            'size': position['size'],
            'entry_price': float(position.get('entryPrice', 0)),
            'pnl': final_pnl,
            'reason': close_reason,
            'closed_at': datetime.now(),
            'duration_minutes': self.get_time_elapsed()
        }
        
        self.closed_positions.append(closed_info)
    
    def get_recent_closes(self, minutes: int = 5) -> List[Dict]:
        """
        Get positions closed in the last N minutes
        
        Args:
            minutes: Look back period
            
        Returns:
            List of closed positions
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        recent = [
            pos for pos in self.closed_positions
            if pos['closed_at'] >= cutoff
        ]
        
        return recent
    
    def format_status_report(self, positions: List[Dict]) -> str:
        """
        Format a human-readable status report
        
        Args:
            positions: Current positions
            
        Returns:
            Formatted string
        """
        summary = self.get_position_summary(positions)
        recent_closes = self.get_recent_closes(5)
        
        lines = []
        lines.append("=" * 60)
        lines.append(f"📊 STATUS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        
        # Open positions
        if summary['count'] > 0:
            lines.append(f"\n🔓 OPEN POSITIONS ({summary['count']}):")
            lines.append("-" * 60)
            
            for pos in summary['positions']:
                side_emoji = "🟢" if pos['side'] == "LONG" else "🔴"
                pnl_emoji = "📈" if pos['unrealized_pnl'] >= 0 else "📉"
                
                lines.append(
                    f"{side_emoji} {pos['symbol']} {pos['side']:<5} | "
                    f"Entry: ${pos['entry_price']:>8.2f} | "
                    f"Mark: ${pos['mark_price']:>8.2f} | "
                    f"{pnl_emoji} PnL: ${pos['unrealized_pnl']:>+8.2f}"
                )
            
            lines.append("-" * 60)
            pnl_emoji = "📈" if summary['total_pnl'] >= 0 else "📉"
            lines.append(
                f"{pnl_emoji} TOTAL PnL: ${summary['total_pnl']:>+.2f} | "
                f"Time: {summary['time_elapsed']}/{self.time_limit}min | "
                f"Target: TP=${self.take_profit:+.0f} SL=${self.stop_loss:+.0f}"
            )
        else:
            lines.append("\n🔓 OPEN POSITIONS: None")
        
        # Recent closes
        if recent_closes:
            lines.append(f"\n🔒 CLOSED (last 5min): {len(recent_closes)}")
            lines.append("-" * 60)
            
            for closed in recent_closes:
                reason_emoji = {
                    'STOP_LOSS': '🛑',
                    'TAKE_PROFIT': '🎯',
                    'TIME_LIMIT': '⏰'
                }.get(closed['reason'], '📍')
                
                pnl_emoji = "✅" if closed['pnl'] >= 0 else "❌"
                
                lines.append(
                    f"{reason_emoji} {closed['symbol']} {closed['side']:<5} | "
                    f"{pnl_emoji} PnL: ${closed['pnl']:>+8.2f} | "
                    f"Duration: {closed['duration_minutes']}min | "
                    f"Reason: {closed['reason']}"
                )
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
