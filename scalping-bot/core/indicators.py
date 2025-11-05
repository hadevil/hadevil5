"""
Technical Indicators for Trading Strategies
Implements EMA, RSI, ATR, VolMA with pandas
"""

import pandas as pd
import numpy as np
from typing import Optional


def ema(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA)
    
    Args:
        series: Price series (typically close)
        period: EMA period
        
    Returns:
        EMA series
    """
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index) using Wilder's method
    
    Args:
        series: Price series (typically close)
        period: RSI period (default 14)
        
    Returns:
        RSI series (0-100)
    """
    delta = series.diff()
    
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # Wilder's smoothing (RMA = Rolling Moving Average)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi_values = 100 - (100 / (1 + rs))
    
    return rsi_values


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 10) -> pd.Series:
    """
    Calculate Average True Range (ATR)
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: ATR period (default 10)
        
    Returns:
        ATR series
    """
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Wilder's smoothing
    atr_values = true_range.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    return atr_values


def atr_ma(atr_series: pd.Series, period: int = 20) -> pd.Series:
    """
    Calculate Simple Moving Average of ATR
    
    Args:
        atr_series: ATR series
        period: MA period (default 20)
        
    Returns:
        ATR MA series
    """
    return atr_series.rolling(window=period).mean()


def volume_ma(volume: pd.Series, period: int = 20) -> pd.Series:
    """
    Calculate Volume Moving Average
    
    Args:
        volume: Volume series
        period: MA period (default 20)
        
    Returns:
        Volume MA series
    """
    return volume.rolling(window=period).mean()


class IndicatorCalculator:
    """
    Centralized indicator calculator for strategies
    Calculates all indicators at once for efficiency
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with OHLCV dataframe
        
        Args:
            df: DataFrame with columns: timestamp, open, high, low, close, volume
        """
        self.df = df.copy()
        self.indicators = {}
        
    def calculate_all(self, ema_fast: int = 20, ema_slow: int = 50, 
                      rsi_period: int = 14, atr_period: int = 10,
                      atr_ma_period: int = 20, vol_ma_period: int = 20):
        """
        Calculate all indicators at once
        
        Args:
            ema_fast: Fast EMA period
            ema_slow: Slow EMA period
            rsi_period: RSI period
            atr_period: ATR period
            atr_ma_period: ATR MA period
            vol_ma_period: Volume MA period
        """
        df = self.df
        
        # EMAs
        self.indicators[f'ema_{ema_fast}'] = ema(df['close'], ema_fast)
        self.indicators[f'ema_{ema_slow}'] = ema(df['close'], ema_slow)
        
        # RSI
        self.indicators[f'rsi_{rsi_period}'] = rsi(df['close'], rsi_period)
        
        # ATR and ATR MA
        self.indicators[f'atr_{atr_period}'] = atr(df['high'], df['low'], df['close'], atr_period)
        self.indicators[f'atr_ma_{atr_ma_period}'] = atr_ma(
            self.indicators[f'atr_{atr_period}'], atr_ma_period
        )
        
        # Volume MA
        self.indicators[f'vol_ma_{vol_ma_period}'] = volume_ma(df['volume'], vol_ma_period)
        
        # Add to dataframe
        for name, values in self.indicators.items():
            self.df[name] = values
            
        return self.df
    
    def get_latest(self, indicator_name: str) -> Optional[float]:
        """
        Get latest value of an indicator
        
        Args:
            indicator_name: Name of indicator
            
        Returns:
            Latest value or None if not available
        """
        if indicator_name in self.df.columns:
            val = self.df[indicator_name].iloc[-1]
            return float(val) if pd.notna(val) else None
        return None
    
    def get_previous(self, indicator_name: str, offset: int = 1) -> Optional[float]:
        """
        Get previous value of an indicator
        
        Args:
            indicator_name: Name of indicator
            offset: How many bars back (default 1)
            
        Returns:
            Previous value or None if not available
        """
        if indicator_name in self.df.columns and len(self.df) > offset:
            val = self.df[indicator_name].iloc[-(offset + 1)]
            return float(val) if pd.notna(val) else None
        return None
