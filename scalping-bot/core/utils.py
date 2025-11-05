"""
Utility functions for the trading bot
"""

import logging
from datetime import datetime
from typing import Dict, Optional


logger = logging.getLogger(__name__)


def normalize_symbol(symbol: str) -> str:
    """
    Normalize symbol format to ApeX format (BTC-USDT)
    
    Args:
        symbol: Symbol like 'BTCUSDT' or 'BTC-USDT'
        
    Returns:
        Normalized symbol with hyphen
    """
    symbol = symbol.upper().strip()
    
    # Already has hyphen
    if '-' in symbol:
        return symbol
    
    # Add hyphen before USDT
    if symbol.endswith('USDT'):
        base = symbol[:-4]
        return f"{base}-USDT"
    
    return symbol


def calculate_quantity(order_value_usd: float, entry_price: float, 
                       min_size: float = 0.001, step_size: float = 0.001) -> float:
    """
    Calculate order quantity based on USD value
    
    Args:
        order_value_usd: Value in USD to trade
        entry_price: Entry price
        min_size: Minimum order size
        step_size: Size increment
        
    Returns:
        Quantity rounded to step size
    """
    qty = order_value_usd / entry_price
    
    # Round to step size
    qty = round(qty / step_size) * step_size
    
    # Ensure minimum
    if qty < min_size:
        logger.warning(f"Calculated qty {qty} < min_size {min_size}, using min_size")
        qty = min_size
    
    return qty


def calculate_pnl(entry_price: float, exit_price: float, quantity: float, 
                  side: str, fee_rate: float = 0.0005) -> Dict[str, float]:
    """
    Calculate PnL for a trade
    
    Args:
        entry_price: Entry price
        exit_price: Exit price
        quantity: Position size
        side: 'LONG' or 'SHORT'
        fee_rate: Taker fee rate
        
    Returns:
        Dict with pnl_usd, fee_usd, net_pnl_usd
    """
    if side == 'LONG':
        gross_pnl = (exit_price - entry_price) * quantity
    else:  # SHORT
        gross_pnl = (entry_price - exit_price) * quantity
    
    # Calculate fees (entry + exit)
    entry_value = entry_price * quantity
    exit_value = exit_price * quantity
    fee_usd = (entry_value + exit_value) * fee_rate
    
    net_pnl = gross_pnl - fee_usd
    
    return {
        'pnl_usd': gross_pnl,
        'fee_usd': fee_usd,
        'net_pnl_usd': net_pnl
    }


def format_price(price: float, tick_size: float = 0.01) -> float:
    """
    Format price to tick size
    
    Args:
        price: Raw price
        tick_size: Price increment
        
    Returns:
        Formatted price
    """
    return round(price / tick_size) * tick_size


def timestamp_to_str(timestamp: int) -> str:
    """
    Convert Unix timestamp to ISO string
    
    Args:
        timestamp: Unix timestamp in seconds or milliseconds
        
    Returns:
        ISO format string
    """
    # Handle milliseconds
    if timestamp > 10**10:
        timestamp = timestamp / 1000
    
    return datetime.fromtimestamp(timestamp).isoformat()


def str_to_timestamp(date_str: str) -> int:
    """
    Convert ISO string to Unix timestamp
    
    Args:
        date_str: ISO format date string
        
    Returns:
        Unix timestamp in milliseconds
    """
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return int(dt.timestamp() * 1000)


def check_tp_sl_hit(current_price: float, entry_price: float, 
                   tp_price: float, sl_price: float, side: str) -> Optional[str]:
    """
    Check if TP or SL was hit
    
    Args:
        current_price: Current market price
        entry_price: Entry price
        tp_price: Take profit price
        sl_price: Stop loss price
        side: 'LONG' or 'SHORT'
        
    Returns:
        'TP' if take profit hit, 'SL' if stop loss hit, None otherwise
    """
    if side == 'LONG':
        if current_price >= tp_price:
            return 'TP'
        elif current_price <= sl_price:
            return 'SL'
    else:  # SHORT
        if current_price <= tp_price:
            return 'TP'
        elif current_price >= sl_price:
            return 'SL'
    
    return None


def log_trade(symbol: str, strategy: str, side: str, entry: float, 
              exit: float, qty: float, tp: float, sl: float, 
              exit_reason: str, pnl_data: Dict, indicators: Dict = None):
    """
    Log trade details in a formatted way
    
    Args:
        symbol: Trading symbol
        strategy: Strategy name
        side: 'LONG' or 'SHORT'
        entry: Entry price
        exit: Exit price
        qty: Quantity
        tp: Take profit price
        sl: Stop loss price
        exit_reason: Why position was closed ('TP', 'SL', etc)
        pnl_data: PnL calculation dict
        indicators: Optional indicator values
    """
    pnl_str = f"${pnl_data['net_pnl_usd']:.2f}"
    if pnl_data['net_pnl_usd'] > 0:
        pnl_str = f"+{pnl_str}"
    
    logger.info(f"═══ TRADE CLOSED ═══")
    logger.info(f"Symbol: {symbol} | Strategy: {strategy} | Side: {side}")
    logger.info(f"Entry: ${entry:.4f} | Exit: ${exit:.4f} | Qty: {qty}")
    logger.info(f"TP: ${tp:.4f} | SL: ${sl:.4f}")
    logger.info(f"Exit Reason: {exit_reason}")
    logger.info(f"PnL: {pnl_str} (Gross: ${pnl_data['pnl_usd']:.2f}, Fee: ${pnl_data['fee_usd']:.2f})")
    
    if indicators:
        logger.info(f"Indicators: {indicators}")
    
    logger.info(f"════════════════════")
