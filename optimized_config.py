"""
Configuração Otimizada para Market Making e Airdrop Farming
Focada em minimizar perdas e maximizar pontos de airdrop
"""

import os
from typing import Dict, List

# Configurações da API
API_CONFIG = {
    'base_url': 'https://api.paradex.trade',
    'websocket_url': 'wss://api.paradex.trade/ws',
    'api_key': os.getenv('PARADEX_API_KEY', ''),
    'secret_key': os.getenv('PARADEX_SECRET_KEY', ''),
    'passphrase': os.getenv('PARADEX_PASSPHRASE', ''),
}

# Configurações de Trading Otimizadas
TRADING_CONFIG = {
    'symbol': 'SOL-USD',
    'base_asset': 'SOL',
    'quote_asset': 'USD',
    'total_capital': 5000,
    'risk_per_trade': 0.01,  # 1% por trade (mais conservador)
    'max_daily_loss': 0.02,  # 2% perda máxima diária
    'max_weekly_loss': 0.05,  # 5% perda máxima semanal
    'min_order_size': 0.05,  # 0.05 SOL mínimo
    'max_order_size': 2.0,   # 2 SOL máximo
    'max_position_size': 100,  # 100 SOL máximo por posição
}

# Configurações de Airdrop Farming
AIRDROP_CONFIG = {
    'daily_volume_target': 1500,  # $1500 por dia (30% do capital)
    'daily_trades_target': 100,   # 100 trades por dia
    'weekly_volume_target': 10500, # $10,500 por semana
    'monthly_volume_target': 45000, # $45,000 por mês
    'min_active_days': 30,        # 30 dias ativos
    'consistency_bonus': 1.2,     # 20% bônus por consistência
    'volume_boost_threshold': 0.7, # Ativar boost se volume < 70%
    'trade_frequency_boost': 0.7,  # Ativar boost se trades < 70%
}

# Configurações de Proteção de Capital
LOSS_PROTECTION = {
    'max_drawdown': 0.03,         # 3% drawdown máximo
    'emergency_stop_loss': 0.02,  # 2% perda máxima por trade
    'hedge_ratio': 0.8,           # 80% do inventário hedgeado
    'recovery_mode': True,        # Ativar modo de recuperação
    'consecutive_loss_limit': 5,  # Limite de perdas consecutivas
    'position_size_multiplier': 1.0,  # Multiplicador base de tamanho
    'spread_multiplier': 1.0,     # Multiplicador base de spread
}

# Configurações de Market Making Otimizado
MARKET_MAKING_CONFIG = {
    'base_spread': 0.0003,        # 0.03% spread base (mais agressivo)
    'min_spread': 0.0001,         # 0.01% spread mínimo
    'max_spread': 0.002,          # 0.2% spread máximo
    'order_refresh_time': 20,     # Refresh a cada 20 segundos
    'max_orders_per_side': 8,     # 8 ordens por lado
    'order_size_multiplier': 0.9, # Reduz tamanho gradualmente
    'inventory_skew_threshold': 0.1, # Threshold para ajuste de inventário
    'arbitrage_threshold': 0.0005,  # 0.05% para arbitragem
    'mean_reversion_threshold': 0.002, # 0.2% para mean reversion
}

# Configurações de Estratégia Avançada
STRATEGY_CONFIG = {
    'volatility_lookback': 50,    # Períodos para volatilidade
    'volume_lookback': 20,        # Períodos para volume
    'trend_lookback': 20,         # Períodos para tendência
    'adaptive_spread': True,      # Spread adaptativo
    'momentum_factor': 0.1,       # Fator de momentum
    'mean_reversion_factor': 0.3, # Fator de mean reversion
    'arbitrage_enabled': True,    # Ativar arbitragem
    'hedging_enabled': True,      # Ativar hedging
    'performance_modes': ['aggressive', 'balanced', 'conservative'],
}

# Configurações de Monitoramento Otimizado
MONITORING_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'optimized_market_maker.log',
    'performance_file': 'optimized_performance.json',
    'backup_interval': 3600,      # Backup a cada hora
    'alert_thresholds': {
        'max_drawdown': 0.03,
        'min_profit_daily': 0.01,
        'max_slippage': 0.002,
        'min_airdrop_score': 0.6,
    }
}

# Configurações de Segurança Avançada
SECURITY_CONFIG = {
    'max_concurrent_orders': 20,  # Máximo 20 ordens simultâneas
    'order_timeout': 300,         # 5 minutos timeout
    'connection_timeout': 30,
    'retry_attempts': 3,
    'circuit_breaker_threshold': 5,
    'emergency_exit_threshold': 0.05, # 5% para saída de emergência
    'position_limit_ratio': 0.1,  # Máximo 10% do capital em posição
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    'aggressive_mode': {
        'spread_multiplier': 0.7,     # 30% menor spread
        'position_multiplier': 1.5,   # 50% maior posição
        'frequency_multiplier': 2.0,  # 2x mais frequente
        'max_orders_per_side': 10,    # 10 ordens por lado
    },
    'balanced_mode': {
        'spread_multiplier': 1.0,     # Spread normal
        'position_multiplier': 1.0,   # Posição normal
        'frequency_multiplier': 1.0,  # Frequência normal
        'max_orders_per_side': 6,     # 6 ordens por lado
    },
    'conservative_mode': {
        'spread_multiplier': 1.5,     # 50% maior spread
        'position_multiplier': 0.6,   # 40% menor posição
        'frequency_multiplier': 0.5,  # 50% menos frequente
        'max_orders_per_side': 3,     # 3 ordens por lado
    }
}

# Configurações de Airdrop Otimizado
AIRDROP_OPTIMIZATION = {
    'volume_boost_active': False,
    'trade_frequency_boost': False,
    'consistency_bonus_active': False,
    'time_based_aggression': True,    # Mais agressivo no final do dia
    'weekend_mode': False,            # Modo especial para fins de semana
    'holiday_mode': False,            # Modo especial para feriados
}

# Configurações específicas para Windows/PowerShell
WINDOWS_CONFIG = {
    'encoding': 'utf-8',
    'newline': '\r\n',
    'path_separator': '\\',
    'temp_dir': os.path.join(os.getenv('TEMP', ''), 'paradex_bot_optimized'),
    'log_rotation': True,
    'backup_retention_days': 30,
}

def get_optimized_config() -> Dict:
    """Retorna todas as configurações otimizadas"""
    return {
        'api': API_CONFIG,
        'trading': TRADING_CONFIG,
        'airdrop': AIRDROP_CONFIG,
        'loss_protection': LOSS_PROTECTION,
        'market_making': MARKET_MAKING_CONFIG,
        'strategy': STRATEGY_CONFIG,
        'monitoring': MONITORING_CONFIG,
        'security': SECURITY_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'airdrop_optimization': AIRDROP_OPTIMIZATION,
        'windows': WINDOWS_CONFIG,
    }

def validate_optimized_config() -> bool:
    """Valida configurações otimizadas"""
    required_keys = ['api_key', 'secret_key', 'passphrase']
    for key in required_keys:
        if not API_CONFIG.get(key):
            print(f"❌ Configuração obrigatória ausente: {key}")
            return False
    
    # Validar limites de risco
    if TRADING_CONFIG['risk_per_trade'] > 0.05:  # 5% máximo
        print("❌ Risk per trade muito alto (máximo 5%)")
        return False
    
    if LOSS_PROTECTION['max_drawdown'] > 0.1:  # 10% máximo
        print("❌ Max drawdown muito alto (máximo 10%)")
        return False
    
    return True

def get_performance_mode_config(mode: str) -> Dict:
    """Retorna configurações para modo de performance específico"""
    return PERFORMANCE_CONFIG.get(mode, PERFORMANCE_CONFIG['balanced'])

def get_airdrop_targets() -> Dict:
    """Retorna metas de airdrop"""
    return {
        'daily_volume': AIRDROP_CONFIG['daily_volume_target'],
        'daily_trades': AIRDROP_CONFIG['daily_trades_target'],
        'weekly_volume': AIRDROP_CONFIG['weekly_volume_target'],
        'monthly_volume': AIRDROP_CONFIG['monthly_volume_target'],
        'min_active_days': AIRDROP_CONFIG['min_active_days'],
    }