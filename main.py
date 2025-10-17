#!/usr/bin/env python3
"""
Apex Omni Trading Bot - Main Entry Point
"""

import sys
import signal
from pathlib import Path

from monitor import setup_logging, print_banner, print_config_summary
from bot import TradingBot


def load_config(config_file: str = "config.txt") -> dict:
    """
    Load configuration from text file
    
    Args:
        config_file: Path to config file
        
    Returns:
        Configuration dictionary
    """
    config = {}
    
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert numeric values
                if key in ['POSITION_SIZE_USD', 'STOP_LOSS_USD', 'TAKE_PROFIT_USD']:
                    config[key] = float(value)
                elif key in ['TIME_LIMIT_MINUTES', 'LEVERAGE', 'REENTRY_DELAY_MINUTES', 'NETWORK_ID']:
                    config[key] = int(value)
                else:
                    config[key] = value
    
    # Validate required fields
    required_fields = [
        'API_KEY', 'API_SECRET', 'API_PASSPHRASE', 'ZK_SEEDS',
        'POSITION_SIZE_USD', 'STOP_LOSS_USD', 'TAKE_PROFIT_USD',
        'TIME_LIMIT_MINUTES', 'LEVERAGE', 'REENTRY_DELAY_MINUTES',
        'LONG_SYMBOLS', 'SHORT_SYMBOLS'
    ]
    
    missing_fields = [field for field in required_fields if field not in config]
    if missing_fields:
        raise ValueError(f"Missing required configuration fields: {missing_fields}")
    
    return config


def main():
    """Main entry point"""
    try:
        # Print banner
        print_banner()
        
        # Setup logging
        logger = setup_logging()
        
        # Load configuration
        import logging
        logger = logging.getLogger(__name__)
        logger.info("📁 Loading configuration...")
        config = load_config("config.txt")
        print_config_summary(config)
        
        # Create bot instance
        logger.info("🤖 Creating bot instance...")
        bot = TradingBot(config)
        
        # Setup signal handlers for graceful shutdown
        shutdown_count = [0]  # Use list to modify in nested function
        
        def signal_handler(sig, frame):
            shutdown_count[0] += 1
            
            if shutdown_count[0] == 1:
                logger.info("")
                logger.info("="*80)
                logger.info("⚠️  CTRL+C PRESSED - GRACEFUL SHUTDOWN")
                logger.info("="*80)
                logger.info("   Bot will close all positions and stop safely")
                logger.info("   This may take 10-30 seconds...")
                logger.info("")
                logger.info("   💡 Press Ctrl+C again to FORCE KILL (not recommended!)")
                logger.info("="*80)
                logger.info("")
                bot.stop(close_positions=True)
            elif shutdown_count[0] >= 2:
                logger.error("")
                logger.error("="*80)
                logger.error("🚨 FORCE KILL - EXITING IMMEDIATELY!")
                logger.error("="*80)
                logger.error("⚠️  Positions were NOT closed!")
                logger.error("   Please check your exchange and close manually if needed")
                logger.error("="*80)
                logger.error("")
                import os
                os._exit(1)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start bot
        logger.info("🚀 Starting bot...")
        logger.info("")
        bot.start()
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("Please create a config.txt file with your settings.")
        sys.exit(1)
    
    except ValueError as e:
        print(f"\n❌ CONFIGURATION ERROR: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Keyboard interrupt - exiting...")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
