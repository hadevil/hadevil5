# ✅ Checklist - Antes de Começar

Use este checklist para garantir que tudo está configurado corretamente antes de começar a fazer market making na Paradex.

## 🔧 Setup Inicial

- [ ] Python 3.8+ instalado
  ```powershell
  python --version  # Deve mostrar 3.8 ou superior
  ```

- [ ] Repositório clonado
  ```powershell
  git clone https://github.com/hadevil/hadevil5.git
  cd hadevil5
  ```

- [ ] Instalação completa executada
  ```powershell
  .\install.ps1
  ```

- [ ] Ambiente virtual ativo
  ```powershell
  .\venv\Scripts\Activate.ps1
  # Deve ver (venv) no início do prompt
  ```

- [ ] Dependências instaladas
  ```powershell
  pip list  # Deve mostrar aiohttp, numpy, etc
  ```

## 🔑 Paradex Setup

- [ ] Conta criada na Paradex
  - Testnet: https://testnet.paradex.trade/
  - Mainnet: https://www.paradex.trade/

- [ ] Carteira conectada (StarkWare wallet)

- [ ] API Keys geradas
  - [ ] API Key copiada
  - [ ] API Secret copiada
  - [ ] Permissões corretas (Trading, não Withdrawal)

- [ ] Fundos depositados
  - [ ] Testnet: Faucet funds obtidos
  - [ ] Mainnet: $5k+ depositado

## ⚙️ Configuração

- [ ] Arquivo `config.json` existe
  ```powershell
  Test-Path config.json  # Deve retornar True
  ```

- [ ] API Keys adicionadas ao `config.json`
  - [ ] `api_key` preenchida (não deve conter "YOUR_")
  - [ ] `api_secret` preenchida (não deve conter "YOUR_")
  - [ ] `testnet` = true para testnet, false para mainnet

- [ ] Parâmetros ajustados
  - [ ] `market` = "SOL-USD-PERP" (ou outro mercado)
  - [ ] `order_size_usd` adequado ao capital
  - [ ] `max_position_usd` = 40-60% do capital total
  - [ ] `base_spread` = 0.0015-0.002 (0.15-0.2%)

- [ ] Perfil de risco escolhido
  - [ ] Conservative (menor risco, menor volume)
  - [ ] Balanced (balanceado)
  - [ ] Aggressive (maior risco, maior volume)

## ✓ Testes

- [ ] Teste de conexão passou
  ```powershell
  python test_connection.py
  # Deve mostrar "ALL TESTS PASSED!"
  ```

- [ ] Ticker recebido com sucesso
  - [ ] Preço atual exibido
  - [ ] Volume 24h exibido

- [ ] Orderbook recebido
  - [ ] Best bid exibido
  - [ ] Best ask exibido
  - [ ] Spread calculado

- [ ] Account conectado
  - [ ] Balances exibidos
  - [ ] Sem erro de autenticação

- [ ] Backtest executado (opcional mas recomendado)
  ```powershell
  python backtest.py
  # Revise os resultados em backtest_results.json
  ```

## 📊 Pre-Flight Check

- [ ] Capital disponível verificado
  - Testnet: Fundos suficientes do faucet
  - Mainnet: Pelo menos $5k depositado

- [ ] Parâmetros validados
  ```python
  order_size_usd * order_levels * 2 < capital  # Deve ser verdadeiro
  ```

- [ ] Estratégia compreendida
  - [ ] Leu TRADING_STRATEGY.md
  - [ ] Entende como market making funciona
  - [ ] Conhece os riscos

- [ ] Monitoramento preparado
  - [ ] Segunda janela/aba de PowerShell aberta
  - [ ] Script de monitor pronto: `.\start_monitor.ps1`

## 🚀 Execução

### Testnet (SEMPRE teste primeiro!)

- [ ] `config.json` com `"testnet": true`
- [ ] Teste de conexão passou
- [ ] Bot iniciado em testnet
  ```powershell
  .\start_bot.ps1
  # ou
  python paradex_market_maker.py
  ```
- [ ] Ordens aparecendo na Paradex UI
- [ ] Logs mostrando atividade
- [ ] Monitor funcionando
- [ ] Bot rodou por pelo menos 1 hora sem erros
- [ ] Performance revisada após 24h

### Produção (Só depois do testnet!)

- [ ] Testnet funcionou perfeitamente por 24h+
- [ ] `config.json` com `"testnet": false`
- [ ] Capital depositado ($5k+)
- [ ] Teste de conexão passou no mainnet
- [ ] Começando com configuração Conservative
- [ ] Bot iniciado
- [ ] Ordens visíveis no mainnet
- [ ] Monitoramento ativo

## 🛡️ Segurança

- [ ] API Keys NÃO compartilhadas
- [ ] Permissões de API apenas para trading (não withdrawal)
- [ ] `.env` e `config.json` em `.gitignore`
- [ ] Backup de configuração feito
  ```powershell
  copy config.json config.backup.json
  ```
- [ ] Entende como parar o bot (Ctrl+C)
- [ ] Sabe como cancelar todas as ordens manualmente na UI

## 📈 Monitoramento Contínuo

Durante as primeiras 24 horas:

- [ ] Verificar logs a cada 1-2 horas
- [ ] Confirmar ordens estão sendo colocadas
- [ ] Verificar fills estão acontecendo
- [ ] Posição não excede limites
- [ ] PnL tracking positivo ou neutro
- [ ] Sem erros repetidos nos logs

Depois de 24h:

- [ ] Analisar performance
- [ ] Calcular fill rate (60-80% é bom)
- [ ] Verificar volume gerado
- [ ] Revisar PnL realizado
- [ ] Decidir se ajusta parâmetros ou continua

## ⚠️ Red Flags - Pare o Bot Se:

- [ ] Perda excede 5% do capital em um dia
- [ ] Posição presa em um lado (sempre long ou sempre short)
- [ ] Fills muito baixos (< 30%) por várias horas
- [ ] Erros de API constantes
- [ ] Comportamento inesperado
- [ ] Mercado extremamente volátil (> 10% moves)

## 🎯 Objetivos de Airdrop

Para maximizar farming:

- [ ] Uptime > 95%
- [ ] Volume diário > $100k
- [ ] Spreads competitivos (< 0.3%)
- [ ] Ordens em múltiplos níveis
- [ ] Presença constante no orderbook
- [ ] Consistency ao longo de semanas

## 📞 Suporte & Recursos

Tenha acesso rápido a:

- [ ] [Documentação Paradex](https://docs.paradex.trade/)
- [ ] [Discord Paradex](https://discord.gg/paradex)
- [ ] README.md deste projeto
- [ ] TRADING_STRATEGY.md para detalhes técnicos
- [ ] QUICK_START.md para referência rápida

## ✅ Final Check

Antes de deixar o bot rodar 24/7:

- [ ] Tudo acima está marcado ✓
- [ ] Bot rodou com sucesso em testnet por 24h+
- [ ] Entendo os riscos
- [ ] Tenho plano para monitorar regularmente
- [ ] Sei como parar o bot se necessário
- [ ] Backup de configuração feito
- [ ] Confortável com capital em risco

---

## 🎉 Pronto para Começar!

Se todos os itens acima estão ✅, você está pronto para começar a fazer market making na Paradex!

**Lembre-se:**
- Comece SEMPRE em testnet
- Use configuração Conservative inicialmente
- Monitore frequentemente nas primeiras 24-48h
- Ajuste parâmetros gradualmente
- NUNCA arrisque mais do que pode perder

**Boa sorte com o farming! 🌾💰**

---

### Quick Commands Reference

```powershell
# Iniciar bot
.\start_bot.ps1

# Monitorar
.\start_monitor.ps1

# Ver logs
Get-Content .\market_maker.log -Tail 50 -Wait

# Testar conexão
python test_connection.py

# Parar bot
# Pressione Ctrl+C na janela do bot
```
