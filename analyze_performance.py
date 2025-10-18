#!/usr/bin/env python3
"""
📊 Análise Rápida de Performance
Script simples para ver como o bot está performando
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime


def analyze_trades(db_path: str = "trades.db"):
    """Analisa trades do database"""
    
    if not Path(db_path).exists():
        print(f"❌ Database não encontrado: {db_path}")
        print("   Execute o bot primeiro para gerar dados!")
        return
    
    conn = sqlite3.connect(db_path)
    
    # Load data
    trades_df = pd.read_sql_query("SELECT * FROM trades WHERE status = 'CLOSED'", conn)
    cycles_df = pd.read_sql_query("SELECT * FROM cycles WHERE status = 'CLOSED'", conn)
    
    if len(trades_df) == 0:
        print("⚠️  Nenhum trade encontrado ainda!")
        print("   Deixe o bot rodar por alguns ciclos primeiro.")
        conn.close()
        return
    
    print("\n" + "="*70)
    print("📊 ANÁLISE DE PERFORMANCE DO BOT")
    print("="*70)
    
    # Overall stats
    print("\n🎯 RESUMO GERAL:")
    print(f"   Total de trades: {len(trades_df)}")
    print(f"   Total de ciclos: {len(cycles_df)}")
    print(f"   PnL total: ${trades_df['realized_pnl'].sum():+.2f}")
    
    wins = (trades_df['realized_pnl'] > 0).sum()
    losses = (trades_df['realized_pnl'] < 0).sum()
    win_rate = (wins / len(trades_df) * 100) if len(trades_df) > 0 else 0
    
    print(f"   Trades ganhos: {wins} ({win_rate:.1f}%)")
    print(f"   Trades perdidos: {losses} ({100-win_rate:.1f}%)")
    
    avg_win = trades_df[trades_df['realized_pnl'] > 0]['realized_pnl'].mean()
    avg_loss = trades_df[trades_df['realized_pnl'] < 0]['realized_pnl'].mean()
    
    if pd.notna(avg_win):
        print(f"   Ganho médio: ${avg_win:+.2f}")
    if pd.notna(avg_loss):
        print(f"   Perda média: ${avg_loss:+.2f}")
    
    if pd.notna(avg_win) and pd.notna(avg_loss) and avg_loss != 0:
        profit_factor = abs(avg_win / avg_loss)
        print(f"   Profit Factor: {profit_factor:.2f}")
    
    # Performance por símbolo
    print("\n" + "="*70)
    print("📈 PERFORMANCE POR SÍMBOLO:")
    print("="*70)
    
    for symbol in trades_df['symbol'].unique():
        symbol_trades = trades_df[trades_df['symbol'] == symbol]
        symbol_pnl = symbol_trades['realized_pnl'].sum()
        symbol_wins = (symbol_trades['realized_pnl'] > 0).sum()
        symbol_total = len(symbol_trades)
        symbol_wr = (symbol_wins / symbol_total * 100) if symbol_total > 0 else 0
        
        print(f"\n{symbol}:")
        print(f"   Trades: {symbol_total}")
        print(f"   PnL: ${symbol_pnl:+.2f}")
        print(f"   Win Rate: {symbol_wr:.1f}%")
    
    # Performance LONG vs SHORT
    print("\n" + "="*70)
    print("🔄 LONG vs SHORT:")
    print("="*70)
    
    for side in ['LONG', 'SHORT']:
        side_trades = trades_df[trades_df['side'] == side]
        if len(side_trades) > 0:
            side_pnl = side_trades['realized_pnl'].sum()
            side_wins = (side_trades['realized_pnl'] > 0).sum()
            side_total = len(side_trades)
            side_wr = (side_wins / side_total * 100)
            
            print(f"\n{side}:")
            print(f"   Trades: {side_total}")
            print(f"   PnL: ${side_pnl:+.2f}")
            print(f"   Win Rate: {side_wr:.1f}%")
    
    # Análise de fechamentos
    print("\n" + "="*70)
    print("🎲 RAZÕES DE FECHAMENTO:")
    print("="*70)
    
    for reason in trades_df['close_reason'].unique():
        if pd.notna(reason):
            reason_trades = trades_df[trades_df['close_reason'] == reason]
            reason_pnl = reason_trades['realized_pnl'].sum()
            reason_count = len(reason_trades)
            reason_avg = reason_trades['realized_pnl'].mean()
            
            print(f"\n{reason}:")
            print(f"   Ocorrências: {reason_count}")
            print(f"   PnL total: ${reason_pnl:+.2f}")
            print(f"   PnL médio: ${reason_avg:+.2f}")
    
    # Análise de ciclos
    if len(cycles_df) > 0:
        print("\n" + "="*70)
        print("♻️  ANÁLISE DE CICLOS:")
        print("="*70)
        
        cycle_pnl_total = cycles_df['total_pnl'].sum()
        cycle_pnl_avg = cycles_df['total_pnl'].mean()
        cycle_duration_avg = cycles_df['duration_minutes'].mean()
        
        cycle_wins = (cycles_df['total_pnl'] > 0).sum()
        cycle_total = len(cycles_df)
        cycle_wr = (cycle_wins / cycle_total * 100)
        
        print(f"\n   Total de ciclos: {cycle_total}")
        print(f"   PnL total: ${cycle_pnl_total:+.2f}")
        print(f"   PnL médio/ciclo: ${cycle_pnl_avg:+.2f}")
        print(f"   Duração média: {cycle_duration_avg:.1f} min")
        print(f"   Ciclos lucrativos: {cycle_wins} ({cycle_wr:.1f}%)")
        
        best_cycle = cycles_df.nlargest(1, 'total_pnl').iloc[0]
        worst_cycle = cycles_df.nsmallest(1, 'total_pnl').iloc[0]
        
        print(f"\n   Melhor ciclo: ${best_cycle['total_pnl']:+.2f} ({best_cycle['close_reason']})")
        print(f"   Pior ciclo: ${worst_cycle['total_pnl']:+.2f} ({worst_cycle['close_reason']})")
    
    # Current parameters
    print("\n" + "="*70)
    print("⚙️  PARÂMETROS USADOS:")
    print("="*70)
    
    if len(trades_df) > 0:
        latest_trade = trades_df.iloc[-1]
        print(f"\n   Stop Loss: ${latest_trade['config_sl']:.0f}")
        print(f"   Take Profit: ${latest_trade['config_tp']:.0f}")
        print(f"   Time Limit: {latest_trade['config_time_limit']:.0f} min")
    
    # Recommendations
    print("\n" + "="*70)
    print("💡 RECOMENDAÇÕES:")
    print("="*70)
    
    if len(cycles_df) >= 10:
        print("\n✅ Você tem dados suficientes para otimização!")
        print("   Execute: python3 backtest_optimizer.py")
        print("   Para encontrar os melhores parâmetros SL/TP/Time")
    else:
        needed = 10 - len(cycles_df)
        print(f"\n⏳ Colete mais dados antes de otimizar")
        print(f"   Ciclos atuais: {len(cycles_df)}")
        print(f"   Recomendado: 10+ ciclos")
        print(f"   Faltam: {needed} ciclos")
        print("\n   Deixe o bot rodar por mais tempo e depois execute:")
        print("   python3 backtest_optimizer.py")
    
    print("\n" + "="*70)
    print()
    
    conn.close()


if __name__ == "__main__":
    analyze_trades()
