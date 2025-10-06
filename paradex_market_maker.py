"""
Paradex Market Maker Bot - Advanced Version
Optimized for airdrop farming with limited capital ($5k)
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import aiohttp
import hmac
import hashlib
from dataclasses import dataclass
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_maker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class OrderLevel:
    """Represents a single order level in the book"""
    price: Decimal
    size: Decimal
    side: str  # 'BUY' or 'SELL'


class ParadexAPI:
    """Paradex API Client with authentication"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.testnet.paradex.trade/v1" if testnet else "https://api.paradex.trade/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _generate_signature(self, timestamp: int, method: str, path: str, body: str = "") -> str:
        """Generate HMAC signature for authenticated requests"""
        message = f"{timestamp}{method}{path}{body}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                      authenticated: bool = False) -> Dict:
        """Make HTTP request to Paradex API"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if authenticated:
            timestamp = int(time.time() * 1000)
            body = json.dumps(data) if data else ""
            signature = self._generate_signature(timestamp, method, endpoint, body)
            headers.update({
                "PARADEX-API-KEY": self.api_key,
                "PARADEX-TIMESTAMP": str(timestamp),
                "PARADEX-SIGNATURE": signature
            })
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            raise
    
    async def get_orderbook(self, market: str, depth: int = 20) -> Dict:
        """Get current orderbook"""
        return await self._request("GET", f"/markets/{market}/orderbook?depth={depth}")
    
    async def get_ticker(self, market: str) -> Dict:
        """Get market ticker data"""
        return await self._request("GET", f"/markets/{market}/ticker")
    
    async def get_account_summary(self) -> Dict:
        """Get account balance and positions"""
        return await self._request("GET", "/account", authenticated=True)
    
    async def place_order(self, market: str, side: str, order_type: str, 
                         size: Decimal, price: Optional[Decimal] = None,
                         client_id: Optional[str] = None) -> Dict:
        """Place a new order"""
        order_data = {
            "market": market,
            "side": side,
            "type": order_type,
            "size": str(size),
        }
        
        if price:
            order_data["price"] = str(price)
        if client_id:
            order_data["client_id"] = client_id
            
        return await self._request("POST", "/orders", data=order_data, authenticated=True)
    
    async def cancel_order(self, order_id: str) -> Dict:
        """Cancel an existing order"""
        return await self._request("DELETE", f"/orders/{order_id}", authenticated=True)
    
    async def cancel_all_orders(self, market: Optional[str] = None) -> Dict:
        """Cancel all orders, optionally filtered by market"""
        endpoint = "/orders/cancel-all"
        data = {"market": market} if market else {}
        return await self._request("POST", endpoint, data=data, authenticated=True)
    
    async def get_open_orders(self, market: Optional[str] = None) -> List[Dict]:
        """Get all open orders"""
        endpoint = "/orders/open"
        if market:
            endpoint += f"?market={market}"
        result = await self._request("GET", endpoint, authenticated=True)
        return result.get("orders", [])


class VolatilityEstimator:
    """Estimates market volatility for dynamic spread adjustment"""
    
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.price_history: List[float] = []
    
    def add_price(self, price: float):
        """Add new price to history"""
        self.price_history.append(price)
        if len(self.price_history) > self.window_size:
            self.price_history.pop(0)
    
    def get_volatility(self) -> float:
        """Calculate historical volatility (standard deviation of returns)"""
        if len(self.price_history) < 2:
            return 0.001  # Default low volatility
        
        returns = np.diff(np.log(self.price_history))
        return float(np.std(returns)) if len(returns) > 0 else 0.001


class InventoryManager:
    """Manages position inventory and skewing"""
    
    def __init__(self, max_position_usd: float, target_position: float = 0.0):
        self.max_position_usd = max_position_usd
        self.target_position = target_position
        self.current_position = 0.0
    
    def update_position(self, position: float):
        """Update current position"""
        self.current_position = position
    
    def get_inventory_skew(self) -> float:
        """Calculate inventory skew factor (-1 to 1)"""
        position_ratio = self.current_position / self.max_position_usd if self.max_position_usd > 0 else 0
        return max(-1.0, min(1.0, position_ratio))
    
    def should_reduce_position(self) -> bool:
        """Check if position should be reduced"""
        return abs(self.current_position) > self.max_position_usd * 0.8


class MarketMakerBot:
    """Advanced Market Maker Bot for Paradex"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api = ParadexAPI(
            api_key=config['api_key'],
            api_secret=config['api_secret'],
            testnet=config.get('testnet', False)
        )
        
        self.market = config['market']
        self.base_spread = Decimal(str(config.get('base_spread', 0.001)))  # 0.1%
        self.order_levels = config.get('order_levels', 5)
        self.level_spacing = Decimal(str(config.get('level_spacing', 0.0005)))  # 0.05%
        self.order_size_usd = Decimal(str(config.get('order_size_usd', 100)))
        self.max_position_usd = config.get('max_position_usd', 2500)
        self.refresh_interval = config.get('refresh_interval', 30)
        self.min_edge = Decimal(str(config.get('min_edge', 0.0002)))  # 0.02% minimum edge
        
        self.volatility_estimator = VolatilityEstimator()
        self.inventory_manager = InventoryManager(self.max_position_usd)
        
        self.active_orders: Dict[str, Dict] = {}
        self.stats = {
            'orders_placed': 0,
            'orders_filled': 0,
            'orders_cancelled': 0,
            'total_volume': 0.0,
            'pnl': 0.0,
            'start_time': datetime.now()
        }
        
        self.running = False
        
    async def start(self):
        """Start the market maker bot"""
        logger.info("Starting Paradex Market Maker Bot")
        self.running = True
        
        async with self.api:
            try:
                # Initial account check
                account = await self.api.get_account_summary()
                logger.info(f"Account connected: {account}")
                
                # Main bot loop
                while self.running:
                    await self.run_iteration()
                    await asyncio.sleep(self.refresh_interval)
                    
            except KeyboardInterrupt:
                logger.info("Shutting down gracefully...")
                await self.shutdown()
            except Exception as e:
                logger.error(f"Fatal error: {e}", exc_info=True)
                await self.shutdown()
    
    async def run_iteration(self):
        """Single iteration of the market making loop"""
        try:
            # Get market data
            ticker = await self.api.get_ticker(self.market)
            orderbook = await self.api.get_orderbook(self.market)
            account = await self.api.get_account_summary()
            
            # Update state
            mid_price = self._calculate_mid_price(orderbook)
            self.volatility_estimator.add_price(float(mid_price))
            
            # Update position
            position = self._get_position_from_account(account)
            self.inventory_manager.update_position(position)
            
            # Calculate optimal quotes
            quotes = self._generate_quotes(mid_price)
            
            # Update orders
            await self._update_orders(quotes)
            
            # Log status
            self._log_status(mid_price, position)
            
        except Exception as e:
            logger.error(f"Error in iteration: {e}", exc_info=True)
    
    def _calculate_mid_price(self, orderbook: Dict) -> Decimal:
        """Calculate mid price from orderbook"""
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        
        if not bids or not asks:
            raise ValueError("Empty orderbook")
        
        best_bid = Decimal(str(bids[0]['price']))
        best_ask = Decimal(str(asks[0]['price']))
        
        return (best_bid + best_ask) / 2
    
    def _get_position_from_account(self, account: Dict) -> float:
        """Extract current position from account data"""
        positions = account.get('positions', [])
        for pos in positions:
            if pos.get('market') == self.market:
                return float(pos.get('size', 0))
        return 0.0
    
    def _generate_quotes(self, mid_price: Decimal) -> List[OrderLevel]:
        """Generate optimized bid/ask quotes"""
        quotes = []
        
        # Calculate dynamic spread based on volatility
        volatility = self.volatility_estimator.get_volatility()
        dynamic_spread = self.base_spread * Decimal(str(1 + volatility * 10))
        dynamic_spread = max(dynamic_spread, self.min_edge * 2)
        
        # Get inventory skew
        inventory_skew = self.inventory_manager.get_inventory_skew()
        skew_adjustment = Decimal(str(inventory_skew * 0.0002))  # 0.02% max skew
        
        # Generate bid levels
        for i in range(self.order_levels):
            offset = dynamic_spread / 2 + self.level_spacing * i
            
            # Adjust for inventory (widen bids if long, narrow if short)
            bid_offset = offset + skew_adjustment
            bid_price = mid_price * (1 - bid_offset)
            
            # Size decreases with distance from mid
            size_multiplier = Decimal(str(1.0 - i * 0.1))
            bid_size = self._calculate_order_size(bid_price) * size_multiplier
            
            quotes.append(OrderLevel(
                price=self._round_price(bid_price),
                size=self._round_size(bid_size),
                side='BUY'
            ))
        
        # Generate ask levels
        for i in range(self.order_levels):
            offset = dynamic_spread / 2 + self.level_spacing * i
            
            # Adjust for inventory (narrow asks if long, widen if short)
            ask_offset = offset - skew_adjustment
            ask_price = mid_price * (1 + ask_offset)
            
            size_multiplier = Decimal(str(1.0 - i * 0.1))
            ask_size = self._calculate_order_size(ask_price) * size_multiplier
            
            quotes.append(OrderLevel(
                price=self._round_price(ask_price),
                size=self._round_size(ask_size),
                side='SELL'
            ))
        
        return quotes
    
    def _calculate_order_size(self, price: Decimal) -> Decimal:
        """Calculate order size in base currency"""
        # Convert USD size to base currency size
        return self.order_size_usd / price
    
    def _round_price(self, price: Decimal) -> Decimal:
        """Round price to valid tick size"""
        # Paradex typically uses 2-4 decimal places for prices
        return price.quantize(Decimal('0.01'))
    
    def _round_size(self, size: Decimal) -> Decimal:
        """Round size to valid lot size"""
        # Round to 4 decimal places for size
        return size.quantize(Decimal('0.0001'))
    
    async def _update_orders(self, new_quotes: List[OrderLevel]):
        """Update orders to match new quotes"""
        try:
            # Get current open orders
            open_orders = await self.api.get_open_orders(self.market)
            
            # Check if we need to cancel and replace
            if self._should_replace_orders(open_orders, new_quotes):
                # Cancel all existing orders
                if open_orders:
                    await self.api.cancel_all_orders(self.market)
                    self.stats['orders_cancelled'] += len(open_orders)
                    logger.info(f"Cancelled {len(open_orders)} orders")
                
                # Place new orders
                await asyncio.sleep(0.5)  # Brief delay after cancellation
                
                for quote in new_quotes:
                    try:
                        client_id = f"{quote.side}_{int(time.time()*1000)}_{quote.price}"
                        
                        result = await self.api.place_order(
                            market=self.market,
                            side=quote.side,
                            order_type='LIMIT',
                            size=quote.size,
                            price=quote.price,
                            client_id=client_id
                        )
                        
                        self.stats['orders_placed'] += 1
                        
                        # Small delay between orders to avoid rate limits
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.warning(f"Failed to place order: {e}")
                
                logger.info(f"Placed {len(new_quotes)} new orders")
                
        except Exception as e:
            logger.error(f"Error updating orders: {e}")
    
    def _should_replace_orders(self, current_orders: List[Dict], 
                              new_quotes: List[OrderLevel]) -> bool:
        """Determine if orders should be cancelled and replaced"""
        if len(current_orders) != len(new_quotes):
            return True
        
        # Check if prices have moved significantly
        for order in current_orders:
            order_price = Decimal(str(order.get('price', 0)))
            order_side = order.get('side', '')
            
            # Find matching quote
            matching_quotes = [q for q in new_quotes if q.side == order_side]
            if not matching_quotes:
                return True
            
            # Check if any quote is close to this order price
            min_diff = min(abs(q.price - order_price) / order_price for q in matching_quotes)
            
            # Replace if price moved more than 0.05%
            if min_diff > Decimal('0.0005'):
                return True
        
        return False
    
    def _log_status(self, mid_price: Decimal, position: float):
        """Log current bot status"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds() / 3600
        volatility = self.volatility_estimator.get_volatility()
        
        logger.info(
            f"Status | Price: ${mid_price:.2f} | "
            f"Position: {position:.4f} | "
            f"Vol: {volatility:.4f} | "
            f"Orders: {self.stats['orders_placed']} | "
            f"Runtime: {runtime:.2f}h"
        )
    
    async def shutdown(self):
        """Gracefully shutdown the bot"""
        logger.info("Shutting down...")
        self.running = False
        
        try:
            # Cancel all orders
            await self.api.cancel_all_orders(self.market)
            logger.info("All orders cancelled")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        # Log final statistics
        self._log_final_stats()
    
    def _log_final_stats(self):
        """Log final bot statistics"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds() / 3600
        
        logger.info("=" * 50)
        logger.info("FINAL STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Runtime: {runtime:.2f} hours")
        logger.info(f"Orders Placed: {self.stats['orders_placed']}")
        logger.info(f"Orders Filled: {self.stats['orders_filled']}")
        logger.info(f"Orders Cancelled: {self.stats['orders_cancelled']}")
        logger.info(f"Total Volume: ${self.stats['total_volume']:.2f}")
        logger.info("=" * 50)


async def main():
    """Main entry point"""
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Please create configuration file.")
        return
    
    # Create and start bot
    bot = MarketMakerBot(config)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
