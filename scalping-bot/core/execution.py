"""
Trade Execution Layer
Supports Paper Trading (simulated) and Live Trading (ApeX)
"""

import logging
import time
from typing import Dict, Optional, Tuple
from datetime import datetime
from core.utils import calculate_quantity, calculate_pnl, format_price, check_tp_sl_hit

logger = logging.getLogger(__name__)


class Executor:
    """Base class for trade executors"""
    
    def __init__(self, config: Dict):
        """
        Initialize executor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.fee_rate = config.get('fee_taker', 0.0005)
        self.slippage = config.get('slippage', 0.0)
        
    def enter_position(self, symbol: str, side: str, entry_price: float,
                      tp_price: float, sl_price: float, 
                      order_value_usd: float) -> Dict:
        """
        Enter a position with TP/SL
        
        Args:
            symbol: Trading symbol
            side: 'LONG' or 'SHORT'
            entry_price: Entry price
            tp_price: Take profit price
            sl_price: Stop loss price
            order_value_usd: Order value in USD
            
        Returns:
            Dict with entry details: {success, entry_price, quantity, order_id}
        """
        raise NotImplementedError("Must implement enter_position()")
    
    def check_exit(self, symbol: str, side: str, entry_price: float,
                   tp_price: float, sl_price: float) -> Optional[Tuple[str, float]]:
        """
        Check if TP or SL was hit
        
        Args:
            symbol: Trading symbol
            side: 'LONG' or 'SHORT'
            entry_price: Entry price
            tp_price: TP price
            sl_price: SL price
            
        Returns:
            Tuple of (exit_reason, exit_price) or None if not hit
        """
        raise NotImplementedError("Must implement check_exit()")
    
    def close_position(self, symbol: str, side: str, quantity: float, 
                      reason: str = 'MANUAL') -> Dict:
        """
        Manually close a position
        
        Args:
            symbol: Trading symbol
            side: 'LONG' or 'SHORT'
            quantity: Position size
            reason: Close reason
            
        Returns:
            Dict with close details: {success, exit_price}
        """
        raise NotImplementedError("Must implement close_position()")
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Current price
        """
        raise NotImplementedError("Must implement get_current_price()")


class PaperExecutor(Executor):
    """
    Paper trading executor (simulated)
    Monitors prices and simulates fills
    """
    
    def __init__(self, config: Dict, data_provider):
        """
        Initialize paper executor
        
        Args:
            config: Configuration dictionary
            data_provider: DataProvider instance for price feeds
        """
        super().__init__(config)
        self.data_provider = data_provider
        self.last_prices = {}  # Cache of last prices
        
    def enter_position(self, symbol: str, side: str, entry_price: float,
                      tp_price: float, sl_price: float, 
                      order_value_usd: float) -> Dict:
        """Enter simulated position"""
        
        try:
            # Apply slippage to entry
            slippage_amt = entry_price * self.slippage
            if side == 'LONG':
                actual_entry = entry_price + slippage_amt
            else:
                actual_entry = entry_price - slippage_amt
            
            # Calculate quantity
            qty = calculate_quantity(order_value_usd, actual_entry)
            
            # Simulate order ID
            order_id = f"PAPER_{symbol}_{int(time.time() * 1000)}"
            
            logger.info(f"📝 [PAPER] Entered {side} position:")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Entry: ${actual_entry:.4f} (slippage: ${slippage_amt:.4f})")
            logger.info(f"   Quantity: {qty}")
            logger.info(f"   TP: ${tp_price:.4f} | SL: ${sl_price:.4f}")
            logger.info(f"   Order Value: ${order_value_usd:.2f}")
            
            return {
                'success': True,
                'entry_price': actual_entry,
                'quantity': qty,
                'order_id': order_id,
                'tp_price': tp_price,
                'sl_price': sl_price
            }
            
        except Exception as e:
            logger.error(f"Failed to enter paper position: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_exit(self, symbol: str, side: str, entry_price: float,
                   tp_price: float, sl_price: float) -> Optional[Tuple[str, float]]:
        """Check if TP/SL hit using current price"""
        
        try:
            current_price = self.get_current_price(symbol)
            
            exit_type = check_tp_sl_hit(current_price, entry_price, tp_price, sl_price, side)
            
            if exit_type:
                # Apply slippage to exit
                slippage_amt = current_price * self.slippage
                if side == 'LONG':
                    actual_exit = current_price - slippage_amt
                else:
                    actual_exit = current_price + slippage_amt
                
                # Use TP/SL price if hit (more realistic)
                if exit_type == 'TP':
                    actual_exit = tp_price
                elif exit_type == 'SL':
                    actual_exit = sl_price
                
                logger.info(f"🎯 [PAPER] {exit_type} hit at ${actual_exit:.4f}")
                
                return (exit_type, actual_exit)
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking exit: {e}")
            return None
    
    def close_position(self, symbol: str, side: str, quantity: float, 
                      reason: str = 'MANUAL') -> Dict:
        """Manually close simulated position"""
        
        try:
            current_price = self.get_current_price(symbol)
            
            # Apply slippage
            slippage_amt = current_price * self.slippage
            if side == 'LONG':
                exit_price = current_price - slippage_amt
            else:
                exit_price = current_price + slippage_amt
            
            logger.info(f"🔒 [PAPER] Closed {side} position: {symbol} @ ${exit_price:.4f} ({reason})")
            
            return {
                'success': True,
                'exit_price': exit_price,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Failed to close paper position: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price from data provider"""
        
        # Try to get latest candle
        try:
            timeframe = self.config.get('timeframe', '15m')
            df = self.data_provider.get_candles(symbol, timeframe, limit=1)
            
            if len(df) > 0:
                price = float(df['close'].iloc[-1])
                self.last_prices[symbol] = price
                return price
            
        except Exception as e:
            logger.warning(f"Failed to get current price from data provider: {e}")
        
        # Fallback to cached price
        if symbol in self.last_prices:
            return self.last_prices[symbol]
        
        raise ValueError(f"No price available for {symbol}")


class ApexExecutor(Executor):
    """
    Live executor for ApeX exchange
    """
    
    def __init__(self, config: Dict, apex_client):
        """
        Initialize ApeX executor
        
        Args:
            config: Configuration dictionary
            apex_client: ApexClient instance
        """
        super().__init__(config)
        self.apex_client = apex_client
        
    def enter_position(self, symbol: str, side: str, entry_price: float,
                      tp_price: float, sl_price: float, 
                      order_value_usd: float) -> Dict:
        """Enter live position on ApeX"""
        
        try:
            # Get symbol config
            if symbol not in self.apex_client.symbol_configs:
                raise ValueError(f"Symbol {symbol} not configured")
            
            symbol_config = self.apex_client.symbol_configs[symbol]
            min_size = float(symbol_config['minOrderSize'])
            step_size = float(symbol_config['stepSize'])
            tick_size = float(symbol_config['tickSize'])
            
            # Calculate quantity
            qty = calculate_quantity(order_value_usd, entry_price, min_size, step_size)
            
            # Format prices
            entry_price = format_price(entry_price, tick_size)
            tp_price = format_price(tp_price, tick_size)
            sl_price = format_price(sl_price, tick_size)
            
            logger.info(f"🔴 [LIVE] Entering {side} position on ApeX:")
            logger.info(f"   Symbol: {symbol} | Qty: {qty}")
            logger.info(f"   Entry: ${entry_price:.4f}")
            logger.info(f"   TP: ${tp_price:.4f} | SL: ${sl_price:.4f}")
            
            # Map side to ApeX format
            apex_side = 'BUY' if side == 'LONG' else 'SELL'
            
            # Check if ApeX supports OCO orders
            # If yes, use OCO; if no, place market order and set TP/SL separately
            
            # Option 1: Market entry + separate TP/SL orders (most common)
            entry_order = self.apex_client.private_client.create_order(
                symbol=symbol,
                side=apex_side,
                type='MARKET',
                size=str(qty),
            )
            
            if not entry_order.get('data'):
                raise Exception(f"Entry order failed: {entry_order}")
            
            order_id = entry_order['data']['orderId']
            
            # Wait for fill
            time.sleep(2)
            
            # Get actual entry price from order
            order_info = self.apex_client.private_client.get_order(orderId=order_id)
            actual_entry = float(order_info['data']['avgPrice'])
            
            logger.info(f"✅ [LIVE] Position entered: {symbol} {side} @ ${actual_entry:.4f}")
            
            # Place TP order (limit, reduce-only)
            tp_side = 'SELL' if side == 'LONG' else 'BUY'
            tp_order = self.apex_client.private_client.create_order(
                symbol=symbol,
                side=tp_side,
                type='LIMIT',
                price=str(tp_price),
                size=str(qty),
                reduceOnly=True
            )
            
            # Place SL order (stop market, reduce-only)
            sl_order = self.apex_client.private_client.create_order(
                symbol=symbol,
                side=tp_side,
                type='STOP_MARKET',
                stopPrice=str(sl_price),
                size=str(qty),
                reduceOnly=True
            )
            
            logger.info(f"✅ [LIVE] TP/SL orders placed")
            
            return {
                'success': True,
                'entry_price': actual_entry,
                'quantity': qty,
                'order_id': order_id,
                'tp_order_id': tp_order['data']['orderId'],
                'sl_order_id': sl_order['data']['orderId'],
                'tp_price': tp_price,
                'sl_price': sl_price
            }
            
        except Exception as e:
            logger.error(f"❌ [LIVE] Failed to enter position: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_exit(self, symbol: str, side: str, entry_price: float,
                   tp_price: float, sl_price: float) -> Optional[Tuple[str, float]]:
        """Check if position was closed (TP/SL hit)"""
        
        try:
            # Check if position still exists
            positions = self.apex_client.get_positions()
            
            pos_exists = any(p['symbol'] == symbol for p in positions)
            
            if not pos_exists:
                # Position closed - determine if TP or SL
                current_price = self.get_current_price(symbol)
                
                if side == 'LONG':
                    if current_price >= tp_price:
                        return ('TP', tp_price)
                    else:
                        return ('SL', sl_price)
                else:
                    if current_price <= tp_price:
                        return ('TP', tp_price)
                    else:
                        return ('SL', sl_price)
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking exit: {e}")
            return None
    
    def close_position(self, symbol: str, side: str, quantity: float, 
                      reason: str = 'MANUAL') -> Dict:
        """Manually close live position"""
        
        try:
            # Cancel TP/SL orders
            self.apex_client.private_client.cancel_all_orders(symbol=symbol)
            
            # Close position
            close_side = 'SELL' if side == 'LONG' else 'BUY'
            
            close_order = self.apex_client.private_client.create_order(
                symbol=symbol,
                side=close_side,
                type='MARKET',
                size=str(quantity),
                reduceOnly=True
            )
            
            time.sleep(1)
            
            # Get exit price
            order_info = self.apex_client.private_client.get_order(
                orderId=close_order['data']['orderId']
            )
            exit_price = float(order_info['data']['avgPrice'])
            
            logger.info(f"🔒 [LIVE] Position closed: {symbol} @ ${exit_price:.4f} ({reason})")
            
            return {
                'success': True,
                'exit_price': exit_price,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"❌ [LIVE] Failed to close position: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price from ApeX"""
        
        ticker = self.apex_client.public_client.ticker_v3(symbol=symbol)
        ticker_data = ticker['data']
        if isinstance(ticker_data, list):
            ticker_data = ticker_data[0]
        
        return float(ticker_data['lastPrice'])


def create_executor(mode: str, config: Dict, apex_client=None, data_provider=None) -> Executor:
    """
    Factory function to create executor
    
    Args:
        mode: 'paper' or 'live'
        config: Configuration dictionary
        apex_client: ApexClient instance (required for live)
        data_provider: DataProvider instance (required for paper)
        
    Returns:
        Executor instance
    """
    if mode == 'paper':
        if data_provider is None:
            raise ValueError("data_provider required for paper mode")
        return PaperExecutor(config, data_provider)
    elif mode == 'live':
        if apex_client is None:
            raise ValueError("apex_client required for live mode")
        return ApexExecutor(config, apex_client)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'paper' or 'live'")
