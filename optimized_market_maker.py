"""
Bot Otimizado de Market Making para Airdrop Farming
Integra todas as estratégias para minimizar perdas e maximizar pontos de airdrop
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
from advanced_strategy import AdvancedMarketMakingStrategy, MarketData, OrderBook
from loss_minimizer import LossMinimizer
from airdrop_optimizer import AirdropOptimizer
from risk_manager import RiskManager
from config import get_config, validate_config

class OptimizedMarketMaker:
    def __init__(self):
        self.config = get_config()
        self.logger = self._setup_logging()
        
        # Componentes principais
        self.client = None
        self.strategy = AdvancedMarketMakingStrategy()
        self.loss_minimizer = LossMinimizer(self.config['trading']['total_capital'])
        self.airdrop_optimizer = AirdropOptimizer(self.config['trading']['total_capital'])
        self.risk_manager = RiskManager()
        
        # Estado do bot
        self.running = False
        self.orders = {}
        self.last_orderbook = None
        self.last_price = 0.0
        self.symbol = self.config['trading']['symbol']
        
        # Estatísticas otimizadas
        self.stats = {
            'orders_placed': 0,
            'orders_filled': 0,
            'orders_cancelled': 0,
            'total_volume': 0.0,
            'total_pnl': 0.0,
            'start_time': datetime.now(),
            'last_update': datetime.now(),
            'airdrop_score': 0.0,
            'capital_efficiency': 1.0
        }
        
        # Controles de performance
        self.performance_mode = 'balanced'  # balanced, aggressive, conservative
        self.last_performance_check = datetime.now()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Configura sistema de logging otimizado"""
        logging.basicConfig(
            level=getattr(logging, self.config['monitoring']['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('optimized_market_maker.log', encoding='utf-8'),
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
        """Inicia o bot otimizado"""
        try:
            self.logger.info("🚀 Iniciando Market Maker Otimizado para Airdrop Farming")
            
            # Validar configurações
            if not validate_config():
                self.logger.error("❌ Configurações inválidas. Verifique as variáveis de ambiente.")
                return False
            
            # Conectar à API
            async with ParadexClient() as client:
                self.client = client
                
                # Verificar conexão e saldo
                balance = await client.get_account_balance()
                self.logger.info(f"💰 Saldo da conta: {balance}")
                
                # Obter preço inicial
                self.last_price = await client.get_current_price(self.symbol)
                self.logger.info(f"📊 Preço inicial {self.symbol}: ${self.last_price:.4f}")
                
                # Iniciar loop principal otimizado
                self.running = True
                await self._optimized_main_loop()
                
        except Exception as e:
            self.logger.error(f"❌ Erro fatal: {e}")
            self.logger.error(traceback.format_exc())
            return False
        finally:
            await self.stop()
    
    async def stop(self):
        """Para o bot de forma segura"""
        self.logger.info("🛑 Parando bot otimizado...")
        self.running = False
        
        # Cancelar todas as ordens abertas
        await self._cancel_all_orders()
        
        # Salvar estatísticas finais
        await self._save_final_stats()
        
        self.logger.info("✅ Bot otimizado parado com sucesso")
    
    async def _optimized_main_loop(self):
        """Loop principal otimizado"""
        self.logger.info("🔄 Iniciando loop principal otimizado")
        
        while self.running:
            try:
                # Verificar controles de segurança
                if self._should_stop_trading():
                    self.logger.warning("⚠️ Trading pausado por controles de segurança")
                    await asyncio.sleep(60)
                    continue
                
                # Atualizar dados de mercado
                await self._update_market_data()
                
                # Ajustar modo de performance
                self._adjust_performance_mode()
                
                # Gerar ordens otimizadas
                orders = await self._generate_optimized_orders()
                
                # Filtrar e colocar ordens
                await self._place_filtered_orders(orders)
                
                # Gerenciar ordens existentes
                await self._manage_existing_orders()
                
                # Atualizar estatísticas
                self._update_optimized_stats()
                
                # Log de status otimizado
                await self._log_optimized_status()
                
                # Aguardar próximo ciclo (frequência dinâmica)
                await asyncio.sleep(self._calculate_optimal_frequency())
                
            except Exception as e:
                self.logger.error(f"❌ Erro no loop principal: {e}")
                self.logger.error(traceback.format_exc())
                await asyncio.sleep(30)
    
    def _should_stop_trading(self) -> bool:
        """Verifica se deve parar de fazer trading"""
        return (
            self.loss_minimizer.should_stop_trading() or
            self.risk_manager.should_stop_trading() or
            self.airdrop_optimizer.should_increase_aggressiveness() and self.performance_mode == 'conservative'
        )
    
    async def _update_market_data(self):
        """Atualiza dados de mercado de forma otimizada"""
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
            
            # Atualizar estratégia com dados otimizados
            market_data = MarketData(
                price=current_price,
                volume=sum([qty for _, qty in bids + asks]),
                volatility=0.0,
                trend=0.0,
                timestamp=datetime.now()
            )
            self.strategy.update_market_data(market_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar dados de mercado: {e}")
    
    def _adjust_performance_mode(self):
        """Ajusta modo de performance baseado no progresso"""
        airdrop_progress = self.airdrop_optimizer.get_airdrop_progress()
        loss_metrics = self.loss_minimizer.get_loss_metrics()
        
        # Determinar modo baseado no progresso e risco
        if loss_metrics.current_drawdown > 0.03:
            self.performance_mode = 'conservative'
        elif airdrop_progress['score'] < 0.6:
            self.performance_mode = 'aggressive'
        else:
            self.performance_mode = 'balanced'
    
    async def _generate_optimized_orders(self) -> List[Dict]:
        """Gera ordens otimizadas baseadas no modo de performance"""
        if not self.last_orderbook or self.last_price <= 0:
            return []
        
        try:
            # Obter capital disponível
            balance = await self.client.get_account_balance()
            available_capital = float(balance.get('available', 0))
            
            orders = []
            
            # Ordens baseadas no modo de performance
            if self.performance_mode == 'aggressive':
                # Modo agressivo para airdrop farming
                orders.extend(self.airdrop_optimizer.generate_airdrop_orders(
                    self.last_price, self.last_orderbook, available_capital
                ))
                
                # Adicionar ordens de arbitragem
                orders.extend(self.strategy.detect_arbitrage_opportunities(self.last_orderbook))
                
            elif self.performance_mode == 'conservative':
                # Modo conservador para proteger capital
                orders.extend(self.strategy.generate_airdrop_orders(
                    self.last_price, self.last_orderbook, available_capital
                ))
                
                # Adicionar ordens de hedge
                orders.extend(self.loss_minimizer.calculate_hedge_orders(
                    self.last_price, self.strategy.current_inventory
                ))
                
            else:  # balanced
                # Modo balanceado
                orders.extend(self.strategy.generate_airdrop_orders(
                    self.last_price, self.last_orderbook, available_capital
                ))
                
                # Adicionar ordens de mean reversion
                orders.extend(self.strategy.calculate_mean_reversion_orders(
                    self.last_price, self.strategy.price_history
                ))
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar ordens: {e}")
            return []
    
    async def _place_filtered_orders(self, orders: List[Dict]):
        """Coloca ordens filtradas pelos controles de segurança"""
        for order in orders:
            try:
                # Verificar se deve colocar a ordem
                if not self.loss_minimizer.should_place_order(order):
                    continue
                
                # Ajustar tamanho da ordem
                if 'quantity' in order:
                    safe_size = self.loss_minimizer.calculate_safe_position_size(
                        order['quantity'], order['price']
                    )
                    order['quantity'] = safe_size
                
                # Ajustar spread
                if 'price' in order:
                    base_spread = abs(order['price'] - self.last_price) / self.last_price
                    safe_spread = self.loss_minimizer.calculate_safe_spread(base_spread)
                    # Aplicar ajuste de spread (simplificado)
                
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
                        'created_at': datetime.now(),
                        'priority': order.get('priority', 'normal')
                    }
                    self.stats['orders_placed'] += 1
                    self.logger.debug(f"Ordem colocada: {order_id} ({order.get('priority', 'normal')})")
                
            except Exception as e:
                self.logger.error(f"Erro ao colocar ordem: {e}")
    
    async def _manage_existing_orders(self):
        """Gerencia ordens existentes de forma otimizada"""
        if not self.orders:
            return
        
        try:
            # Obter ordens abertas da exchange
            open_orders = await self.client.get_open_orders(self.symbol)
            open_order_ids = {order['orderId'] for order in open_orders}
            
            # Processar ordens preenchidas
            for order_id, order_data in list(self.orders.items()):
                if order_id not in open_order_ids and order_data['status'] == 'open':
                    await self._handle_filled_order(order_data)
                    self.orders.pop(order_id, None)
            
            # Cancelar ordens antigas baseado na prioridade
            current_time = datetime.now()
            for order_id, order_data in list(self.orders.items()):
                age_seconds = (current_time - order_data['created_at']).seconds
                priority = order_data.get('priority', 'normal')
                
                # Timeouts baseados na prioridade
                timeout = {
                    'emergency': 30,
                    'arbitrage': 60,
                    'hedge': 120,
                    'airdrop_optimization': 180,
                    'normal': 300
                }.get(priority, 300)
                
                if age_seconds > timeout:
                    await self._cancel_order(order_id)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerenciar ordens: {e}")
    
    async def _handle_filled_order(self, order_data: Dict):
        """Processa ordem preenchida de forma otimizada"""
        try:
            # Calcular PnL aproximado
            price_diff = abs(order_data['price'] - self.last_price)
            pnl = price_diff * order_data['quantity'] * 0.5
            
            # Ajustar PnL baseado no lado da ordem
            if order_data['side'] == 'sell':
                pnl = pnl
            else:
                pnl = -pnl
            
            # Dados da trade
            trade_data = {
                'pnl': pnl,
                'volume': order_data['price'] * order_data['quantity'],
                'price': order_data['price'],
                'quantity': order_data['quantity'],
                'priority': order_data.get('priority', 'normal')
            }
            
            # Atualizar todos os componentes
            self.loss_minimizer.update_trade_result(trade_data)
            self.airdrop_optimizer.update_trade(trade_data)
            self.risk_manager.update_trade(trade_data)
            self.strategy.update_inventory([order_data])
            
            # Atualizar estatísticas
            self.stats['orders_filled'] += 1
            self.stats['total_volume'] += trade_data['volume']
            self.stats['total_pnl'] += pnl
            
            self.logger.info(f"✅ Ordem preenchida: {order_data['side']} {order_data['quantity']:.4f} @ ${order_data['price']:.4f} (PnL: ${pnl:.4f})")
            
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
    
    def _calculate_optimal_frequency(self) -> int:
        """Calcula frequência ótima de trading"""
        base_frequency = self.config['market_making']['order_refresh_time']
        
        # Ajustar baseado no modo de performance
        if self.performance_mode == 'aggressive':
            return max(10, base_frequency // 2)  # Mais frequente
        elif self.performance_mode == 'conservative':
            return base_frequency * 2  # Menos frequente
        else:
            return base_frequency
    
    def _update_optimized_stats(self):
        """Atualiza estatísticas otimizadas"""
        self.stats['last_update'] = datetime.now()
        
        # Calcular score de airdrop
        airdrop_progress = self.airdrop_optimizer.get_airdrop_progress()
        self.stats['airdrop_score'] = airdrop_progress['score']
        
        # Calcular eficiência de capital
        loss_metrics = self.loss_minimizer.get_loss_metrics()
        self.stats['capital_efficiency'] = loss_metrics.capital_efficiency
    
    async def _log_optimized_status(self):
        """Log de status otimizado"""
        if self.stats['orders_placed'] % 5 == 0:  # A cada 5 ordens
            airdrop_progress = self.airdrop_optimizer.get_airdrop_progress()
            loss_metrics = self.loss_minimizer.get_loss_metrics()
            risk_metrics = self.risk_manager.get_risk_metrics()
            
            self.logger.info(f"""
🎯 STATUS OTIMIZADO - Modo: {self.performance_mode.upper()}
💰 Capital: ${loss_metrics.capital_efficiency * self.config['trading']['total_capital']:.2f}
📊 PnL Total: ${self.stats['total_pnl']:.2f}
📈 PnL Diário: ${risk_metrics.daily_pnl:.2f}
📉 Drawdown: {loss_metrics.current_drawdown:.2%}
🔄 Ordens: {self.stats['orders_placed']} colocadas, {self.stats['orders_filled']} preenchidas
📊 Volume Diário: ${airdrop_progress['daily']['volume']:.2f} / ${airdrop_progress['daily']['target_volume']:.2f}
🎯 Score Airdrop: {airdrop_progress['score']:.1%}
⚡ Eficiência: {self.stats['capital_efficiency']:.1%}
            """)
    
    async def _save_final_stats(self):
        """Salva estatísticas finais"""
        try:
            final_stats = {
                'stats': self.stats,
                'airdrop_progress': self.airdrop_optimizer.get_airdrop_progress(),
                'loss_metrics': self.loss_minimizer.get_loss_metrics().__dict__,
                'risk_metrics': self.risk_manager.get_risk_metrics().__dict__,
                'performance_mode': self.performance_mode,
                'timestamp': datetime.now().isoformat()
            }
            
            with open('optimized_performance.json', 'w') as f:
                json.dump(final_stats, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar estatísticas finais: {e}")

async def main():
    """Função principal"""
    bot = OptimizedMarketMaker()
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