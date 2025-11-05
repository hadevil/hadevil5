"""
Database Module - SQLite storage for trades and analytics
Stores all trades for backtesting and performance analysis
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class TradingDatabase:
    """SQLite database for storing trading history"""
    
    def __init__(self, db_path: str = "trades.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Create database and tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            # Create trades table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_time TIMESTAMP NOT NULL,
                    exit_time TIMESTAMP,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    size REAL NOT NULL,
                    leverage INTEGER NOT NULL,
                    unrealized_pnl REAL DEFAULT 0,
                    realized_pnl REAL,
                    fees REAL DEFAULT 0,
                    close_reason TEXT,
                    duration_minutes INTEGER,
                    config_sl REAL,
                    config_tp REAL,
                    config_time_limit INTEGER,
                    status TEXT DEFAULT 'OPEN',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create cycles table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT UNIQUE NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    total_pnl REAL,
                    close_reason TEXT,
                    duration_minutes INTEGER,
                    num_positions INTEGER DEFAULT 0,
                    config_snapshot TEXT,
                    status TEXT DEFAULT 'ACTIVE',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create performance_metrics table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    avg_win REAL DEFAULT 0,
                    avg_loss REAL DEFAULT 0,
                    profit_factor REAL DEFAULT 0,
                    max_drawdown REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            """)
            
            # Create health_checks table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    api_status TEXT NOT NULL,
                    response_time_ms REAL,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_trades_cycle ON trades(cycle_id)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cycles_start_time ON cycles(start_time)")
            
            self.conn.commit()
            logger.info(f"✅ Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise
    
    def start_cycle(self, cycle_id: str, config: Dict) -> bool:
        """
        Start a new trading cycle
        
        Args:
            cycle_id: Unique cycle identifier
            config: Configuration snapshot
            
        Returns:
            True if successful
        """
        try:
            self.conn.execute("""
                INSERT INTO cycles (cycle_id, start_time, config_snapshot, status)
                VALUES (?, ?, ?, 'ACTIVE')
            """, (cycle_id, datetime.now(), json.dumps(config)))
            self.conn.commit()
            logger.info(f"✅ Started cycle: {cycle_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start cycle: {e}")
            return False
    
    def end_cycle(self, cycle_id: str, total_pnl: float, close_reason: str, duration_minutes: int) -> bool:
        """
        End a trading cycle
        
        Args:
            cycle_id: Cycle identifier
            total_pnl: Final PnL for the cycle
            close_reason: Reason for closing
            duration_minutes: Duration in minutes
            
        Returns:
            True if successful
        """
        try:
            self.conn.execute("""
                UPDATE cycles 
                SET end_time = ?, total_pnl = ?, close_reason = ?, 
                    duration_minutes = ?, status = 'CLOSED'
                WHERE cycle_id = ?
            """, (datetime.now(), total_pnl, close_reason, duration_minutes, cycle_id))
            self.conn.commit()
            logger.info(f"✅ Ended cycle: {cycle_id} | PnL: ${total_pnl:+.2f}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to end cycle: {e}")
            return False
    
    def record_position_open(self, cycle_id: str, position: Dict, config: Dict) -> bool:
        """
        Record a position opening
        
        Args:
            cycle_id: Cycle identifier
            position: Position data from API
            config: Current config (for SL/TP/Time)
            
        Returns:
            True if successful
        """
        try:
            self.conn.execute("""
                INSERT INTO trades (
                    cycle_id, symbol, side, entry_time, entry_price, size, leverage,
                    config_sl, config_tp, config_time_limit, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
            """, (
                cycle_id,
                position.get('symbol'),
                position.get('side'),
                datetime.now(),
                float(position.get('entryPrice', 0)),
                float(position.get('size', 0)),
                int(config.get('LEVERAGE', 20)),
                float(config.get('STOP_LOSS_USD', 0)),
                float(config.get('TAKE_PROFIT_USD', 0)),
                int(config.get('TIME_LIMIT_MINUTES', 0))
            ))
            
            # Update cycle position count
            self.conn.execute("""
                UPDATE cycles 
                SET num_positions = num_positions + 1
                WHERE cycle_id = ?
            """, (cycle_id,))
            
            self.conn.commit()
            logger.debug(f"✅ Recorded position open: {position.get('symbol')}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to record position open: {e}")
            return False
    
    def record_position_close(self, cycle_id: str, symbol: str, exit_price: float, 
                             realized_pnl: float, close_reason: str, fees: float = 0) -> bool:
        """
        Record a position closing
        
        Args:
            cycle_id: Cycle identifier
            symbol: Trading symbol
            exit_price: Exit price
            realized_pnl: Final PnL
            close_reason: Reason for closing
            fees: Trading fees
            
        Returns:
            True if successful
        """
        try:
            # Get entry time to calculate duration
            cursor = self.conn.execute("""
                SELECT entry_time FROM trades
                WHERE cycle_id = ? AND symbol = ? AND status = 'OPEN'
                ORDER BY entry_time DESC LIMIT 1
            """, (cycle_id, symbol))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"⚠️  No open position found for {symbol} in cycle {cycle_id}")
                return False
            
            entry_time = datetime.fromisoformat(row['entry_time'])
            duration = int((datetime.now() - entry_time).total_seconds() / 60)
            
            self.conn.execute("""
                UPDATE trades
                SET exit_time = ?, exit_price = ?, realized_pnl = ?, 
                    close_reason = ?, duration_minutes = ?, fees = ?, status = 'CLOSED'
                WHERE cycle_id = ? AND symbol = ? AND status = 'OPEN'
            """, (datetime.now(), exit_price, realized_pnl, close_reason, duration, fees, cycle_id, symbol))
            
            self.conn.commit()
            logger.debug(f"✅ Recorded position close: {symbol} | PnL: ${realized_pnl:+.2f}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to record position close: {e}")
            return False
    
    def update_position_pnl(self, cycle_id: str, symbol: str, unrealized_pnl: float) -> bool:
        """
        Update unrealized PnL for an open position
        
        Args:
            cycle_id: Cycle identifier
            symbol: Trading symbol
            unrealized_pnl: Current unrealized PnL
            
        Returns:
            True if successful
        """
        try:
            self.conn.execute("""
                UPDATE trades
                SET unrealized_pnl = ?
                WHERE cycle_id = ? AND symbol = ? AND status = 'OPEN'
            """, (unrealized_pnl, cycle_id, symbol))
            self.conn.commit()
            return True
        except Exception as e:
            logger.debug(f"Failed to update PnL: {e}")
            return False
    
    def record_health_check(self, api_status: str, response_time_ms: Optional[float] = None, 
                           error_message: Optional[str] = None) -> bool:
        """
        Record an API health check
        
        Args:
            api_status: 'OK' or 'ERROR'
            response_time_ms: API response time in milliseconds
            error_message: Error message if failed
            
        Returns:
            True if successful
        """
        try:
            self.conn.execute("""
                INSERT INTO health_checks (timestamp, api_status, response_time_ms, error_message)
                VALUES (?, ?, ?, ?)
            """, (datetime.now(), api_status, response_time_ms, error_message))
            self.conn.commit()
            return True
        except Exception as e:
            logger.debug(f"Failed to record health check: {e}")
            return False
    
    def get_trades_by_symbol(self, symbol: str, limit: int = 100) -> List[Dict]:
        """
        Get trade history for a specific symbol
        
        Args:
            symbol: Trading symbol
            limit: Maximum number of trades to return
            
        Returns:
            List of trade dictionaries
        """
        try:
            cursor = self.conn.execute("""
                SELECT * FROM trades
                WHERE symbol = ? AND status = 'CLOSED'
                ORDER BY entry_time DESC
                LIMIT ?
            """, (symbol, limit))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"❌ Failed to get trades: {e}")
            return []
    
    def get_performance_stats(self, days: int = 30) -> Dict:
        """
        Get performance statistics for the last N days
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with performance metrics
        """
        try:
            cursor = self.conn.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN realized_pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(realized_pnl) as total_pnl,
                    AVG(CASE WHEN realized_pnl > 0 THEN realized_pnl END) as avg_win,
                    AVG(CASE WHEN realized_pnl < 0 THEN realized_pnl END) as avg_loss,
                    MAX(realized_pnl) as best_trade,
                    MIN(realized_pnl) as worst_trade
                FROM trades
                WHERE status = 'CLOSED' 
                AND entry_time >= datetime('now', '-' || ? || ' days')
            """, (days,))
            
            row = cursor.fetchone()
            if not row:
                return {}
            
            stats = dict(row)
            
            # Calculate additional metrics
            if stats['total_trades'] > 0:
                stats['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100
            else:
                stats['win_rate'] = 0
            
            if stats['avg_loss'] and stats['avg_loss'] != 0:
                stats['profit_factor'] = abs(stats['avg_win'] / stats['avg_loss']) if stats['avg_win'] else 0
            else:
                stats['profit_factor'] = 0
            
            return stats
        except Exception as e:
            logger.error(f"❌ Failed to get performance stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("✅ Database connection closed")
