#!/usr/bin/env python3
"""
🔬 Backtest Optimizer
Simula diferentes combinações de SL/TP/Time em dados reais
Para encontrar os melhores parâmetros
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import itertools
from pathlib import Path


class BacktestOptimizer:
    """Otimizador de parâmetros usando dados históricos"""
    
    def __init__(self, db_path: str = "trades.db"):
        """
        Initialize optimizer
        
        Args:
            db_path: Path to trading database
        """
        self.db_path = db_path
        self.conn = None
        self.trades_df = None
        self.cycles_df = None
        
        # Connect and load data
        self._connect()
        self._load_data()
    
    def _connect(self):
        """Connect to database"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(
                f"❌ Database não encontrado: {self.db_path}\n"
                f"   Execute o bot primeiro para gerar dados!"
            )
        
        self.conn = sqlite3.connect(self.db_path)
        print(f"✅ Conectado: {self.db_path}")
    
    def _load_data(self):
        """Load trades and cycles from database"""
        # Load closed trades
        self.trades_df = pd.read_sql_query("""
            SELECT * FROM trades WHERE status = 'CLOSED'
        """, self.conn)
        
        # Load cycles
        self.cycles_df = pd.read_sql_query("""
            SELECT * FROM cycles WHERE status = 'CLOSED'
        """, self.conn)
        
        print(f"✅ Carregados: {len(self.trades_df)} trades, {len(self.cycles_df)} ciclos")
        
        if len(self.trades_df) == 0:
            raise ValueError(
                "⚠️  Nenhum trade encontrado no database!\n"
                "   Execute o bot primeiro para coletar dados."
            )
    
    def simulate_cycle_with_params(self, cycle_id: str, sl: float, tp: float, 
                                   time_limit: int) -> Dict:
        """
        Simula um ciclo com novos parâmetros SL/TP/Time
        
        Args:
            cycle_id: ID do ciclo
            sl: Stop Loss em USD (negativo)
            tp: Take Profit em USD (positivo)
            time_limit: Tempo limite em minutos
            
        Returns:
            Dict com resultado simulado
        """
        # Get all trades from this cycle
        cycle_trades = self.trades_df[self.trades_df['cycle_id'] == cycle_id].copy()
        
        if len(cycle_trades) == 0:
            return None
        
        # Get cycle start time
        cycle_info = self.cycles_df[self.cycles_df['cycle_id'] == cycle_id].iloc[0]
        start_time = pd.to_datetime(cycle_info['start_time'])
        
        # Simulate monitoring loop
        # We need to reconstruct what PnL would be at each moment
        # For simplicity, we assume linear PnL progression
        
        max_duration = cycle_trades['duration_minutes'].max()
        if pd.isna(max_duration):
            max_duration = time_limit
        
        # Sample PnL at each minute
        simulated_pnl = []
        
        for minute in range(0, int(max_duration) + 1):
            # Calculate PnL at this minute for each position
            minute_pnl = 0
            
            for _, trade in cycle_trades.iterrows():
                trade_duration = trade['duration_minutes']
                if pd.isna(trade_duration):
                    trade_duration = 0
                
                if minute <= trade_duration:
                    # Position still open, calculate proportional PnL
                    if trade_duration > 0:
                        proportion = minute / trade_duration
                        minute_pnl += trade['realized_pnl'] * proportion
                    else:
                        minute_pnl += 0
                else:
                    # Position already closed
                    minute_pnl += trade['realized_pnl']
            
            simulated_pnl.append({
                'minute': minute,
                'total_pnl': minute_pnl
            })
            
            # Check exit conditions
            if minute_pnl >= tp:
                return {
                    'cycle_id': cycle_id,
                    'simulated_sl': sl,
                    'simulated_tp': tp,
                    'simulated_time': time_limit,
                    'exit_reason': 'TAKE_PROFIT',
                    'exit_minute': minute,
                    'final_pnl': minute_pnl,
                    'original_pnl': cycle_info['total_pnl'],
                    'original_reason': cycle_info['close_reason'],
                    'original_duration': cycle_info['duration_minutes']
                }
            
            if minute_pnl <= sl:
                return {
                    'cycle_id': cycle_id,
                    'simulated_sl': sl,
                    'simulated_tp': tp,
                    'simulated_time': time_limit,
                    'exit_reason': 'STOP_LOSS',
                    'exit_minute': minute,
                    'final_pnl': minute_pnl,
                    'original_pnl': cycle_info['total_pnl'],
                    'original_reason': cycle_info['close_reason'],
                    'original_duration': cycle_info['duration_minutes']
                }
            
            if minute >= time_limit:
                return {
                    'cycle_id': cycle_id,
                    'simulated_sl': sl,
                    'simulated_tp': tp,
                    'simulated_time': time_limit,
                    'exit_reason': 'TIME_LIMIT',
                    'exit_minute': minute,
                    'final_pnl': minute_pnl,
                    'original_pnl': cycle_info['total_pnl'],
                    'original_reason': cycle_info['close_reason'],
                    'original_duration': cycle_info['duration_minutes']
                }
        
        # Should not reach here, but if it does, return time limit result
        return {
            'cycle_id': cycle_id,
            'simulated_sl': sl,
            'simulated_tp': tp,
            'simulated_time': time_limit,
            'exit_reason': 'TIME_LIMIT',
            'exit_minute': time_limit,
            'final_pnl': simulated_pnl[-1]['total_pnl'] if simulated_pnl else 0,
            'original_pnl': cycle_info['total_pnl'],
            'original_reason': cycle_info['close_reason'],
            'original_duration': cycle_info['duration_minutes']
        }
    
    def optimize(self, 
                 sl_range: List[float] = [-50, -75, -100, -125, -150, -200],
                 tp_range: List[float] = [100, 150, 200, 250, 300, 400],
                 time_range: List[int] = [30, 45, 60, 90, 120]) -> pd.DataFrame:
        """
        Testa todas as combinações de SL/TP/Time
        
        Args:
            sl_range: Lista de Stop Loss para testar
            tp_range: Lista de Take Profit para testar
            time_range: Lista de tempos limite para testar
            
        Returns:
            DataFrame com resultados de todas combinações
        """
        print("\n" + "="*70)
        print("🔬 INICIANDO OTIMIZAÇÃO DE PARÂMETROS")
        print("="*70)
        
        total_combinations = len(sl_range) * len(tp_range) * len(time_range)
        print(f"📊 Testando {total_combinations} combinações...")
        print(f"   SL: {sl_range}")
        print(f"   TP: {tp_range}")
        print(f"   Time: {time_range}")
        print(f"   Ciclos: {len(self.cycles_df)}")
        print()
        
        results = []
        
        # Test all combinations
        for sl, tp, time_limit in itertools.product(sl_range, tp_range, time_range):
            combination_results = []
            
            # Simulate each cycle with these parameters
            for cycle_id in self.cycles_df['cycle_id']:
                result = self.simulate_cycle_with_params(cycle_id, sl, tp, time_limit)
                if result:
                    combination_results.append(result)
            
            # Calculate aggregate metrics for this combination
            if combination_results:
                df_combo = pd.DataFrame(combination_results)
                
                total_pnl = df_combo['final_pnl'].sum()
                avg_pnl = df_combo['final_pnl'].mean()
                wins = (df_combo['final_pnl'] > 0).sum()
                losses = (df_combo['final_pnl'] < 0).sum()
                win_rate = (wins / len(df_combo)) * 100 if len(df_combo) > 0 else 0
                
                avg_win = df_combo[df_combo['final_pnl'] > 0]['final_pnl'].mean()
                avg_loss = df_combo[df_combo['final_pnl'] < 0]['final_pnl'].mean()
                
                if pd.notna(avg_win) and pd.notna(avg_loss) and avg_loss != 0:
                    profit_factor = abs(avg_win / avg_loss)
                else:
                    profit_factor = 0
                
                avg_duration = df_combo['exit_minute'].mean()
                
                tp_hits = (df_combo['exit_reason'] == 'TAKE_PROFIT').sum()
                sl_hits = (df_combo['exit_reason'] == 'STOP_LOSS').sum()
                time_hits = (df_combo['exit_reason'] == 'TIME_LIMIT').sum()
                
                results.append({
                    'sl': sl,
                    'tp': tp,
                    'time_limit': time_limit,
                    'total_pnl': total_pnl,
                    'avg_pnl': avg_pnl,
                    'trades': len(df_combo),
                    'wins': wins,
                    'losses': losses,
                    'win_rate': win_rate,
                    'avg_win': avg_win if pd.notna(avg_win) else 0,
                    'avg_loss': avg_loss if pd.notna(avg_loss) else 0,
                    'profit_factor': profit_factor,
                    'avg_duration': avg_duration,
                    'tp_hits': tp_hits,
                    'sl_hits': sl_hits,
                    'time_hits': time_hits
                })
        
        results_df = pd.DataFrame(results)
        
        print("✅ Otimização concluída!")
        print()
        
        return results_df
    
    def print_top_results(self, results_df: pd.DataFrame, top_n: int = 10):
        """
        Mostra os melhores resultados
        
        Args:
            results_df: DataFrame com resultados
            top_n: Número de resultados para mostrar
        """
        print("="*70)
        print(f"🏆 TOP {top_n} MELHORES COMBINAÇÕES (por PnL total)")
        print("="*70)
        
        top = results_df.nlargest(top_n, 'total_pnl')
        
        for idx, row in top.iterrows():
            print(f"\n#{idx+1}")
            print(f"   SL: ${row['sl']:.0f} | TP: ${row['tp']:.0f} | Time: {row['time_limit']:.0f}min")
            print(f"   💰 Total PnL: ${row['total_pnl']:+.2f}")
            print(f"   📊 Avg PnL: ${row['avg_pnl']:+.2f}")
            print(f"   🎯 Win Rate: {row['win_rate']:.1f}% ({row['wins']:.0f}W / {row['losses']:.0f}L)")
            print(f"   📈 Profit Factor: {row['profit_factor']:.2f}")
            print(f"   ⏱️  Avg Duration: {row['avg_duration']:.0f} min")
            print(f"   🎲 Exits: TP={row['tp_hits']:.0f} | SL={row['sl_hits']:.0f} | Time={row['time_hits']:.0f}")
        
        print("\n" + "="*70)
        print("🎯 MELHOR COMBINAÇÃO RECOMENDADA:")
        print("="*70)
        best = top.iloc[0]
        print(f"\nEdite seu config.txt:")
        print(f"   STOP_LOSS_USD={best['sl']:.0f}")
        print(f"   TAKE_PROFIT_USD={best['tp']:.0f}")
        print(f"   TIME_LIMIT_MINUTES={best['time_limit']:.0f}")
        print()
        print(f"Resultado esperado:")
        print(f"   💰 Avg PnL por ciclo: ${best['avg_pnl']:+.2f}")
        print(f"   🎯 Win Rate: {best['win_rate']:.1f}%")
        print(f"   📈 Profit Factor: {best['profit_factor']:.2f}")
        print()
    
    def save_results(self, results_df: pd.DataFrame, filename: str = "backtest_results.csv"):
        """
        Salva resultados em CSV
        
        Args:
            results_df: DataFrame com resultados
            filename: Nome do arquivo
        """
        results_df.to_csv(filename, index=False)
        print(f"✅ Resultados salvos: {filename}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🔬 BACKTEST OPTIMIZER - Encontrar Melhor SL/TP/Time")
    print("="*70)
    print()
    
    try:
        # Initialize optimizer
        optimizer = BacktestOptimizer("trades.db")
        
        # Show current data summary
        print("📊 DADOS DISPONÍVEIS:")
        print(f"   Total trades: {len(optimizer.trades_df)}")
        print(f"   Total ciclos: {len(optimizer.cycles_df)}")
        
        if len(optimizer.cycles_df) > 0:
            print(f"   PnL total real: ${optimizer.cycles_df['total_pnl'].sum():.2f}")
            print(f"   Período: {optimizer.cycles_df['start_time'].min()} a {optimizer.cycles_df['start_time'].max()}")
        
        print()
        
        # Run optimization
        results_df = optimizer.optimize(
            sl_range=[-50, -75, -100, -125, -150, -200],
            tp_range=[100, 150, 200, 250, 300, 400],
            time_range=[30, 45, 60, 90, 120]
        )
        
        # Show top results
        optimizer.print_top_results(results_df, top_n=10)
        
        # Save results
        optimizer.save_results(results_df, "backtest_results.csv")
        
        # Additional analysis
        print("\n" + "="*70)
        print("📊 ANÁLISE ADICIONAL")
        print("="*70)
        
        print("\n🎯 Melhor SL (mantendo TP=200, Time=60):")
        filtered = results_df[(results_df['tp'] == 200) & (results_df['time_limit'] == 60)]
        if len(filtered) > 0:
            best_sl = filtered.nlargest(1, 'total_pnl').iloc[0]
            print(f"   SL: ${best_sl['sl']:.0f} → PnL: ${best_sl['total_pnl']:+.2f}")
        
        print("\n💰 Melhor TP (mantendo SL=-100, Time=60):")
        filtered = results_df[(results_df['sl'] == -100) & (results_df['time_limit'] == 60)]
        if len(filtered) > 0:
            best_tp = filtered.nlargest(1, 'total_pnl').iloc[0]
            print(f"   TP: ${best_tp['tp']:.0f} → PnL: ${best_tp['total_pnl']:+.2f}")
        
        print("\n⏱️  Melhor Time (mantendo SL=-100, TP=200):")
        filtered = results_df[(results_df['sl'] == -100) & (results_df['tp'] == 200)]
        if len(filtered) > 0:
            best_time = filtered.nlargest(1, 'total_pnl').iloc[0]
            print(f"   Time: {best_time['time_limit']:.0f}min → PnL: ${best_time['total_pnl']:+.2f}")
        
        print()
        
        optimizer.close()
        
    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\n💡 COMO USAR:")
        print("   1. Execute o bot primeiro: python3 main.py")
        print("   2. Deixe rodar por alguns ciclos (pelo menos 10-20)")
        print("   3. Depois execute este script: python3 backtest_optimizer.py")
        print()
        
    except ValueError as e:
        print(f"\n{e}")
        print()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
