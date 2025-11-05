"""
Apex Omni API Client Wrapper
Handles all API interactions with Apex Omni exchange

Based on official Apex documentation:
https://api-docs.omni.apex.exchange/
https://github.com/ApeX-Protocol/apexpro-openapi
"""

import time
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from apexomni.http_private_sign import HttpPrivateSign
from apexomni.http_public import HttpPublic
from apexomni.constants import APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB
from apexomni.helpers.util import round_size

from resilience import ResilientAPIClient, with_retry
from logger_config import performance_metrics, PerformanceLogger

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
        
        # Wrap with resilient client
        self.resilient_client = ResilientAPIClient(self.private_client, rate_limit=10)
        
    def _init_clients(self):
        """Initialize HTTP clients for public and private endpoints"""
        try:
            # Public client (no auth needed) - with increased timeout
            self.public_client = HttpPublic(self.endpoint, timeout=30)
            
            # Private client with signing (for orders and positions) - with increased timeout
            self.private_client = HttpPrivateSign(
                self.endpoint,
                network_id=self.network_id,
                zk_seeds=self.config['ZK_SEEDS'],
                zk_l2Key=self.config.get('ZK_L2KEY', ''),
                api_key_credentials={
                    'key': self.config['API_KEY'],
                    'secret': self.config['API_SECRET'],
                    'passphrase': self.config['API_PASSPHRASE']
                },
                timeout=30
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
    
    def get_klines(self, symbol: str, interval: str, limit: int = 200) -> List[Dict]:
        """
        Get historical klines/candles data
        
        Args:
            symbol: Trading symbol (e.g., 'BTC-USDT')
            interval: Candle interval ('1', '5', '15', '60', '240', 'D')
                     1=1min, 5=5min, 15=15min, 60=1h, 240=4h, D=1day
            limit: Number of candles to fetch (default 200)
            
        Returns:
            List of kline dicts with OHLCV data
        """
        try:
            # ApeX Omni API endpoint for klines
            # Check if method exists in public client
            if hasattr(self.public_client, 'klines_v3'):
                result = self.public_client.klines_v3(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
                
                if result.get('code') == 0 and result.get('data'):
                    return result['data']
                else:
                    logger.warning(f"Klines API returned no data: {result}")
                    return []
            
            elif hasattr(self.public_client, 'klines'):
                # Try alternative method name
                result = self.public_client.klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
                
                if result.get('code') == 0 and result.get('data'):
                    return result['data']
                else:
                    logger.warning(f"Klines API returned no data: {result}")
                    return []
            
            else:
                logger.warning("Klines method not found in ApeX public client")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol}: {e}")
            return []
    
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
            with PerformanceLogger('get_account', performance_metrics):
                account = self.resilient_client.call('get_account_v3')
            return account
        except Exception as e:
            logger.error(f"❌ Failed to get account: {e}")
            raise
    
    def get_balance(self) -> float:
        """
        Get available balance in USDT from account
        
        Returns:
            Available balance in USDT
        """
        try:
            # Use get_account_v3 which returns account info including balance
            account_data = self.resilient_client.call('get_account_v3')
            
            # Log top-level structure for debugging
            logger.debug(f"🔍 Account data top-level keys: {list(account_data.keys())}")
            
            # Response structure varies - try multiple paths
            balance = None
            
            # PATH 1: Check contractWallets (CORRECT for Apex Omni perpetual trading)
            if 'contractWallets' in account_data:
                logger.debug(f"✅ Found contractWallets with {len(account_data['contractWallets'])} wallets")
                for wallet in account_data['contractWallets']:
                    token = wallet.get('token', 'UNKNOWN')
                    wallet_balance = wallet.get('balance', '0')
                    logger.debug(f"   Wallet: token={token}, balance={wallet_balance}")
                    
                    if token == 'USDT':
                        balance = float(wallet_balance)
                        logger.info(f"💰 Balance from contractWallets: ${balance:.2f} USDT")
                        return balance
                
                logger.warning("⚠️  No USDT wallet found in contractWallets")
            else:
                logger.warning("⚠️  contractWallets not found in response")
            
            # PATH 2: Check data.account (alternative structure)
            if 'data' in account_data and 'account' in account_data['data']:
                account = account_data['data']['account']
                
                # Try availableBalance
                if 'availableBalance' in account:
                    balance = float(account['availableBalance'])
                    logger.debug(f"💰 Balance from data.account.availableBalance: ${balance:.2f}")
                    return balance
                
                # Try equity
                if 'equity' in account:
                    balance = float(account['equity'])
                    logger.debug(f"💰 Balance from data.account.equity: ${balance:.2f}")
                    return balance
            
            # PATH 3: Check spotWallets as fallback
            if 'spotWallets' in account_data:
                for wallet in account_data['spotWallets']:
                    if wallet.get('tokenId') == '141':  # USDT token ID
                        balance = float(wallet.get('balance', 0))
                        logger.debug(f"💰 Balance from spotWallets: ${balance:.2f}")
                        return balance
            
            # If we get here, couldn't find balance
            logger.warning(f"⚠️  Could not find balance in response. Top-level keys: {list(account_data.keys())}")
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Failed to get balance: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return 0.0
    
    def validate_balance(self, required_usd: float) -> bool:
        """
        Validate if sufficient balance available
        
        Args:
            required_usd: Required USD amount (margin needed with leverage)
            
        Returns:
            True if sufficient balance
        """
        try:
            balance = self.get_balance()
            
            # If balance is 0, might be a parsing issue - log account info
            if balance == 0.0:
                logger.warning("⚠️  Balance returned 0. Fetching account details for debug...")
                try:
                    account = self.private_client.get_account_v3()
                    logger.info(f"📊 Account response keys: {list(account.keys())}")
                    if 'data' in account:
                        logger.info(f"📊 Data keys: {list(account['data'].keys())}")
                        if 'account' in account['data']:
                            acc = account['data']['account']
                            logger.info(f"📊 Account keys: {list(acc.keys())}")
                            logger.info(f"📊 Account info: equity={acc.get('equity')}, "
                                       f"available={acc.get('availableBalance')}, "
                                       f"totalValue={acc.get('totalValue')}")
                except Exception as debug_e:
                    logger.error(f"Debug fetch failed: {debug_e}")
            
            logger.info(f"💰 Balance check: ${balance:.2f} available, ${required_usd:.2f} required")
            
            if balance <= 0.0:
                logger.error(f"❌ Balance is zero or negative: ${balance:.2f}")
                logger.error("   This might indicate:")
                logger.error("   1. No funds in account")
                logger.error("   2. API parsing issue")
                logger.error("   3. Wrong account/network")
                return False
            
            if balance < required_usd:
                logger.warning(f"⚠️  Low balance: ${balance:.2f} < ${required_usd:.2f}")
                logger.warning(f"   Consider reducing position size or adding funds")
                return False
            
            logger.info(f"✅ Sufficient balance: ${balance:.2f} >= ${required_usd:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Balance validation failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
    
    def get_positions(self) -> List[Dict]:
        """
        Get all open positions with calculated unrealized PnL
        
        Returns:
            List of position dictionaries with unrealizedPnl added
        """
        try:
            account = self.get_account()
            positions = account.get('positions', [])
            
            # Filter only positions with size > 0
            active_positions = [
                pos for pos in positions 
                if pos.get('size') and float(pos['size']) != 0
            ]
            
            # Calculate unrealized PnL and add market price for each position
            for pos in active_positions:
                symbol = pos['symbol']
                try:
                    # Get current price
                    ticker = self.public_client.ticker_v3(symbol=symbol)
                    ticker_data = ticker['data']
                    if isinstance(ticker_data, list):
                        ticker_data = ticker_data[0]
                    current_price = float(ticker_data['lastPrice'])
                    
                    # Add mark price (use last price as approximation)
                    pos['markPrice'] = current_price
                    
                    # Calculate PnL
                    pnl = self.calculate_unrealized_pnl(pos, current_price)
                    pos['unrealizedPnl'] = pnl
                    pos['realizedPnl'] = 0.0  # Not available from API
                    
                except Exception as e:
                    logger.error(f"❌ Failed to calculate PnL for {symbol}: {e}")
                    import traceback
                    logger.error(f"   Traceback: {traceback.format_exc()}")
                    pos['unrealizedPnl'] = 0.0
                    pos['realizedPnl'] = 0.0
                    pos['markPrice'] = float(pos.get('entryPrice', 0))
            
            return active_positions
            
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
            raise
    
    def calculate_unrealized_pnl(self, position: Dict, current_price: Optional[float] = None) -> float:
        """
        Calculate unrealized PnL for a position manually
        (Apex Omni API doesn't return unrealizedPnl in positions)
        
        Args:
            position: Position dictionary with symbol, side, size, entryPrice
            current_price: Optional current price (if not provided, will fetch from ticker)
            
        Returns:
            Unrealized PnL in USD
        """
        try:
            symbol = position['symbol']
            side = position['side']
            size_str = position.get('size', '0')
            entry_price_str = position.get('entryPrice', '0')
            
            # Convert to float
            size = float(size_str)
            entry_price = float(entry_price_str)
            
            # Validate data
            if size == 0:
                logger.warning(f"⚠️  Size is 0 for {symbol} - position not filled yet")
                return 0.0
            
            if entry_price == 0:
                logger.warning(f"⚠️  Entry price is 0 for {symbol} - position not filled yet")
                return 0.0
            
            # Get current market price if not provided
            if current_price is None:
                ticker = self.public_client.ticker_v3(symbol=symbol)
                ticker_data = ticker['data']
                if isinstance(ticker_data, list):
                    ticker_data = ticker_data[0]
                current_price = float(ticker_data['lastPrice'])
            
            # Calculate PnL based on direction
            if side == 'LONG':
                # Long: profit when price goes up
                price_diff = current_price - entry_price
            else:  # SHORT
                # Short: profit when price goes down
                price_diff = entry_price - current_price
            
            # PnL = price_difference * position_size
            pnl = price_diff * size
            
            return pnl
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate PnL for {position.get('symbol', 'UNKNOWN')}: {e}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return 0.0
    
    def get_order_status(self, order_id: str) -> Dict:
        """
        Get order status by ID
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Order details
        """
        try:
            order = self.private_client.get_order_by_id_v3(id=order_id)
            return order
        except Exception as e:
            logger.error(f"❌ Failed to get order status: {e}")
            return {}
    
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
            # Get current price from ticker
            # ticker_v3 automatically removes hyphen from symbol
            ticker = self.public_client.ticker_v3(symbol=symbol)
            
            # Response format: {"data": [{"symbol": "BTCUSDT", "lastPrice": "67500.00", ...}]}
            ticker_data = ticker['data']
            if isinstance(ticker_data, list):
                ticker_data = ticker_data[0]
            
            # Get lastPrice from ticker
            current_price = float(ticker_data['lastPrice'])
            
            # Calculate size: (USD amount) / price
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
            
            # Check order status
            order_data = order.get('data', {})
            order_id = order_data.get('id', 'N/A')
            order_status = order_data.get('status', 'UNKNOWN')
            
            logger.info(f"✅ Order created: ID={order_id}, Status={order_status}")
            
            # Log full order response for debugging
            logger.debug(f"   Order response: {order_data}")
            
            # Warn if order might not be filled
            if order_status in ['PENDING', 'UNTRIGGERED', 'OPEN']:
                logger.warning(f"⚠️  Order {order_id} is {order_status}, may not fill immediately")
                logger.warning(f"   The position may show as size=0 until order is filled")
            elif order_status == 'FILLED':
                logger.info(f"🎯 Order {order_id} FILLED successfully")
            elif order_status == 'UNKNOWN':
                logger.warning(f"⚠️  Order status is UNKNOWN - check order manually")
                logger.warning(f"   Order data: {order_data}")
            
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
