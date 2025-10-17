"""
Gerenciador de posições Long&Short
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from exchange_manager import ExchangeManager
from config import config

logger = logging.getLogger(__name__)

class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"

class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    PENDING_OPEN = "pending_open"
    PENDING_CLOSE = "pending_close"

@dataclass
class Position:
    """Representa uma posição de trading"""
    id: str
    symbol: str
    side: PositionSide
    entry_price: float
    amount: float
    entry_time: datetime
    status: PositionStatus
    tp_price: Optional[float] = None
    sl_price: Optional[float] = None
    tp_order_id: Optional[str] = None
    sl_order_id: Optional[str] = None
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None
    pnl_percentage: Optional[float] = None

class PositionManager:
    """Gerenciador de posições Long&Short"""
    
    def __init__(self, exchange_manager: ExchangeManager):
        self.exchange_manager = exchange_manager
        self.positions: Dict[str, Position] = {}
        self.position_counter = 0
        self.reopen_queue: List[Dict] = []
    
    async def open_long_short_positions(self, long_asset: str, short_asset: str,
                                      tp_percentage: float = None, 
                                      sl_percentage: float = None) -> Tuple[Optional[str], Optional[str]]:
        """Abre posições long e short simultaneamente"""
        try:
            if tp_percentage is None:
                tp_percentage = config.default_tp_percentage
            if sl_percentage is None:
                sl_percentage = config.default_sl_percentage
            
            logger.info(f"Abrindo posições - Long: {long_asset}, Short: {short_asset}")
            
            # Obter preços atuais
            long_ticker = await self.exchange_manager.get_ticker(long_asset)
            short_ticker = await self.exchange_manager.get_ticker(short_asset)
            
            long_price = long_ticker['last']
            short_price = short_ticker['last']
            
            # Calcular tamanhos das posições
            long_amount = self.exchange_manager.calculate_position_size(long_asset, long_price)
            short_amount = self.exchange_manager.calculate_position_size(short_asset, short_price)
            
            # Criar posições
            long_position = await self._create_position(
                long_asset, PositionSide.LONG, long_price, long_amount, tp_percentage, sl_percentage
            )
            short_position = await self._create_position(
                short_asset, PositionSide.SHORT, short_price, short_amount, tp_percentage, sl_percentage
            )
            
            if long_position and short_position:
                logger.info(f"Posições criadas - Long ID: {long_position.id}, Short ID: {short_position.id}")
                return long_position.id, short_position.id
            else:
                logger.error("Falha ao criar posições")
                return None, None
                
        except Exception as e:
            logger.error(f"Erro ao abrir posições: {e}")
            return None, None
    
    async def _create_position(self, symbol: str, side: PositionSide, price: float,
                             amount: float, tp_percentage: float, sl_percentage: float) -> Optional[Position]:
        """Cria uma nova posição"""
        try:
            # Gerar ID único
            self.position_counter += 1
            position_id = f"{side.value}_{symbol}_{self.position_counter}_{int(datetime.now().timestamp())}"
            
            # Calcular preços de TP e SL
            if side == PositionSide.LONG:
                tp_price = price * (1 + tp_percentage / 100)
                sl_price = price * (1 - sl_percentage / 100)
            else:  # SHORT
                tp_price = price * (1 - tp_percentage / 100)
                sl_price = price * (1 + sl_percentage / 100)
            
            # Executar ordem de entrada
            entry_order = await self.exchange_manager.place_market_order(
                symbol, side.value, amount
            )
            
            if not entry_order:
                logger.error(f"Falha ao executar ordem de entrada para {symbol}")
                return None
            
            # Criar posição
            position = Position(
                id=position_id,
                symbol=symbol,
                side=side,
                entry_price=price,
                amount=amount,
                entry_time=datetime.now(),
                status=PositionStatus.OPEN,
                tp_price=tp_price,
                sl_price=sl_price
            )
            
            # Colocar ordens de TP e SL
            try:
                tp_order = await self.exchange_manager.place_take_profit_order(
                    symbol, "sell" if side == PositionSide.LONG else "buy", 
                    amount, tp_price
                )
                if tp_order:
                    position.tp_order_id = tp_order['id']
                
                sl_order = await self.exchange_manager.place_stop_loss_order(
                    symbol, "sell" if side == PositionSide.LONG else "buy",
                    amount, sl_price
                )
                if sl_order:
                    position.sl_order_id = sl_order['id']
                    
            except Exception as e:
                logger.warning(f"Erro ao colocar ordens TP/SL para {symbol}: {e}")
            
            # Armazenar posição
            self.positions[position_id] = position
            
            return position
            
        except Exception as e:
            logger.error(f"Erro ao criar posição para {symbol}: {e}")
            return None
    
    async def close_position(self, position_id: str, reason: str = "manual") -> bool:
        """Fecha uma posição"""
        try:
            position = self.positions.get(position_id)
            if not position:
                logger.error(f"Posição {position_id} não encontrada")
                return False
            
            if position.status != PositionStatus.OPEN:
                logger.warning(f"Posição {position_id} não está aberta")
                return False
            
            logger.info(f"Fechando posição {position_id} - Motivo: {reason}")
            
            # Cancelar ordens TP e SL
            if position.tp_order_id:
                await self.exchange_manager.cancel_order(position.tp_order_id, position.symbol)
            if position.sl_order_id:
                await self.exchange_manager.cancel_order(position.sl_order_id, position.symbol)
            
            # Obter preço atual
            ticker = await self.exchange_manager.get_ticker(position.symbol)
            current_price = ticker['last']
            
            # Executar ordem de fechamento
            close_side = "sell" if position.side == PositionSide.LONG else "buy"
            close_order = await self.exchange_manager.place_market_order(
                position.symbol, close_side, position.amount
            )
            
            if close_order:
                # Atualizar posição
                position.status = PositionStatus.CLOSED
                position.exit_price = current_price
                position.exit_time = datetime.now()
                
                # Calcular PnL
                if position.side == PositionSide.LONG:
                    position.pnl = (current_price - position.entry_price) * position.amount
                else:  # SHORT
                    position.pnl = (position.entry_price - current_price) * position.amount
                
                position.pnl_percentage = (position.pnl / (position.entry_price * position.amount)) * 100
                
                logger.info(f"Posição {position_id} fechada - PnL: {position.pnl:.2f} USDT ({position.pnl_percentage:.2f}%)")
                return True
            else:
                logger.error(f"Falha ao fechar posição {position_id}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao fechar posição {position_id}: {e}")
            return False
    
    async def check_positions_status(self) -> List[Dict]:
        """Verifica status de todas as posições abertas"""
        updates = []
        
        for position_id, position in self.positions.items():
            if position.status != PositionStatus.OPEN:
                continue
            
            try:
                # Verificar se atingiu tempo máximo
                if self._should_close_by_time(position):
                    await self.close_position(position_id, "tempo_maximo")
                    updates.append({
                        'position_id': position_id,
                        'action': 'closed',
                        'reason': 'tempo_maximo'
                    })
                    continue
                
                # Verificar ordens abertas
                open_orders = await self.exchange_manager.get_open_orders(position.symbol)
                order_ids = [order['id'] for order in open_orders]
                
                # Se TP ou SL foi executado
                if position.tp_order_id not in order_ids or position.sl_order_id not in order_ids:
                    await self.close_position(position_id, "tp_sl_executado")
                    updates.append({
                        'position_id': position_id,
                        'action': 'closed',
                        'reason': 'tp_sl_executado'
                    })
                    continue
                
            except Exception as e:
                logger.error(f"Erro ao verificar posição {position_id}: {e}")
        
        return updates
    
    def _should_close_by_time(self, position: Position) -> bool:
        """Verifica se posição deve ser fechada por tempo"""
        time_elapsed = datetime.now() - position.entry_time
        max_duration = timedelta(hours=config.max_position_duration_hours)
        return time_elapsed >= max_duration
    
    async def schedule_reopen(self, long_asset: str, short_asset: str, 
                            tp_percentage: float = None, sl_percentage: float = None):
        """Agenda reabertura de posições após delay"""
        reopen_time = datetime.now() + timedelta(minutes=config.reopen_delay_minutes)
        
        reopen_data = {
            'timestamp': reopen_time,
            'long_asset': long_asset,
            'short_asset': short_asset,
            'tp_percentage': tp_percentage or config.default_tp_percentage,
            'sl_percentage': sl_percentage or config.default_sl_percentage
        }
        
        self.reopen_queue.append(reopen_data)
        logger.info(f"Reabertura agendada para {reopen_time} - Long: {long_asset}, Short: {short_asset}")
    
    async def process_reopen_queue(self) -> List[Dict]:
        """Processa fila de reabertura"""
        now = datetime.now()
        to_reopen = []
        remaining_queue = []
        
        for reopen_data in self.reopen_queue:
            if reopen_data['timestamp'] <= now:
                to_reopen.append(reopen_data)
            else:
                remaining_queue.append(reopen_data)
        
        self.reopen_queue = remaining_queue
        results = []
        
        for reopen_data in to_reopen:
            try:
                long_id, short_id = await self.open_long_short_positions(
                    reopen_data['long_asset'],
                    reopen_data['short_asset'],
                    reopen_data['tp_percentage'],
                    reopen_data['sl_percentage']
                )
                
                results.append({
                    'action': 'reopened',
                    'long_asset': reopen_data['long_asset'],
                    'short_asset': reopen_data['short_asset'],
                    'long_id': long_id,
                    'short_id': short_id
                })
                
            except Exception as e:
                logger.error(f"Erro na reabertura: {e}")
                results.append({
                    'action': 'reopen_failed',
                    'error': str(e)
                })
        
        return results
    
    def get_positions_summary(self) -> Dict:
        """Obtém resumo das posições"""
        open_positions = [p for p in self.positions.values() if p.status == PositionStatus.OPEN]
        closed_positions = [p for p in self.positions.values() if p.status == PositionStatus.CLOSED]
        
        total_pnl = sum(p.pnl or 0 for p in closed_positions)
        total_pnl_percentage = sum(p.pnl_percentage or 0 for p in closed_positions)
        
        return {
            'open_count': len(open_positions),
            'closed_count': len(closed_positions),
            'total_pnl': total_pnl,
            'total_pnl_percentage': total_pnl_percentage,
            'reopen_queue_size': len(self.reopen_queue)
        }