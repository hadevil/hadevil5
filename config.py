"""
Configurações do sistema Long&Short
"""
import os
from dataclasses import dataclass
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TradingConfig:
    """Configurações de trading"""
    # Lista de ativos disponíveis para trading
    available_assets: List[str] = None
    
    # Configurações de tempo
    selection_interval_hours: int = 2  # Intervalo para seleção de ativos
    max_position_duration_hours: int = 24  # Duração máxima da posição
    reopen_delay_minutes: int = 8  # Delay para reabertura
    
    # Configurações de risco
    default_tp_percentage: float = 2.0  # Take Profit padrão em %
    default_sl_percentage: float = 1.0  # Stop Loss padrão em %
    
    # Configurações da exchange
    exchange_name: str = "binance"
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    sandbox: bool = True
    
    # Configurações de capital
    max_position_size_usdt: float = 1000.0
    risk_per_trade_percentage: float = 1.0
    
    def __post_init__(self):
        if self.available_assets is None:
            self.available_assets = [
                "BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", 
                "DOTUSDT", "LINKUSDT", "UNIUSDT", "AVAXUSDT"
            ]
        
        # Carregar credenciais do ambiente
        self.api_key = os.getenv("EXCHANGE_API_KEY")
        self.api_secret = os.getenv("EXCHANGE_API_SECRET")

# Configuração global
config = TradingConfig()