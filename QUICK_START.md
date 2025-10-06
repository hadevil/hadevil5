# 🚀 Quick Start - 5 Minutos para Começar

## Setup Rápido (Windows/PowerShell)

### 1. Instalar Python
```powershell
# Baixe de: https://www.python.org/downloads/
# Durante instalação, marque "Add Python to PATH"
```

### 2. Clone e Configure
```powershell
# Clone o repositório
git clone https://github.com/hadevil/hadevil5.git
cd hadevil5

# Crie ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Se der erro de ExecutionPolicy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instale dependências
pip install -r requirements.txt
```

### 3. Configure API Keys

Edite `config.json` e adicione suas credenciais:
```json
{
  "api_key": "SUA_API_KEY_AQUI",
  "api_secret": "SEU_API_SECRET_AQUI",
  "testnet": true
}
```

### 4. Teste em Testnet
```powershell
# Rode o bot
python paradex_market_maker.py
```

### 5. Monitore Performance
```powershell
# Em outra janela PowerShell
python monitor.py
```

## Configuração Recomendada para $5k

```json
{
  "market": "SOL-USD-PERP",
  "base_spread": 0.0015,
  "order_levels": 5,
  "order_size_usd": 100,
  "max_position_usd": 2500,
  "refresh_interval": 30
}
```

## Verificar se Está Funcionando

1. **Logs**: Deve ver mensagens como:
```
Status | Price: $XXX | Position: X.XX | Orders: XXX
```

2. **No Paradex**: Veja suas ordens na interface
   - Acesse: https://www.paradex.trade/
   - Vá em "Orders" - deve ver 10 ordens (5 buy, 5 sell)

3. **Volume**: Após algumas horas, verifique volume traded

## Próximos Passos

✅ Rode em testnet por 24h  
✅ Verifique logs e performance  
✅ Ajuste parâmetros se necessário  
✅ Mude `"testnet": false` para produção  
✅ Comece com capital pequeno  
✅ Scale up gradualmente  

## Troubleshooting Comum

### "ModuleNotFoundError"
```powershell
pip install -r requirements.txt
```

### "API Key Invalid"
- Verifique API key em config.json
- Confirme se está usando testnet/mainnet correto

### "Insufficient Balance"
- Deposite fundos na Paradex
- Ou reduza `order_size_usd` no config

### Bot Para Sozinho
- Verifique internet
- Veja logs em `market_maker.log`

## Suporte

- 📖 README.md completo
- 🐛 Issues no GitHub
- 💬 Discord Paradex

**Boa sorte! 🚀**
