"""
Trading Bot Main Logic
Orchestrates the entire trading cycle: open, monitor, close, reopen
"""

import time
import logging
import uuid
import threading
from typing import Dict, List, Optional
from datetime import datetime

from apex_client import ApexClient
from position_manager import PositionManager
from database import TradingDatabase
from logger_config import audit_logger
from monitor import (
    print_cycle_start, print_cycle_end, print_waiting_reentry,
    print_error
)

logger = logging.getLogger(__name__)


class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, config: Dict):
        """
        Initialize trading bot
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.cycle_count = 0
        self.is_running = False
        self.current_cycle_id = None
        self.shutdown_event = threading.Event()  # For immediate interruption
        
        # Initialize components
        logger.info("🔧 Initializing bot components...")
        self.apex_client = ApexClient(config)
        self.position_manager = PositionManager(config, self.apex_client)
        self.database = TradingDatabase()
        
        # Parse trading symbols
        self.symbols_long = self._parse_symbols(config['LONG_SYMBOLS'])
        self.symbols_short = self._parse_symbols(config['SHORT_SYMBOLS'])
        
        logger.info(f"✅ Bot initialized successfully")
    
    def _parse_symbols(self, symbols_str: str) -> List[str]:
        """
        Parse comma-separated symbols and add -USDT suffix
        
        Args:
            symbols_str: Comma-separated symbol string (e.g., "BTC,ETH,SOL")
            
        Returns:
            List of full symbol names (e.g., ["BTC-USDT", "ETH-USDT"])
        """
        if not symbols_str or symbols_str.strip() == "":
            return []
        
        symbols = [s.strip() for s in symbols_str.split(',') if s.strip()]
        return [f"{sym}-USDT" if not sym.endswith('-USDT') else sym for sym in symbols]
    
    def validate_symbols(self) -> bool:
        """
        Validate that all configured symbols are tradeable
        
        Returns:
            True if all valid, False otherwise
        """
        logger.info("🔍 Validating trading symbols...")
        
        all_symbols = self.symbols_long + self.symbols_short
        available_symbols = self.apex_client.get_available_symbols()
        
        invalid_symbols = []
        for symbol in all_symbols:
            if not self.apex_client.validate_symbol(symbol):
                invalid_symbols.append(symbol)
        
        if invalid_symbols:
            logger.error(f"❌ Invalid symbols: {invalid_symbols}")
            logger.error(f"   Available symbols: {', '.join(available_symbols[:20])}...")
            return False
        
        logger.info(f"✅ All symbols valid")
        logger.info(f"   Long:  {self.symbols_long}")
        logger.info(f"   Short: {self.symbols_short}")
        
        return True
    
    def check_existing_positions(self) -> bool:
        """
        Check for existing open positions (recovery scenario)
        
        Returns:
            True if positions exist, False otherwise
        """
        try:
            positions = self.apex_client.get_positions()
            
            if positions:
                logger.warning(f"⚠️  Found {len(positions)} existing open positions!")
                for pos in positions:
                    logger.warning(f"   - {pos['symbol']} {pos['side']}: {pos['size']} @ ${pos.get('entryPrice', '?')}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check existing positions: {e}")
            return False
    
    def close_all_positions(self, reason: str = "MANUAL") -> bool:
        """
        Close all open positions
        
        Args:
            reason: Reason for closing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            positions = self.apex_client.get_positions()
            
            if not positions:
                logger.info("ℹ️  No positions to close")
                return True
            
            logger.info(f"🔒 Closing {len(positions)} positions...")
            
            failed_closes = []
            
            for pos in positions:
                try:
                    # Track for position manager
                    pnl = float(pos.get('unrealizedPnl', 0))
                    self.position_manager.add_closed_position(pos, reason, pnl)
                    
                    # Close the position
                    close_order = self.apex_client.close_position(pos)
                    logger.info(f"   ✅ Closed {pos['symbol']} {pos['side']}")
                    
                    # Record in database
                    if self.current_cycle_id:
                        exit_price = float(pos.get('markPrice', pos.get('entryPrice', 0)))
                        self.database.record_position_close(
                            self.current_cycle_id,
                            pos['symbol'],
                            exit_price,
                            pnl,
                            reason,
                            fees=0  # TODO: get fees from order response
                        )
                    
                    # Small delay between closes
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed to close {pos['symbol']}: {e}")
                    failed_closes.append(pos)
            
            if failed_closes:
                logger.warning(f"⚠️  {len(failed_closes)} positions failed to close")
                # Try emergency hedge
                self._emergency_hedge(failed_closes)
                return False
            
            logger.info("✅ All positions closed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error closing positions: {e}")
            return False
    
    def _emergency_hedge(self, failed_positions: List[Dict]):
        """
        Open opposite positions to hedge failed closes
        
        Args:
            failed_positions: List of positions that failed to close
        """
        logger.warning("🚨 Attempting emergency hedge for failed closes...")
        
        for pos in failed_positions:
            try:
                symbol = pos['symbol']
                size = pos['size']
                current_side = pos['side']
                
                # Open opposite position
                hedge_side = "SELL" if current_side == "LONG" else "BUY"
                
                logger.warning(f"   Opening {hedge_side} hedge for {symbol} {current_side}")
                
                self.apex_client.open_position(
                    symbol=symbol,
                    side=hedge_side,
                    size=size,
                    leverage=int(self.config['LEVERAGE'])
                )
                
                logger.warning(f"   ✅ Hedge opened for {symbol}")
                
                # Now try to close both
                time.sleep(1)
                positions = self.apex_client.get_positions()
                for p in positions:
                    if p['symbol'] == symbol:
                        try:
                            self.apex_client.close_position(p)
                            logger.info(f"   ✅ Closed hedged {p['symbol']} {p['side']}")
                        except Exception as e:
                            logger.error(f"   ❌ Failed to close hedged position: {e}")
                
            except Exception as e:
                logger.error(f"   ❌ Emergency hedge failed for {pos['symbol']}: {e}")
    
    def open_all_positions(self) -> bool:
        """
        Open all configured positions (long + short)
        
        Returns:
            True if all successful, False if any failed
        """
        try:
            position_size_usd = float(self.config['POSITION_SIZE_USD'])
            leverage = int(self.config['LEVERAGE'])
            
            # Calculate total required balance
            total_assets = len(self.symbols_long) + len(self.symbols_short)
            total_required = position_size_usd * total_assets
            
            # Validate balance
            logger.info(f"💰 Validating balance for {total_assets} positions...")
            if not self.apex_client.validate_balance(total_required):
                logger.error(f"❌ Insufficient balance for opening positions")
                audit_logger.log_action('balance_validation_failed', {
                    'required': total_required,
                    'positions': total_assets
                })
                return False
            
            logger.info(f"📈 Opening positions: ${position_size_usd} per asset @ {leverage}x leverage")
            
            opened_positions = []
            failed_positions = []
            
            # Open LONG positions
            for symbol in self.symbols_long:
                try:
                    logger.info(f"   Opening LONG: {symbol}")
                    
                    # Calculate size
                    size, price = self.apex_client.calculate_position_size(
                        symbol, position_size_usd, leverage
                    )
                    
                    # Open position
                    order = self.apex_client.open_position(
                        symbol=symbol,
                        side="BUY",
                        size=size,
                        leverage=leverage
                    )
                    
                    opened_positions.append(symbol)
                    logger.info(f"   ✅ {symbol} LONG opened")
                    
                    # Small delay between orders
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed to open {symbol} LONG: {e}")
                    failed_positions.append(symbol)
            
            # Open SHORT positions
            for symbol in self.symbols_short:
                try:
                    logger.info(f"   Opening SHORT: {symbol}")
                    
                    # Calculate size
                    size, price = self.apex_client.calculate_position_size(
                        symbol, position_size_usd, leverage
                    )
                    
                    # Open position
                    order = self.apex_client.open_position(
                        symbol=symbol,
                        side="SELL",
                        size=size,
                        leverage=leverage
                    )
                    
                    opened_positions.append(symbol)
                    logger.info(f"   ✅ {symbol} SHORT opened")
                    
                    # Record in database
                    position_data = {
                        'symbol': symbol,
                        'side': 'SHORT',
                        'size': size,
                        'entryPrice': order.get('data', {}).get('price', '0')
                    }
                    self.database.record_position_open(self.current_cycle_id, position_data, self.config)
                    
                    # Small delay between orders
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed to open {symbol} SHORT: {e}")
                    failed_positions.append(symbol)
            
            # Check results
            if failed_positions:
                logger.error(f"❌ {len(failed_positions)} positions failed to open: {failed_positions}")
                logger.warning("🔒 Closing successfully opened positions...")
                
                # Close all opened positions
                self.close_all_positions(reason="PARTIAL_OPEN_FAILURE")
                
                return False
            
            logger.info(f"✅ All {len(opened_positions)} positions opened successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error opening positions: {e}")
            return False
    
    def monitor_positions(self) -> tuple[bool, str]:
        """
        Monitor positions and check exit conditions
        
        Returns:
            Tuple of (should_close, reason)
        """
        try:
            positions = self.apex_client.get_positions()
            
            if not positions:
                logger.warning("⚠️  No positions found during monitoring")
                # Check if positions were closed manually
                elapsed = self.position_manager.get_time_elapsed()
                if elapsed > 1:  # More than 1 minute since start
                    logger.error("🚨 POSITIONS CLOSED MANUALLY!")
                    logger.error("   All positions were closed outside the bot")
                    logger.error("   Bot will shutdown to prevent issues")
                    return True, "MANUAL_CLOSE"
                return True, "NO_POSITIONS"
            
            should_close, reason = self.position_manager.check_exit_conditions(positions)
            
            return should_close, reason
            
        except Exception as e:
            logger.error(f"❌ Error monitoring positions: {e}")
            return False, "MONITOR_ERROR"
    
    def print_status(self):
        """Print current status report"""
        try:
            positions = self.apex_client.get_positions()
            report = self.position_manager.format_status_report(positions)
            print(report)
            
        except Exception as e:
            logger.error(f"❌ Error generating status report: {e}")
    
    def run_cycle(self) -> bool:
        """
        Run one complete trading cycle
        
        Returns:
            True if successful, False otherwise
        """
        self.cycle_count += 1
        print_cycle_start(self.cycle_count)
        
        # Generate unique cycle ID
        self.current_cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.cycle_count}"
        
        # Start new cycle tracking
        self.position_manager.start_new_cycle()
        self.database.start_cycle(self.current_cycle_id, self.config)
        
        # Open all positions
        if not self.open_all_positions():
            logger.error("❌ Failed to open positions, aborting cycle")
            return False
        
        # Wait for orders to fill and verify positions
        logger.info("⏳ Waiting for orders to fill...")
        time.sleep(5)
        
        # Verify positions were actually opened
        positions = self.apex_client.get_positions()
        if not positions:
            logger.error("❌ CRITICAL: Orders created but NO POSITIONS found!")
            logger.error("   This means orders were NOT FILLED by the exchange")
            logger.error("   Possible causes:")
            logger.error("   1. Market orders rejected due to slippage")
            logger.error("   2. Insufficient liquidity")
            logger.error("   3. Orders still pending (very slow fill)")
            logger.error("")
            logger.error("   Waiting 10 more seconds for delayed fill...")
            time.sleep(10)
            
            # Check again
            positions = self.apex_client.get_positions()
            if not positions:
                logger.error("❌ Still no positions after 15 seconds!")
                logger.error("   Aborting cycle - orders failed to fill")
                return False
            else:
                logger.info(f"✅ Positions finally appeared: {len(positions)} active")
        else:
            logger.info(f"✅ Verified {len(positions)} positions are open")
        
        # Monitor loop
        logger.info("👀 Starting monitoring loop...")
        last_status_time = time.time()
        status_interval = 5 * 60  # 5 minutes in seconds
        
        while self.is_running:
            try:
                # Check exit conditions
                should_close, reason = self.monitor_positions()
                
                # Show current PnL on every check
                try:
                    positions = self.apex_client.get_positions()
                    if positions:
                        total_pnl = self.position_manager.calculate_total_pnl(positions)
                        elapsed = self.position_manager.get_time_elapsed()
                        logger.info(f"💰 PnL: ${total_pnl:+.2f} | Time: {elapsed}/{self.config['TIME_LIMIT_MINUTES']}min | Target: TP=${self.config['TAKE_PROFIT_USD']:+.0f} SL=${self.config['STOP_LOSS_USD']:+.0f}")
                except Exception as e:
                    logger.debug(f"Could not get PnL: {e}")
                
                if should_close and reason != "MONITOR_ERROR":
                    # Check if manual close
                    if reason == "MANUAL_CLOSE":
                        logger.error("")
                        logger.error("=" * 80)
                        logger.error("🚨 MANUAL CLOSURE DETECTED")
                        logger.error("=" * 80)
                        logger.error("   Positions were closed manually on the platform")
                        logger.error("   Bot cannot continue safely - STOPPING")
                        logger.error("=" * 80)
                        logger.error("")
                        self.stop()
                        return False
                    
                    # Get final positions for PnL
                    positions = self.apex_client.get_positions()
                    total_pnl = self.position_manager.calculate_total_pnl(positions)
                    duration = self.position_manager.get_time_elapsed()
                    
                    # Print cycle end
                    print_cycle_end(reason, total_pnl, duration)
                    
                    # Record cycle end in database
                    self.database.end_cycle(self.current_cycle_id, total_pnl, reason, duration)
                    
                    # Close all positions
                    if not self.close_all_positions(reason):
                        logger.error("❌ Some positions failed to close")
                    
                    return True
                
                # Print status every 5 minutes
                current_time = time.time()
                if current_time - last_status_time >= status_interval:
                    self.print_status()
                    last_status_time = current_time
                
                # Sleep before next check (30 seconds)
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.warning("⚠️  Keyboard interrupt received")
                raise
            
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(30)
        
        return False
    
    def start(self):
        """Start the bot main loop"""
        try:
            self.is_running = True
            
            # Validate symbols
            if not self.validate_symbols():
                logger.error("❌ Symbol validation failed, cannot start bot")
                return
            
            # Check for existing positions (recovery)
            if self.check_existing_positions():
                logger.warning("⚠️  Existing positions found - closing them first...")
                self.close_all_positions(reason="RECOVERY")
                time.sleep(5)
            
            # Main loop
            while self.is_running:
                try:
                    # Run one cycle
                    if not self.run_cycle():
                        logger.error("❌ Cycle failed")
                    
                    # Wait before reopening
                    reentry_delay = int(self.config['REENTRY_DELAY_MINUTES'])
                    print_waiting_reentry(reentry_delay)
                    
                    # Sleep with countdown
                    for remaining in range(reentry_delay, 0, -1):
                        if not self.is_running:
                            break
                        if remaining % 2 == 0:  # Log every 2 minutes
                            logger.info(f"⏳ Reopening in {remaining} minutes...")
                        time.sleep(60)
                    
                except KeyboardInterrupt:
                    logger.warning("⚠️  Keyboard interrupt - shutting down gracefully...")
                    break
                
                except Exception as e:
                    logger.error(f"❌ Unexpected error in main loop: {e}")
                    print_error("MAIN_LOOP", str(e))
                    logger.info("⏳ Waiting 60 seconds before retry...")
                    time.sleep(60)
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            print_error("FATAL", str(e))
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Stopping bot...")
        self.is_running = False
        
        # Try to close any open positions
        try:
            positions = self.apex_client.get_positions()
            if positions:
                logger.info("🔒 Closing open positions...")
                self.close_all_positions(reason="SHUTDOWN")
        except Exception as e:
            logger.error(f"❌ Error closing positions during shutdown: {e}")
        
        logger.info("✅ Bot stopped")
