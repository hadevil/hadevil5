# 📥 COMANDOS PARA BAIXAR O BOT ATUALIZADO

## 🎯 OPÇÃO 1: Atualizar via Git (RECOMENDADO)

Se você já tem o bot na sua máquina, use estes comandos:

```bash
# 1. Entre na pasta do bot
cd ~/apex-trading-bot

# 2. Veja em que branch você está
git branch

# 3. Mude para o branch correto (se necessário)
git checkout cursor/bot-de-trading-autom-tico-para-perp-dex-c105

# 4. Baixe as atualizações
git pull origin cursor/bot-de-trading-autom-tico-para-perp-dex-c105

# 5. Verifique se pegou tudo
git log --oneline -5

# 6. Liste os arquivos novos
ls -lh *.py *.md

# PRONTO! ✅
```

---

## 🆕 OPÇÃO 2: Download do Zero

Se não tem o bot ainda, ou quer começar limpo:

```bash
# 1. Clone o repositório
cd ~
git clone https://github.com/hadevil/hadevil5.git apex-trading-bot

# 2. Entre na pasta
cd apex-trading-bot

# 3. Mude para o branch correto
git checkout cursor/bot-de-trading-autom-tico-para-perp-dex-c105

# 4. Verifique os arquivos
ls -lh *.py

# PRONTO! ✅
```

---

## 🔍 VERIFICAR SE PEGOU AS ATUALIZAÇÕES

```bash
cd ~/apex-trading-bot

# Ver se tem os arquivos novos
ls -lh backtest_optimizer.py analyze_performance.py test_leverage.py

# Ver se a correção de alavancagem está no bot.py
grep -n "total_margin_required" bot.py

# Deve mostrar algo como:
# 240:            total_margin_required = total_position_value / leverage
```

---

## 📦 ARQUIVOS NOVOS QUE VOCÊ VAI TER

```
✅ backtest_optimizer.py       # Otimizador de SL/TP/Time
✅ analyze_performance.py      # Análise rápida
✅ test_leverage.py            # Teste de alavancagem
✅ HOW_TO_BACKTEST.md         # Guia completo
✅ LEVERAGE_FIXED.md          # Explicação da correção
✅ bot.py                     # Corrigido (alavancagem)
```

---

## 🚀 DEPOIS DE BAIXAR

### 1. Configure (se ainda não configurou)

```bash
cd ~/apex-trading-bot

# Copie o exemplo
cp config.example.txt config.txt

# Edite com seus dados
nano config.txt
```

### 2. Configure POSITION_SIZE_USD com alavancagem

```bash
# Para seu saldo de $2,442 com 20x:

# Conservador (50%):
POSITION_SIZE_USD=6000

# Recomendado (90%):
POSITION_SIZE_USD=11000

# Máximo (99%):
POSITION_SIZE_USD=12200
```

### 3. Teste a alavancagem

```bash
python3 test_leverage.py

# Mostra se seu POSITION_SIZE_USD está correto
```

### 4. Rode o bot

```bash
python3 main.py
```

---

## 🔧 SE DER ERRO DE DEPENDÊNCIAS

```bash
cd ~/apex-trading-bot

# Instalar pandas (para backtest)
pip3 install pandas

# Ou instalar tudo
pip3 install -r requirements.txt
```

---

## 💡 COMANDOS ÚTEIS

### Ver mudanças no código

```bash
cd ~/apex-trading-bot

# Ver o que mudou no bot.py
git diff HEAD~1 bot.py
```

### Ver todos os arquivos Python

```bash
cd ~/apex-trading-bot
ls -lh *.py
```

### Ver logs do git

```bash
cd ~/apex-trading-bot
git log --oneline -10
```

---

## 🎯 RESUMO RÁPIDO

```bash
# Atualizar bot existente:
cd ~/apex-trading-bot
git pull origin cursor/bot-de-trading-autom-tico-para-perp-dex-c105

# Testar alavancagem:
python3 test_leverage.py

# Editar config (se necessário):
nano config.txt

# Rodar:
python3 main.py
```

---

## ✅ CHECKLIST

Após baixar, verifique:

- [ ] Arquivo `backtest_optimizer.py` existe
- [ ] Arquivo `analyze_performance.py` existe  
- [ ] Arquivo `test_leverage.py` existe
- [ ] `grep "total_margin_required" bot.py` encontra a linha
- [ ] `python3 test_leverage.py` roda sem erro
- [ ] `config.txt` está configurado
- [ ] `POSITION_SIZE_USD` está ajustado para seu saldo

---

**Pronto! Agora é só baixar e usar! 🚀**
