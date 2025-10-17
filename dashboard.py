"""
Dashboard web para controle do Long&Short Bot
"""
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import threading
import json
from long_short_bot import LongShortBot
from config import config

# Inicializar app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Long&Short Bot Dashboard"

# Variável global para o bot
bot_instance = None
bot_thread = None

def create_dashboard_layout():
    """Cria layout do dashboard"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Long&Short Bot Dashboard", className="text-center mb-4"),
                html.Hr()
            ])
        ]),
        
        # Status do Bot
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Status do Bot"),
                    dbc.CardBody([
                        html.Div(id="bot-status"),
                        dbc.ButtonGroup([
                            dbc.Button("Iniciar", id="start-bot-btn", color="success", className="me-2"),
                            dbc.Button("Parar", id="stop-bot-btn", color="danger", className="me-2"),
                            dbc.Button("Atualizar", id="refresh-btn", color="info")
                        ])
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Configurações
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Configurações"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Take Profit (%)"),
                                dbc.Input(
                                    id="tp-input",
                                    type="number",
                                    value=config.default_tp_percentage,
                                    step=0.1,
                                    min=0.1,
                                    max=10.0
                                )
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Stop Loss (%)"),
                                dbc.Input(
                                    id="sl-input",
                                    type="number",
                                    value=config.default_sl_percentage,
                                    step=0.1,
                                    min=0.1,
                                    max=10.0
                                )
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Duração Máxima (h)"),
                                dbc.Input(
                                    id="duration-input",
                                    type="number",
                                    value=config.max_position_duration_hours,
                                    step=1,
                                    min=1,
                                    max=168
                                )
                            ], width=4)
                        ], className="mb-3"),
                        dbc.Button("Aplicar Configurações", id="apply-config-btn", color="primary")
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Posições Atuais
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Posições Atuais"),
                    dbc.CardBody([
                        html.Div(id="current-positions")
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Estatísticas"),
                    dbc.CardBody([
                        html.Div(id="bot-stats")
                    ])
                ])
            ], width=6)
        ], className="mb-4"),
        
        # Gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Histórico de PnL"),
                    dbc.CardBody([
                        dcc.Graph(id="pnl-chart")
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Logs
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Logs Recentes"),
                    dbc.CardBody([
                        html.Div(id="logs-display", style={"height": "300px", "overflow-y": "auto"})
                    ])
                ])
            ], width=12)
        ]),
        
        # Intervalo de atualização
        dcc.Interval(
            id='interval-component',
            interval=5000,  # Atualizar a cada 5 segundos
            n_intervals=0
        )
    ], fluid=True)

# Layout do app
app.layout = create_dashboard_layout()

def run_bot():
    """Executa o bot em thread separada"""
    global bot_instance
    try:
        bot_instance = LongShortBot()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot_instance.start())
    except Exception as e:
        print(f"Erro no bot: {e}")

@app.callback(
    [Output("bot-status", "children"),
     Output("current-positions", "children"),
     Output("bot-stats", "children"),
     Output("pnl-chart", "figure"),
     Output("logs-display", "children")],
    [Input("interval-component", "n_intervals"),
     Input("refresh-btn", "n_clicks")],
    prevent_initial_call=False
)
def update_dashboard(n_intervals, refresh_clicks):
    """Atualiza dashboard"""
    global bot_instance
    
    # Status do bot
    if bot_instance and bot_instance.running:
        status_color = "success"
        status_text = "Bot Rodando"
        status_icon = "🟢"
    else:
        status_color = "danger"
        status_text = "Bot Parado"
        status_icon = "🔴"
    
    status_card = dbc.Alert(
        f"{status_icon} {status_text}",
        color=status_color,
        className="mb-0"
    )
    
    # Posições atuais
    if bot_instance:
        status = bot_instance.get_status()
        positions_summary = status['positions']
        
        positions_content = [
            html.P(f"Posições Abertas: {positions_summary['open_count']}"),
            html.P(f"Posições Fechadas: {positions_summary['closed_count']}"),
            html.P(f"PnL Total: {positions_summary['total_pnl']:.2f} USDT"),
            html.P(f"Fila de Reabertura: {positions_summary['reopen_queue_size']}")
        ]
        
        if status['current_long_id']:
            positions_content.append(html.P(f"Long ID: {status['current_long_id']}"))
        if status['current_short_id']:
            positions_content.append(html.P(f"Short ID: {status['current_short_id']}"))
    else:
        positions_content = [html.P("Bot não inicializado")]
    
    # Estatísticas
    if bot_instance:
        stats = status['stats']
        stats_content = [
            html.P(f"Total de Trades: {stats['total_trades']}"),
            html.P(f"Trades Lucrativos: {stats['profitable_trades']}"),
            html.P(f"PnL Total: {stats['total_pnl']:.2f} USDT"),
        ]
        
        if stats['total_trades'] > 0:
            win_rate = (stats['profitable_trades'] / stats['total_trades']) * 100
            stats_content.append(html.P(f"Taxa de Acerto: {win_rate:.2f}%"))
        
        if stats['start_time']:
            runtime = datetime.now() - stats['start_time']
            stats_content.append(html.P(f"Tempo de Execução: {str(runtime).split('.')[0]}"))
    else:
        stats_content = [html.P("Nenhuma estatística disponível")]
    
    # Gráfico de PnL (simulado)
    pnl_data = []
    if bot_instance:
        positions = bot_instance.position_manager.positions
        closed_positions = [p for p in positions.values() if p.status.value == 'closed']
        
        cumulative_pnl = 0
        for pos in closed_positions:
            if pos.pnl:
                cumulative_pnl += pos.pnl
                pnl_data.append({
                    'timestamp': pos.exit_time,
                    'pnl': cumulative_pnl
                })
    
    if pnl_data:
        df = pd.DataFrame(pnl_data)
        fig = px.line(df, x='timestamp', y='pnl', title='PnL Acumulado')
        fig.update_layout(showlegend=False)
    else:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado de PnL disponível", 
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(title="PnL Acumulado")
    
    # Logs (simulado)
    logs_content = [
        html.P(f"[{datetime.now().strftime('%H:%M:%S')}] Dashboard atualizado"),
        html.P(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {status_text}"),
    ]
    
    return status_card, positions_content, stats_content, fig, logs_content

@app.callback(
    Output("start-bot-btn", "n_clicks"),
    [Input("start-bot-btn", "n_clicks")],
    prevent_initial_call=True
)
def start_bot(n_clicks):
    """Inicia o bot"""
    global bot_instance, bot_thread
    
    if n_clicks and not bot_instance:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
    
    return 0

@app.callback(
    Output("stop-bot-btn", "n_clicks"),
    [Input("stop-bot-btn", "n_clicks")],
    prevent_initial_call=True
)
def stop_bot(n_clicks):
    """Para o bot"""
    global bot_instance
    
    if n_clicks and bot_instance:
        bot_instance.stop()
    
    return 0

@app.callback(
    Output("apply-config-btn", "n_clicks"),
    [Input("apply-config-btn", "n_clicks")],
    [State("tp-input", "value"),
     State("sl-input", "value"),
     State("duration-input", "value")],
    prevent_initial_call=True
)
def apply_config(n_clicks, tp_value, sl_value, duration_value):
    """Aplica configurações"""
    global bot_instance
    
    if n_clicks and bot_instance:
        bot_instance.update_config(
            tp_percentage=tp_value,
            sl_percentage=sl_value,
            max_duration_hours=duration_value
        )
    
    return 0

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)