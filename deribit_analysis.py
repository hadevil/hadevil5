#!/usr/bin/env python3
"""
Análise de opções da Deribit para queda de 40% no BTC/ETH
Vencimento: Junho 2026
"""

import requests
import json
from datetime import datetime
from typing import List, Dict

class DeribitAnalyzer:
    BASE_URL = "https://www.deribit.com/api/v2/public"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_instruments(self, currency: str, kind: str = "option") -> List[Dict]:
        """Busca instrumentos disponíveis para uma moeda"""
        url = f"{self.BASE_URL}/get_instruments"
        params = {
            "currency": currency,
            "kind": kind,
            "expired": "false"
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()["result"]
    
    def get_order_book(self, instrument_name: str) -> Dict:
        """Busca o order book de um instrumento"""
        url = f"{self.BASE_URL}/get_order_book"
        params = {"instrument_name": instrument_name}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()["result"]
    
    def get_index_price(self, currency: str) -> float:
        """Obtém o preço atual do índice"""
        url = f"{self.BASE_URL}/get_index_price"
        params = {"index_name": f"{currency.lower()}_usd"}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()["result"]["index_price"]
    
    def filter_june_2026_options(self, instruments: List[Dict]) -> List[Dict]:
        """Filtra opções com vencimento em junho de 2026"""
        june_2026_options = []
        
        for inst in instruments:
            # Nome do instrumento: BTC-28JUN26-50000-P (exemplo)
            if "26JUN26" in inst["instrument_name"] or "27JUN26" in inst["instrument_name"] or "25JUN26" in inst["instrument_name"]:
                june_2026_options.append(inst)
        
        return june_2026_options
    
    def analyze_put_options(self, currency: str, target_drop: float = 0.40):
        """Analisa opções de PUT para uma moeda específica"""
        print(f"\n{'='*80}")
        print(f"Analisando opções de PUT para {currency}")
        print(f"{'='*80}")
        
        # Obtém preço atual
        current_price = self.get_index_price(currency)
        target_price = current_price * (1 - target_drop)
        
        print(f"Preço atual: ${current_price:,.2f}")
        print(f"Preço alvo (queda de {target_drop*100}%): ${target_price:,.2f}")
        
        # Busca instrumentos
        instruments = self.get_instruments(currency, "option")
        june_2026_puts = [
            inst for inst in instruments 
            if "JUN26" in inst["instrument_name"] and inst["option_type"] == "put"
        ]
        
        print(f"\nTotal de opções PUT encontradas para Jun/2026: {len(june_2026_puts)}")
        
        # Analisa cada opção
        options_analysis = []
        
        for inst in june_2026_puts:
            try:
                instrument_name = inst["instrument_name"]
                strike = inst["strike"]
                
                # Busca preço da opção
                order_book = self.get_order_book(instrument_name)
                
                # Usa o preço ask (preço de compra)
                if order_book.get("best_ask_price"):
                    option_price = order_book["best_ask_price"]
                elif order_book.get("mark_price"):
                    option_price = order_book["mark_price"]
                else:
                    continue
                
                # Calcula payoff no vencimento com queda de 40%
                intrinsic_value = max(0, strike - target_price)
                
                # ROI se o preço cair 40%
                if option_price > 0:
                    roi = ((intrinsic_value - option_price) / option_price) * 100
                    profit = intrinsic_value - option_price
                    
                    options_analysis.append({
                        "instrument": instrument_name,
                        "strike": strike,
                        "current_option_price": option_price,
                        "intrinsic_value_at_target": intrinsic_value,
                        "profit": profit,
                        "roi_percent": roi,
                        "mark_iv": order_book.get("mark_iv", 0),
                        "bid": order_book.get("best_bid_price", 0),
                        "ask": order_book.get("best_ask_price", 0)
                    })
                    
            except Exception as e:
                continue
        
        # Ordena por ROI (maior para menor)
        options_analysis.sort(key=lambda x: x["roi_percent"], reverse=True)
        
        return {
            "currency": currency,
            "current_price": current_price,
            "target_price": target_price,
            "options": options_analysis
        }
    
    def print_top_options(self, analysis: Dict, top_n: int = 10):
        """Imprime as melhores opções"""
        currency = analysis["currency"]
        options = analysis["options"]
        
        print(f"\n{'='*120}")
        print(f"TOP {top_n} OPÇÕES DE PUT PARA {currency} - MAIOR ROI COM QUEDA DE 40%")
        print(f"{'='*120}")
        print(f"{'#':<4} {'Instrumento':<30} {'Strike':<12} {'Preço Opção':<15} {'Valor no Alvo':<15} {'Lucro':<12} {'ROI %':<10}")
        print(f"{'-'*120}")
        
        for i, opt in enumerate(options[:top_n], 1):
            print(f"{i:<4} {opt['instrument']:<30} ${opt['strike']:<11,.2f} "
                  f"${opt['current_option_price']:<14,.2f} ${opt['intrinsic_value_at_target']:<14,.2f} "
                  f"${opt['profit']:<11,.2f} {opt['roi_percent']:<10,.1f}")
        
        print(f"\n{'='*120}")
        
        # Melhor opção
        if options:
            best = options[0]
            print(f"\n🏆 MELHOR OPÇÃO PARA {currency}:")
            print(f"   Instrumento: {best['instrument']}")
            print(f"   Strike: ${best['strike']:,.2f}")
            print(f"   Preço atual da opção: ${best['current_option_price']:,.2f}")
            print(f"   Valor no vencimento (queda 40%): ${best['intrinsic_value_at_target']:,.2f}")
            print(f"   Lucro estimado: ${best['profit']:,.2f}")
            print(f"   ROI: {best['roi_percent']:.1f}%")

def main():
    analyzer = DeribitAnalyzer()
    
    print("\n" + "="*120)
    print(" "*30 + "ANÁLISE DE OPÇÕES DERIBIT - QUEDA DE 40%")
    print(" "*35 + "VENCIMENTO: JUNHO 2026")
    print("="*120)
    
    # Analisa BTC
    btc_analysis = analyzer.analyze_put_options("BTC", 0.40)
    analyzer.print_top_options(btc_analysis, top_n=15)
    
    # Analisa ETH
    eth_analysis = analyzer.analyze_put_options("ETH", 0.40)
    analyzer.print_top_options(eth_analysis, top_n=15)
    
    # Comparação final
    print("\n" + "="*120)
    print(" "*40 + "COMPARAÇÃO FINAL: BTC vs ETH")
    print("="*120)
    
    if btc_analysis["options"] and eth_analysis["options"]:
        best_btc = btc_analysis["options"][0]
        best_eth = eth_analysis["options"][0]
        
        print(f"\n📊 BITCOIN (BTC):")
        print(f"   Preço atual: ${btc_analysis['current_price']:,.2f}")
        print(f"   Preço com queda de 40%: ${btc_analysis['target_price']:,.2f}")
        print(f"   Melhor opção: {best_btc['instrument']}")
        print(f"   ROI máximo: {best_btc['roi_percent']:.1f}%")
        print(f"   Lucro por contrato: ${best_btc['profit']:,.2f}")
        
        print(f"\n📊 ETHEREUM (ETH):")
        print(f"   Preço atual: ${eth_analysis['current_price']:,.2f}")
        print(f"   Preço com queda de 40%: ${eth_analysis['target_price']:,.2f}")
        print(f"   Melhor opção: {best_eth['instrument']}")
        print(f"   ROI máximo: {best_eth['roi_percent']:.1f}%")
        print(f"   Lucro por contrato: ${best_eth['profit']:,.2f}")
        
        print(f"\n{'='*120}")
        if best_btc['roi_percent'] > best_eth['roi_percent']:
            diff = best_btc['roi_percent'] - best_eth['roi_percent']
            print(f"\n🎯 VENCEDOR: BITCOIN (BTC)")
            print(f"   ROI superior em {diff:.1f} pontos percentuais")
            print(f"   Recomendação: {best_btc['instrument']}")
        else:
            diff = best_eth['roi_percent'] - best_btc['roi_percent']
            print(f"\n🎯 VENCEDOR: ETHEREUM (ETH)")
            print(f"   ROI superior em {diff:.1f} pontos percentuais")
            print(f"   Recomendação: {best_eth['instrument']}")
        
        print(f"\n{'='*120}")
        print("\n⚠️  DISCLAIMER:")
        print("   Esta é uma análise baseada em preços atuais e não constitui recomendação de investimento.")
        print("   Opções envolvem riscos significativos. Consulte um profissional financeiro.")
        print(f"{'='*120}\n")

if __name__ == "__main__":
    main()
