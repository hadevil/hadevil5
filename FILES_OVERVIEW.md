# 📁 Visão Geral dos Arquivos

Guia completo de todos os arquivos do projeto e suas funções.

## 🎯 Arquivos Principais

### `paradex_market_maker.py` ⭐
**Arquivo principal do bot de market making**
- Implementa toda a lógica de trading
- Gerencia conexão com API da Paradex
- Coloca e cancela ordens automaticamente
- Gerencia inventário e risco
- Ajusta spreads dinamicamente
- ~600 linhas de código otimizado

**Como usar:**
```powershell
python paradex_market_maker.py
```

### `config.json`
**Arquivo de configuração principal**
- API keys da Paradex
- Parâmetros de trading (spread, levels, sizes)
- Configurações de risco
- Market a ser traded (SOL-USD-PERP)

**Nota:** Você deve criar este arquivo! Use `config_conservative.json` como template.

## 📊 Configurações

### `config_conservative.json`
- Spread: 0.2%
- Risk: Baixo
- Retorno esperado: $100-160/dia
- **Para quem**: Iniciantes, primeira vez

### `config_balanced.json`
- Spread: 0.15%
- Risk: Médio
- Retorno esperado: $150-225/dia
- **Para quem**: Após testar conservative

### `config_aggressive.json`
- Spread: 0.1%
- Risk: Alto
- Retorno esperado: $150-250/dia
- **Para quem**: Experiência + tolerância a risco

## 🛠️ Utilitários

### `utils.py`
**Funções auxiliares**
- Cálculos de PnL, ROI, Sharpe Ratio
- Performance tracking
- Validação de configuração
- Formatação de números
- ~400 linhas

### `monitor.py`
**Dashboard de monitoramento**
- Exibe estatísticas em tempo real
- Parsing de logs
- Métricas de performance
- Atualiza a cada 5 segundos

**Como usar:**
```powershell
python monitor.py
```

### `test_connection.py`
**Testa conexão com Paradex**
- Verifica API keys
- Testa endpoints
- Valida configuração
- Mostra balances e posições

**Como usar:**
```powershell
python test_connection.py
```

### `backtest.py`
**Simulador de trading**
- Simula 24h de market making
- Testa diferentes configurações
- Gera métricas de performance
- Não usa capital real

**Como usar:**
```powershell
python backtest.py
```

### `optimize_config.py`
**Gerador de configurações otimizadas**
- Gera 3 perfis (conservative, balanced, aggressive)
- Calcula tamanhos ótimos
- Estima performance
- Análise detalhada

**Como usar:**
```powershell
python optimize_config.py
```

## 🚀 Scripts PowerShell

### `install.ps1`
**Instalador automático**
- Verifica Python
- Cria ambiente virtual
- Instala dependências
- Gera configurações
- Setup completo em um comando

**Como usar:**
```powershell
.\install.ps1
```

### `start_bot.ps1`
**Inicia o bot facilmente**
- Ativa ambiente virtual
- Verifica configuração
- Inicia o market maker
- Tratamento de erros

**Como usar:**
```powershell
.\start_bot.ps1
```

### `start_monitor.ps1`
**Inicia o monitor**
- Ativa ambiente virtual
- Inicia dashboard
- Fácil de usar

**Como usar:**
```powershell
.\start_monitor.ps1
```

### `run_backtest.ps1`
**Executa backtesting**
- Ativa ambiente virtual
- Roda simulações
- Gera relatórios

**Como usar:**
```powershell
.\run_backtest.ps1
```

## 📚 Documentação

### `README.md` ⭐
**Documentação principal**
- Instalação completa
- Como usar
- Troubleshooting
- Otimização para airdrop
- Performance esperada
- ~400 linhas

### `QUICK_START.md`
**Guia rápido de 5 minutos**
- Setup em passos simples
- Comandos essenciais
- Configuração mínima
- Para começar rapidamente

### `TRADING_STRATEGY.md` ⭐
**Detalhes técnicos da estratégia**
- Como funciona market making
- Algoritmos implementados
- Inventory skewing
- Dynamic spreads
- Cenários e respostas
- ~500 linhas de explicação técnica

### `CHECKLIST.md`
**Checklist antes de começar**
- Verificação passo a passo
- Testes a realizar
- Red flags
- Final check
- ~200 itens

### `FILES_OVERVIEW.md` (este arquivo)
**Visão geral de todos os arquivos**
- O que cada arquivo faz
- Como usar cada um
- Ordem de uso

## 🔧 Configuração

### `.env.example`
**Template para variáveis de ambiente**
- Copie para `.env`
- Adicione API keys
- Configurações sensíveis

### `.gitignore`
**Arquivos ignorados pelo git**
- Protege API keys
- Ignora logs
- Ignora arquivos temporários

### `requirements.txt`
**Dependências Python**
- aiohttp (HTTP async)
- numpy (cálculos)
- pandas (análise)
- websockets (streaming)

### `setup.py`
**Instalação como pacote Python**
- Permite `pip install .`
- Metadata do projeto
- Dependências

## 📝 Ordem de Uso Recomendada

### 1️⃣ Primeira Vez - Setup
```
1. README.md (ler visão geral)
2. install.ps1 (executar instalação)
3. optimize_config.py (gerar configurações)
4. Editar config.json (adicionar API keys)
5. test_connection.py (verificar setup)
```

### 2️⃣ Antes de Tradear - Aprender
```
6. TRADING_STRATEGY.md (entender estratégia)
7. backtest.py (simular trading)
8. CHECKLIST.md (verificar tudo)
```

### 3️⃣ Começar - Testnet
```
9. start_bot.ps1 (iniciar em testnet)
10. start_monitor.ps1 (monitorar)
11. Observar por 24h
```

### 4️⃣ Produção - Mainnet
```
12. Editar config.json (testnet=false)
13. test_connection.py (verificar mainnet)
14. start_bot.ps1 (iniciar em produção)
15. Monitorar frequentemente
```

## 🎯 Arquivos por Caso de Uso

### "Quero instalar tudo rapidamente"
```
1. install.ps1
2. Editar config.json
3. start_bot.ps1
```

### "Quero entender a estratégia"
```
1. TRADING_STRATEGY.md
2. paradex_market_maker.py (ler código)
3. backtest.py (rodar simulações)
```

### "Quero otimizar parâmetros"
```
1. optimize_config.py (gerar perfis)
2. backtest.py (testar cada perfil)
3. Ajustar config.json
```

### "Tenho um problema"
```
1. CHECKLIST.md (verificar setup)
2. test_connection.py (diagnosticar)
3. README.md seção Troubleshooting
```

### "Quero monitorar performance"
```
1. monitor.py (dashboard real-time)
2. market_maker.log (logs detalhados)
3. utils.py (análise de performance)
```

## 📊 Estrutura do Projeto

```
hadevil5/
├── 🎯 Core
│   ├── paradex_market_maker.py    # Bot principal
│   ├── config.json                # Configuração (você cria)
│   └── utils.py                   # Utilidades
│
├── 🛠️ Tools
│   ├── monitor.py                 # Monitoramento
│   ├── test_connection.py         # Teste de conexão
│   ├── backtest.py                # Backtesting
│   └── optimize_config.py         # Otimização
│
├── 📊 Configs
│   ├── config_conservative.json   # Perfil conservador
│   ├── config_balanced.json       # Perfil balanceado
│   └── config_aggressive.json     # Perfil agressivo
│
├── 🚀 Scripts
│   ├── install.ps1                # Instalador
│   ├── start_bot.ps1              # Iniciar bot
│   ├── start_monitor.ps1          # Iniciar monitor
│   └── run_backtest.ps1           # Rodar backtest
│
├── 📚 Docs
│   ├── README.md                  # Documentação principal
│   ├── QUICK_START.md             # Início rápido
│   ├── TRADING_STRATEGY.md        # Estratégia detalhada
│   ├── CHECKLIST.md               # Checklist
│   └── FILES_OVERVIEW.md          # Este arquivo
│
└── ⚙️ Setup
    ├── requirements.txt           # Dependências
    ├── setup.py                   # Setup do pacote
    ├── .env.example               # Template env
    └── .gitignore                 # Git ignore
```

## 🔑 Arquivos Sensíveis (NÃO compartilhar)

⚠️ **NUNCA commitear ou compartilhar:**
- `config.json` (contém API keys)
- `.env` (contém secrets)
- `market_maker.log` (pode conter informações sensíveis)
- `*.backup` (backups de config)

✅ **Seguro para compartilhar:**
- Todos os `.py`
- Todos os `.md`
- Todos os `.ps1`
- `config_*.json` (templates sem API keys)
- `.env.example` (template)

## 💡 Dicas

### Para Iniciantes
1. Comece lendo: `README.md` → `QUICK_START.md`
2. Execute: `install.ps1`
3. Teste: `test_connection.py`
4. Simule: `backtest.py`
5. Rode em testnet primeiro!

### Para Avançados
1. Leia: `TRADING_STRATEGY.md`
2. Customize: `paradex_market_maker.py`
3. Otimize: `optimize_config.py`
4. Analise: `utils.py` → `PerformanceTracker`
5. Ajuste spread dinamicamente

### Para Debugging
1. Ative logging DEBUG em `paradex_market_maker.py` linha 24
2. Use `test_connection.py` para verificar conectividade
3. Cheque `market_maker.log` para erros
4. Use `CHECKLIST.md` para verificação sistemática

## 🆘 Suporte

Se algo não estiver claro:

1. **Leia a documentação** na ordem:
   - QUICK_START.md (5 min)
   - README.md (20 min)
   - TRADING_STRATEGY.md (30 min)

2. **Execute os testes**:
   - `test_connection.py`
   - `backtest.py`

3. **Verifique o checklist**:
   - CHECKLIST.md

4. **Recursos externos**:
   - [Docs Paradex](https://docs.paradex.trade/)
   - [Discord Paradex](https://discord.gg/paradex)

## ✅ Resumo

Este projeto contém:
- ✅ 1 bot de market making completo
- ✅ 3 configurações otimizadas
- ✅ 5 ferramentas de análise
- ✅ 4 scripts de automação
- ✅ 5 documentos educacionais
- ✅ Tudo para começar market making profissionalmente!

**Total: ~20 arquivos, ~3000 linhas de código, documentação completa**

---

**Pronto para começar? Execute:**
```powershell
.\install.ps1
```

**Boa sorte! 🚀**
