"""
Sistema de seleção de ativos para Long&Short
"""
import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from exchange_manager import ExchangeManager
from config import config

logger = logging.getLogger(__name__)

@dataclass
class AssetData:
    """Dados de um ativo"""
    symbol: str
    price: float
    volume_24h: float
    price_change_24h: float
    volatility: float
    score: float = 0.0

class AssetSelector:
    """Seletor de ativos para Long&Short"""
    
    def __init__(self, exchange_manager: ExchangeManager):
        self.exchange_manager = exchange_manager
        self.last_selection_time = None
        self.current_long_asset = None
        self.current_short_asset = None
        self.asset_history = []
    
    async def select_assets(self) -> Tuple[Optional[str], Optional[str]]:
        """Seleciona ativos para long e short"""
        try:
            # Verificar se é hora de selecionar novos ativos
            if not self._should_select_new_assets():
                return self.current_long_asset, self.current_short_asset
            
            logger.info("Iniciando seleção de ativos...")
            
            # Obter dados de todos os ativos
            assets_data = await self._get_assets_data()
            
            if not assets_data:
                logger.warning("Nenhum dado de ativo obtido")
                return None, None
            
            # Calcular scores para cada ativo
            scored_assets = self._calculate_asset_scores(assets_data)
            
            # Selecionar melhor ativo para long e short
            long_asset, short_asset = self._select_best_pair(scored_assets)
            
            # Atualizar seleções atuais
            self.current_long_asset = long_asset
            self.current_short_asset = short_asset
            self.last_selection_time = datetime.now()
            
            # Registrar no histórico
            self.asset_history.append({
                'timestamp': self.last_selection_time,
                'long_asset': long_asset,
                'short_asset': short_asset,
                'long_score': next((a.score for a in scored_assets if a.symbol == long_asset), 0),
                'short_score': next((a.score for a in scored_assets if a.symbol == short_asset), 0)
            })
            
            logger.info(f"Ativos selecionados - Long: {long_asset}, Short: {short_asset}")
            return long_asset, short_asset
            
        except Exception as e:
            logger.error(f"Erro na seleção de ativos: {e}")
            return None, None
    
    def _should_select_new_assets(self) -> bool:
        """Verifica se deve selecionar novos ativos"""
        if self.last_selection_time is None:
            return True
        
        time_since_last = datetime.now() - self.last_selection_time
        return time_since_last >= timedelta(hours=config.selection_interval_hours)
    
    async def _get_assets_data(self) -> List[AssetData]:
        """Obtém dados de todos os ativos disponíveis"""
        assets_data = []
        
        for symbol in config.available_assets:
            try:
                ticker = await self.exchange_manager.get_ticker(symbol)
                
                asset = AssetData(
                    symbol=symbol,
                    price=ticker['last'],
                    volume_24h=ticker['quoteVolume'],
                    price_change_24h=ticker['percentage'],
                    volatility=self._calculate_volatility(ticker)
                )
                
                assets_data.append(asset)
                
            except Exception as e:
                logger.warning(f"Erro ao obter dados para {symbol}: {e}")
                continue
        
        return assets_data
    
    def _calculate_volatility(self, ticker: Dict) -> float:
        """Calcula volatilidade baseada no high/low"""
        try:
            high = ticker['high']
            low = ticker['low']
            if high and low and high > 0:
                return ((high - low) / high) * 100
        except:
            pass
        return 0.0
    
    def _calculate_asset_scores(self, assets: List[AssetData]) -> List[AssetData]:
        """Calcula score para cada ativo baseado em critérios"""
        for asset in assets:
            score = 0.0
            
            # Critério 1: Volume (maior volume = maior score)
            if asset.volume_24h > 0:
                volume_score = min(asset.volume_24h / 1000000, 50)  # Normalizar volume
                score += volume_score
            
            # Critério 2: Volatilidade (volatilidade moderada = maior score)
            if 2 <= asset.volatility <= 8:  # Volatilidade ideal entre 2-8%
                score += 30
            elif 1 <= asset.volatility <= 12:  # Volatilidade aceitável
                score += 15
            
            # Critério 3: Momentum (tendência de preço)
            if abs(asset.price_change_24h) > 0:
                momentum_score = min(abs(asset.price_change_24h) * 2, 20)
                score += momentum_score
            
            # Critério 4: Randomização para evitar sempre os mesmos ativos
            score += random.uniform(0, 10)
            
            asset.score = score
        
        return sorted(assets, key=lambda x: x.score, reverse=True)
    
    def _select_best_pair(self, scored_assets: List[AssetData]) -> Tuple[Optional[str], Optional[str]]:
        """Seleciona o melhor par de ativos para long e short"""
        if len(scored_assets) < 2:
            return None, None
        
        # Selecionar top 3 ativos para maior diversificação
        top_assets = scored_assets[:min(3, len(scored_assets))]
        
        # Para long: ativo com maior score (tendência de alta)
        long_asset = top_assets[0].symbol
        
        # Para short: ativo com menor momentum ou score mais baixo
        short_candidates = [a for a in scored_assets if a.symbol != long_asset]
        if short_candidates:
            # Selecionar ativo com menor momentum positivo ou momentum negativo
            short_asset = min(short_candidates, 
                            key=lambda x: x.price_change_24h if x.price_change_24h > 0 else x.score).symbol
        else:
            short_asset = scored_assets[1].symbol
        
        return long_asset, short_asset
    
    def get_selection_history(self, limit: int = 10) -> List[Dict]:
        """Obtém histórico de seleções"""
        return self.asset_history[-limit:]
    
    def force_new_selection(self):
        """Força nova seleção de ativos"""
        self.last_selection_time = None
        logger.info("Forçando nova seleção de ativos")