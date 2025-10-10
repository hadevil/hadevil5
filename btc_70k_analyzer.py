#!/usr/bin/env python3
"""
Analisador de Opções PUT BTC para Cenário de $70,000
Calcula qual opção oferece melhor retorno se BTC chegar a $70k até junho 2026
"""

from datetime import datetime, date
from typing import Dict, List

class BTC70KAnalyzer:
    def __init__(self, current_btc_price: float = 100000):
        self.current_btc_price = current_btc_price
        self.target_price = 70000  # Preço alvo em junho 2026
        self.current_date = date.today()
        self.expiration_date = date(2026, 6, 30)
        self.days_to_expiry = (self.expiration_date - self.current_date).days
        
    def calculate_put_payoff(self, strike_price: float, put_price: float) -> Dict:
        """
        Calcula o payoff de uma opção PUT se BTC chegar a $70,000
        
        Args:
            strike_price: Preço de exercício da opção
            put_price: Preço pago pela opção
        
        Returns:
            Dict com informações do payoff
        """
        # Payoff da opção PUT = max(0, strike - target_price)
        intrinsic_value = max(0, strike_price - self.target_price)
        
        # Lucro/Prejuízo = intrinsic_value - put_price
        profit_loss = intrinsic_value - put_price
        
        # Retorno percentual
        return_percentage = (profit_loss / put_price) * 100 if put_price > 0 else 0
        
        # ROI (Return on Investment)
        roi = profit_loss / put_price if put_price > 0 else 0
        
        # Valor total por contrato (assumindo 1 BTC por contrato)
        total_value = intrinsic_value
        
        return {
            'strike_price': strike_price,
            'current_price': self.current_btc_price,
            'target_price': self.target_price,
            'put_price': put_price,
            'intrinsic_value': intrinsic_value,
            'profit_loss': profit_loss,
            'return_percentage': return_percentage,
            'roi': roi,
            'total_value': total_value,
            'is_profitable': profit_loss > 0,
            'moneyness': self._get_moneyness(strike_price)
        }
    
    def _get_moneyness(self, strike_price: float) -> str:
        """Determina se a opção está ITM, ATM ou OTM"""
        if strike_price > self.target_price:
            return "ITM (In The Money)"
        elif strike_price == self.target_price:
            return "ATM (At The Money)"
        else:
            return "OTM (Out of The Money)"
    
    def analyze_multiple_strikes(self) -> List[Dict]:
        """
        Analisa múltiplos strikes para encontrar o melhor retorno
        """
        # Diferentes strikes para análise
        strikes = [90000, 85000, 80000, 75000, 70000, 65000, 60000, 55000, 50000]
        
        # Preços estimados das opções PUT (baseado em volatilidade típica)
        # Estes são valores estimados - você deve verificar no site da Deribit
        estimated_put_prices = {
            90000: 15000,  # ITM - muito caro
            85000: 10000,  # ITM
            80000: 6000,   # ITM
            75000: 3500,   # ITM
            70000: 2000,   # ATM
            65000: 1200,   # OTM
            60000: 700,    # OTM
            55000: 400,    # OTM
            50000: 200     # OTM
        }
        
        scenarios = []
        
        for strike in strikes:
            put_price = estimated_put_prices.get(strike, 1000)
            scenario = self.calculate_put_payoff(strike, put_price)
            scenarios.append(scenario)
        
        return scenarios
    
    def find_best_options(self) -> Dict:
        """
        Encontra as melhores opções baseadas em diferentes critérios
        """
        scenarios = self.analyze_multiple_strikes()
        
        # Melhor retorno percentual
        best_return = max(scenarios, key=lambda x: x['return_percentage'])
        
        # Melhor lucro absoluto
        best_profit = max(scenarios, key=lambda x: x['profit_loss'])
        
        # Melhor ROI
        best_roi = max(scenarios, key=lambda x: x['roi'])
        
        # Opções lucrativas
        profitable_options = [s for s in scenarios if s['is_profitable']]
        
        return {
            'best_return_percentage': best_return,
            'best_absolute_profit': best_profit,
            'best_roi': best_roi,
            'profitable_options': profitable_options,
            'all_scenarios': scenarios
        }
    
    def print_analysis(self):
        """
        Imprime análise completa
        """
        print("=" * 80)
        print("ANÁLISE DE OPÇÕES PUT BTC - CENÁRIO $70,000 EM JUNHO 2026")
        print("=" * 80)
        print(f"Preço atual BTC: ${self.current_btc_price:,.0f}")
        print(f"Preço alvo: ${self.target_price:,.0f}")
        print(f"Queda necessária: {((self.current_btc_price - self.target_price) / self.current_btc_price * 100):.1f}%")
        print(f"Dias até vencimento: {self.days_to_expiry}")
        print()
        
        analysis = self.find_best_options()
        
        print("ANÁLISE DETALHADA POR STRIKE:")
        print("-" * 80)
        print(f"{'Strike':<10} {'Preço PUT':<12} {'Valor Intr.':<12} {'Lucro':<12} {'Retorno %':<12} {'Status':<15}")
        print("-" * 80)
        
        for scenario in analysis['all_scenarios']:
            status = "✅ LUCRO" if scenario['is_profitable'] else "❌ PREJUÍZO"
            print(f"${scenario['strike_price']:,.0f}     "
                  f"${scenario['put_price']:,.0f}      "
                  f"${scenario['intrinsic_value']:,.0f}      "
                  f"${scenario['profit_loss']:,.0f}      "
                  f"{scenario['return_percentage']:+.1f}%      "
                  f"{status}")
        
        print("\n" + "=" * 80)
        print("MELHORES OPÇÕES:")
        print("=" * 80)
        
        print(f"🏆 MELHOR RETORNO PERCENTUAL:")
        best_ret = analysis['best_return_percentage']
        print(f"   Strike: ${best_ret['strike_price']:,.0f}")
        print(f"   Preço PUT: ${best_ret['put_price']:,.0f}")
        print(f"   Retorno: {best_ret['return_percentage']:+.1f}%")
        print(f"   Lucro: ${best_ret['profit_loss']:,.0f}")
        print(f"   Status: {best_ret['moneyness']}")
        
        print(f"\n💰 MELHOR LUCRO ABSOLUTO:")
        best_prof = analysis['best_absolute_profit']
        print(f"   Strike: ${best_prof['strike_price']:,.0f}")
        print(f"   Preço PUT: ${best_prof['put_price']:,.0f}")
        print(f"   Retorno: {best_prof['return_percentage']:+.1f}%")
        print(f"   Lucro: ${best_prof['profit_loss']:,.0f}")
        print(f"   Status: {best_prof['moneyness']}")
        
        print(f"\n📈 MELHOR ROI:")
        best_roi = analysis['best_roi']
        print(f"   Strike: ${best_roi['strike_price']:,.0f}")
        print(f"   Preço PUT: ${best_roi['put_price']:,.0f}")
        print(f"   Retorno: {best_roi['return_percentage']:+.1f}%")
        print(f"   Lucro: ${best_roi['profit_loss']:,.0f}")
        print(f"   Status: {best_roi['moneyness']}")
        
        print(f"\n✅ OPÇÕES LUCRATIVAS ({len(analysis['profitable_options'])} total):")
        for option in analysis['profitable_options']:
            print(f"   Strike ${option['strike_price']:,.0f}: "
                  f"{option['return_percentage']:+.1f}% "
                  f"(${option['profit_loss']:,.0f} lucro)")
        
        print("\n" + "=" * 80)
        print("RECOMENDAÇÕES:")
        print("=" * 80)
        
        if analysis['profitable_options']:
            print("✅ EXISTEM OPÇÕES LUCRATIVAS se BTC chegar a $70,000")
            print("\n📋 ESTRATÉGIAS RECOMENDADAS:")
            print("1. Para MÁXIMO RETORNO: Strike mais alto possível (ITM)")
            print("2. Para MELHOR RISCO/RETORNO: Strike próximo a $80,000")
            print("3. Para MENOR CUSTO: Strike próximo a $75,000")
            print("\n⚠️  CONSIDERAÇÕES:")
            print("- Opções ITM são mais caras mas mais seguras")
            print("- Opções OTM são mais baratas mas mais arriscadas")
            print("- Verifique preços reais no site da Deribit")
            print("- Considere liquidez e spread bid-ask")
        else:
            print("❌ NENHUMA OPÇÃO É LUCRATIVA se BTC chegar a $70,000")
            print("   Isso significa que o preço atual das opções está muito alto")
            print("   ou o cenário de $70,000 não é suficiente para gerar lucro")
        
        print("\n" + "=" * 80)
        print("PRÓXIMOS PASSOS:")
        print("=" * 80)
        print("1. Acesse https://www.deribit.com/")
        print("2. Verifique preços reais das opções PUT")
        print("3. Foque nos strikes entre $75,000 e $85,000")
        print("4. Compare com esta análise")
        print("5. Considere sua tolerância ao risco")

def main():
    """
    Função principal
    """
    # Você pode ajustar o preço atual do BTC
    current_btc_price = 100000  # Ajuste conforme preço atual
    
    analyzer = BTC70KAnalyzer(current_btc_price)
    
    print("IMPORTANTE: Esta análise usa preços estimados das opções.")
    print("Para análise precisa, verifique os preços reais no site da Deribit.")
    print("Acesse: https://www.deribit.com/")
    print()
    
    analyzer.print_analysis()

if __name__ == "__main__":
    main()