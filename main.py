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
        logger.info("📁 Loading configuration...")
        config = load_config("config.txt")
        print_config_summary(config)
        
        # Create bot instance
        logger.info("🤖 Creating bot instance...")
        bot = TradingBot(config)
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info(f"\n⚠️  Received signal {sig}, shutting down gracefully...")
            bot.stop()
            sys.exit(0)
        
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
