"""
Configurações do Bot Market Maker para Paradex
Otimizado para SOL com capital limitado (5k)
"""

import os
from typing import Dict, List

# Configurações da API
API_CONFIG = {
    'base_url': 'https://api.paradex.trade',  # URL base da API da Paradex
    'websocket_url': 'wss://api.paradex.trade/ws',  # WebSocket para dados em tempo real
    'api_key': os.getenv('PARADEX_API_KEY', ''),
    'secret_key': os.getenv('PARADEX_SECRET_KEY', ''),
    'passphrase': os.getenv('PARADEX_PASSPHRASE', ''),
}

# Configurações do Trading
TRADING_CONFIG = {
    'symbol': 'SOL-USD',  # Par principal para trading
    'base_asset': 'SOL',
    'quote_asset': 'USD',
    'max_position_size': 1000,  # Máximo de SOL por posição
    'min_order_size': 0.1,  # Mínimo de SOL por ordem
    'max_order_size': 50,  # Máximo de SOL por ordem
    'total_capital': 5000,  # Capital total disponível
    'risk_per_trade': 0.02,  # 2% do capital por trade
    'max_daily_loss': 0.05,  # 5% de perda máxima diária
}

# Configurações de Market Making
MARKET_MAKING_CONFIG = {
    'spread_percentage': 0.001,  # 0.1% de spread
    'min_spread': 0.0005,  # Spread mínimo de 0.05%
    'max_spread': 0.005,  # Spread máximo de 0.5%
    'order_refresh_time': 30,  # Refresh das ordens a cada 30 segundos
    'max_orders_per_side': 3,  # Máximo de 3 ordens por lado
    'order_size_multiplier': 1.2,  # Multiplicador para tamanho das ordens
    'inventory_skew_threshold': 0.1,  # Threshold para ajustar spread baseado no inventário
}

# Configurações de Estratégia Adaptativa
STRATEGY_CONFIG = {
    'volatility_lookback': 100,  # Períodos para calcular volatilidade
    'volume_lookback': 50,  # Períodos para calcular volume médio
    'trend_lookback': 20,  # Períodos para detectar tendência
    'adaptive_spread': True,  # Ativar spread adaptativo
    'momentum_factor': 0.1,  # Fator de momentum para ajuste de spread
    'mean_reversion_factor': 0.05,  # Fator de mean reversion
}

# Configurações de Monitoramento
MONITORING_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'market_maker.log',
    'performance_file': 'performance.json',
    'alert_thresholds': {
        'max_drawdown': 0.03,  # 3% de drawdown máximo
        'min_profit': 0.01,  # 1% de lucro mínimo esperado
        'max_slippage': 0.002,  # 2% de slippage máximo
    }
}

# Configurações de Segurança
SECURITY_CONFIG = {
    'max_concurrent_orders': 10,
    'order_timeout': 60,  # Timeout para ordens em segundos
    'connection_timeout': 30,
    'retry_attempts': 3,
    'circuit_breaker_threshold': 5,  # Número de falhas antes de parar
}

# Configurações específicas para Windows/PowerShell
WINDOWS_CONFIG = {
    'encoding': 'utf-8',
    'newline': '\r\n',
    'path_separator': '\\',
    'temp_dir': os.path.join(os.getenv('TEMP', ''), 'paradex_bot'),
}

# Configurações de Airdrop Farming
AIRDROP_CONFIG = {
    'min_volume_daily': 1000,  # Volume mínimo diário em USD
    'min_trades_daily': 50,  # Número mínimo de trades diários
    'min_active_days': 30,  # Dias mínimos de atividade
    'target_volume_multiplier': 1.5,  # Multiplicador do volume alvo
    'volume_tracking_window': 24,  # Janela de tracking em horas
}

def get_config() -> Dict:
    """Retorna todas as configurações como um dicionário"""
    return {
        'api': API_CONFIG,
        'trading': TRADING_CONFIG,
        'market_making': MARKET_MAKING_CONFIG,
        'strategy': STRATEGY_CONFIG,
        'monitoring': MONITORING_CONFIG,
        'security': SECURITY_CONFIG,
        'windows': WINDOWS_CONFIG,
        'airdrop': AIRDROP_CONFIG,
    }

def validate_config() -> bool:
    """Valida se todas as configurações necessárias estão presentes"""
    required_keys = ['api_key', 'secret_key', 'passphrase']
    for key in required_keys:
        if not API_CONFIG.get(key):
            print(f"❌ Configuração obrigatória ausente: {key}")
            return False
    return True