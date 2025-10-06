# 🤖 Market Maker Bot para Paradex - Airdrop Farming

Bot de market making otimizado para SOL na Paradex, focado em farming de airdrop com capital limitado (5k USD).

## ✨ Características Principais

- **Market Making Adaptativo**: Spread dinâmico baseado em volatilidade, volume e tendência
- **Gestão de Risco Avançada**: Circuit breaker, drawdown limits, position sizing inteligente
- **Otimizado para Airdrop**: Foco em volume e frequência de trades para qualificação
- **Capital Limitado**: Estratégias específicas para operar com 5k USD
- **Windows/PowerShell**: Scripts de configuração e execução para Windows
- **Monitoramento Completo**: Logs detalhados e métricas de performance

## 🚀 Instalação Rápida

### 1. Pré-requisitos
- Windows 10/11
- Python 3.8+ ([Download](https://www.python.org/downloads/))
- PowerShell 5.1+

### 2. Configuração Automática
```powershell
# Execute no PowerShell como Administrador
.\setup_windows.ps1
```

### 3. Configurar API Keys
1. Edite o arquivo `.env`
2. Substitua as chaves de exemplo pelas suas chaves reais da Paradex:
```env
PARADEX_API_KEY=sua_api_key_aqui
PARADEX_SECRET_KEY=sua_secret_key_aqui
PARADEX_PASSPHRASE=sua_passphrase_aqui
```

### 4. Executar o Bot
```powershell
.\run_bot.ps1
```

## 📊 Estratégia de Market Making

### Spread Adaptativo
- **Base**: 0.1% de spread
- **Volatilidade**: Aumenta spread em mercados voláteis
- **Volume**: Reduz spread quando volume aumenta
- **Tendência**: Ajusta spread baseado na direção do mercado
- **Inventário**: Compensa desbalanceamento de posições

### Gestão de Risco
- **Position Sizing**: Máximo 2% do capital por trade
- **Drawdown Limit**: Para trading em 3% de drawdown
- **Circuit Breaker**: Pausa após 5 perdas consecutivas
- **Daily Loss Limit**: Máximo 5% de perda diária

### Otimizações para Airdrop
- **Volume Target**: 20% do capital em volume diário
- **Trade Frequency**: Mínimo 50 trades por dia
- **Active Days**: Foco em consistência diária
- **Spread Efficiency**: Balance entre lucro e volume

## 🔧 Configurações Avançadas

### Ajustar Parâmetros
Edite `config.py` para personalizar:

```python
# Configurações de Trading
TRADING_CONFIG = {
    'total_capital': 5000,  # Seu capital total
    'risk_per_trade': 0.02,  # 2% por trade
    'max_daily_loss': 0.05,  # 5% perda máxima diária
}

# Configurações de Market Making
MARKET_MAKING_CONFIG = {
    'spread_percentage': 0.001,  # 0.1% spread base
    'max_orders_per_side': 3,  # Ordens por lado
    'order_refresh_time': 30,  # Refresh a cada 30s
}
```

### Monitoramento
- **Logs**: `market_maker.log`
- **Performance**: `performance.json`
- **Métricas**: Console em tempo real

## 📈 Métricas de Performance

O bot monitora automaticamente:

- **PnL Total e Diário**
- **Drawdown Atual e Máximo**
- **Volume de Trading**
- **Taxa de Sucesso das Ordens**
- **Progresso do Airdrop**
- **Alertas de Risco**

## ⚠️ Avisos Importantes

### Gestão de Capital
- Este bot é otimizado para capital limitado
- Nunca arrisque mais do que pode perder
- Monitore regularmente o desempenho
- Ajuste parâmetros conforme necessário

### Riscos de Market Making
- **Slippage**: Preços podem se mover contra você
- **Volatilidade**: Mercados voláteis aumentam riscos
- **Liquidez**: Baixa liquidez pode causar perdas
- **Tecnologia**: Falhas técnicas podem causar perdas

### Compliance
- Verifique regulamentações locais
- Mantenha registros de todas as transações
- Considere implicações fiscais
- Use apenas capital que pode perder

## 🛠️ Solução de Problemas

### Erro de Conexão
```powershell
# Verificar conectividade
ping api.paradex.trade
```

### Erro de API
- Verifique se as chaves estão corretas
- Confirme se a conta tem permissões de trading
- Verifique limites de rate da API

### Erro de Dependências
```powershell
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Bot Não Inicia
1. Verifique se o ambiente virtual está ativo
2. Confirme se o arquivo `.env` está configurado
3. Verifique os logs em `market_maker.log`

## 📚 Estrutura do Projeto

```
paradex-market-maker/
├── market_maker_bot.py      # Bot principal
├── paradex_client.py        # Cliente da API
├── market_making_strategy.py # Estratégia adaptativa
├── risk_manager.py          # Gestão de risco
├── config.py               # Configurações
├── requirements.txt        # Dependências
├── setup_windows.ps1      # Script de configuração
├── run_bot.ps1           # Script de execução
├── .env.example          # Exemplo de configuração
└── README.md             # Este arquivo
```

## 🤝 Suporte

Para dúvidas ou problemas:

1. Verifique os logs em `market_maker.log`
2. Consulte a documentação da Paradex
3. Revise as configurações em `config.py`
4. Teste com capital pequeno primeiro

## ⚖️ Disclaimer

Este software é fornecido "como está" para fins educacionais. O uso é por sua conta e risco. Os desenvolvedores não se responsabilizam por perdas financeiras. Sempre faça sua própria pesquisa e considere consultar um profissional financeiro.

---

**🎯 Boa sorte com seu farming de airdrop na Paradex!**