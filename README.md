# 🤖 Market Maker Bot Otimizado para Paradex - Airdrop Farming

Bot de market making **altamente otimizado** para SOL na Paradex, focado em **minimizar perdas** e **maximizar pontos de airdrop** com capital limitado (5k USD).

## ✨ Características Principais

- **🎯 Airdrop Farming Agressivo**: Estratégias específicas para maximizar pontos de airdrop
- **🛡️ Proteção de Capital Avançada**: Sistema de minimização de perdas com controles dinâmicos
- **⚡ Arbitragem Interna**: Detecta e explora oportunidades de arbitragem na própria exchange
- **🔄 Mean Reversion Inteligente**: Aproveita movimentos de reversão à média
- **🛡️ Hedging Automático**: Protege posições automaticamente
- **📊 Modos Adaptativos**: Balanceado, Agressivo e Conservador baseado no desempenho
- **🎯 Otimização de Volume**: Foco em atingir metas diárias de volume e trades
- **💡 Controles Dinâmicos**: Ajusta parâmetros em tempo real baseado no progresso

## 🚀 Instalação Rápida

### 1. Pré-requisitos
- Windows 10/11
- Python 3.8+ ([Download](https://www.python.org/downloads/))
- PowerShell 5.1+

### 2. Configuração Automática Otimizada
```powershell
# Execute no PowerShell como Administrador
.\setup_optimized.ps1
```

### 3. Configurar API Keys
1. Edite o arquivo `.env`
2. Substitua as chaves de exemplo pelas suas chaves reais da Paradex:
```env
PARADEX_API_KEY=sua_api_key_aqui
PARADEX_SECRET_KEY=sua_secret_key_aqui
PARADEX_PASSPHRASE=sua_passphrase_aqui
```

### 4. Executar o Bot Otimizado
```powershell
.\run_optimized.ps1
```

## 📊 Estratégias Avançadas de Market Making

### 🎯 Airdrop Farming Otimizado
- **Volume Diário**: $1,500 por dia (30% do capital)
- **Trades Diários**: 100 trades por dia
- **Consistência**: Bônus de 20% por performance consistente
- **Spread Agressivo**: 0.03% base para maximizar execuções
- **Múltiplas Ordens**: Até 8 ordens por lado para mais execuções

### 🛡️ Proteção de Capital Avançada
- **Position Sizing Dinâmico**: 0.5% a 2% baseado no drawdown
- **Drawdown Limit**: Para trading em 3% de drawdown
- **Emergency Stop**: 2% de perda máxima por trade
- **Hedging Automático**: 80% do inventário é hedgeado
- **Recovery Mode**: Estratégia conservadora após perdas

### ⚡ Arbitragem e Mean Reversion
- **Arbitragem Interna**: Detecta spreads > 0.05%
- **Mean Reversion**: Aproveita desvios > 0.2% da média
- **Hedging Inteligente**: Protege posições automaticamente
- **Controles Dinâmicos**: Ajusta parâmetros em tempo real

### 📊 Modos de Performance Adaptativos
- **Agressivo**: Foco em airdrop farming (volume baixo)
- **Balanceado**: Equilibrio entre lucro e volume
- **Conservador**: Proteção de capital (drawdown alto)

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