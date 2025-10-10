# Guia de Análise de Opções Deribit - Queda de 40%

## Resumo da Análise

Com base na simulação realizada, **tanto BTC quanto ETH oferecem retornos similares** para opções PUT com queda de 40% até junho de 2026.

### Melhores Cenários (Simulação):
- **BTC PUT Strike $80,000**: Retorno estimado de +300%
- **ETH PUT Strike $3,200**: Retorno estimado de +300%

## Como Fazer a Análise Real no Site da Deribit

### 1. Acesse o Site
- Vá para: https://www.deribit.com/
- Faça login na sua conta

### 2. Navegue para Opções
- Clique em "Options" no menu principal
- Selecione "BTC" ou "ETH"

### 3. Configure os Filtros
- **Vencimento**: Junho 2026 (ou 30JUN26)
- **Tipo**: PUT (opções de venda)
- **Moeda**: USD

### 4. Strikes Recomendados para Análise

#### Para BTC (assumindo preço atual ~$100,000):
- **$80,000** - ATM (At The Money) - Maior potencial de lucro
- **$70,000** - OTM (Out of The Money) - Boa relação risco/retorno
- **$60,000** - OTM - Limite da queda de 40%

#### Para ETH (assumindo preço atual ~$4,000):
- **$3,200** - ATM - Maior potencial de lucro
- **$2,800** - OTM - Boa relação risco/retorno
- **$2,400** - OTM - Limite da queda de 40%

### 5. Fatores Importantes a Considerar

#### Preços das Opções
- Anote o **preço de compra** (bid/ask) de cada opção
- Considere o spread bid-ask para liquidez

#### Gregas (Greeks)
- **Delta**: Sensibilidade ao preço do ativo
- **Gamma**: Sensibilidade do delta
- **Theta**: Decaimento temporal
- **Vega**: Sensibilidade à volatilidade

#### Volatilidade
- Verifique a volatilidade implícita (IV)
- Compare com volatilidade histórica
- Considere se a IV está alta ou baixa

### 6. Cálculo Manual de Retorno

Para cada opção que você considerar:

```
Preço Final (após queda 40%) = Preço Atual × 0.6
Valor Intrínseco = max(0, Strike - Preço Final)
Lucro/Prejuízo = Valor Intrínseco - Preço da Opção
Retorno % = (Lucro/Prejuízo / Preço da Opção) × 100
```

### 7. Exemplo Prático

**BTC PUT Strike $80,000:**
- Preço atual BTC: $100,000
- Preço após queda 40%: $60,000
- Valor intrínseco: max(0, $80,000 - $60,000) = $20,000
- Se preço da opção = $5,000
- Lucro = $20,000 - $5,000 = $15,000
- Retorno = ($15,000 / $5,000) × 100 = 300%

### 8. Considerações de Risco

#### Riscos das Opções PUT:
- **Perda Total**: Se o preço não cair 40%, perde 100% do investimento
- **Decaimento Temporal**: Valor diminui conforme se aproxima do vencimento
- **Volatilidade**: Mudanças na volatilidade afetam o preço

#### Estratégias Alternativas:
- **Spreads**: Comprar PUT e vender PUT com strike menor
- **Straddles**: Comprar PUT e CALL simultaneamente
- **Estratégias de Hedge**: Usar opções para proteger posições existentes

### 9. Checklist Final

Antes de investir, verifique:
- [ ] Preços reais das opções no site
- [ ] Liquidez (volume de negociação)
- [ ] Spread bid-ask aceitável
- [ ] Volatilidade implícita razoável
- [ ] Tempo até vencimento adequado
- [ ] Capital disponível para investimento
- [ ] Tolerância ao risco

### 10. Ferramentas Úteis

- **Calculadora de Opções**: Use ferramentas online para calcular gregas
- **Gráficos**: Analise tendências históricas de preços
- **Notícias**: Mantenha-se atualizado com eventos do mercado
- **Simulador**: Teste diferentes cenários antes de investir

## Conclusão

A análise sugere que **ambas as opções (BTC e ETH) oferecem potencial similar** para retornos em caso de queda de 40%. A escolha final deve ser baseada em:

1. **Preços reais** das opções no site da Deribit
2. **Liquidez** e facilidade de negociação
3. **Sua confiança** na direção do mercado
4. **Capital disponível** para investimento
5. **Tolerância ao risco** e horizonte de investimento

**Lembre-se**: Esta é uma análise educacional. Sempre consulte um consultor financeiro antes de tomar decisões de investimento.