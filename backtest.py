"""
Backtest para Market Making Strategy
Simula performance histórica da estratégia
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
import logging

from market_making_strategy import AdaptiveMarketMakingStrategy, MarketData
from risk_manager import RiskManager
from config import get_config

class BacktestEngine:
    def __init__(self, data_file: str = None):
        self.config = get_config()
        self.strategy = AdaptiveMarketMakingStrategy()
        self.risk_manager = RiskManager()
        self.logger = logging.getLogger(__name__)
        
        # Dados históricos
        self.price_data = []
        self.volume_data = []
        self.trades = []
        
        # Resultados
        self.results = {
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
            'total_volume': 0.0,
            'daily_returns': [],
            'equity_curve': []
        }
    
    def load_sample_data(self, days: int = 30):
        """Carrega dados de exemplo para backtest"""
        # Gerar dados sintéticos baseados em movimento realista de SOL
        np.random.seed(42)  # Para reprodutibilidade
        
        start_price = 100.0  # Preço inicial de SOL
        n_periods = days * 24 * 60  # Minutos em 30 dias
        
        # Gerar preços com random walk
        returns = np.random.normal(0, 0.001, n_periods)  # 0.1% de volatilidade por minuto
        prices = [start_price]
        
        for ret in returns:
            new_price = prices[-1] * (1 + ret)
            prices.append(new_price)
        
        # Gerar volumes correlacionados com volatilidade
        volumes = []
        for i in range(1, len(prices)):
            price_change = abs(prices[i] - prices[i-1]) / prices[i-1]
            base_volume = 1000 + price_change * 10000  # Volume baseado na volatilidade
            volume = max(100, base_volume + np.random.normal(0, 500))
            volumes.append(volume)
        
        # Criar timestamps
        start_time = datetime.now() - timedelta(days=days)
        timestamps = [start_time + timedelta(minutes=i) for i in range(n_periods)]
        
        self.price_data = prices[1:]  # Remover preço inicial
        self.volume_data = volumes
        self.timestamps = timestamps
        
        self.logger.info(f"Dados de exemplo carregados: {len(self.price_data)} períodos")
    
    def run_backtest(self, initial_capital: float = 5000):
        """Executa backtest da estratégia"""
        self.logger.info("Iniciando backtest...")
        
        if not self.price_data:
            self.load_sample_data()
        
        # Resetar estratégia e risk manager
        self.strategy = AdaptiveMarketMakingStrategy()
        self.risk_manager = RiskManager()
        self.risk_manager.initial_capital = initial_capital
        
        current_capital = initial_capital
        equity_curve = [initial_capital]
        daily_returns = []
        
        # Simular cada período
        for i in range(len(self.price_data)):
            current_price = self.price_data[i]
            current_volume = self.volume_data[i]
            current_time = self.timestamps[i]
            
            # Atualizar dados de mercado
            market_data = MarketData(
                price=current_price,
                volume=current_volume,
                volatility=0.0,  # Será calculado pela estratégia
                trend=0.0,  # Será calculado pela estratégia
                timestamp=current_time
            )
            self.strategy.update_market_data(market_data)
            
            # Simular ordens (simplificado)
            if i % 10 == 0:  # A cada 10 minutos
                # Calcular spread
                bid_price, ask_price = self.strategy.calculate_adaptive_spread(current_price)
                spread = (ask_price - bid_price) / current_price
                
                # Simular execução de ordens com probabilidade baseada no spread
                execution_prob = max(0.1, 1 - spread * 100)  # Maior spread = menor probabilidade
                
                if np.random.random() < execution_prob:
                    # Simular trade
                    trade_side = np.random.choice(['buy', 'sell'])
                    trade_price = bid_price if trade_side == 'buy' else ask_price
                    trade_size = min(1.0, current_capital * 0.01 / trade_price)  # 1% do capital
                    
                    # Calcular PnL (simplificado)
                    if trade_side == 'buy':
                        # Comprou, lucra se preço sobe
                        pnl = trade_size * (current_price - trade_price)
                        self.risk_manager.current_inventory += trade_size
                    else:
                        # Vendeu, lucra se preço desce
                        pnl = trade_size * (trade_price - current_price)
                        self.risk_manager.current_inventory -= trade_size
                    
                    # Atualizar capital
                    current_capital += pnl
                    
                    # Registrar trade
                    trade_data = {
                        'timestamp': current_time,
                        'side': trade_side,
                        'price': trade_price,
                        'quantity': trade_size,
                        'pnl': pnl,
                        'volume': trade_price * trade_size
                    }
                    self.trades.append(trade_data)
                    
                    # Atualizar risk manager
                    self.risk_manager.update_trade(trade_data)
            
            # Atualizar curva de equity
            equity_curve.append(current_capital)
            
            # Calcular retorno diário
            if i > 0 and i % (24 * 60) == 0:  # A cada dia
                daily_return = (equity_curve[-1] - equity_curve[-(24*60)]) / equity_curve[-(24*60)]
                daily_returns.append(daily_return)
        
        # Calcular métricas finais
        self._calculate_results(equity_curve, daily_returns)
        
        self.logger.info("Backtest concluído")
        return self.results
    
    def _calculate_results(self, equity_curve: List[float], daily_returns: List[float]):
        """Calcula métricas de performance"""
        if not equity_curve or not daily_returns:
            return
        
        # Retorno total
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        
        # Sharpe ratio
        if len(daily_returns) > 1:
            sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
        else:
            sharpe_ratio = 0.0
        
        # Drawdown máximo
        peak = equity_curve[0]
        max_drawdown = 0.0
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # Taxa de sucesso
        winning_trades = sum(1 for trade in self.trades if trade['pnl'] > 0)
        win_rate = winning_trades / len(self.trades) if self.trades else 0.0
        
        # Volume total
        total_volume = sum(trade['volume'] for trade in self.trades)
        
        self.results = {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': len(self.trades),
            'total_volume': total_volume,
            'daily_returns': daily_returns,
            'equity_curve': equity_curve,
            'final_capital': equity_curve[-1],
            'trades': self.trades
        }
    
    def print_results(self):
        """Imprime resultados do backtest"""
        print("=" * 60)
        print("📊 RESULTADOS DO BACKTEST")
        print("=" * 60)
        print(f"💰 Capital Inicial: ${self.config['trading']['total_capital']:,.2f}")
        print(f"💰 Capital Final: ${self.results['final_capital']:,.2f}")
        print(f"📈 Retorno Total: {self.results['total_return']:.2%}")
        print(f"⚡ Sharpe Ratio: {self.results['sharpe_ratio']:.2f}")
        print(f"📉 Drawdown Máximo: {self.results['max_drawdown']:.2%}")
        print(f"🎯 Taxa de Sucesso: {self.results['win_rate']:.2%}")
        print(f"🔄 Total de Trades: {self.results['total_trades']}")
        print(f"📊 Volume Total: ${self.results['total_volume']:,.2f}")
        print("=" * 60)
    
    def save_results(self, filename: str = "backtest_results.json"):
        """Salva resultados em arquivo JSON"""
        # Converter numpy arrays para listas para JSON
        results_copy = self.results.copy()
        if 'equity_curve' in results_copy:
            results_copy['equity_curve'] = [float(x) for x in results_copy['equity_curve']]
        if 'daily_returns' in results_copy:
            results_copy['daily_returns'] = [float(x) for x in results_copy['daily_returns']]
        
        # Converter timestamps para strings
        if 'trades' in results_copy:
            for trade in results_copy['trades']:
                if 'timestamp' in trade:
                    trade['timestamp'] = trade['timestamp'].isoformat()
        
        with open(filename, 'w') as f:
            json.dump(results_copy, f, indent=2)
        
        self.logger.info(f"Resultados salvos em {filename}")

def main():
    """Função principal para executar backtest"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backtest da estratégia de market making")
    parser.add_argument("--days", "-d", type=int, default=30,
                       help="Número de dias para backtest")
    parser.add_argument("--capital", "-c", type=float, default=5000,
                       help="Capital inicial")
    parser.add_argument("--output", "-o", default="backtest_results.json",
                       help="Arquivo de saída")
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Executar backtest
    engine = BacktestEngine()
    results = engine.run_backtest(args.capital)
    
    # Mostrar resultados
    engine.print_results()
    
    # Salvar resultados
    engine.save_results(args.output)

if __name__ == "__main__":
    main()