"""
Apex Omni API Client Wrapper
Handles all API interactions with Apex Omni exchange
"""

import time
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from apexomni.http_private_sign import HttpPrivateSign
from apexomni.http_public import HttpPublic
from apexomni.constants import APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB
from apexomni.helpers.util import round_size

logger = logging.getLogger(__name__)


class ApexClient:
    """Wrapper for Apex Omni API operations"""
    
    def __init__(self, config: Dict):
        """
        Initialize Apex client with credentials
        
        Args:
            config: Dictionary with API credentials and settings
        """
        self.config = config
        self.endpoint = APEX_OMNI_HTTP_MAIN
        self.network_id = NETWORKID_OMNI_MAIN_ARB
        
        # Initialize clients
        self._init_clients()
        
        # Cache for symbol configurations
        self.symbol_configs = {}
        self.load_symbol_configs()
        
    def _init_clients(self):
        """Initialize HTTP clients for public and private endpoints"""
        try:
            # Public client (no auth needed)
            self.public_client = HttpPublic(self.endpoint)
            
            # Private client with signing (for orders and positions)
            self.private_client = HttpPrivateSign(
                self.endpoint,
                network_id=self.network_id,
                zk_seeds=self.config['ZK_SEEDS'],
                zk_l2Key=self.config.get('ZK_L2KEY', ''),
                api_key_credentials={
                    'key': self.config['API_KEY'],
                    'secret': self.config['API_SECRET'],
                    'passphrase': self.config['API_PASSPHRASE']
                }
            )
            
            logger.info("✅ Apex clients initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Apex clients: {e}")
            raise
    
    def load_symbol_configs(self):
        """Load and cache symbol configurations from Apex"""
        try:
            configs = self.private_client.configs_v3()
            perpetual_contracts = configs['data']['contractConfig']['perpetualContract']
            
            for symbol_data in perpetual_contracts:
                symbol = symbol_data['symbol']
                self.symbol_configs[symbol] = {
                    'stepSize': symbol_data['stepSize'],
                    'tickSize': symbol_data['tickSize'],
                    'minOrderSize': symbol_data.get('minOrderSize', '0.001'),
                    'maxLeverage': symbol_data.get('maxLeverage', '50'),
                }
            
            logger.info(f"✅ Loaded {len(self.symbol_configs)} symbol configurations")
            
        except Exception as e:
            logger.error(f"❌ Failed to load symbol configs: {e}")
            raise
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if symbol exists and is tradeable
        
        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            
        Returns:
            True if valid, False otherwise
        """
        return symbol in self.symbol_configs
    
    def get_available_symbols(self) -> List[str]:
        """Get list of all available trading symbols"""
        return list(self.symbol_configs.keys())
    
    def get_account(self) -> Dict:
        """
        Get account data including positions and balance
        
        Returns:
            Dictionary with account info
        """
        try:
            account = self.private_client.get_account_v3()
            return account
        except Exception as e:
            logger.error(f"❌ Failed to get account: {e}")
            raise
    
    def get_positions(self) -> List[Dict]:
        """
        Get all open positions
        
        Returns:
            List of position dictionaries
        """
        try:
            account = self.get_account()
            positions = account.get('positions', [])
            
            # Filter only positions with size > 0
            active_positions = [
                pos for pos in positions 
                if pos.get('size') and float(pos['size']) != 0
            ]
            
            return active_positions
            
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
            raise
    
    def get_worst_price(self, symbol: str, side: str, size: str) -> str:
        """
        Get worst price from orderbook for market order
        
        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            side: BUY or SELL
            size: Order size
            
        Returns:
            Worst price as string
        """
        try:
            result = self.private_client.get_worst_price_v3(
                symbol=symbol,
                side=side,
                size=size
            )
            
            worst_price = result['data']['worstPrice']
            return worst_price
            
        except Exception as e:
            logger.error(f"❌ Failed to get worst price for {symbol}: {e}")
            raise
    
    def calculate_position_size(self, symbol: str, usd_amount: float, leverage: int) -> Tuple[str, str]:
        """
        Calculate position size in contracts from USD amount
        
        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            usd_amount: USD amount to trade
            leverage: Leverage to use
            
        Returns:
            Tuple of (size, price)
        """
        try:
            # Get current price
            ticker = self.public_client.ticker_v3(symbol=symbol)
            # API returns data as list, get first element
            ticker_data = ticker['data'][0] if isinstance(ticker['data'], list) else ticker['data']
            current_price = float(ticker_data.get('lastPrice') or ticker_data.get('close'))
            
            # Calculate size: (USD amount) / price
            # With leverage, we can control more with less
            # But position size is still: notional_value / price
            raw_size = usd_amount / current_price
            
            # Round to step size
            symbol_config = self.symbol_configs[symbol]
            size = round_size(str(raw_size), symbol_config['stepSize'])
            price = round_size(str(current_price), symbol_config['tickSize'])
            
            logger.info(f"📊 {symbol}: ${usd_amount} → {size} contracts @ ${price}")
            
            return size, price
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate position size for {symbol}: {e}")
            raise
    
    def open_position(self, symbol: str, side: str, size: str, leverage: int = 20) -> Dict:
        """
        Open a market position
        
        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            side: BUY (long) or SELL (short)
            size: Position size in contracts
            leverage: Leverage to use
            
        Returns:
            Order response
        """
        try:
            # Get worst price for market order
            worst_price = self.get_worst_price(symbol, side, size)
            
            # Add slippage protection (10% worse)
            price_float = float(worst_price)
            if side == "BUY":
                protected_price = price_float * 1.10  # 10% higher for buy
            else:
                protected_price = price_float * 0.90  # 10% lower for sell
            
            # Round price
            symbol_config = self.symbol_configs[symbol]
            price = round_size(str(protected_price), symbol_config['tickSize'])
            
            # Create market order
            logger.info(f"📈 Opening {side} position: {symbol} size={size} price={price}")
            
            order = self.private_client.create_order_v3(
                symbol=symbol,
                side=side,
                type="MARKET",
                size=size,
                price=price,
                timeInForce="IMMEDIATE_OR_CANCEL"
            )
            
            logger.info(f"✅ Order created: {order.get('data', {}).get('id', 'N/A')}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Failed to open position {symbol} {side}: {e}")
            raise
    
    def close_position(self, position: Dict) -> Dict:
        """
        Close an existing position using market order
        
        Args:
            position: Position dictionary from get_positions()
            
        Returns:
            Order response
        """
        try:
            symbol = position['symbol']
            size = position['size']
            side = position['side']
            
            # Opposite side to close
            close_side = "SELL" if side == "LONG" else "BUY"
            
            # Get worst price
            worst_price = self.get_worst_price(symbol, close_side, size)
            
            # Add slippage protection
            price_float = float(worst_price)
            if close_side == "BUY":
                protected_price = price_float * 1.10
            else:
                protected_price = price_float * 0.90
            
            # Round price
            symbol_config = self.symbol_configs[symbol]
            price = round_size(str(protected_price), symbol_config['tickSize'])
            
            logger.info(f"📉 Closing {side} position: {symbol} size={size} price={price}")
            
            order = self.private_client.create_order_v3(
                symbol=symbol,
                side=close_side,
                type="MARKET",
                size=size,
                price=price,
                reduceOnly=True,  # Important: only reduce position, don't flip
                timeInForce="IMMEDIATE_OR_CANCEL"
            )
            
            logger.info(f"✅ Close order created: {order.get('data', {}).get('id', 'N/A')}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Failed to close position {position['symbol']}: {e}")
            raise
    
    def cancel_all_orders(self, symbol: Optional[str] = None) -> Dict:
        """
        Cancel all open orders
        
        Args:
            symbol: Optional symbol to cancel (None = all symbols)
            
        Returns:
            Cancel response
        """
        try:
            if symbol:
                result = self.private_client.delete_open_orders_v3(symbol=symbol)
            else:
                result = self.private_client.delete_open_orders_v3()
            
            logger.info(f"✅ Cancelled all orders{' for ' + symbol if symbol else ''}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel orders: {e}")
            raise
