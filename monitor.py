"""
Monitoring System
Handles logging, notifications, and status reporting
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Configure logging for the bot"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"bot_{timestamp}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    
    # Set levels for specific loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("🚀 APEX OMNI TRADING BOT - STARTING")
    logger.info("=" * 80)
    logger.info(f"📝 Logging to: {log_file}")
    
    return logger


def print_banner():
    """Print startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║               APEX OMNI TRADING BOT v1.0                      ║
    ║                                                               ║
    ║           Automated Long/Short Trading System                 ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_config_summary(config: dict):
    """Print configuration summary"""
    logger = logging.getLogger(__name__)
    
    logger.info("")
    logger.info("⚙️  CONFIGURATION:")
    logger.info("-" * 80)
    logger.info(f"   Position Size:  ${config['POSITION_SIZE_USD']:,.2f} USD")
    logger.info(f"   Stop Loss:      ${config['STOP_LOSS_USD']:+,.2f} USD")
    logger.info(f"   Take Profit:    ${config['TAKE_PROFIT_USD']:+,.2f} USD")
    logger.info(f"   Time Limit:     {config['TIME_LIMIT_MINUTES']} minutes")
    logger.info(f"   Leverage:       {config['LEVERAGE']}x")
    logger.info(f"   Reentry Delay:  {config['REENTRY_DELAY_MINUTES']} minutes")
    logger.info(f"   Long Symbols:   {config['LONG_SYMBOLS']}")
    logger.info(f"   Short Symbols:  {config['SHORT_SYMBOLS']}")
    logger.info("-" * 80)
    logger.info("")


def print_startup_checks(symbols_long: list, symbols_short: list, valid: bool):
    """Print startup validation results"""
    logger = logging.getLogger(__name__)
    
    logger.info("🔍 STARTUP VALIDATION:")
    logger.info("-" * 80)
    
    if valid:
        logger.info("   ✅ All symbols validated")
        logger.info(f"   📈 Long:  {', '.join(symbols_long)}")
        logger.info(f"   📉 Short: {', '.join(symbols_short)}")
    else:
        logger.error("   ❌ Symbol validation failed")
    
    logger.info("-" * 80)
    logger.info("")


def print_cycle_start(cycle_num: int):
    """Print cycle start notification"""
    logger = logging.getLogger(__name__)
    
    logger.info("")
    logger.info("=" * 80)
    logger.info(f"🔄 STARTING TRADING CYCLE #{cycle_num}")
    logger.info("=" * 80)
    logger.info("")


def print_cycle_end(reason: str, total_pnl: float, duration_minutes: int):
    """Print cycle end notification"""
    logger = logging.getLogger(__name__)
    
    reason_messages = {
        'STOP_LOSS': '🛑 STOP LOSS TRIGGERED',
        'TAKE_PROFIT': '🎯 TAKE PROFIT TRIGGERED',
        'TIME_LIMIT': '⏰ TIME LIMIT REACHED'
    }
    
    message = reason_messages.get(reason, f"📍 CYCLE ENDED: {reason}")
    
    logger.info("")
    logger.info("=" * 80)
    logger.info(message)
    logger.info(f"   Final PnL: ${total_pnl:+,.2f} USD")
    logger.info(f"   Duration:  {duration_minutes} minutes")
    logger.info("=" * 80)
    logger.info("")


def print_waiting_reentry(minutes: int):
    """Print reentry wait notification"""
    logger = logging.getLogger(__name__)
    
    logger.info("")
    logger.info(f"⏳ Waiting {minutes} minutes before reopening positions...")
    logger.info("")


def print_error(error_type: str, error_message: str):
    """Print error notification"""
    logger = logging.getLogger(__name__)
    
    logger.error("")
    logger.error("=" * 80)
    logger.error(f"❌ ERROR: {error_type}")
    logger.error(f"   Message: {error_message}")
    logger.error("=" * 80)
    logger.error("")


def print_shutdown():
    """Print shutdown message"""
    logger = logging.getLogger(__name__)
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("🛑 BOT SHUTTING DOWN")
    logger.info("=" * 80)
    logger.info("")
