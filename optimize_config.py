"""
Configuration optimizer for Paradex Market Maker Bot
Helps find optimal parameters for your capital and risk tolerance
"""

import json
from typing import Dict


def calculate_optimal_config(
    capital: float = 5000,
    risk_tolerance: str = 'balanced',  # 'conservative', 'balanced', 'aggressive'
    target_market: str = 'SOL-USD-PERP'
) -> Dict:
    """Calculate optimal configuration based on capital and risk tolerance"""
    
    configs = {
        'conservative': {
            'base_spread': 0.002,          # 0.2%
            'order_levels': 3,
            'level_spacing': 0.0007,       # 0.07%
            'max_position_pct': 0.4,       # 40% of capital
            'order_size_pct': 0.025,       # 2.5% of capital per order
            'refresh_interval': 60,         # 1 minute
            'min_edge': 0.0003             # 0.03%
        },
        'balanced': {
            'base_spread': 0.0015,         # 0.15%
            'order_levels': 5,
            'level_spacing': 0.0005,       # 0.05%
            'max_position_pct': 0.5,       # 50% of capital
            'order_size_pct': 0.02,        # 2% of capital per order
            'refresh_interval': 30,         # 30 seconds
            'min_edge': 0.0002             # 0.02%
        },
        'aggressive': {
            'base_spread': 0.001,          # 0.1%
            'order_levels': 7,
            'level_spacing': 0.0003,       # 0.03%
            'max_position_pct': 0.6,       # 60% of capital
            'order_size_pct': 0.018,       # 1.8% of capital per order
            'refresh_interval': 20,         # 20 seconds
            'min_edge': 0.00015            # 0.015%
        }
    }
    
    profile = configs.get(risk_tolerance, configs['balanced'])
    
    # Calculate actual values based on capital
    max_position_usd = capital * profile['max_position_pct']
    order_size_usd = capital * profile['order_size_pct']
    
    config = {
        'api_key': 'YOUR_PARADEX_API_KEY',
        'api_secret': 'YOUR_PARADEX_API_SECRET',
        'testnet': True,
        'market': target_market,
        
        'base_spread': profile['base_spread'],
        'order_levels': profile['order_levels'],
        'level_spacing': profile['level_spacing'],
        'order_size_usd': round(order_size_usd, 2),
        'max_position_usd': round(max_position_usd, 2),
        'refresh_interval': profile['refresh_interval'],
        'min_edge': profile['min_edge'],
        
        'risk_management': {
            'max_daily_loss': round(capital * 0.02, 2),  # 2% of capital
            'max_position_leverage': 2,
            'stop_loss_pct': 0.05
        },
        
        'advanced_features': {
            'enable_inventory_skewing': True,
            'enable_volatility_adjustment': True,
            'enable_order_size_scaling': True,
            'competition_mode': True
        }
    }
    
    return config


def print_config_analysis(config: Dict, capital: float):
    """Print analysis of configuration"""
    print("\n" + "="*70)
    print("CONFIGURATION ANALYSIS")
    print("="*70)
    print()
    
    print(f"Capital: ${capital:,.2f}")
    print(f"Market: {config['market']}")
    print()
    
    print("ORDER PARAMETERS:")
    print(f"  Base Spread:        {config['base_spread']*100:.3f}%")
    print(f"  Order Levels:       {config['order_levels']} per side")
    print(f"  Level Spacing:      {config['level_spacing']*100:.3f}%")
    print(f"  Order Size:         ${config['order_size_usd']:.2f}")
    print(f"  Max Position:       ${config['max_position_usd']:.2f} ({config['max_position_usd']/capital*100:.1f}% of capital)")
    print(f"  Refresh Interval:   {config['refresh_interval']}s")
    print()
    
    # Calculate estimates
    total_orders = config['order_levels'] * 2
    total_capital_used = total_orders * config['order_size_usd']
    
    print("CAPITAL ALLOCATION:")
    print(f"  Total Orders:       {total_orders} ({config['order_levels']} buy + {config['order_levels']} sell)")
    print(f"  Capital per Order:  ${config['order_size_usd']:.2f}")
    print(f"  Total if All Fill:  ${total_capital_used:,.2f}")
    print(f"  Max Position:       ${config['max_position_usd']:,.2f}")
    print(f"  Reserved Capital:   ${capital - config['max_position_usd']:,.2f}")
    print()
    
    # Estimate daily performance
    intervals_per_day = (24 * 60 * 60) / config['refresh_interval']
    estimated_orders_per_day = intervals_per_day * total_orders * 0.7  # 70% fill rate
    estimated_volume_per_day = estimated_orders_per_day * config['order_size_usd']
    estimated_daily_pnl = estimated_volume_per_day * config['base_spread'] * 0.5  # 50% of spread captured
    
    print("ESTIMATED DAILY PERFORMANCE:")
    print(f"  Refresh Cycles:     {intervals_per_day:.0f} per day")
    print(f"  Orders Placed:      {intervals_per_day * total_orders:.0f}")
    print(f"  Orders Filled:      {estimated_orders_per_day:.0f} (70% fill rate)")
    print(f"  Trading Volume:     ${estimated_volume_per_day:,.2f}")
    print(f"  Estimated PnL:      ${estimated_daily_pnl:.2f}")
    print(f"  Daily ROI:          {estimated_daily_pnl/capital*100:.2f}%")
    print()
    
    print("RISK METRICS:")
    print(f"  Max Daily Loss:     ${config['risk_management']['max_daily_loss']:.2f}")
    print(f"  Position Leverage:  {config['risk_management']['max_position_leverage']}x")
    print(f"  Stop Loss:          {config['risk_management']['stop_loss_pct']*100:.1f}%")
    print()
    
    print("="*70)
    print()


def main():
    """Generate optimized configurations"""
    print("\n" + "="*70)
    print("PARADEX MARKET MAKER - CONFIGURATION OPTIMIZER")
    print("="*70)
    print()
    
    capital = 5000
    market = 'SOL-USD-PERP'
    
    profiles = ['conservative', 'balanced', 'aggressive']
    
    for profile in profiles:
        print(f"\n{'='*70}")
        print(f"{profile.upper()} PROFILE")
        print(f"{'='*70}")
        
        config = calculate_optimal_config(
            capital=capital,
            risk_tolerance=profile,
            target_market=market
        )
        
        print_config_analysis(config, capital)
        
        # Save configuration
        filename = f'config_{profile}.json'
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Configuration saved to {filename}")
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    print()
    print("1. START with Conservative profile to test:")
    print("   cp config_conservative.json config.json")
    print()
    print("2. MONITOR performance for 24-48 hours")
    print()
    print("3. ADJUST to Balanced if comfortable:")
    print("   cp config_balanced.json config.json")
    print()
    print("4. ONLY use Aggressive if you understand the risks")
    print()
    print("="*70)
    print()


if __name__ == "__main__":
    main()
