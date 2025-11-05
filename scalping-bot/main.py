"""
Scalping Bot - Main Entry Point
CLI and main trading loop
"""

import argparse
import logging
import time
import sys
import signal
from pathlib import Path
from datetime import datetime
import yaml
import pandas as pd

from core.indicators import IndicatorCalculator
from core.strategies import create_strategy
from core.data_provider import create_data_provider
from core.execution import create_executor
from core.position_state import PositionStateManager, PositionState
from core.utils import normalize_symbol, calculate_pnl, log_trade

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


class ScalpingBot:
    """
    Main scalping bot orchestrator
    Runs one strategy on one symbol
    """
    
    def __init__(self, config: Dict):
        """
        Initialize bot
        
        Args:
            config: Full configuration dictionary
        """
        self.config = config
        self.general = config['general']
        self.running = False
        self.shutdown = False
        
        # Extract settings
        self.symbol = normalize_symbol(self.general['symbol'])
        self.strategy_name = self.general['strategy']
        self.timeframe = self.general['timeframe']
        self.use_long = self.general['use_long']
        self.use_short = self.general['use_short']
        self.order_value_usd = self.general['order_value_usd']
        
        # Mode
        self.mode = self.general.get('mode', 'paper')  # 'paper' or 'live'
        self.data_source = self.general.get('data_source', 'csv')  # 'live' or 'csv'
        
        logger.info(f"🤖 Initializing Scalping Bot")
        logger.info(f"   Symbol: {self.symbol}")
        logger.info(f"   Strategy: {self.strategy_name}")
        logger.info(f"   Timeframe: {self.timeframe}")
        logger.info(f"   Mode: {self.mode.upper()}")
        logger.info(f"   Data Source: {self.data_source.upper()}")
        logger.info(f"   Order Value: ${self.order_value_usd}")
        
        # Initialize components
        self._init_components()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _init_components(self):
        """Initialize all bot components"""
        
        # Initialize ApeX client if needed
        self.apex_client = None
        if self.mode == 'live' or self.data_source == 'live':
            from apex_client import ApexClient
            
            apex_config = self.config.get('apex', {})
            if not apex_config.get('api_key'):
                raise ValueError("ApeX credentials required for live mode/data. Add 'apex' section to config.")
            
            self.apex_client = ApexClient(apex_config)
            logger.info("✅ ApeX client initialized")
        
        # Data provider
        self.data_provider = create_data_provider(
            self.data_source,
            apex_client=self.apex_client,
            csv_folder=self.general.get('csv_folder', './data')
        )
        logger.info(f"✅ Data provider initialized ({self.data_source})")
        
        # Executor
        self.executor = create_executor(
            self.mode,
            config=self.general,
            apex_client=self.apex_client,
            data_provider=self.data_provider
        )
        logger.info(f"✅ Executor initialized ({self.mode})")
        
        # Strategy
        strategy_params = self.config['strategies'][self.strategy_name]
        self.strategy = create_strategy(self.strategy_name, strategy_params)
        logger.info(f"✅ Strategy {self.strategy_name} initialized")
        
        # Position state manager
        self.state_manager = PositionStateManager(
            state_file=self.general.get('state_file', './state/position_state.json')
        )
        logger.info(f"✅ State manager initialized")
        
        # Trade logger
        self.trade_log_path = Path(self.general.get('trade_log', './logs/trades.csv'))
        self.trade_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file if doesn't exist
        if not self.trade_log_path.exists():
            with open(self.trade_log_path, 'w') as f:
                f.write('timestamp,symbol,strategy,side,entry_price,exit_price,quantity,'
                       'tp_price,sl_price,exit_reason,pnl_usd,fee_usd,net_pnl_usd,'
                       'atr,rsi,ema_fast,ema_slow\n')
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.warning(f"⚠️  Received signal {signum}, shutting down...")
        self.shutdown = True
        self.running = False
        
    def run(self):
        """Main bot loop"""
        
        self.running = True
        logger.info("🚀 Starting bot main loop...")
        
        # Check for existing position on startup
        if self.state_manager.has_position():
            logger.warning("⚠️  Found existing position on startup, resuming...")
        
        poll_interval = self._get_poll_interval()
        
        while self.running and not self.shutdown:
            try:
                # Main logic
                if self.state_manager.has_position():
                    self._monitor_position()
                else:
                    self._check_entry_signal()
                
                # Sleep until next check
                time.sleep(poll_interval)
                
            except KeyboardInterrupt:
                logger.warning("⚠️  Keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}", exc_info=True)
                time.sleep(poll_interval)
        
        logger.info("👋 Bot stopped")
        
    def _get_poll_interval(self) -> int:
        """Get poll interval based on timeframe"""
        intervals = {
            '1m': 10,
            '5m': 30,
            '15m': 60,
            '1h': 180,
            '4h': 600,
        }
        return intervals.get(self.timeframe, 60)
    
    def _check_entry_signal(self):
        """Check for entry signals"""
        
        try:
            # Fetch candles
            df = self.data_provider.get_candles(self.symbol, self.timeframe, limit=200)
            
            if len(df) < 50:
                logger.warning(f"Insufficient data: {len(df)} candles")
                return
            
            # Calculate indicators
            strategy_params = self.config['strategies'][self.strategy_name]
            ema_fast = strategy_params.get('ema_fast', 20)
            ema_slow = strategy_params.get('ema_slow', 50)
            
            calc = IndicatorCalculator(df)
            df = calc.calculate_all(
                ema_fast=ema_fast,
                ema_slow=ema_slow,
                rsi_period=14,
                atr_period=10,
                atr_ma_period=20,
                vol_ma_period=20
            )
            
            # Check signal
            signal = self.strategy.check_signal(df, self.use_long, self.use_short)
            
            if signal.direction != 'NONE':
                logger.info(f"🎯 Signal detected: {signal.reason}")
                self._enter_position(signal, df)
            else:
                logger.debug(f"No signal: {signal.reason}")
                
        except Exception as e:
            logger.error(f"Error checking entry signal: {e}", exc_info=True)
    
    def _enter_position(self, signal, df: pd.DataFrame):
        """Enter a position based on signal"""
        
        try:
            # Execute entry
            result = self.executor.enter_position(
                symbol=self.symbol,
                side=signal.direction,
                entry_price=signal.entry_price,
                tp_price=signal.tp_price,
                sl_price=signal.sl_price,
                order_value_usd=self.order_value_usd
            )
            
            if not result.get('success'):
                logger.error(f"Failed to enter position: {result.get('error')}")
                return
            
            # Save position state
            current = df.iloc[-1]
            position = PositionState(
                symbol=self.symbol,
                strategy=self.strategy_name,
                side=signal.direction,
                entry_price=result['entry_price'],
                entry_time=datetime.now().isoformat(),
                quantity=result['quantity'],
                tp_price=signal.tp_price,
                sl_price=signal.sl_price,
                atr_value=signal.atr_value,
                order_value_usd=self.order_value_usd,
                entry_reason=signal.reason,
                indicators={
                    'rsi': float(current.get('rsi_14', 0)),
                    'ema_fast': float(current.get(f'ema_{self.config["strategies"][self.strategy_name]["ema_fast"]}', 0)),
                    'ema_slow': float(current.get(f'ema_{self.config["strategies"][self.strategy_name]["ema_slow"]}', 0)),
                }
            )
            
            self.state_manager.open_position(position)
            
            logger.info(f"✅ Position opened successfully")
            
        except Exception as e:
            logger.error(f"Error entering position: {e}", exc_info=True)
    
    def _monitor_position(self):
        """Monitor open position for TP/SL"""
        
        try:
            position = self.state_manager.get_position()
            
            if not position:
                logger.warning("No position to monitor")
                return
            
            # Check if TP/SL hit
            exit_result = self.executor.check_exit(
                symbol=position.symbol,
                side=position.side,
                entry_price=position.entry_price,
                tp_price=position.tp_price,
                sl_price=position.sl_price
            )
            
            if exit_result:
                exit_reason, exit_price = exit_result
                self._close_position(exit_reason, exit_price)
            else:
                logger.debug(f"Position monitoring: {position.symbol} {position.side} @ ${position.entry_price}")
                
        except Exception as e:
            logger.error(f"Error monitoring position: {e}", exc_info=True)
    
    def _close_position(self, exit_reason: str, exit_price: float):
        """Close position and log trade"""
        
        try:
            position = self.state_manager.get_position()
            
            if not position:
                logger.warning("No position to close")
                return
            
            # Calculate PnL
            pnl_data = calculate_pnl(
                entry_price=position.entry_price,
                exit_price=exit_price,
                quantity=position.quantity,
                side=position.side,
                fee_rate=self.general.get('fee_taker', 0.0005)
            )
            
            # Log trade
            log_trade(
                symbol=position.symbol,
                strategy=position.strategy,
                side=position.side,
                entry=position.entry_price,
                exit=exit_price,
                qty=position.quantity,
                tp=position.tp_price,
                sl=position.sl_price,
                exit_reason=exit_reason,
                pnl_data=pnl_data,
                indicators=position.indicators
            )
            
            # Write to CSV
            with open(self.trade_log_path, 'a') as f:
                f.write(f"{datetime.now().isoformat()},{position.symbol},{position.strategy},"
                       f"{position.side},{position.entry_price},{exit_price},{position.quantity},"
                       f"{position.tp_price},{position.sl_price},{exit_reason},"
                       f"{pnl_data['pnl_usd']:.2f},{pnl_data['fee_usd']:.2f},{pnl_data['net_pnl_usd']:.2f},"
                       f"{position.atr_value},{position.indicators.get('rsi', '')},"
                       f"{position.indicators.get('ema_fast', '')},{position.indicators.get('ema_slow', '')}\n")
            
            # Close position in state
            self.state_manager.close_position()
            
            logger.info(f"✅ Trade logged to {self.trade_log_path}")
            
        except Exception as e:
            logger.error(f"Error closing position: {e}", exc_info=True)


def load_config(config_file: str) -> Dict:
    """Load configuration from YAML file"""
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def merge_cli_args(config: Dict, args: argparse.Namespace) -> Dict:
    """Merge CLI arguments into config"""
    
    # Override general settings
    if args.symbol:
        config['general']['symbol'] = args.symbol
    if args.strategy:
        config['general']['strategy'] = args.strategy
    if args.timeframe:
        config['general']['timeframe'] = args.timeframe
    if args.order_value_usd:
        config['general']['order_value_usd'] = args.order_value_usd
    if args.mode:
        config['general']['mode'] = args.mode
    if args.data_source:
        config['general']['data_source'] = args.data_source
    
    # Override use_long/use_short
    if args.use_long is not None:
        config['general']['use_long'] = args.use_long
    if args.use_short is not None:
        config['general']['use_short'] = args.use_short
    
    # Override strategy params
    if args.strategy and args.strategy in config['strategies']:
        strategy_config = config['strategies'][args.strategy]
        
        if args.tp_atr:
            strategy_config['tp_atr_mult'] = args.tp_atr
        if args.sl_atr:
            strategy_config['sl_atr_mult'] = args.sl_atr
    
    return config


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Scalping Bot - Directional Trading')
    
    # Main arguments
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to config file (default: config.yaml)')
    parser.add_argument('--symbol', type=str,
                       help='Trading symbol (e.g., BTCUSDT, BTC-USDT)')
    parser.add_argument('--strategy', type=str, choices=['C1', 'C2', 'C4'],
                       help='Strategy to use (C1, C2, C4)')
    parser.add_argument('--timeframe', type=str, choices=['1m', '5m', '15m', '1h', '4h'],
                       help='Candle timeframe (15m, 1h)')
    parser.add_argument('--order_value_usd', type=float,
                       help='Order value in USD')
    parser.add_argument('--mode', type=str, choices=['paper', 'live'],
                       help='Trading mode: paper or live')
    parser.add_argument('--data_source', type=str, choices=['live', 'csv'],
                       help='Data source: live or csv')
    
    # Strategy overrides
    parser.add_argument('--tp_atr', type=float,
                       help='TP ATR multiplier (override)')
    parser.add_argument('--sl_atr', type=float,
                       help='SL ATR multiplier (override)')
    
    # Long/Short toggles
    parser.add_argument('--use_long', type=lambda x: x.lower() == 'true', default=None,
                       help='Enable long signals (true/false)')
    parser.add_argument('--use_short', type=lambda x: x.lower() == 'true', default=None,
                       help='Enable short signals (true/false)')
    
    args = parser.parse_args()
    
    # Load config
    try:
        config = load_config(args.config)
        logger.info(f"✅ Loaded config from {args.config}")
    except FileNotFoundError:
        logger.error(f"❌ Config file not found: {args.config}")
        logger.error("   Create config.yaml or specify --config path")
        sys.exit(1)
    
    # Merge CLI args
    config = merge_cli_args(config, args)
    
    # Validate required settings
    if 'symbol' not in config['general'] or not config['general']['symbol']:
        logger.error("❌ Symbol required. Set in config.yaml or use --symbol")
        sys.exit(1)
    
    if 'strategy' not in config['general'] or not config['general']['strategy']:
        logger.error("❌ Strategy required. Set in config.yaml or use --strategy")
        sys.exit(1)
    
    # Initialize and run bot
    try:
        bot = ScalpingBot(config)
        bot.run()
    except KeyboardInterrupt:
        logger.info("👋 Shutdown by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
