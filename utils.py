"""
Utility functions for Paradex Market Maker Bot
"""

import json
import logging
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config.json') -> Dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file {config_path} not found")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        raise


def save_config(config: Dict, config_path: str = 'config.json'):
    """Save configuration to JSON file"""
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    logger.info(f"Configuration saved to {config_path}")


def calculate_position_value(position_size: float, price: float) -> float:
    """Calculate USD value of a position"""
    return abs(position_size * price)


def calculate_required_margin(position_value: float, leverage: float = 1.0) -> float:
    """Calculate required margin for a position"""
    return position_value / leverage


def calculate_liquidation_price(entry_price: float, leverage: float, 
                                side: str, maintenance_margin: float = 0.05) -> float:
    """Calculate liquidation price for a position"""
    if side.upper() == 'LONG':
        return entry_price * (1 - (1 / leverage) + maintenance_margin)
    else:  # SHORT
        return entry_price * (1 + (1 / leverage) - maintenance_margin)


def calculate_pnl(entry_price: float, current_price: float, 
                 position_size: float) -> float:
    """Calculate unrealized PnL"""
    if position_size > 0:  # Long position
        return (current_price - entry_price) * position_size
    else:  # Short position
        return (entry_price - current_price) * abs(position_size)


def calculate_roi(pnl: float, initial_capital: float) -> float:
    """Calculate return on investment percentage"""
    return (pnl / initial_capital) * 100 if initial_capital > 0 else 0


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
    """Calculate Sharpe ratio for performance evaluation"""
    if not returns or len(returns) < 2:
        return 0.0
    
    import numpy as np
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    return np.mean(excess_returns) / np.std(excess_returns)


def format_number(num: float, decimals: int = 2) -> str:
    """Format number with thousand separators"""
    return f"{num:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage"""
    return f"{value:.{decimals}f}%"


def format_usd(value: float) -> str:
    """Format value as USD currency"""
    return f"${format_number(value, 2)}"


def parse_env_file(env_path: str = '.env') -> Dict[str, str]:
    """Parse .env file and return dictionary of values"""
    env_vars = {}
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        logger.warning(f".env file not found at {env_path}")
    
    return env_vars


def calculate_optimal_order_size(capital: float, num_levels: int, 
                                 max_position_pct: float = 0.5) -> float:
    """Calculate optimal order size given capital and number of levels"""
    max_position = capital * max_position_pct
    # Each side has num_levels orders
    total_levels = num_levels * 2
    # Account for different sizes at different levels (weighted average ~0.7)
    effective_levels = total_levels * 0.7
    
    return max_position / effective_levels


def estimate_daily_volume(order_size: float, refresh_interval: int, 
                         fill_rate: float = 0.7) -> float:
    """Estimate daily trading volume"""
    # Intervals per day
    intervals_per_day = (24 * 60 * 60) / refresh_interval
    # Average orders per interval (both sides)
    avg_orders_per_interval = 10  # Assuming 5 levels per side
    # Daily filled orders
    daily_fills = intervals_per_day * avg_orders_per_interval * fill_rate
    # Daily volume
    return daily_fills * order_size


def estimate_daily_pnl(daily_volume: float, avg_spread: float, 
                      costs_pct: float = 0.0002) -> float:
    """Estimate daily PnL from market making"""
    gross_pnl = daily_volume * avg_spread
    costs = daily_volume * costs_pct  # Trading fees/slippage
    return gross_pnl - costs


class PerformanceTracker:
    """Track and analyze bot performance"""
    
    def __init__(self):
        self.trades: List[Dict] = []
        self.daily_pnl: List[float] = []
        self.start_time = datetime.now()
        
    def add_trade(self, trade: Dict):
        """Add a trade to history"""
        trade['timestamp'] = datetime.now()
        self.trades.append(trade)
        
    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'total_volume': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'avg_trade_pnl': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
        
        total_volume = sum(t.get('volume', 0) for t in self.trades)
        total_pnl = sum(t.get('pnl', 0) for t in self.trades)
        winning_trades = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        
        pnl_series = [t.get('pnl', 0) for t in self.trades]
        cumulative_pnl = np.cumsum(pnl_series) if pnl_series else [0]
        max_drawdown = self._calculate_max_drawdown(cumulative_pnl)
        
        return {
            'total_trades': len(self.trades),
            'total_volume': total_volume,
            'total_pnl': total_pnl,
            'win_rate': (winning_trades / len(self.trades)) * 100,
            'avg_trade_pnl': total_pnl / len(self.trades),
            'sharpe_ratio': calculate_sharpe_ratio(pnl_series),
            'max_drawdown': max_drawdown,
            'runtime_hours': (datetime.now() - self.start_time).total_seconds() / 3600
        }
    
    def _calculate_max_drawdown(self, cumulative_pnl: List[float]) -> float:
        """Calculate maximum drawdown from cumulative PnL"""
        if not cumulative_pnl:
            return 0.0
        
        peak = cumulative_pnl[0]
        max_dd = 0.0
        
        for value in cumulative_pnl:
            if value > peak:
                peak = value
            drawdown = peak - value
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def export_to_json(self, filename: str = 'performance.json'):
        """Export performance data to JSON"""
        data = {
            'metrics': self.calculate_metrics(),
            'trades': self.trades,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Performance data exported to {filename}")


def validate_config(config: Dict) -> bool:
    """Validate configuration parameters"""
    required_fields = ['api_key', 'api_secret', 'market', 'base_spread', 
                      'order_size_usd', 'max_position_usd']
    
    for field in required_fields:
        if field not in config:
            logger.error(f"Missing required config field: {field}")
            return False
    
    # Validate numeric ranges
    if config['base_spread'] <= 0 or config['base_spread'] > 0.1:
        logger.error("base_spread must be between 0 and 0.1 (10%)")
        return False
    
    if config['order_size_usd'] <= 0:
        logger.error("order_size_usd must be positive")
        return False
    
    if config['max_position_usd'] <= 0:
        logger.error("max_position_usd must be positive")
        return False
    
    return True


if __name__ == "__main__":
    # Example usage
    config = load_config()
    
    if validate_config(config):
        print("✓ Configuration valid")
        
        # Calculate optimal parameters
        capital = 5000
        optimal_size = calculate_optimal_order_size(capital, 5)
        print(f"Optimal order size: ${optimal_size:.2f}")
        
        # Estimate performance
        daily_volume = estimate_daily_volume(optimal_size, 30)
        print(f"Estimated daily volume: ${daily_volume:.2f}")
        
        daily_pnl = estimate_daily_pnl(daily_volume, 0.0015)
        print(f"Estimated daily PnL: ${daily_pnl:.2f}")
