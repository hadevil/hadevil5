"""
Monitor Avançado de Performance para Market Maker Bot Otimizado
Interface em tempo real para acompanhar métricas de airdrop farming
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

class OptimizedBotMonitor:
    def __init__(self, performance_file: str = "optimized_performance.json"):
        self.performance_file = performance_file
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
        # Cores para diferentes estados
        self.colors = {
            'success': 'green',
            'warning': 'yellow',
            'error': 'red',
            'info': 'blue',
            'highlight': 'cyan'
        }
        
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
            return str(uptime).split('.')[0]
        except:
            return "N/A"
    
    def create_header_panel(self, data: Dict) -> Panel:
        """Cria painel de cabeçalho"""
        stats = data.get('stats', {})
        uptime = self.get_uptime(stats.get('start_time', ''))
        
        header_text = f"""
🤖 MARKET MAKER BOT OTIMIZADO - AIRDROP FARMING
📅 Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⏱️  Tempo de execução: {uptime}
🎯 Modo: {data.get('performance_mode', 'N/A').upper()}
        """
        
        return Panel(header_text, title="Status do Bot", border_style="blue")
    
    def create_airdrop_panel(self, data: Dict) -> Panel:
        """Cria painel de progresso do airdrop"""
        airdrop_progress = data.get('airdrop_progress', {})
        
        # Progresso diário
        daily = airdrop_progress.get('daily', {})
        daily_volume_ratio = daily.get('volume_ratio', 0)
        daily_trades_ratio = daily.get('trades_ratio', 0)
        
        # Score geral
        overall_score = airdrop_progress.get('score', 0)
        
        # Determinar cor baseada no progresso
        if overall_score >= 0.8:
            color = self.colors['success']
        elif overall_score >= 0.6:
            color = self.colors['warning']
        else:
            color = self.colors['error']
        
        airdrop_text = f"""
📊 VOLUME DIÁRIO: {self.format_currency(daily.get('volume', 0))} / {self.format_currency(daily.get('target_volume', 0))}
📈 Progresso: {self.format_percentage(daily_volume_ratio)}

🔄 TRADES DIÁRIOS: {daily.get('trades', 0)} / {daily.get('target_trades', 0)}
📈 Progresso: {self.format_percentage(daily_trades_ratio)}

🎯 SCORE GERAL: {self.format_percentage(overall_score)}
        """
        
        return Panel(airdrop_text, title="Progresso Airdrop", border_style=color)
    
    def create_performance_panel(self, data: Dict) -> Panel:
        """Cria painel de performance"""
        stats = data.get('stats', {})
        loss_metrics = data.get('loss_metrics', {})
        risk_metrics = data.get('risk_metrics', {})
        
        # Determinar cor baseada no PnL
        total_pnl = stats.get('total_pnl', 0)
        if total_pnl > 0:
            pnl_color = self.colors['success']
        elif total_pnl > -100:
            pnl_color = self.colors['warning']
        else:
            pnl_color = self.colors['error']
        
        performance_text = f"""
💰 CAPITAL: {self.format_currency(loss_metrics.get('capital_efficiency', 1) * 5000)}
📊 PnL Total: {self.format_currency(total_pnl)}
📈 PnL Diário: {self.format_currency(risk_metrics.get('daily_pnl', 0))}
📉 Drawdown: {self.format_percentage(loss_metrics.get('current_drawdown', 0))}
⚡ Eficiência: {self.format_percentage(loss_metrics.get('capital_efficiency', 1))}
        """
        
        return Panel(performance_text, title="Performance", border_style=pnl_color)
    
    def create_trading_panel(self, data: Dict) -> Panel:
        """Cria painel de trading"""
        stats = data.get('stats', {})
        
        # Calcular taxas
        orders_placed = stats.get('orders_placed', 0)
        orders_filled = stats.get('orders_filled', 0)
        orders_cancelled = stats.get('orders_cancelled', 0)
        
        fill_rate = (orders_filled / orders_placed * 100) if orders_placed > 0 else 0
        
        trading_text = f"""
📈 Ordens Colocadas: {orders_placed}
✅ Ordens Preenchidas: {orders_filled}
❌ Ordens Canceladas: {orders_cancelled}
📊 Taxa de Preenchimento: {fill_rate:.1f}%
💰 Volume Total: {self.format_currency(stats.get('total_volume', 0))}
        """
        
        return Panel(trading_text, title="Atividade de Trading", border_style="cyan")
    
    def create_risk_panel(self, data: Dict) -> Panel:
        """Cria painel de risco"""
        loss_metrics = data.get('loss_metrics', {})
        risk_metrics = data.get('risk_metrics', {})
        
        # Determinar cor baseada no risco
        drawdown = loss_metrics.get('current_drawdown', 0)
        if drawdown < 0.01:
            risk_color = self.colors['success']
        elif drawdown < 0.03:
            risk_color = self.colors['warning']
        else:
            risk_color = self.colors['error']
        
        risk_text = f"""
⚠️  Drawdown Atual: {self.format_percentage(drawdown)}
📉 Drawdown Máximo: {self.format_percentage(loss_metrics.get('max_drawdown', 0))}
🔄 Perdas Consecutivas: {loss_metrics.get('consecutive_losses', 0)}
🛡️  Fator de Recuperação: {loss_metrics.get('recovery_factor', 1):.2f}
        """
        
        return Panel(risk_text, title="Gestão de Risco", border_style=risk_color)
    
    def create_progress_bars(self, data: Dict) -> List[Progress]:
        """Cria barras de progresso"""
        airdrop_progress = data.get('airdrop_progress', {})
        daily = airdrop_progress.get('daily', {})
        
        # Barra de volume
        volume_progress = Progress(
            TextColumn("[bold blue]Volume Diário"),
            BarColumn(bar_width=20),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        volume_task = volume_progress.add_task("Volume", total=100)
        volume_progress.update(volume_task, completed=daily.get('volume_ratio', 0) * 100)
        
        # Barra de trades
        trades_progress = Progress(
            TextColumn("[bold green]Trades Diários"),
            BarColumn(bar_width=20),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        trades_task = trades_progress.add_task("Trades", total=100)
        trades_progress.update(trades_task, completed=daily.get('trades_ratio', 0) * 100)
        
        return [volume_progress, trades_progress]
    
    def create_layout(self, data: Dict) -> Layout:
        """Cria layout da interface"""
        layout = Layout()
        
        # Dividir em seções
        layout.split_column(
            Layout(self.create_header_panel(data), size=6),
            Layout(name="main"),
            Layout(name="progress", size=6)
        )
        
        # Dividir seção principal
        layout["main"].split_row(
            Layout(self.create_airdrop_panel(data), name="left"),
            Layout(name="right")
        )
        
        # Dividir seção direita
        layout["right"].split_column(
            Layout(self.create_performance_panel(data)),
            Layout(self.create_trading_panel(data)),
            Layout(self.create_risk_panel(data))
        )
        
        # Adicionar barras de progresso
        progress_bars = self.create_progress_bars(data)
        progress_text = "\n".join([str(bar) for bar in progress_bars])
        layout["progress"].update(Panel(progress_text, title="Progresso Diário", border_style="magenta"))
        
        return layout
    
    def run_monitor(self, refresh_interval: int = 2):
        """Executa monitor com refresh automático"""
        try:
            with Live(self.create_layout({}), refresh_per_second=0.5) as live:
                while True:
                    data = self.load_performance_data()
                    layout = self.create_layout(data)
                    live.update(layout)
                    time.sleep(refresh_interval)
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Monitor finalizado pelo usuário[/bold red]")
        except Exception as e:
            self.console.print(f"\n[bold red]Erro no monitor: {e}[/bold red]")

def main():
    """Função principal do monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Otimizado do Market Maker Bot")
    parser.add_argument("--file", "-f", default="optimized_performance.json",
                       help="Arquivo de dados de performance")
    parser.add_argument("--interval", "-i", type=int, default=2,
                       help="Intervalo de refresh em segundos")
    
    args = parser.parse_args()
    
    # Verificar se rich está instalado
    try:
        from rich.console import Console
    except ImportError:
        print("❌ Rich não está instalado. Execute: pip install rich")
        sys.exit(1)
    
    monitor = OptimizedBotMonitor(args.file)
    monitor.run_monitor(args.interval)

if __name__ == "__main__":
    main()