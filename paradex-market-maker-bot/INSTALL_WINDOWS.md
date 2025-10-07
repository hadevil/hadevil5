# 🚀 Guia de Instalação - Windows PowerShell

## 📋 PASSO A PASSO COMPLETO PARA WINDOWS

### ✅ PASSO 1: Verificar/Instalar Python

1. **Abra PowerShell como Administrador:**
   - Pressione `Win + X` → "Windows PowerShell (Admin)"

2. **Verifique se Python está instalado:**
   ```powershell
   python --version
   ```

3. **Se Python NÃO estiver instalado:**
   - Baixe de: https://python.org/downloads/
   - **IMPORTANTE:** Marque "Add Python to PATH" durante instalação
   - Recomendado: Python 3.10 ou superior

4. **Verifique novamente:**
   ```powershell
   python --version
   pip --version
   ```

### ✅ PASSO 2: Baixar o Projeto

**Opção A - Usando Git (Recomendado):**
```powershell
# Instalar Git (se não tiver)
winget install --id Git.Git -e --source winget

# Clonar o projeto
git clone https://github.com/seu-usuario/paradex-market-maker-bot.git
cd paradex-market-maker-bot
```

**Opção B - Download Manual:**
1. Baixe o ZIP do projeto
2. Extraia para uma pasta
3. Abra PowerShell na pasta extraída:
   ```powershell
   cd "C:\caminho\para\sua\pasta\paradex-market-maker-bot"
   ```

### ✅ PASSO 3: Instalar Dependências

```powershell
# Método 1: Usando o script automático (RECOMENDADO)
.\run_windows.ps1 -Install

# Método 2: Instalação manual
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Método 3: Se houver problemas com pip
python -m pip install requests pandas openpyxl web3 eth-account questionary python-dotenv
```

**Se aparecer erro de permissão:**
```powershell
# Execute como Administrador:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ✅ PASSO 4: Configurar Conta Paradex

1. **Obter credenciais da Paradex:**
   - Vá para: https://paradex.trade/
   - Crie/login na sua conta
   - Configure API keys se necessário

2. **Editar configuração:**
   ```powershell
   .\run_windows.ps1 -Config
   ```
   Isso abrirá o arquivo `config_windows.json` no Bloco de Notas.

3. **Editar as credenciais:**
   ```json
   {
     "account": {
       "address": "0xSEU_ENDERECO_AQUI",
       "private_key": "0xSUA_PRIVATE_KEY_AQUI",
       "api_key": "SUA_API_KEY_AQUI",
       "api_secret": "SEU_API_SECRET_AQUI"
     }
   }
   ```

4. **Salvar e fechar** o arquivo.

### ✅ PASSO 5: Testar o Bot

1. **Verificar instalação:**
   ```powershell
   python -c "import requests, pandas, web3; print('✅ Todas as dependências OK!')"
   ```

2. **Teste básico do bot:**
   ```powershell
   python main.py
   ```
   Escolha a opção 1 para configurar conta e teste.

### ✅ PASSO 6: Executar o Bot

```powershell
# Método 1: Usando o script (RECOMENDADO)
.\run_windows.ps1 -Run

# Método 2: Direto
python main.py
```

## 🔧 COMANDOS IMPORTANTES

### 📁 Navegação no PowerShell:
```powershell
# Ver onde você está
pwd

# Listar arquivos
ls

# Entrar em diretório
cd nome_da_pasta

# Voltar um nível
cd ..
```

### 🛠️ Comandos Úteis:
```powershell
# Verificar se porta está em uso
netstat -an | findstr :80

# Ver processos Python rodando
tasklist | findstr python

# Matar processo Python
taskkill /f /im python.exe
```

## 🚨 SOLUÇÃO DE PROBLEMAS COMUNS

### ❌ "Python não reconhecido"
**Solução:**
```powershell
# Reinstalar Python com PATH marcado
# OU adicionar manualmente ao PATH:
$env:Path += ";C:\Python310;C:\Python310\Scripts"
```

### ❌ "Erro de permissão" ou "Access denied"
**Solução:**
```powershell
# Execute PowerShell como Administrador
# OU use:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ "No module named 'requests'" ou similar
**Solução:**
```powershell
# Reinstalar dependências
python -m pip uninstall requests pandas web3
python -m pip install requests pandas openpyxl web3 eth-account questionary python-dotenv
```

### ❌ "Erro ao conectar na Paradex"
**Solução:**
1. Verifique suas credenciais no `config_windows.json`
2. Teste conexão manual:
   ```python
   import requests
   response = requests.get("https://api.paradex.trade/api/v1/ticker")
   print(response.status_code)
   ```

### ❌ "Ordem rejeitada" ou erros de trading
**Solução:**
1. Verifique se tem fundos suficientes
2. Ajuste os valores no `config_windows.json`:
   ```json
   {
     "trading": {
       "order_value_usd": {"min": 5, "max": 15}
     }
   }
   ```

## 📊 PRIMEIROS PASSOS COM O BOT

### 1. **Configuração Inicial:**
```powershell
# 1. Configure sua conta
.\run_windows.ps1 -Config

# 2. Edite config_windows.json com suas credenciais

# 3. Teste
.\run_windows.ps1 -Run
```

### 2. **Menu do Bot:**
```
📋 Menu Principal - Paradex Market Maker

1. ⚙️  Configurar conta
2. 🚀 Iniciar trading
3. 📊 Ver status
4. ⚠️  Parar trading
5. ❌ Sair
```

### 3. **Primeira Execução:**
- Escolha opção 1 para configurar conta
- Digite suas credenciais quando solicitado
- Escolha opção 2 para começar a operar
- Monitore os logs iniciais

## 🎯 DICAS PARA SUCESSO

### 💡 **Antes de Começar:**
1. **Comece pequeno** - Use valores mínimos primeiro
2. **Monitore constantemente** - Não deixe rodando sem supervisão
3. **Tenha fundos suficientes** - Mínimo $5k como planejado
4. **Entenda os riscos** - Pode haver perdas financeiras

### 📈 **Otimização:**
- **Ajuste configurações** baseado no desempenho
- **Monitore os logs** em `logs/trading.log`
- **Aumente gradualmente** os valores conforme confiança

### 🛡️ **Segurança:**
- **Nunca compartilhe** sua private key
- **Use VPN** se necessário
- **Mantenha backups** da configuração (sem credenciais sensíveis)

## 📞 PRECISANDO DE AJUDA?

### Comandos de Diagnóstico:
```powershell
# Verificar Python e dependências
python --version
python -c "import sys; print(sys.path)"

# Verificar conectividade
ping google.com
Test-NetConnection -ComputerName api.paradex.trade -Port 443

# Ver logs detalhados
Get-Content logs/trading.log -Tail 20
```

### Problemas Persistentes:
1. Verifique se seguiu todos os passos
2. Compare sua configuração com `config_example.json`
3. Teste em modo manual antes de automatizar
4. Verifique conexão com a Paradex

**🎉 Pronto! Seu bot está configurado e pronto para farmar airdrops na Paradex!**