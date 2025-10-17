# Long&Short Bot

Sistema automatizado de trading Long&Short com reabertura automática de posições.

## Funcionalidades

- **Seleção Automática de Ativos**: A cada 2 horas, seleciona automaticamente os melhores ativos para long e short
- **Ordens a Mercado**: Executa ordens de entrada e saída a mercado
- **Controle de Risco**: Configuração de Take Profit (TP) e Stop Loss (SL) baseados em percentual
- **Duração Máxima**: Fecha posições automaticamente após X horas se não atingir TP/SL
- **Reabertura Automática**: Reabre posições 8 minutos após fechamento (exceto por tempo máximo)
- **Dashboard Web**: Interface para monitoramento e configuração em tempo real
- **Logging Completo**: Sistema de logs para auditoria e debugging

## Instalação

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Configurar credenciais**:
```bash
cp .env.example .env
# Editar .env com suas credenciais da exchange
```

3. **Executar o sistema**:
```bash
# Modo completo (bot + dashboard)
python main.py --mode both

# Apenas o bot
python main.py --mode bot

# Apenas o dashboard
python main.py --mode dashboard
```

## Configuração

### Variáveis de Ambiente (.env)
```env
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here
```

### Configurações do Bot (config.py)
- `available_assets`: Lista de ativos para trading
- `selection_interval_hours`: Intervalo para seleção de ativos (padrão: 2h)
- `max_position_duration_hours`: Duração máxima das posições (padrão: 24h)
- `reopen_delay_minutes`: Delay para reabertura (padrão: 8min)
- `default_tp_percentage`: Take Profit padrão (padrão: 2%)
- `default_sl_percentage`: Stop Loss padrão (padrão: 1%)

## Como Funciona

### 1. Seleção de Ativos
- A cada 2 horas, o sistema analisa todos os ativos disponíveis
- Calcula score baseado em volume, volatilidade e momentum
- Seleciona o melhor ativo para long e short

### 2. Abertura de Posições
- Executa ordens a mercado para long e short simultaneamente
- Coloca ordens de TP e SL automaticamente
- Monitora posições continuamente

### 3. Fechamento de Posições
- **Por TP/SL**: Fecha automaticamente quando atinge take profit ou stop loss
- **Por Tempo**: Fecha após duração máxima configurada
- **Manual**: Pode ser fechado via dashboard

### 4. Reabertura Automática
- Após fechamento por TP/SL, agenda reabertura em 8 minutos
- Não reabre se fechado por tempo máximo
- Mantém os mesmos ativos selecionados

## Dashboard Web

Acesse `http://localhost:8050` para:
- Monitorar status do bot em tempo real
- Ver posições atuais e estatísticas
- Ajustar configurações (TP, SL, duração)
- Visualizar gráficos de PnL
- Acompanhar logs do sistema

## Estrutura do Projeto

```
├── main.py                 # Arquivo principal
├── long_short_bot.py      # Bot principal
├── exchange_manager.py    # Gerenciador de exchange
├── asset_selector.py      # Seletor de ativos
├── position_manager.py    # Gerenciador de posições
├── dashboard.py           # Interface web
├── config.py             # Configurações
├── requirements.txt      # Dependências
└── .env.example         # Exemplo de configuração
```

## Monitoramento

### Logs
- Logs salvos em `long_short_bot.log`
- Níveis: DEBUG, INFO, WARNING, ERROR
- Incluem todas as operações e erros

### Estatísticas
- Total de trades executados
- Trades lucrativos vs perdedores
- PnL total e por trade
- Taxa de acerto
- Tempo de execução

## Segurança

- **Sandbox Mode**: Por padrão, usa modo sandbox da exchange
- **Rate Limiting**: Respeita limites da API
- **Error Handling**: Tratamento robusto de erros
- **Position Sizing**: Controle de tamanho das posições

## Exemplo de Uso

```python
from long_short_bot import LongShortBot

# Criar instância do bot
bot = LongShortBot()

# Atualizar configurações
bot.update_config(
    tp_percentage=2.5,      # 2.5% de TP
    sl_percentage=1.5,      # 1.5% de SL
    max_duration_hours=12   # 12 horas máximo
)

# Iniciar bot
await bot.start()
```

## Troubleshooting

### Erro de Conexão com Exchange
- Verificar credenciais no arquivo .env
- Confirmar se a exchange suporta as operações necessárias
- Verificar se está em modo sandbox ou produção

### Bot Não Seleciona Ativos
- Verificar se a lista de ativos está correta
- Confirmar conectividade com a exchange
- Verificar logs para erros específicos

### Dashboard Não Carrega
- Verificar se a porta 8050 está disponível
- Confirmar se todas as dependências foram instaladas
- Verificar logs do dashboard

## Suporte

Para dúvidas ou problemas:
1. Verificar logs em `long_short_bot.log`
2. Consultar documentação da exchange utilizada
3. Verificar configurações no arquivo `config.py`