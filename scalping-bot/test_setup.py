"""
Quick test script to verify bot setup
Run this to check if all modules load correctly
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all core modules can be imported"""
    try:
        logger.info("Testing imports...")
        
        from core import indicators
        logger.info("✅ core.indicators")
        
        from core import strategies
        logger.info("✅ core.strategies")
        
        from core import data_provider
        logger.info("✅ core.data_provider")
        
        from core import execution
        logger.info("✅ core.execution")
        
        from core import position_state
        logger.info("✅ core.position_state")
        
        from core import utils
        logger.info("✅ core.utils")
        
        logger.info("")
        logger.info("✅ All core modules loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False


def test_indicator_calculation():
    """Test indicator calculations"""
    try:
        logger.info("")
        logger.info("Testing indicator calculations...")
        
        import pandas as pd
        import numpy as np
        from core.indicators import ema, rsi, atr, IndicatorCalculator
        
        # Create dummy data
        dates = pd.date_range('2025-01-01', periods=100, freq='15min')
        prices = 65000 + np.random.randn(100) * 100
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': prices + 50,
            'low': prices - 50,
            'close': prices,
            'volume': np.random.uniform(1000000, 2000000, 100)
        })
        
        # Calculate indicators
        calc = IndicatorCalculator(df)
        df = calc.calculate_all(ema_fast=20, ema_slow=50)
        
        # Check if indicators exist
        assert 'ema_20' in df.columns
        assert 'ema_50' in df.columns
        assert 'rsi_14' in df.columns
        assert 'atr_10' in df.columns
        
        logger.info("✅ Indicator calculations work!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Indicator test failed: {e}")
        return False


def test_strategy_signal():
    """Test strategy signal generation"""
    try:
        logger.info("")
        logger.info("Testing strategy signals...")
        
        import pandas as pd
        import numpy as np
        from core.indicators import IndicatorCalculator
        from core.strategies import create_strategy
        
        # Create dummy data
        dates = pd.date_range('2025-01-01', periods=100, freq='15min')
        prices = 65000 + np.cumsum(np.random.randn(100) * 10)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': prices + 50,
            'low': prices - 50,
            'close': prices,
            'volume': np.random.uniform(1000000, 2000000, 100)
        })
        
        # Calculate indicators
        calc = IndicatorCalculator(df)
        df = calc.calculate_all(ema_fast=20, ema_slow=50)
        
        # Test C2 strategy
        params = {
            'ema_fast': 9,
            'ema_slow': 21,
            'rsi_min': 45,
            'rsi_max': 60,
            'tp_atr_mult': 1.4,
            'sl_atr_mult': 0.6,
            'filter_atr': True,
            'anchor_vol_mult': 1.5
        }
        
        strategy = create_strategy('C2', params)
        signal = strategy.check_signal(df, use_long=True, use_short=True)
        
        logger.info(f"Signal: {signal.direction} - {signal.reason}")
        logger.info("✅ Strategy signal generation works!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test config loading"""
    try:
        logger.info("")
        logger.info("Testing config loading...")
        
        import yaml
        
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'general' in config
        assert 'strategies' in config
        assert 'C1' in config['strategies']
        assert 'C2' in config['strategies']
        assert 'C4' in config['strategies']
        
        logger.info("✅ Config loading works!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Config test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("========================================")
    logger.info("  Scalping Bot - Setup Test")
    logger.info("========================================")
    
    tests = [
        test_imports,
        test_indicator_calculation,
        test_strategy_signal,
        test_config_loading,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    logger.info("")
    logger.info("========================================")
    if all(results):
        logger.info("✅ All tests passed! Bot is ready.")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Edit config.yaml with your settings")
        logger.info("  2. Run: python main.py --symbol BTCUSDT --strategy C2 --mode paper --data_source csv")
        return 0
    else:
        logger.error("❌ Some tests failed. Check errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
