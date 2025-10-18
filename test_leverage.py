#!/usr/bin/env python3
"""
🧪 Teste de Alavancagem
Verifica se os cálculos de margem estão corretos
"""

def test_leverage_calculation():
    """Testa cálculo de margem com alavancagem"""
    
    print("\n" + "="*70)
    print("🧪 TESTE DE ALAVANCAGEM")
    print("="*70)
    
    # Cenário do usuário
    balance = 2442.00  # Saldo na conta
    leverage = 20      # Alavancagem configurada
    position_size_usd = 12000  # Tamanho desejado por posição
    num_positions = 4  # 2 LONG + 2 SHORT
    
    print(f"\n📊 DADOS:")
    print(f"   Saldo na conta: ${balance:,.2f}")
    print(f"   Alavancagem: {leverage}x")
    print(f"   Posição desejada: ${position_size_usd:,.2f} cada")
    print(f"   Número de posições: {num_positions}")
    
    print(f"\n💰 CÁLCULOS:")
    
    # Valor total das posições
    total_position_value = position_size_usd * num_positions
    print(f"   Valor total posições: ${total_position_value:,.2f}")
    
    # Margem necessária (COM alavancagem)
    total_margin_required = total_position_value / leverage
    print(f"   Margem necessária (÷{leverage}): ${total_margin_required:,.2f}")
    
    # Verificar se tem saldo
    has_balance = balance >= total_margin_required
    
    print(f"\n✅ RESULTADO:")
    if has_balance:
        remaining = balance - total_margin_required
        print(f"   ✅ SALDO SUFICIENTE!")
        print(f"   Saldo disponível: ${balance:,.2f}")
        print(f"   Margem necessária: ${total_margin_required:,.2f}")
        print(f"   Margem restante: ${remaining:,.2f}")
    else:
        deficit = total_margin_required - balance
        print(f"   ❌ SALDO INSUFICIENTE!")
        print(f"   Saldo disponível: ${balance:,.2f}")
        print(f"   Margem necessária: ${total_margin_required:,.2f}")
        print(f"   Falta: ${deficit:,.2f}")
    
    print(f"\n📈 DETALHES POR POSIÇÃO:")
    margin_per_position = position_size_usd / leverage
    print(f"   Valor da posição: ${position_size_usd:,.2f}")
    print(f"   Margem usada: ${margin_per_position:,.2f}")
    print(f"   Alavancagem: {leverage}x")
    
    # Exemplos com diferentes valores
    print(f"\n" + "="*70)
    print("💡 EXEMPLOS DE POSITION_SIZE_USD:")
    print("="*70)
    
    examples = [
        ("Conservador (50%)", 6000),
        ("Moderado (75%)", 9000),
        ("Máximo seguro (90%)", 11000),
        ("Arriscado (100%)", 12210),
        ("MUITO arriscado", 15000),
    ]
    
    for name, size in examples:
        total_value = size * num_positions
        margin_needed = total_value / leverage
        percentage = (margin_needed / balance) * 100
        
        status = "✅" if margin_needed <= balance else "❌"
        
        print(f"\n{name}: POSITION_SIZE_USD={size}")
        print(f"   Posições totais: ${total_value:,.2f}")
        print(f"   Margem necessária: ${margin_needed:,.2f} ({percentage:.1f}% do saldo) {status}")
    
    print(f"\n" + "="*70)
    print("🎯 RECOMENDAÇÃO:")
    print("="*70)
    
    # Calcular valor ideal (usa 90% do saldo)
    safe_margin = balance * 0.90
    safe_total_value = safe_margin * leverage
    safe_position_size = safe_total_value / num_positions
    
    print(f"\nPara usar 90% do saldo com segurança:")
    print(f"   POSITION_SIZE_USD={int(safe_position_size)}")
    print(f"   Posições: 4 × ${safe_position_size:,.0f} = ${safe_total_value:,.0f}")
    print(f"   Margem: ${safe_margin:,.2f} (90% de ${balance:,.2f})")
    print(f"   Sobra: ${balance - safe_margin:,.2f} para liquidação")
    
    print()


if __name__ == "__main__":
    test_leverage_calculation()
