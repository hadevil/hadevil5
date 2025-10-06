"""
Backtesting module for Paradex Market Maker Bot
Simulates bot performance using historical data
"""

import asyncio
import json
import logging
from typing import Dict, List, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import random
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketSimulator:
    """Simulates market conditions for backtesting"""
    
    def __init__(self, initial_price: float = 100.0, volatility: float = 0.02):
        self.price = initial_price
        self.volatility = volatility
        self.orderbook = {'bids': [], 'asks': []}
        
    def simulate_price_movement(self) -> float:
        """Simulate price movement using geometric Brownian motion"""
        # Random walk with drift
        drift = 0.0  # No drift for market making
        shock = np.random.normal(0, self.volatility)
        
        self.price *= (1 + drift + shock)
        return self.price
    
    def generate_orderbook(self, levels: int = 10) -> Dict:
        """Generate realistic orderbook around current price"""
        bids = []
        asks = []
        
        spread = self.price * 0.001  # 0.1% spread
        
        for i in range(levels):
            # Bids (buy orders)
            bid_price = self.price - spread/2 - (i * self.price * 0.0002)
            bid_size = random.uniform(0.5, 2.0) * (1 / (i + 1))
            bids.append({'price': bid_price, 'size': bid_size})
            
            # Asks (sell orders)
            ask_price = self.price + spread/2 + (i * self.price * 0.0002)
            ask_size = random.uniform(0.5, 2.0) * (1 / (i + 1))
            asks.append({'price': ask_price, 'size': ask_size})
        
        self.orderbook = {'bids': bids, 'asks': asks}
        return self.orderbook
    
    def check_order_fill(self, order: Dict) -> bool:
        """Simulate if an order would be filled"""
        if order['side'] == 'BUY':
            # Buy order fills if market goes below our price
            best_ask = self.orderbook['asks'][0]['price']
            fill_probability = max(0, min(1, (order['price'] - best_ask) / (self.price * 0.001)))
        else:  # SELL
            # Sell order fills if market goes above our price
            best_bid = self.orderbook['bids'][0]['price']
            fill_probability = max(0, min(1, (best_bid - order['price']) / (self.price * 0.001)))
        
        # Add randomness
        return random.random() < fill_probability * 0.3  # 30% base fill rate


class BacktestEngine:
    """Backtesting engine for market making strategy"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.simulator = MarketSimulator(
            initial_price=config.get('initial_price', 100.0),
            volatility=config.get('volatility', 0.02)
        )
        
        self.capital = config.get('initial_capital', 5000)
        self.position = 0.0
        self.cash = self.capital
        self.orders = []
        
        self.trades = []
        self.pnl_history = []
        
    def run_backtest(self, periods: int = 2880) -> Dict:
        """Run backtest simulation (2880 periods = 24h at 30s intervals)"""
        logger.info(f"Starting backtest for {periods} periods...")
        
        for period in range(periods):
            # Simulate market movement
            current_price = self.simulator.simulate_price_movement()
            self.simulator.generate_orderbook()
            
            # Check if existing orders filled
            self._check_fills(current_price)
            
            # Cancel all orders (simulating refresh)
            self.orders = []
            
            # Place new orders
            self._place_orders(current_price)
            
            # Calculate PnL
            pnl = self._calculate_pnl(current_price)
            self.pnl_history.append(pnl)
            
            # Log progress
            if period % 288 == 0:  # Every 2.4 hours
                logger.info(
                    f"Period {period}/{periods} | "
                    f"Price: ${current_price:.2f} | "
                    f"Position: {self.position:.4f} | "
                    f"PnL: ${pnl:.2f}"
                )
        
        # Calculate final metrics
        results = self._calculate_results()
        return results
    
    def _place_orders(self, mid_price: float):
        """Place market making orders"""
        order_levels = self.config.get('order_levels', 5)
        base_spread = self.config.get('base_spread', 0.0015)
        order_size_usd = self.config.get('order_size_usd', 100)
        level_spacing = self.config.get('level_spacing', 0.0005)
        
        # Calculate order size in base currency
        order_size = order_size_usd / mid_price
        
        # Place bid orders
        for i in range(order_levels):
            offset = base_spread/2 + level_spacing * i
            price = mid_price * (1 - offset)
            size = order_size * (1 - i * 0.1)  # Decreasing size
            
            self.orders.append({
                'side': 'BUY',
                'price': price,
                'size': size,
                'placed_at': mid_price
            })
        
        # Place ask orders
        for i in range(order_levels):
            offset = base_spread/2 + level_spacing * i
            price = mid_price * (1 + offset)
            size = order_size * (1 - i * 0.1)
            
            self.orders.append({
                'side': 'SELL',
                'price': price,
                'size': size,
                'placed_at': mid_price
            })
    
    def _check_fills(self, current_price: float):
        """Check if any orders got filled"""
        filled_orders = []
        
        for order in self.orders:
            if self.simulator.check_order_fill(order):
                # Order filled
                filled_orders.append(order)
                
                # Update position and cash
                if order['side'] == 'BUY':
                    self.position += order['size']
                    self.cash -= order['size'] * order['price']
                else:  # SELL
                    self.position -= order['size']
                    self.cash += order['size'] * order['price']
                
                # Record trade
                self.trades.append({
                    'side': order['side'],
                    'price': order['price'],
                    'size': order['size'],
                    'value': order['size'] * order['price'],
                    'fill_price': current_price
                })
        
        # Remove filled orders
        self.orders = [o for o in self.orders if o not in filled_orders]
    
    def _calculate_pnl(self, current_price: float) -> float:
        """Calculate current PnL"""
        position_value = self.position * current_price
        total_value = self.cash + position_value
        return total_value - self.capital
    
    def _calculate_results(self) -> Dict:
        """Calculate final backtest results"""
        final_price = self.simulator.price
        final_pnl = self._calculate_pnl(final_price)
        
        total_volume = sum(t['value'] for t in self.trades)
        num_trades = len(self.trades)
        
        # Calculate metrics
        avg_trade_size = total_volume / num_trades if num_trades > 0 else 0
        roi = (final_pnl / self.capital) * 100
        
        # Calculate Sharpe ratio
        if len(self.pnl_history) > 1:
            returns = np.diff(self.pnl_history)
            sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe = 0
        
        # Max drawdown
        cumulative_pnl = np.array(self.pnl_history)
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdown = running_max - cumulative_pnl
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        
        results = {
            'final_pnl': final_pnl,
            'roi_pct': roi,
            'total_trades': num_trades,
            'total_volume': total_volume,
            'avg_trade_size': avg_trade_size,
            'final_position': self.position,
            'final_cash': self.cash,
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_drawdown),
            'win_rate': self._calculate_win_rate()
        }
        
        return results
    
    def _calculate_win_rate(self) -> float:
        """Calculate percentage of profitable trades"""
        if not self.trades:
            return 0.0
        
        profitable = 0
        for i in range(0, len(self.trades)-1, 2):
            if i+1 < len(self.trades):
                # Pair buy and sell
                buy_trade = next((t for t in self.trades[i:i+2] if t['side'] == 'BUY'), None)
                sell_trade = next((t for t in self.trades[i:i+2] if t['side'] == 'SELL'), None)
                
                if buy_trade and sell_trade:
                    if sell_trade['price'] > buy_trade['price']:
                        profitable += 1
        
        total_pairs = len(self.trades) // 2
        return (profitable / total_pairs * 100) if total_pairs > 0 else 0
    
    def print_results(self, results: Dict):
        """Print backtest results"""
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Capital:    ${self.capital:,.2f}")
        print(f"Final PnL:          ${results['final_pnl']:,.2f}")
        print(f"ROI:                {results['roi_pct']:.2f}%")
        print(f"Total Trades:       {results['total_trades']}")
        print(f"Total Volume:       ${results['total_volume']:,.2f}")
        print(f"Avg Trade Size:     ${results['avg_trade_size']:.2f}")
        print(f"Win Rate:           {results['win_rate']:.2f}%")
        print(f"Sharpe Ratio:       {results['sharpe_ratio']:.3f}")
        print(f"Max Drawdown:       ${results['max_drawdown']:.2f}")
        print(f"Final Position:     {results['final_position']:.4f}")
        print(f"Final Cash:         ${results['final_cash']:,.2f}")
        print("="*60)


def run_backtest_scenarios():
    """Run multiple backtest scenarios with different parameters"""
    scenarios = [
        {
            'name': 'Conservative',
            'config': {
                'initial_capital': 5000,
                'initial_price': 100,
                'volatility': 0.01,
                'base_spread': 0.002,
                'order_levels': 3,
                'order_size_usd': 150,
                'level_spacing': 0.0005
            }
        },
        {
            'name': 'Balanced',
            'config': {
                'initial_capital': 5000,
                'initial_price': 100,
                'volatility': 0.02,
                'base_spread': 0.0015,
                'order_levels': 5,
                'order_size_usd': 100,
                'level_spacing': 0.0005
            }
        },
        {
            'name': 'Aggressive',
            'config': {
                'initial_capital': 5000,
                'initial_price': 100,
                'volatility': 0.03,
                'base_spread': 0.001,
                'order_levels': 7,
                'order_size_usd': 80,
                'level_spacing': 0.0003
            }
        }
    ]
    
    results_summary = []
    
    for scenario in scenarios:
        logger.info(f"\nRunning {scenario['name']} scenario...")
        engine = BacktestEngine(scenario['config'])
        results = engine.run_backtest(periods=2880)  # 24 hours
        
        results['scenario'] = scenario['name']
        results_summary.append(results)
        
        engine.print_results(results)
    
    # Save results
    with open('backtest_results.json', 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    logger.info("\nBacktest results saved to backtest_results.json")


if __name__ == "__main__":
    run_backtest_scenarios()
