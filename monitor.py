"""
Monitor de Performance para Market Maker Bot
Interface para acompanhar métricas em tempo real
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

class BotMonitor:
    def __init__(self, performance_file: str = "performance.json"):
        self.performance_file = performance_file
        self.logger = logging.getLogger(__name__)
        
    def load_performance_data(self) -> Dict[str, Any]:
        """Carrega dados de performance do arquivo"""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados de performance: {e}")
            return {}
    
    def format_currency(self, value: float) -> str:
        """Formata valor como moeda"""
        return f"${value:,.2f}"
    
    def format_percentage(self, value: float) -> str:
        """Formata valor como porcentagem"""
        return f"{value:.2%}"
    
    def get_uptime(self, start_time: str) -> str:
        """Calcula tempo de execução"""
        try:
            start = datetime.fromisoformat(start_time)
            uptime = datetime.now() - start
            return str(uptime).split('.')[0]  # Remove microsegundos
        except:
            return "N/A"
    
    def print_dashboard(self):
        """Imprime dashboard de performance"""
        data = self.load_performance_data()
        
        if not data:
            print("❌ Nenhum dado de performance encontrado")
            return
        
        # Limpar tela (Windows)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("🤖 MARKET MAKER BOT - DASHBOARD DE PERFORMANCE")
        print("=" * 80)
        print(f"📅 Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Estatísticas básicas
        stats = data.get('stats', {})
        print("📊 ESTATÍSTICAS GERAIS")
        print("-" * 40)
        print(f"⏱️  Tempo de execução: {self.get_uptime(stats.get('start_time', ''))}")
        print(f"📈 Ordens colocadas: {stats.get('orders_placed', 0)}")
        print(f"✅ Ordens preenchidas: {stats.get('orders_filled', 0)}")
        print(f"❌ Ordens canceladas: {stats.get('orders_cancelled', 0)}")
        print(f"💰 Volume total: {self.format_currency(stats.get('total_volume', 0))}")
        print()
        
        # Métricas de risco
        risk_metrics = data.get('risk_metrics', {})
        print("⚠️  GESTÃO DE RISCO")
        print("-" * 40)
        print(f"💵 PnL Total: {self.format_currency(risk_metrics.get('current_pnl', 0))}")
        print(f"📊 PnL Diário: {self.format_currency(risk_metrics.get('daily_pnl', 0))}")
        print(f"📉 Drawdown Atual: {self.format_percentage(risk_metrics.get('current_drawdown', 0))}")
        print(f"📉 Drawdown Máximo: {self.format_percentage(risk_metrics.get('max_drawdown', 0))}")
        print(f"🎯 Taxa de Sucesso: {self.format_percentage(risk_metrics.get('win_rate', 0))}")
        print(f"📊 Trades Diários: {risk_metrics.get('trade_count', 0)}")
        print()
        
        # Progresso do Airdrop
        airdrop_progress = data.get('airdrop_progress', {})
        print("🎯 PROGRESSO AIRDROP")
        print("-" * 40)
        volume_progress = airdrop_progress.get('volume_progress', 0)
        trades_progress = airdrop_progress.get('trades_progress', 0)
        
        print(f"📊 Volume Diário: {self.format_currency(airdrop_progress.get('daily_volume', 0))}")
        print(f"🎯 Meta Volume: {self.format_currency(airdrop_progress.get('target_volume', 0))}")
        print(f"📈 Progresso Volume: {self.format_percentage(volume_progress)}")
        print()
        print(f"🔄 Trades Diários: {airdrop_progress.get('daily_trades', 0)}")
        print(f"🎯 Meta Trades: {airdrop_progress.get('target_trades', 0)}")
        print(f"📈 Progresso Trades: {self.format_percentage(trades_progress)}")
        print()
        
        # Status geral
        is_on_track = airdrop_progress.get('is_on_track', False)
        status_icon = "✅" if is_on_track else "⚠️"
        status_text = "NO TRACK" if is_on_track else "ATENÇÃO"
        print(f"{status_icon} Status Airdrop: {status_text}")
        print()
        
        # Métricas da estratégia
        strategy_metrics = data.get('strategy_metrics', {})
        if strategy_metrics:
            print("🧠 MÉTRICAS DA ESTRATÉGIA")
            print("-" * 40)
            print(f"📊 Retorno Total: {self.format_percentage(strategy_metrics.get('total_return', 0))}")
            print(f"📈 Volatilidade: {self.format_percentage(strategy_metrics.get('volatility', 0))}")
            print(f"⚡ Sharpe Ratio: {strategy_metrics.get('sharpe_ratio', 0):.2f}")
            print(f"📊 Pontos de Dados: {strategy_metrics.get('data_points', 0)}")
            print()
        
        print("=" * 80)
        print("💡 Pressione Ctrl+C para sair do monitor")
        print("=" * 80)
    
    def run_monitor(self, refresh_interval: int = 5):
        """Executa monitor com refresh automático"""
        try:
            while True:
                self.print_dashboard()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\n👋 Monitor finalizado")

def main():
    """Função principal do monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor de Performance do Market Maker Bot")
    parser.add_argument("--file", "-f", default="performance.json", 
                       help="Arquivo de dados de performance")
    parser.add_argument("--interval", "-i", type=int, default=5,
                       help="Intervalo de refresh em segundos")
    
    args = parser.parse_args()
    
    monitor = BotMonitor(args.file)
    monitor.run_monitor(args.interval)

if __name__ == "__main__":
    main()