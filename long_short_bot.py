"""
Bot principal Long&Short com reabertura automática
"""
import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from exchange_manager import ExchangeManager
from asset_selector import AssetSelector
from position_manager import PositionManager, PositionStatus
from config import config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('long_short_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class LongShortBot:
    """Bot principal para estratégia Long&Short"""
    
    def __init__(self):
        self.exchange_manager = ExchangeManager()
        self.asset_selector = AssetSelector(self.exchange_manager)
        self.position_manager = PositionManager(self.exchange_manager)
        self.running = False
        self.current_long_id = None
        self.current_short_id = None
        
        # Configurações de controle
        self.tp_percentage = config.default_tp_percentage
        self.sl_percentage = config.default_sl_percentage
        self.max_duration_hours = config.max_position_duration_hours
        
        # Estatísticas
        self.stats = {
            'total_trades': 0,
            'profitable_trades': 0,
            'total_pnl': 0.0,
            'start_time': None
        }
    
    async def start(self):
        """Inicia o bot"""
        try:
            logger.info("Iniciando Long&Short Bot...")
            self.running = True
            self.stats['start_time'] = datetime.now()
            
            # Verificar conexão com exchange
            balance = await self.exchange_manager.get_balance()
            logger.info(f"Saldo disponível: {balance.get('USDT', {}).get('free', 0):.2f} USDT")
            
            # Loop principal
            while self.running:
                try:
                    await self._main_loop()
                    await asyncio.sleep(30)  # Verificar a cada 30 segundos
                    
                except KeyboardInterrupt:
                    logger.info("Interrupção recebida, parando bot...")
                    break
                except Exception as e:
                    logger.error(f"Erro no loop principal: {e}")
                    await asyncio.sleep(60)  # Aguardar antes de tentar novamente
            
            await self._cleanup()
            
        except Exception as e:
            logger.error(f"Erro fatal ao iniciar bot: {e}")
            raise
    
    async def _main_loop(self):
        """Loop principal do bot"""
        # 1. Verificar se há posições abertas
        if self.current_long_id or self.current_short_id:
            await self._monitor_positions()
        
        # 2. Processar fila de reabertura
        reopen_results = await self.position_manager.process_reopen_queue()
        if reopen_results:
            logger.info(f"Processadas {len(reopen_results)} reaberturas")
        
        # 3. Selecionar novos ativos se necessário
        if not self.current_long_id and not self.current_short_id:
            await self._select_and_open_positions()
    
    async def _monitor_positions(self):
        """Monitora posições abertas"""
        try:
            updates = await self.position_manager.check_positions_status()
            
            for update in updates:
                if update['action'] == 'closed':
                    position_id = update['position_id']
                    reason = update['reason']
                    
                    # Atualizar IDs atuais
                    if position_id == self.current_long_id:
                        self.current_long_id = None
                    if position_id == self.current_short_id:
                        self.current_short_id = None
                    
                    # Obter dados da posição para estatísticas
                    position = self.position_manager.positions.get(position_id)
                    if position:
                        self._update_stats(position)
                        
                        # Agendar reabertura se não foi fechado por tempo máximo
                        if reason != 'tempo_maximo':
                            await self._schedule_reopen(position.symbol)
                    
                    logger.info(f"Posição {position_id} fechada - Motivo: {reason}")
            
        except Exception as e:
            logger.error(f"Erro ao monitorar posições: {e}")
    
    async def _select_and_open_positions(self):
        """Seleciona ativos e abre posições"""
        try:
            # Selecionar ativos
            long_asset, short_asset = await self.asset_selector.select_assets()
            
            if not long_asset or not short_asset:
                logger.warning("Não foi possível selecionar ativos")
                return
            
            logger.info(f"Ativos selecionados - Long: {long_asset}, Short: {short_asset}")
            
            # Abrir posições
            long_id, short_id = await self.position_manager.open_long_short_positions(
                long_asset, short_asset, self.tp_percentage, self.sl_percentage
            )
            
            if long_id and short_id:
                self.current_long_id = long_id
                self.current_short_id = short_id
                self.stats['total_trades'] += 1
                logger.info(f"Posições abertas - Long ID: {long_id}, Short ID: {short_id}")
            else:
                logger.error("Falha ao abrir posições")
        
        except Exception as e:
            logger.error(f"Erro ao selecionar e abrir posições: {e}")
    
    async def _schedule_reopen(self, symbol: str):
        """Agenda reabertura de posições"""
        try:
            # Obter ativos atuais
            long_asset, short_asset = self.asset_selector.current_long_asset, self.asset_selector.current_short_asset
            
            if long_asset and short_asset:
                await self.position_manager.schedule_reopen(
                    long_asset, short_asset, self.tp_percentage, self.sl_percentage
                )
                logger.info(f"Reabertura agendada para {long_asset} e {short_asset}")
        
        except Exception as e:
            logger.error(f"Erro ao agendar reabertura: {e}")
    
    def _update_stats(self, position):
        """Atualiza estatísticas do bot"""
        if position.pnl is not None:
            self.stats['total_pnl'] += position.pnl
            if position.pnl > 0:
                self.stats['profitable_trades'] += 1
    
    async def _cleanup(self):
        """Limpeza ao parar o bot"""
        try:
            logger.info("Fazendo limpeza...")
            
            # Fechar posições abertas
            if self.current_long_id:
                await self.position_manager.close_position(self.current_long_id, "bot_stop")
            if self.current_short_id:
                await self.position_manager.close_position(self.current_short_id, "bot_stop")
            
            # Mostrar estatísticas finais
            self._show_final_stats()
            
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
    
    def _show_final_stats(self):
        """Mostra estatísticas finais"""
        runtime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else timedelta(0)
        
        logger.info("=== ESTATÍSTICAS FINAIS ===")
        logger.info(f"Tempo de execução: {runtime}")
        logger.info(f"Total de trades: {self.stats['total_trades']}")
        logger.info(f"Trades lucrativos: {self.stats['profitable_trades']}")
        logger.info(f"PnL total: {self.stats['total_pnl']:.2f} USDT")
        
        if self.stats['total_trades'] > 0:
            win_rate = (self.stats['profitable_trades'] / self.stats['total_trades']) * 100
            logger.info(f"Taxa de acerto: {win_rate:.2f}%")
    
    def update_config(self, tp_percentage: float = None, sl_percentage: float = None,
                     max_duration_hours: int = None):
        """Atualiza configurações do bot"""
        if tp_percentage is not None:
            self.tp_percentage = tp_percentage
        if sl_percentage is not None:
            self.sl_percentage = sl_percentage
        if max_duration_hours is not None:
            self.max_duration_hours = max_duration_hours
        
        logger.info(f"Configurações atualizadas - TP: {self.tp_percentage}%, SL: {self.sl_percentage}%, Max Duration: {self.max_duration_hours}h")
    
    def get_status(self) -> Dict:
        """Obtém status atual do bot"""
        positions_summary = self.position_manager.get_positions_summary()
        
        return {
            'running': self.running,
            'current_long_id': self.current_long_id,
            'current_short_id': self.current_short_id,
            'config': {
                'tp_percentage': self.tp_percentage,
                'sl_percentage': self.sl_percentage,
                'max_duration_hours': self.max_duration_hours
            },
            'positions': positions_summary,
            'stats': self.stats
        }
    
    def stop(self):
        """Para o bot"""
        logger.info("Parando bot...")
        self.running = False

# Função principal
async def main():
    """Função principal"""
    bot = LongShortBot()
    
    # Configurar handler para interrupção
    def signal_handler(signum, frame):
        logger.info("Sinal de interrupção recebido")
        bot.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    finally:
        logger.info("Bot finalizado")

if __name__ == "__main__":
    asyncio.run(main())