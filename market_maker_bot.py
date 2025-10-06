"""
Bot Principal de Market Making para Paradex
Integra todas as funcionalidades para trading automatizado
"""

import asyncio
import logging
import json
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback
from pathlib import Path

from paradex_client import ParadexClient
from market_making_strategy import AdaptiveMarketMakingStrategy, MarketData, OrderBook
from risk_manager import RiskManager
from config import get_config, validate_config

class MarketMakerBot:
    def __init__(self):
        self.config = get_config()
        self.logger = self._setup_logging()
        self.client = None
        self.strategy = AdaptiveMarketMakingStrategy()
        self.risk_manager = RiskManager()
        self.running = False
        self.orders = {}  # {order_id: order_data}
        self.last_orderbook = None
        self.last_price = 0.0
        self.symbol = self.config['trading']['symbol']
        
        # Estatísticas
        self.stats = {
            'orders_placed': 0,
            'orders_filled': 0,
            'orders_cancelled': 0,
            'total_volume': 0.0,
            'start_time': datetime.now(),
            'last_update': datetime.now()
        }
        
        # Setup signal handlers para Windows
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Configura sistema de logging"""
        logging.basicConfig(
            level=getattr(logging, self.config['monitoring']['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['monitoring']['log_file'], encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def _setup_signal_handlers(self):
        """Configura handlers de sinal para shutdown graceful"""
        def signal_handler(signum, frame):
            self.logger.info(f"Sinal {signum} recebido. Iniciando shutdown...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Inicia o bot"""
        try:
            self.logger.info("🚀 Iniciando Market Maker Bot para Paradex")
            
            # Validar configurações
            if not validate_config():
                self.logger.error("❌ Configurações inválidas. Verifique as variáveis de ambiente.")
                return False
            
            # Conectar à API
            async with ParadexClient() as client:
                self.client = client
                
                # Verificar conexão
                balance = await client.get_account_balance()
                self.logger.info(f"💰 Saldo da conta: {balance}")
                
                # Obter preço inicial
                self.last_price = await client.get_current_price(self.symbol)
                self.logger.info(f"📊 Preço inicial {self.symbol}: ${self.last_price:.4f}")
                
                # Iniciar loop principal
                self.running = True
                await self._main_loop()
                
        except Exception as e:
            self.logger.error(f"❌ Erro fatal: {e}")
            self.logger.error(traceback.format_exc())
            return False
        finally:
            await self.stop()
    
    async def stop(self):
        """Para o bot de forma segura"""
        self.logger.info("🛑 Parando bot...")
        self.running = False
        
        # Cancelar todas as ordens abertas
        await self._cancel_all_orders()
        
        # Salvar estatísticas
        await self._save_performance_data()
        
        self.logger.info("✅ Bot parado com sucesso")
    
    async def _main_loop(self):
        """Loop principal do bot"""
        self.logger.info("🔄 Iniciando loop principal")
        
        while self.running:
            try:
                # Verificar circuit breaker
                if self.risk_manager.should_stop_trading():
                    self.logger.warning("⚠️ Trading pausado por gestão de risco")
                    await asyncio.sleep(60)
                    continue
                
                # Obter dados de mercado
                await self._update_market_data()
                
                # Gerar ordens
                orders = await self._generate_orders()
                
                # Colocar ordens
                await self._place_orders(orders)
                
                # Gerenciar ordens existentes
                await self._manage_existing_orders()
                
                # Atualizar estatísticas
                self._update_stats()
                
                # Log de status
                await self._log_status()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.config['market_making']['order_refresh_time'])
                
            except Exception as e:
                self.logger.error(f"❌ Erro no loop principal: {e}")
                self.logger.error(traceback.format_exc())
                await asyncio.sleep(30)  # Aguardar antes de tentar novamente
    
    async def _update_market_data(self):
        """Atualiza dados de mercado"""
        try:
            # Obter preço atual
            current_price = await self.client.get_current_price(self.symbol)
            if current_price > 0:
                self.last_price = current_price
            
            # Obter livro de ordens
            orderbook_data = await self.client.get_orderbook(self.symbol)
            bids = [(float(bid[0]), float(bid[1])) for bid in orderbook_data.get('bids', [])]
            asks = [(float(ask[0]), float(ask[1])) for ask in orderbook_data.get('asks', [])]
            
            self.last_orderbook = OrderBook(
                bids=bids,
                asks=asks,
                timestamp=datetime.now()
            )
            
            # Atualizar estratégia
            market_data = MarketData(
                price=current_price,
                volume=sum([qty for _, qty in bids + asks]),
                volatility=0.0,  # Será calculado pela estratégia
                trend=0.0,  # Será calculado pela estratégia
                timestamp=datetime.now()
            )
            self.strategy.update_market_data(market_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar dados de mercado: {e}")
    
    async def _generate_orders(self) -> List[Dict]:
        """Gera ordens baseadas na estratégia"""
        if not self.last_orderbook or self.last_price <= 0:
            return []
        
        try:
            # Calcular capital disponível
            balance = await self.client.get_account_balance()
            available_capital = float(balance.get('available', 0))
            
            # Gerar ordens da estratégia
            orders = self.strategy.generate_orders(
                self.last_price,
                self.last_orderbook,
                available_capital
            )
            
            # Filtrar ordens baseado no risk manager
            filtered_orders = []
            for order in orders:
                if self.risk_manager.should_place_order(
                    order['side'],
                    order['price'],
                    order['quantity'],
                    self.last_price
                ):
                    filtered_orders.append(order)
            
            return filtered_orders
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar ordens: {e}")
            return []
    
    async def _place_orders(self, orders: List[Dict]):
        """Coloca ordens na exchange"""
        for order in orders:
            try:
                # Adicionar símbolo
                order['symbol'] = self.symbol
                
                # Colocar ordem
                response = await self.client.place_order(**order)
                
                if 'orderId' in response:
                    order_id = response['orderId']
                    self.orders[order_id] = {
                        **order,
                        'order_id': order_id,
                        'status': 'open',
                        'created_at': datetime.now()
                    }
                    self.stats['orders_placed'] += 1
                    self.logger.debug(f"Ordem colocada: {order_id}")
                
            except Exception as e:
                self.logger.error(f"Erro ao colocar ordem: {e}")
    
    async def _manage_existing_orders(self):
        """Gerencia ordens existentes"""
        if not self.orders:
            return
        
        try:
            # Obter ordens abertas da exchange
            open_orders = await self.client.get_open_orders(self.symbol)
            open_order_ids = {order['orderId'] for order in open_orders}
            
            # Verificar ordens que foram preenchidas ou canceladas
            for order_id, order_data in list(self.orders.items()):
                if order_id not in open_order_ids:
                    # Ordem não está mais aberta
                    if order_data['status'] == 'open':
                        # Assumir que foi preenchida
                        await self._handle_filled_order(order_data)
                        self.orders.pop(order_id, None)
            
            # Cancelar ordens antigas (mais de 5 minutos)
            current_time = datetime.now()
            for order_id, order_data in list(self.orders.items()):
                if (current_time - order_data['created_at']).seconds > 300:  # 5 minutos
                    await self._cancel_order(order_id)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerenciar ordens: {e}")
    
    async def _handle_filled_order(self, order_data: Dict):
        """Processa ordem preenchida"""
        try:
            # Calcular PnL aproximado (simplificado)
            price_diff = abs(order_data['price'] - self.last_price)
            pnl = price_diff * order_data['quantity'] * 0.5  # Aproximação
            
            # Atualizar risk manager
            trade_data = {
                'pnl': pnl if order_data['side'] == 'sell' else -pnl,
                'volume': order_data['price'] * order_data['quantity'],
                'price': order_data['price'],
                'quantity': order_data['quantity']
            }
            self.risk_manager.update_trade(trade_data)
            
            # Atualizar estratégia
            self.strategy.update_inventory([order_data])
            
            # Atualizar estatísticas
            self.stats['orders_filled'] += 1
            self.stats['total_volume'] += trade_data['volume']
            
            self.logger.info(f"✅ Ordem preenchida: {order_data['side']} {order_data['quantity']} @ {order_data['price']}")
            
        except Exception as e:
            self.logger.error(f"Erro ao processar ordem preenchida: {e}")
    
    async def _cancel_order(self, order_id: str):
        """Cancela uma ordem"""
        try:
            await self.client.cancel_order(order_id)
            self.orders.pop(order_id, None)
            self.stats['orders_cancelled'] += 1
            self.logger.debug(f"Ordem cancelada: {order_id}")
        except Exception as e:
            self.logger.error(f"Erro ao cancelar ordem {order_id}: {e}")
    
    async def _cancel_all_orders(self):
        """Cancela todas as ordens abertas"""
        for order_id in list(self.orders.keys()):
            await self._cancel_order(order_id)
    
    def _update_stats(self):
        """Atualiza estatísticas"""
        self.stats['last_update'] = datetime.now()
    
    async def _log_status(self):
        """Log de status do bot"""
        if self.stats['orders_placed'] % 10 == 0:  # A cada 10 ordens
            risk_metrics = self.risk_manager.get_risk_metrics()
            strategy_metrics = self.strategy.get_performance_metrics()
            airdrop_progress = self.risk_manager.get_airdrop_progress()
            
            self.logger.info(f"""
📊 Status do Bot:
💰 PnL Total: ${risk_metrics.current_pnl:.2f}
📈 PnL Diário: ${risk_metrics.daily_pnl:.2f}
📉 Drawdown: {risk_metrics.current_drawdown:.2%}
🔄 Ordens: {self.stats['orders_placed']} colocadas, {self.stats['orders_filled']} preenchidas
📊 Volume Diário: ${risk_metrics.daily_volume:.2f}
🎯 Airdrop: {airdrop_progress['volume_progress']:.1%} volume, {airdrop_progress['trades_progress']:.1%} trades
            """)
    
    async def _save_performance_data(self):
        """Salva dados de performance"""
        try:
            performance_data = {
                'stats': self.stats,
                'risk_metrics': self.risk_manager.get_risk_metrics().__dict__,
                'strategy_metrics': self.strategy.get_performance_metrics(),
                'airdrop_progress': self.risk_manager.get_airdrop_progress(),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.config['monitoring']['performance_file'], 'w') as f:
                json.dump(performance_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados de performance: {e}")

async def main():
    """Função principal"""
    bot = MarketMakerBot()
    await bot.start()

if __name__ == "__main__":
    # Configurar encoding para Windows
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        traceback.print_exc()