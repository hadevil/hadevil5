"""
Data providers for candle/OHLCV data
Supports Live (HTTP from ApeX) and CSV (for testing)
"""

import pandas as pd
import logging
import time
from typing import Optional, List
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class DataProvider:
    """Base class for data providers"""
    
    def get_candles(self, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """
        Get OHLCV candles
        
        Args:
            symbol: Trading symbol
            timeframe: '15m' or '1h'
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        raise NotImplementedError("Must implement get_candles()")


class LiveDataProvider(DataProvider):
    """
    Live data provider using ApeX HTTP API
    """
    
    def __init__(self, apex_client):
        """
        Initialize with ApeX client
        
        Args:
            apex_client: ApexClient instance
        """
        self.apex_client = apex_client
        
    def get_candles(self, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """
        Fetch live candles from ApeX
        
        Args:
            symbol: Symbol (e.g., 'BTC-USDT')
            timeframe: '15m' or '1h'
            limit: Number of candles
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Map timeframe to ApeX format
            interval_map = {
                '15m': '15',
                '1h': '60',
                '5m': '5',
                '1m': '1',
                '4h': '240',
                '1d': 'D',
            }
            
            interval = interval_map.get(timeframe)
            if not interval:
                raise ValueError(f"Unsupported timeframe: {timeframe}")
            
            # Fetch klines from ApeX
            # Note: ApeX public client should have a method like klines_v3() or similar
            # Since it's not in the apex_client.py we saw, we'll use ticker and create a fallback
            
            logger.info(f"Fetching {limit} {timeframe} candles for {symbol}...")
            
            # Use the new get_klines method from apex_client
            klines = self.apex_client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            if klines and len(klines) > 0:
                # Parse klines data
                # Expected format: [[timestamp, open, high, low, close, volume], ...]
                # or [{'t': timestamp, 'o': open, 'h': high, 'l': low, 'c': close, 'v': volume}, ...]
                
                if isinstance(klines[0], list):
                    # Array format
                    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                elif isinstance(klines[0], dict):
                    # Dict format - map keys
                    df = pd.DataFrame(klines)
                    # Rename columns if needed
                    column_map = {
                        't': 'timestamp', 'time': 'timestamp',
                        'o': 'open', 'open': 'open',
                        'h': 'high', 'high': 'high',
                        'l': 'low', 'low': 'low',
                        'c': 'close', 'close': 'close',
                        'v': 'volume', 'volume': 'volume'
                    }
                    df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
                else:
                    raise ValueError(f"Unknown klines format: {type(klines[0])}")
                
            else:
                # Fallback: create synthetic data for testing
                logger.warning(f"⚠️  No klines data from API, using synthetic data (for testing only)")
                
                ticker = self.apex_client.public_client.ticker_v3(symbol=symbol)
                ticker_data = ticker['data']
                if isinstance(ticker_data, list):
                    ticker_data = ticker_data[0]
                
                current_price = float(ticker_data['lastPrice'])
                
                # Create synthetic historical data (for testing only)
                df = self._create_synthetic_candles(current_price, timeframe, limit)
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"✅ Fetched {len(df)} candles for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch candles for {symbol}: {e}")
            raise
    
    def _create_synthetic_candles(self, current_price: float, timeframe: str, 
                                  limit: int) -> pd.DataFrame:
        """
        Create synthetic candles for testing (when klines API not available)
        
        Args:
            current_price: Current market price
            timeframe: Timeframe string
            limit: Number of candles
            
        Returns:
            DataFrame with synthetic OHLCV data
        """
        import numpy as np
        
        # Parse timeframe to minutes
        tf_minutes = {'1m': 1, '5m': 5, '15m': 15, '1h': 60, '4h': 240, '1d': 1440}
        minutes = tf_minutes.get(timeframe, 15)
        
        # Generate timestamps going backwards
        now = datetime.now()
        timestamps = [now - timedelta(minutes=minutes * i) for i in range(limit, 0, -1)]
        timestamps_ms = [int(ts.timestamp() * 1000) for ts in timestamps]
        
        # Generate random walk around current price
        np.random.seed(42)
        prices = [current_price]
        for _ in range(limit - 1):
            change = np.random.normal(0, current_price * 0.001)  # 0.1% volatility
            prices.append(prices[-1] + change)
        
        # Create OHLCV
        data = []
        for i, (ts, price) in enumerate(zip(timestamps_ms, prices)):
            volatility = price * 0.002  # 0.2% range
            open_price = price + np.random.uniform(-volatility, volatility)
            close_price = price + np.random.uniform(-volatility, volatility)
            high_price = max(open_price, close_price) + abs(np.random.uniform(0, volatility))
            low_price = min(open_price, close_price) - abs(np.random.uniform(0, volatility))
            volume = np.random.uniform(1000000, 5000000)
            
            data.append([ts, open_price, high_price, low_price, close_price, volume])
        
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        logger.warning("⚠️  Using SYNTHETIC candles - for testing only!")
        
        return df


class CSVDataProvider(DataProvider):
    """
    CSV data provider for backtesting
    Expected format: CSV files named like 'BTCUSDT_15m.csv' in data folder
    """
    
    def __init__(self, csv_folder: str = './data'):
        """
        Initialize CSV provider
        
        Args:
            csv_folder: Path to folder containing CSV files
        """
        self.csv_folder = Path(csv_folder)
        self.cache = {}  # Cache loaded CSV files
        
    def get_candles(self, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """
        Load candles from CSV file
        
        Args:
            symbol: Symbol (e.g., 'BTC-USDT' or 'BTCUSDT')
            timeframe: '15m' or '1h'
            limit: Number of recent candles to return
            
        Returns:
            DataFrame with OHLCV data
        """
        # Normalize symbol for filename (remove hyphen)
        symbol_clean = symbol.replace('-', '')
        
        # Try different filename patterns
        possible_filenames = [
            f"{symbol_clean}_{timeframe}.csv",
            f"{symbol}_{timeframe}.csv",
            f"{symbol_clean.lower()}_{timeframe}.csv",
        ]
        
        df = None
        for filename in possible_filenames:
            filepath = self.csv_folder / filename
            
            if filepath.exists():
                logger.info(f"Loading CSV: {filepath}")
                
                # Check cache
                cache_key = str(filepath)
                if cache_key in self.cache:
                    df = self.cache[cache_key].copy()
                else:
                    # Load CSV
                    df = pd.read_csv(filepath)
                    
                    # Validate columns
                    required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    if not all(col in df.columns for col in required_cols):
                        raise ValueError(f"CSV must have columns: {required_cols}, got: {df.columns.tolist()}")
                    
                    # Parse timestamp
                    if df['timestamp'].dtype == 'object':
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                    else:
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Convert types
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col])
                    
                    # Sort
                    df = df.sort_values('timestamp').reset_index(drop=True)
                    
                    # Cache
                    self.cache[cache_key] = df.copy()
                
                break
        
        if df is None:
            raise FileNotFoundError(
                f"No CSV file found for {symbol} {timeframe}. "
                f"Tried: {', '.join(possible_filenames)} in {self.csv_folder}"
            )
        
        # Return last N candles
        df = df.tail(limit).reset_index(drop=True)
        
        logger.info(f"✅ Loaded {len(df)} candles from CSV")
        
        return df


def create_data_provider(data_source: str, apex_client=None, csv_folder: str = './data') -> DataProvider:
    """
    Factory function to create data provider
    
    Args:
        data_source: 'live' or 'csv'
        apex_client: ApexClient instance (required for live)
        csv_folder: CSV folder path (for csv source)
        
    Returns:
        DataProvider instance
    """
    if data_source == 'live':
        if apex_client is None:
            raise ValueError("apex_client required for live data source")
        return LiveDataProvider(apex_client)
    elif data_source == 'csv':
        return CSVDataProvider(csv_folder)
    else:
        raise ValueError(f"Unknown data_source: {data_source}. Use 'live' or 'csv'")
