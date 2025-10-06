# 🤖 Paradex Market Maker Bot - Otimizado para Airdrop Farming

**Bot de Market Making desenvolvido especialmente para farming de airdrops na Paradex com pouco capital (5k).**

## 🚀 Características Principais

- ✅ **Otimizado para pouco capital** - Configurado especificamente para contas com $5,000
- ✅ **Foco em SOL** - Estratégia centrada no par SOL-USD para maximizar volume
- ✅ **Market Making eficiente** - Coloca ordens buy/sell próximas do preço atual
- ✅ **Gerenciamento de risco avançado** - Controle de LTV, stop loss, take profit
- ✅ **Compatível com Windows/PowerShell** - Scripts otimizados para Windows
- ✅ **Farming de airdrop** - Estratégias para maximizar volume de trading

## 📋 Requisitos

- **Python 3.8+** (Recomendado: 3.10+)
- **Sistema operacional**: Windows 10/11
- **Conta Paradex** com API configurada
- **Capital inicial**: $5,000 (configurado para funcionar com esse valor)

## 🛠️ Instalação

### 1. Clonar e entrar no diretório
```bash
git clone <url-do-repositorio>
cd paradex-market-maker-bot
```

### 2. Executar instalação automática (Windows PowerShell)
```powershell
.\run_windows.ps1 -Install
```

### 3. Configurar sua conta
```powershell
.\run_windows.ps1 -Config
```

Edite o arquivo `config_windows.json` com suas credenciais:
```json
{
    "account": {
        "address": "0x...",
        "private_key": "0x...",
        "api_key": "...",
        "api_secret": "..."
    }
}
```

## ⚙️ Configuração

### Configuração para Pouco Capital ($5k)

O arquivo `config_windows.json` já vem otimizado:

```json
{
    "trading": {
        "order_value_usd": {
            "min": 8,
            "max": 25
        },
        "max_leverage": 1.2,
        "max_position_ltv": 75,
        "max_daily_volume_usd": 800
    },
    "pairs": {
        "primary_pairs": ["SOL-USD"],
        "focus_on_sol": true
    }
}
```

### Parâmetros Importantes:

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `order_value_usd` | $8-$25 | Tamanho das ordens individuais |
| `max_leverage` | 1.2x | Alavancagem máxima permitida |
| `max_position_ltv` | 75% | LTV máximo antes de fechar posições |
| `max_daily_volume_usd` | $800 | Volume máximo por dia |
| `primary_pairs` | SOL-USD | Par principal para trading |

## 🚀 Como Usar

### Iniciar o Bot
```powershell
.\run_windows.ps1 -Run
```

### Menu Interativo
O bot oferece um menu interativo com as seguintes opções:

1. **⚙️ Configurar conta** - Inserir credenciais da Paradex
2. **🚀 Iniciar trading** - Começar operações automáticas
3. **📊 Ver status** - Ver estatísticas atuais
4. **⚠️ Parar trading** - Parar operações
5. **❌ Sair** - Encerrar o programa

## 🎯 Estratégia de Trading

### Market Making para Airdrop

O bot utiliza estratégia de **Market Making**:

1. **Coloca ordens buy e sell** próximas do preço atual
2. **Mantém spread pequeno** (0.1-0.2%) para alta probabilidade de execução
3. **Gerencia posições ativamente** com stop loss e take profit
4. **Foca em volume constante** para farming de airdrop

### Otimizações para Pouco Capital

- **Ordens pequenas**: $8-$25 para minimizar exposição
- **Baixa alavancagem**: 1.2x máximo
- **Controle de risco**: LTV máximo de 75%
- **Volume conservador**: $800/dia máximo

## 📊 Gerenciamento de Risco

### Recursos de Segurança

- **Stop Loss**: Fecha posições com perda de 3%
- **Take Profit**: Realiza lucro de 1.5%
- **Controle de LTV**: Monitora alavancagem em tempo real
- **Limite diário**: Não excede volume máximo por dia
- **Monitoramento contínuo**: Verifica posições a cada ciclo

### Indicadores Monitorados

- 📈 **Exposição total** em USD
- 📊 **LTV atual** (Loan-to-Value)
- 💰 **PnL não realizado**
- 📉 **Drawdown máximo**
- 📊 **Volume diário**

## 🔧 Personalização

### Ajustar para Seu Capital

Se você tiver capital diferente de $5k, ajuste:

```json
{
    "trading": {
        "max_leverage": 1.5,  // Para $10k+
        "max_daily_volume_usd": 1500  // Proporcional ao capital
    }
}
```

### Focar em Outros Pares

Para operar outros pares além de SOL:

```json
{
    "pairs": {
        "primary_pairs": ["SOL-USD", "ETH-USD", "BTC-USD"]
    }
}
```

## 🚨 Avisos Importantes

### ⚠️ Riscos

- **Este é um bot experimental** - Use por sua conta e risco
- **Pode haver perdas financeiras** - Especialmente com alta volatilidade
- **Monitore constantemente** - Não deixe rodando sem supervisão
- **Comece com valores pequenos** - Teste antes de aumentar exposição

### 📝 Limitações

- **Não é à prova de falhas** - Exchanges podem mudar APIs
- **Dependente de conexão** - Precisa de internet estável
- **Não garante lucros** - Estratégia pode não ser rentável

## 🆘 Suporte e Problemas

### Problemas Comuns

1. **"Python não encontrado"**
   - Instale Python 3.8+ de python.org
   - Marque "Add Python to PATH" na instalação

2. **"Módulo não encontrado"**
   ```powershell
   .\run_windows.ps1 -Install
   ```

3. **Erro de configuração**
   - Verifique credenciais no `config_windows.json`
   - Certifique-se que a conta tem fundos suficientes

### 📞 Contato

Para dúvidas ou problemas:
- Verifique os logs em `logs/trading.log`
- Teste em modo manual antes de automatizar
- Comece com configurações conservadoras

## 📈 Estratégias Avançadas

### Para Maximizar Airdrop

1. **Mantenha alta frequência** de ordens (mas dentro dos limites)
2. **Diversifique horários** - Não opere apenas em horário comercial
3. **Mantenha consistência** - Volume constante é melhor que picos
4. **Monitore métricas** - Ajuste baseado no desempenho

### Otimizações para Mais Volume

```json
{
    "trading": {
        "delay_between_orders_min": {
            "min": 1,
            "max": 3
        },
        "order_duration_min": {
            "min": 8,
            "max": 15
        }
    }
}
```

**⚠️ Cuidado**: Mais volume = mais risco. Ajuste gradualmente.

## 🎉 Sucesso!

Com configuração adequada e monitoramento constante, este bot pode ajudar significativamente no farming de airdrops da Paradex. Lembre-se de que consistência e gerenciamento de risco são fundamentais para o sucesso a longo prazo.

**Boa sorte e trades seguros! 🚀**