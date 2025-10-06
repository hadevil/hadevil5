"""
Real-time monitoring dashboard for Paradex Market Maker Bot
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import aiohttp

logger = logging.getLogger(__name__)


class BotMonitor:
    """Monitor bot performance and statistics"""
    
    def __init__(self, log_file: str = 'market_maker.log'):
        self.log_file = log_file
        self.stats = {
            'total_orders': 0,
            'filled_orders': 0,
            'cancelled_orders': 0,
            'volume_24h': 0.0,
            'pnl_24h': 0.0,
            'uptime': 0,
            'current_spread': 0.0,
            'current_position': 0.0
        }
    
    def parse_logs(self) -> Dict:
        """Parse log file for statistics"""
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                
            # Extract relevant metrics from logs
            for line in reversed(lines[-100:]):  # Check last 100 lines
                if 'Orders Placed:' in line:
                    # Parse order statistics
                    pass
                elif 'Position:' in line:
                    # Parse position info
                    pass
                    
        except FileNotFoundError:
            logger.warning(f"Log file {self.log_file} not found")
            
        return self.stats
    
    def display_dashboard(self):
        """Display real-time dashboard in terminal"""
        print("\n" + "="*60)
        print("PARADEX MARKET MAKER - LIVE DASHBOARD")
        print("="*60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*60)
        print(f"Total Orders:       {self.stats['total_orders']}")
        print(f"Filled Orders:      {self.stats['filled_orders']}")
        print(f"Cancel Rate:        {self.stats['cancelled_orders']}")
        print(f"24h Volume:         ${self.stats['volume_24h']:.2f}")
        print(f"24h PnL:            ${self.stats['pnl_24h']:.2f}")
        print(f"Current Position:   {self.stats['current_position']:.4f}")
        print(f"Current Spread:     {self.stats['current_spread']:.4f}%")
        print(f"Uptime:            {self.stats['uptime']}h")
        print("="*60)
    
    async def run(self, refresh_interval: int = 5):
        """Run monitoring dashboard"""
        while True:
            self.parse_logs()
            self.display_dashboard()
            await asyncio.sleep(refresh_interval)


async def main():
    monitor = BotMonitor()
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
