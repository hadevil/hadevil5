#!/usr/bin/env python3
"""
Analisador de Opções Deribit para BTC e ETH
Calcula retornos potenciais para opções PUT com queda de 40% até junho 2026
"""

import math
from datetime import datetime, date
from typing import Dict, List, Tuple

class DeribitOptionsAnalyzer:
    def __init__(self):
        self.current_date = date.today()
        self.expiration_date = date(2026, 6, 30)  # Assumindo vencimento em 30/06/2026
        self.days_to_expiry = (self.expiration_date - self.current_date).days
        
    def calculate_put_payoff(self, strike_price: float, current_price: float, 
                           put_price: float, final_price: float) -> Dict:
        """
        Calcula o payoff de uma opção PUT
        
        Args:
            strike_price: Preço de exercício da opção
            current_price: Preço atual do ativo
            put_price: Preço pago pela opção
            final_price: Preço final do ativo (após queda de 40%)
        
        Returns:
            Dict com informações do payoff
        """
        # Preço final após queda de 40%
        final_price_40_drop = current_price * 0.6
        
        # Payoff da opção PUT = max(0, strike - final_price)
        intrinsic_value = max(0, strike_price - final_price_40_drop)
        
        # Lucro/Prejuízo = intrinsic_value - put_price
        profit_loss = intrinsic_value - put_price
        
        # Retorno percentual
        return_percentage = (profit_loss / put_price) * 100 if put_price > 0 else 0
        
        # ROI (Return on Investment)
        roi = profit_loss / put_price if put_price > 0 else 0
        
        return {
            'strike_price': strike_price,
            'current_price': current_price,
            'put_price': put_price,
            'final_price_40_drop': final_price_40_drop,
            'intrinsic_value': intrinsic_value,
            'profit_loss': profit_loss,
            'return_percentage': return_percentage,
            'roi': roi,
            'is_profitable': profit_loss > 0
        }
    
    def analyze_btc_options(self, current_btc_price: float = 100000) -> List[Dict]:
        """
        Analisa opções PUT de BTC com diferentes strikes
        Assumindo preço atual de BTC em $100,000
        """
        btc_scenarios = []
        
        # Diferentes strikes para análise (em USD)
        strikes = [80000, 70000, 60000, 50000, 40000, 30000]
        
        # Preços estimados das opções (baseado em volatilidade típica)
        # Estes são valores estimados - você deve verificar no site da Deribit
        estimated_put_prices = {
            80000: 5000,   # ATM
            70000: 3000,   # OTM
            60000: 1500,   # OTM
            50000: 800,    # OTM
            40000: 400,    # OTM
            30000: 200     # OTM
        }
        
        for strike in strikes:
            put_price = estimated_put_prices.get(strike, 1000)
            scenario = self.calculate_put_payoff(
                strike, current_btc_price, put_price, current_btc_price * 0.6
            )
            btc_scenarios.append(scenario)
        
        return btc_scenarios
    
    def analyze_eth_options(self, current_eth_price: float = 4000) -> List[Dict]:
        """
        Analisa opções PUT de ETH com diferentes strikes
        Assumindo preço atual de ETH em $4,000
        """
        eth_scenarios = []
        
        # Diferentes strikes para análise (em USD)
        strikes = [3200, 2800, 2400, 2000, 1600, 1200]
        
        # Preços estimados das opções (baseado em volatilidade típica)
        estimated_put_prices = {
            3200: 200,     # ATM
            2800: 120,     # OTM
            2400: 60,      # OTM
            2000: 30,      # OTM
            1600: 15,      # OTM
            1200: 8        # OTM
        }
        
        for strike in strikes:
            put_price = estimated_put_prices.get(strike, 50)
            scenario = self.calculate_put_payoff(
                strike, current_eth_price, put_price, current_eth_price * 0.6
            )
            eth_scenarios.append(scenario)
        
        return eth_scenarios
    
    def compare_btc_vs_eth(self, btc_price: float = 100000, eth_price: float = 4000) -> Dict:
        """
        Compara potencial de retorno entre BTC e ETH options
        """
        btc_scenarios = self.analyze_btc_options(btc_price)
        eth_scenarios = self.analyze_eth_options(eth_price)
        
        # Encontra o melhor retorno para cada
        best_btc = max(btc_scenarios, key=lambda x: x['return_percentage'])
        best_eth = max(eth_scenarios, key=lambda x: x['return_percentage'])
        
        return {
            'btc_analysis': {
                'best_scenario': best_btc,
                'all_scenarios': btc_scenarios
            },
            'eth_analysis': {
                'best_scenario': best_eth,
                'all_scenarios': eth_scenarios
            },
            'recommendation': self._get_recommendation(best_btc, best_eth)
        }
    
    def _get_recommendation(self, best_btc: Dict, best_eth: Dict) -> str:
        """
        Gera recomendação baseada na análise
        """
        if best_btc['return_percentage'] > best_eth['return_percentage']:
            return f"BTC oferece melhor retorno: {best_btc['return_percentage']:.1f}% vs {best_eth['return_percentage']:.1f}%"
        elif best_eth['return_percentage'] > best_btc['return_percentage']:
            return f"ETH oferece melhor retorno: {best_eth['return_percentage']:.1f}% vs {best_btc['return_percentage']:.1f}%"
        else:
            return "Ambos oferecem retornos similares"
    
    def print_analysis(self, btc_price: float = 100000, eth_price: float = 4000):
        """
        Imprime análise completa
        """
        print("=" * 80)
        print("ANÁLISE DE OPÇÕES DERIBIT - QUEDA DE 40% ATÉ JUNHO 2026")
        print("=" * 80)
        print(f"Data atual: {self.current_date}")
        print(f"Vencimento: {self.expiration_date}")
        print(f"Dias até vencimento: {self.days_to_expiry}")
        print()
        
        comparison = self.compare_btc_vs_eth(btc_price, eth_price)
        
        print("ANÁLISE BTC:")
        print("-" * 40)
        print(f"Preço atual BTC: ${btc_price:,.0f}")
        print(f"Preço após queda de 40%: ${btc_price * 0.6:,.0f}")
        print()
        
        for scenario in comparison['btc_analysis']['all_scenarios']:
            status = "✅ LUCRO" if scenario['is_profitable'] else "❌ PREJUÍZO"
            print(f"Strike ${scenario['strike_price']:,.0f} | "
                  f"Preço PUT: ${scenario['put_price']:,.0f} | "
                  f"Retorno: {scenario['return_percentage']:+.1f}% | "
                  f"{status}")
        
        print("\n" + "=" * 40)
        print("ANÁLISE ETH:")
        print("-" * 40)
        print(f"Preço atual ETH: ${eth_price:,.0f}")
        print(f"Preço após queda de 40%: ${eth_price * 0.6:,.0f}")
        print()
        
        for scenario in comparison['eth_analysis']['all_scenarios']:
            status = "✅ LUCRO" if scenario['is_profitable'] else "❌ PREJUÍZO"
            print(f"Strike ${scenario['strike_price']:,.0f} | "
                  f"Preço PUT: ${scenario['put_price']:,.0f} | "
                  f"Retorno: {scenario['return_percentage']:+.1f}% | "
                  f"{status}")
        
        print("\n" + "=" * 40)
        print("RECOMENDAÇÃO:")
        print("-" * 40)
        print(comparison['recommendation'])
        
        print("\n" + "=" * 40)
        print("MELHORES CENÁRIOS:")
        print("-" * 40)
        print(f"BTC - Strike ${comparison['btc_analysis']['best_scenario']['strike_price']:,.0f}: "
              f"{comparison['btc_analysis']['best_scenario']['return_percentage']:+.1f}%")
        print(f"ETH - Strike ${comparison['eth_analysis']['best_scenario']['strike_price']:,.0f}: "
              f"{comparison['eth_analysis']['best_scenario']['return_percentage']:+.1f}%")

def main():
    """
    Função principal para executar a análise
    """
    analyzer = DeribitOptionsAnalyzer()
    
    # Você pode ajustar estes preços conforme o mercado atual
    current_btc_price = 100000  # Ajuste conforme preço atual
    current_eth_price = 4000    # Ajuste conforme preço atual
    
    print("IMPORTANTE: Este é um exemplo com preços estimados.")
    print("Para análise precisa, verifique os preços reais no site da Deribit.")
    print("Acesse: https://www.deribit.com/")
    print()
    
    analyzer.print_analysis(current_btc_price, current_eth_price)
    
    print("\n" + "=" * 80)
    print("INSTRUÇÕES PARA ANÁLISE REAL:")
    print("=" * 80)
    print("1. Acesse https://www.deribit.com/")
    print("2. Vá para 'Options' > 'BTC' ou 'ETH'")
    print("3. Filtre por vencimento: Junho 2026")
    print("4. Procure por opções PUT (venda)")
    print("5. Anote os preços das opções com strikes próximos a:")
    print("   - BTC: $60,000, $50,000, $40,000")
    print("   - ETH: $2,400, $2,000, $1,600")
    print("6. Use este script com os preços reais para calcular retornos")
    print("7. Considere também: volatilidade, gregas, liquidez")

if __name__ == "__main__":
    main()