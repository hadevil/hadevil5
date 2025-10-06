# 🔐 Como Configurar Conta Paradex para o Bot

## 📋 PASSO A PASSO PARA CONFIGURAR SUA CONTA

### ✅ PASSO 1: Criar Conta na Paradex

1. **Acesse o site:**
   - Vá para: https://paradex.trade/

2. **Crie sua conta:**
   - Clique em "Connect Wallet" ou "Sign Up"
   - Conecte sua carteira (MetaMask, Phantom, etc.)
   - Complete o processo de verificação

3. **Deposite fundos:**
   - Transfira pelo menos $5,000+ para sua conta
   - Recomendado: USDC ou outros stablecoins

### ✅ PASSO 2: Obter Chaves da API (Se Necessário)

**Nota:** Alguns bots podem precisar de API keys. Verifique na documentação da Paradex.

1. **Acesse configurações:**
   - Vá para Settings/Account/API Keys

2. **Crie nova chave:**
   - Clique em "Create API Key"
   - Permissões necessárias:
     - ✅ Read (leitura de dados)
     - ✅ Trade (executar ordens)
     - ❌ Withdraw (não necessário)

3. **Anote as credenciais:**
   ```
   API Key: sua_api_key_aqui
   Secret Key: seu_secret_aqui
   ```

### ✅ PASSO 3: Configurar no Arquivo do Bot

1. **Abra o arquivo de configuração:**
   ```powershell
   .\run_windows.ps1 -Config
   ```

2. **Edite `config_windows.json`:**
   ```json
   {
     "account": {
       "address": "0x1234567890abcdef...",
       "private_key": "0xabcdef1234567890...",
       "api_key": "sua_api_key_aqui",
       "api_secret": "seu_secret_aqui"
     }
   }
   ```

### 🔍 ONDE ENCONTRAR CADA CREDENCIAL:

#### **Address (Endereço da Carteira):**
```
📍 MetaMask: Clique na conta → Copy address
📍 Phantom: Settings → Copy wallet address
📍 Formato: 0x1234567890abcdef1234567890abcdef12345678
```

#### **Private Key (Chave Privada):**
```
⚠️  MUITO IMPORTANTE - Mantenha segura!

📍 MetaMask:
   - Settings → Security & Privacy
   - Clique em "Reveal Secret Recovery Phrase" (NÃO a seed phrase!)
   - Procure por "Export Private Key"

📍 Phantom:
   - Settings → Private keys
   - Export private key

📍 Formato: 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
```

#### **API Key e Secret (Se necessário):**
```
📍 Site da Paradex:
   - Login na sua conta
   - Settings → API Keys
   - Create new key
   - Copy API Key e API Secret
```

### ✅ PASSO 4: Verificar Configuração

1. **Teste básico:**
   ```powershell
   python -c "
   import json
   with open('config_windows.json', 'r') as f:
       config = json.load(f)
   print('✅ Configuração carregada com sucesso!')
   print('📧 Address:', config['account']['address'][:10] + '...')
   print('🔑 Private Key:', config['account']['private_key'][:10] + '...')
   "
   ```

2. **Teste de conectividade:**
   ```python
   import requests
   try:
       response = requests.get('https://api.paradex.trade/api/v1/ticker', timeout=5)
       print(f'✅ Conectividade OK! Status: {response.status_code}')
   except Exception as e:
       print(f'❌ Erro de conexão: {e}')
   ```

### ⚠️ DICAS DE SEGURANÇA CRÍTICAS:

1. **Nunca compartilhe** sua private key
2. **Use apenas em ambiente seguro**
3. **Faça backup** da configuração (sem credenciais)
4. **Monitore atividade** regularmente
5. **Use VPN** se necessário

## 🚨 SOLUÇÃO DE PROBLEMAS DE CONTA

### ❌ "Endereço inválido"
```
✅ Verifique se começa com 0x
✅ Certifique-se que tem 42 caracteres
✅ Não inclua espaços extras
```

### ❌ "Private key inválida"
```
✅ Verifique se começa com 0x
✅ Certifique-se que tem 64 caracteres hexadecimais
✅ Não confunda com seed phrase (12-24 palavras)
```

### ❌ "API key inválida"
```
✅ Verifique se copiou corretamente
✅ Certifique-se que tem as permissões necessárias
✅ Regenerar se necessário
```

### ❌ "Saldo insuficiente"
```
✅ Deposite pelo menos $5,000
✅ Verifique se está na rede correta
✅ Confirme o depósito na blockchain
```

## 📋 CHECKLIST FINAL ANTES DE EXECUTAR:

- [ ] Conta Paradex criada e verificada
- [ ] Fundos depositados ($5,000+)
- [ ] Endereço da carteira copiado corretamente
- [ ] Private key obtida e segura
- [ ] API keys configuradas (se necessário)
- [ ] Arquivo config_windows.json editado
- [ ] Teste de conectividade passou
- [ ] Python e dependências instalados

## 🎯 PRÓXIMOS PASSOS:

1. ✅ Complete a configuração acima
2. ✅ Execute `.\run_windows.ps1 -Run`
3. ✅ Monitore os primeiros ciclos
4. ✅ Ajuste configurações conforme necessário

**🎉 Sua conta está pronta! Vamos começar a farmar airdrops! 🚀**