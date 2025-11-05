# 🔧 Solução de Conflito de Dependências

## ⚠️ Problema

Você tem outros pacotes Python instalados globalmente que conflitam com as dependências do bot Apex:

```
❌ paradex-py 0.5.0rc2 quer web3<7.0.0 (você tem 7.14.0)
❌ paradex-py 0.5.0rc2 quer eth-account<0.12.0 (você tem 0.13.7)
❌ ledgereth 0.9.1 quer eth-utils<3.0.0 (você tem 5.3.1)
❌ starknet-py 0.27.0 quer websockets>=15.0.1 (você tem 12.0)
```

## ✅ Solução: Virtual Environment

Criamos um **ambiente Python isolado** só para o bot Apex, sem afetar seus outros projetos!

---

## 🚀 Como Usar (3 Comandos Simples)

### **1️⃣ Atualizar o código:**
```bash
cd ~/apex-trading-bot
git pull origin cursor/bot-de-trading-autom-tico-para-perp-dex-c105
```

### **2️⃣ Setup automático (primeira vez):**
```bash
bash setup_venv.sh
```

Isso vai:
- ✅ Criar pasta `venv/` com Python isolado
- ✅ Instalar versões compatíveis das dependências
- ✅ Verificar se tudo funcionou
- ✅ Mostrar instruções de uso

### **3️⃣ Rodar o bot:**

**Opção A - Script conveniente:**
```bash
bash run_bot.sh
```

**Opção B - Manual:**
```bash
source venv/bin/activate
python3 main.py
# Quando terminar:
deactivate
```

---

## 📦 O Que É Um Virtual Environment?

É uma pasta (`venv/`) que contém:
- ✅ Python isolado
- ✅ Dependências específicas do projeto
- ✅ Não afeta outros projetos
- ✅ Não afeta Python global

**Analogia:** É como ter um container Docker, mas mais leve!

---

## 🔍 Estrutura Após Setup

```
apex-trading-bot/
├── venv/                    ← NOVO! Ambiente isolado
│   ├── bin/
│   │   ├── python3          ← Python do bot
│   │   └── pip              ← Pip do bot
│   └── lib/                 ← Dependências do bot
├── main.py
├── bot.py
├── config.txt
├── setup_venv.sh           ← NOVO! Setup automático
├── run_bot.sh              ← NOVO! Rodar bot facilmente
└── requirements.txt        ← Versões compatíveis
```

---

## ✅ Verificar Se Funcionou

Depois de rodar `bash setup_venv.sh`, você deve ver:

```
========================================
✅ SETUP COMPLETO!
========================================

Para usar o bot:

  1. Ativar ambiente virtual:
     source venv/bin/activate

  2. Rodar o bot:
     python3 main.py

  3. Desativar quando terminar:
     deactivate
```

---

## 🛠️ Troubleshooting

### **Erro: "python3-venv not found"**
```bash
sudo apt update
sudo apt install -y python3-venv
bash setup_venv.sh
```

### **Erro: "Permission denied"**
```bash
chmod +x setup_venv.sh run_bot.sh
bash setup_venv.sh
```

### **Preciso reinstalar tudo?**
```bash
rm -rf venv
bash setup_venv.sh
```

### **Meus outros projetos vão funcionar?**
✅ SIM! O venv só afeta este bot. Seus outros projetos (paradex-py, starknet-py) continuam funcionando normalmente!

---

## 🔄 Workflow Diário

```bash
# Iniciar bot
cd ~/apex-trading-bot
bash run_bot.sh

# Bot rodando...
# Ctrl+C para parar

# Continuar outros projetos normalmente
cd ~/meu-outro-projeto
python3 script.py  # Usa Python global
```

---

## 📊 Versões Instaladas no Venv

```
apexomni>=1.0.0
web3>=6.19.0,<7.0.0         ← Compatível com paradex
eth-account>=0.11.0,<0.12.0 ← Compatível com paradex
eth-utils>=2.1.0,<3.0.0     ← Compatível com ledgereth
rlp>=3.0.0,<4.0.0           ← Compatível com ledgereth
websockets>=15.0,<16.0      ← Compatível com starknet
```

---

## 💡 Dicas

1. **Sempre ative o venv antes de usar o bot:**
   ```bash
   source venv/bin/activate
   ```

2. **Desative quando terminar:**
   ```bash
   deactivate
   ```

3. **Ou use o script run_bot.sh** que faz isso automaticamente!

4. **Atualizar dependências:**
   ```bash
   source venv/bin/activate
   pip install --upgrade -r requirements.txt
   ```

---

## ✅ Benefícios

- ✅ **Zero conflitos** com outros projetos
- ✅ **Setup de 1 comando** (setup_venv.sh)
- ✅ **Rodar de 1 comando** (run_bot.sh)
- ✅ **Reprodutível** em qualquer máquina
- ✅ **Best practice** de Python

---

**Pronto para usar! 🚀**

Execute:
```bash
cd ~/apex-trading-bot
git pull
bash setup_venv.sh
bash run_bot.sh
```
