"""
Trading Strategies: C1, C2, C4
Fixed logic with configurable parameters
"""

import pandas as pd
import logging
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """Trading signal"""
    direction: str  # 'LONG', 'SHORT', or 'NONE'
    entry_price: float
    tp_price: float
    sl_price: float
    atr_value: float
    reason: str
    
    
class StrategyBase:
    """Base class for all strategies"""
    
    def __init__(self, params: Dict):
        """
        Initialize strategy with parameters
        
        Args:
            params: Strategy parameters dictionary
        """
        self.params = params
        self.name = self.__class__.__name__
        
    def check_signal(self, df: pd.DataFrame, use_long: bool = True, 
                     use_short: bool = True) -> Signal:
        """
        Check for trading signal
        
        Args:
            df: DataFrame with OHLCV and indicators
            use_long: Allow long signals
            use_short: Allow short signals
            
        Returns:
            Signal object
        """
        raise NotImplementedError("Must implement check_signal()")
        
    def _calculate_tp_sl(self, entry_price: float, atr_value: float, 
                         direction: str) -> Tuple[float, float]:
        """
        Calculate TP and SL prices based on ATR multiples
        
        Args:
            entry_price: Entry price
            atr_value: Current ATR value
            direction: 'LONG' or 'SHORT'
            
        Returns:
            Tuple of (tp_price, sl_price)
        """
        tp_mult = self.params.get('tp_atr_mult', 1.0)
        sl_mult = self.params.get('sl_atr_mult', 0.5)
        
        if direction == 'LONG':
            tp_price = entry_price + (atr_value * tp_mult)
            sl_price = entry_price - (atr_value * sl_mult)
        else:  # SHORT
            tp_price = entry_price - (atr_value * tp_mult)
            sl_price = entry_price + (atr_value * sl_mult)
            
        return tp_price, sl_price


class C1Strategy(StrategyBase):
    """
    C1 — Breakout Falso (Reversão curta)
    
    Default params (from backtest):
        ema_fast: 20, ema_slow: 50
        rsi_min: 40, rsi_max: 65
        tp_atr_mult: 1.8, sl_atr_mult: 0.8
        filter_volume: True, volume_ma_mult: 1.2
        range_lookback: 12
    """
    
    def check_signal(self, df: pd.DataFrame, use_long: bool = True, 
                     use_short: bool = True) -> Signal:
        """Check for C1 fakeout breakout signal"""
        
        if len(df) < self.params.get('range_lookback', 12) + 2:
            return Signal('NONE', 0, 0, 0, 0, 'Insufficient data')
        
        # Get parameters
        ema_fast = self.params.get('ema_fast', 20)
        ema_slow = self.params.get('ema_slow', 50)
        rsi_min = self.params.get('rsi_min', 40)
        rsi_max = self.params.get('rsi_max', 65)
        filter_volume = self.params.get('filter_volume', True)
        volume_ma_mult = self.params.get('volume_ma_mult', 1.2)
        range_lookback = self.params.get('range_lookback', 12)
        
        # Current bar (n) and previous bar (n-1)
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Get indicator values
        ema_f = current[f'ema_{ema_fast}']
        ema_s = current[f'ema_{ema_slow}']
        rsi_val = current[f'rsi_14']
        vol = current['volume']
        vol_ma = current[f'vol_ma_20']
        atr_val = current['atr_10']
        
        # Check for NaN
        if pd.isna([ema_f, ema_s, rsi_val, atr_val]).any():
            return Signal('NONE', 0, 0, 0, 0, 'Indicators not ready')
        
        # Long signal logic
        if use_long:
            # Calculate range minimum (last 12 bars)
            range_low = df['low'].iloc[-range_lookback:].min()
            
            # Fakeout condition: previous close < range_low AND current close > range_low
            fakeout = previous['close'] < range_low and current['close'] > range_low
            
            # Filters
            trend_ok = ema_f > ema_s
            rsi_ok = rsi_min <= rsi_val <= rsi_max
            vol_ok = (vol > volume_ma_mult * vol_ma) if filter_volume else True
            
            if fakeout and trend_ok and rsi_ok and vol_ok:
                entry = current['close']
                tp, sl = self._calculate_tp_sl(entry, atr_val, 'LONG')
                reason = (f"C1 LONG: fakeout confirmado (close_prev={previous['close']:.2f} < "
                         f"range_min={range_low:.2f} < close={current['close']:.2f}), "
                         f"EMA{ema_fast}={ema_f:.2f} > EMA{ema_slow}={ema_s:.2f}, "
                         f"RSI={rsi_val:.1f}")
                return Signal('LONG', entry, tp, sl, atr_val, reason)
        
        # Short signal logic
        if use_short:
            # Calculate range maximum (last 12 bars)
            range_high = df['high'].iloc[-range_lookback:].max()
            
            # Fakeout condition: previous close > range_high AND current close < range_high
            fakeout = previous['close'] > range_high and current['close'] < range_high
            
            # Filters
            trend_ok = ema_f < ema_s
            rsi_ok = rsi_min <= rsi_val <= rsi_max
            vol_ok = (vol > volume_ma_mult * vol_ma) if filter_volume else True
            
            if fakeout and trend_ok and rsi_ok and vol_ok:
                entry = current['close']
                tp, sl = self._calculate_tp_sl(entry, atr_val, 'SHORT')
                reason = (f"C1 SHORT: fakeout confirmado (close_prev={previous['close']:.2f} > "
                         f"range_max={range_high:.2f} > close={current['close']:.2f}), "
                         f"EMA{ema_fast}={ema_f:.2f} < EMA{ema_slow}={ema_s:.2f}, "
                         f"RSI={rsi_val:.1f}")
                return Signal('SHORT', entry, tp, sl, atr_val, reason)
        
        return Signal('NONE', 0, 0, 0, 0, 'No C1 signal')


class C2Strategy(StrategyBase):
    """
    C2 — Candle de Expansão (Momentum scalp)
    
    Default params (from backtest):
        ema_fast: 9, ema_slow: 21
        rsi_min: 45, rsi_max: 60
        tp_atr_mult: 1.4, sl_atr_mult: 0.6
        filter_atr: True
        anchor_vol_mult: 1.5
    """
    
    def check_signal(self, df: pd.DataFrame, use_long: bool = True, 
                     use_short: bool = True) -> Signal:
        """Check for C2 expansion candle signal"""
        
        if len(df) < 3:
            return Signal('NONE', 0, 0, 0, 0, 'Insufficient data')
        
        # Get parameters
        ema_fast = self.params.get('ema_fast', 9)
        ema_slow = self.params.get('ema_slow', 21)
        rsi_min = self.params.get('rsi_min', 45)
        rsi_max = self.params.get('rsi_max', 60)
        filter_atr = self.params.get('filter_atr', True)
        anchor_vol_mult = self.params.get('anchor_vol_mult', 1.5)
        
        # Current bar (n) and anchor bar (n-1)
        current = df.iloc[-1]
        anchor = df.iloc[-2]
        
        # Get indicator values
        ema_f = current[f'ema_{ema_fast}']
        ema_s = current[f'ema_{ema_slow}']
        rsi_val = current[f'rsi_14']
        atr_val = current['atr_10']
        atr_ma_val = current['atr_ma_20']
        vol_ma = anchor[f'vol_ma_20']
        
        # Check for NaN
        if pd.isna([ema_f, ema_s, rsi_val, atr_val, atr_ma_val]).any():
            return Signal('NONE', 0, 0, 0, 0, 'Indicators not ready')
        
        # Check if anchor bar is valid
        anchor_range = anchor['high'] - anchor['low']
        anchor_atr = anchor['atr_10']
        anchor_vol = anchor['volume']
        
        is_anchor_valid = (anchor_range > anchor_atr and 
                          anchor_vol > anchor_vol_mult * vol_ma)
        
        if not is_anchor_valid:
            return Signal('NONE', 0, 0, 0, 0, 'No valid anchor candle')
        
        # Long signal logic
        if use_long:
            # Breakout condition: current close > anchor high
            breakout = current['close'] > anchor['high']
            
            # Filters
            trend_ok = ema_f > ema_s
            rsi_ok = rsi_min <= rsi_val <= rsi_max
            atr_ok = (atr_val > atr_ma_val) if filter_atr else True
            
            if breakout and trend_ok and rsi_ok and atr_ok:
                entry = current['close']
                tp, sl = self._calculate_tp_sl(entry, atr_val, 'LONG')
                reason = (f"C2 LONG: âncora confirmada (range={anchor_range:.2f} > ATR={anchor_atr:.2f}, "
                         f"vol={anchor_vol:.0f} > {anchor_vol_mult}×VolMA), "
                         f"breakout: close={current['close']:.2f} > anchor_high={anchor['high']:.2f}, "
                         f"EMA{ema_fast}={ema_f:.2f} > EMA{ema_slow}={ema_s:.2f}, RSI={rsi_val:.1f}")
                return Signal('LONG', entry, tp, sl, atr_val, reason)
        
        # Short signal logic
        if use_short:
            # Breakout condition: current close < anchor low
            breakout = current['close'] < anchor['low']
            
            # Filters
            trend_ok = ema_f < ema_s
            rsi_ok = rsi_min <= rsi_val <= rsi_max
            atr_ok = (atr_val > atr_ma_val) if filter_atr else True
            
            if breakout and trend_ok and rsi_ok and atr_ok:
                entry = current['close']
                tp, sl = self._calculate_tp_sl(entry, atr_val, 'SHORT')
                reason = (f"C2 SHORT: âncora confirmada (range={anchor_range:.2f} > ATR={anchor_atr:.2f}, "
                         f"vol={anchor_vol:.0f} > {anchor_vol_mult}×VolMA), "
                         f"breakout: close={current['close']:.2f} < anchor_low={anchor['low']:.2f}, "
                         f"EMA{ema_fast}={ema_f:.2f} < EMA{ema_slow}={ema_s:.2f}, RSI={rsi_val:.1f}")
                return Signal('SHORT', entry, tp, sl, atr_val, reason)
        
        return Signal('NONE', 0, 0, 0, 0, 'No C2 signal')


class C4Strategy(StrategyBase):
    """
    C4 — Pullback na Tendência (Trend scalp)
    
    Default params (from backtest):
        ema_fast: 13, ema_slow: 34
        rsi_min: 47, rsi_max: 57
        tp_atr_mult: 1.0, sl_atr_mult: 0.5
        filter_pullback: True
    """
    
    def check_signal(self, df: pd.DataFrame, use_long: bool = True, 
                     use_short: bool = True) -> Signal:
        """Check for C4 pullback trend signal"""
        
        if len(df) < 2:
            return Signal('NONE', 0, 0, 0, 0, 'Insufficient data')
        
        # Get parameters
        ema_fast = self.params.get('ema_fast', 13)
        ema_slow = self.params.get('ema_slow', 34)
        rsi_min = self.params.get('rsi_min', 47)
        rsi_max = self.params.get('rsi_max', 57)
        filter_pullback = self.params.get('filter_pullback', True)
        
        # Current bar
        current = df.iloc[-1]
        
        # Get indicator values
        ema_f = current[f'ema_{ema_fast}']
        ema_s = current[f'ema_{ema_slow}']
        rsi_val = current[f'rsi_14']
        atr_val = current['atr_10']
        close = current['close']
        
        # Check for NaN
        if pd.isna([ema_f, ema_s, rsi_val, atr_val]).any():
            return Signal('NONE', 0, 0, 0, 0, 'Indicators not ready')
        
        # Long signal logic
        if use_long:
            # Trend: EMA_fast > EMA_slow
            trend_ok = ema_f > ema_s
            
            # Pullback: close < EMA_fast (if filter enabled)
            pullback_ok = (close < ema_f) if filter_pullback else True
            
            # RSI filter
            rsi_ok = rsi_min <= rsi_val <= rsi_max
            
            if trend_ok and pullback_ok and rsi_ok:
                entry = close
                tp, sl = self._calculate_tp_sl(entry, atr_val, 'LONG')
                reason = (f"C4 LONG: tendência EMA{ema_fast}={ema_f:.2f} > EMA{ema_slow}={ema_s:.2f}, "
                         f"pullback: close={close:.2f} < EMA{ema_fast}, RSI={rsi_val:.1f}")
                return Signal('LONG', entry, tp, sl, atr_val, reason)
        
        # Short signal logic
        if use_short:
            # Trend: EMA_fast < EMA_slow
            trend_ok = ema_f < ema_s
            
            # Pullback: close > EMA_fast (if filter enabled)
            pullback_ok = (close > ema_f) if filter_pullback else True
            
            # RSI filter
            rsi_ok = rsi_min <= rsi_val <= rsi_max
            
            if trend_ok and pullback_ok and rsi_ok:
                entry = close
                tp, sl = self._calculate_tp_sl(entry, atr_val, 'SHORT')
                reason = (f"C4 SHORT: tendência EMA{ema_fast}={ema_f:.2f} < EMA{ema_slow}={ema_s:.2f}, "
                         f"pullback: close={close:.2f} > EMA{ema_fast}, RSI={rsi_val:.1f}")
                return Signal('SHORT', entry, tp, sl, atr_val, reason)
        
        return Signal('NONE', 0, 0, 0, 0, 'No C4 signal')


def create_strategy(strategy_name: str, params: Dict) -> StrategyBase:
    """
    Factory function to create strategy instances
    
    Args:
        strategy_name: 'C1', 'C2', or 'C4'
        params: Strategy parameters
        
    Returns:
        Strategy instance
    """
    strategies = {
        'C1': C1Strategy,
        'C2': C2Strategy,
        'C4': C4Strategy,
    }
    
    if strategy_name not in strategies:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(strategies.keys())}")
    
    return strategies[strategy_name](params)
