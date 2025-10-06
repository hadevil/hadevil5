"""
Script de teste para verificar se o bot está funcionando corretamente
"""

import asyncio
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Testa se todas as importações estão funcionando"""
    logger.info("🧪 Testando importações...")
    
    try:
        import requests
        logger.info("✅ requests")
    except ImportError as e:
        logger.error(f"❌ requests: {e}")
        return False
    
    try:
        import numpy as np
        logger.info("✅ numpy")
    except ImportError as e:
        logger.error(f"❌ numpy: {e}")
        return False
    
    try:
        import pandas as pd
        logger.info("✅ pandas")
    except ImportError as e:
        logger.error(f"❌ pandas: {e}")
        return False
    
    try:
        import aiohttp
        logger.info("✅ aiohttp")
    except ImportError as e:
        logger.error(f"❌ aiohttp: {e}")
        return False
    
    try:
        import websockets
        logger.info("✅ websockets")
    except ImportError as e:
        logger.error(f"❌ websockets: {e}")
        return False
    
    return True

def test_config():
    """Testa se as configurações estão corretas"""
    logger.info("🔧 Testando configurações...")
    
    try:
        from config import get_config, validate_config
        config = get_config()
        
        # Verificar se todas as seções estão presentes
        required_sections = ['api', 'trading', 'market_making', 'strategy', 'monitoring', 'security']
        for section in required_sections:
            if section not in config:
                logger.error(f"❌ Seção de configuração ausente: {section}")
                return False
            logger.info(f"✅ {section}")
        
        # Testar validação (deve falhar sem chaves reais)
        if validate_config():
            logger.warning("⚠️ Validação passou sem chaves reais - verifique se as chaves estão configuradas")
        else:
            logger.info("✅ Validação falhou corretamente (chaves não configuradas)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nas configurações: {e}")
        return False

def test_strategy():
    """Testa a estratégia de market making"""
    logger.info("🧠 Testando estratégia...")
    
    try:
        from market_making_strategy import AdaptiveMarketMakingStrategy, MarketData
        from datetime import datetime
        
        strategy = AdaptiveMarketMakingStrategy()
        
        # Testar com dados de exemplo
        market_data = MarketData(
            price=100.0,
            volume=1000.0,
            volatility=0.02,
            trend=0.001,
            timestamp=datetime.now()
        )
        
        strategy.update_market_data(market_data)
        
        # Testar cálculo de spread
        bid_price, ask_price = strategy.calculate_adaptive_spread(100.0)
        
        if bid_price > 0 and ask_price > 0 and ask_price > bid_price:
            logger.info(f"✅ Spread calculado: bid=${bid_price:.4f}, ask=${ask_price:.4f}")
        else:
            logger.error(f"❌ Spread inválido: bid=${bid_price:.4f}, ask=${ask_price:.4f}")
            return False
        
        # Testar cálculo de tamanho de ordem
        bid_size, ask_size = strategy.calculate_order_sizes(100.0, 5000.0)
        
        if bid_size > 0 and ask_size > 0:
            logger.info(f"✅ Tamanhos de ordem: bid={bid_size:.4f}, ask={ask_size:.4f}")
        else:
            logger.error(f"❌ Tamanhos de ordem inválidos: bid={bid_size:.4f}, ask={ask_size:.4f}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na estratégia: {e}")
        return False

def test_risk_manager():
    """Testa o gerenciador de risco"""
    logger.info("⚠️ Testando gerenciador de risco...")
    
    try:
        from risk_manager import RiskManager
        
        risk_manager = RiskManager()
        
        # Testar métricas iniciais
        metrics = risk_manager.get_risk_metrics()
        
        if metrics.current_pnl == 0.0 and metrics.daily_pnl == 0.0:
            logger.info("✅ Métricas iniciais corretas")
        else:
            logger.error(f"❌ Métricas iniciais incorretas: {metrics}")
            return False
        
        # Testar atualização de trade
        trade_data = {
            'pnl': 10.0,
            'volume': 1000.0,
            'price': 100.0,
            'quantity': 10.0
        }
        
        risk_manager.update_trade(trade_data)
        
        updated_metrics = risk_manager.get_risk_metrics()
        
        if updated_metrics.current_pnl == 10.0 and updated_metrics.daily_pnl == 10.0:
            logger.info("✅ Atualização de trade funcionando")
        else:
            logger.error(f"❌ Atualização de trade falhou: {updated_metrics}")
            return False
        
        # Testar circuit breaker
        if not risk_manager.should_stop_trading():
            logger.info("✅ Circuit breaker inativo corretamente")
        else:
            logger.error("❌ Circuit breaker ativo incorretamente")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no gerenciador de risco: {e}")
        return False

def test_paradex_client():
    """Testa o cliente da Paradex (sem conexão real)"""
    logger.info("🔌 Testando cliente Paradex...")
    
    try:
        from paradex_client import ParadexClient
        
        # Testar inicialização
        client = ParadexClient()
        
        if client.api_key == "" and client.secret_key == "":
            logger.info("✅ Cliente inicializado corretamente (sem chaves)")
        else:
            logger.warning("⚠️ Cliente com chaves configuradas")
        
        # Testar geração de headers (sem chaves reais)
        try:
            headers = client._get_headers('GET', '/test', '')
            logger.info("✅ Geração de headers funcionando")
        except Exception as e:
            logger.warning(f"⚠️ Geração de headers falhou (esperado sem chaves): {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no cliente Paradex: {e}")
        return False

async def test_async_components():
    """Testa componentes assíncronos"""
    logger.info("🔄 Testando componentes assíncronos...")
    
    try:
        # Testar se as funções assíncronas podem ser chamadas
        from market_maker_bot import MarketMakerBot
        
        bot = MarketMakerBot()
        
        if bot.symbol == "SOL-USD":
            logger.info("✅ Bot inicializado corretamente")
        else:
            logger.error(f"❌ Símbolo incorreto: {bot.symbol}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nos componentes assíncronos: {e}")
        return False

def main():
    """Função principal de teste"""
    logger.info("🚀 Iniciando testes do Market Maker Bot")
    logger.info("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Configurações", test_config),
        ("Estratégia", test_strategy),
        ("Gerenciador de Risco", test_risk_manager),
        ("Cliente Paradex", test_paradex_client),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Executando: {test_name}")
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASSOU")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FALHOU")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERRO - {e}")
    
    # Teste assíncrono
    logger.info(f"\n🧪 Executando: Componentes Assíncronos")
    try:
        if asyncio.run(test_async_components()):
            logger.info(f"✅ Componentes Assíncronos: PASSOU")
            passed += 1
        else:
            logger.error(f"❌ Componentes Assíncronos: FALHOU")
    except Exception as e:
        logger.error(f"❌ Componentes Assíncronos: ERRO - {e}")
    
    total += 1
    
    # Resultado final
    logger.info("\n" + "=" * 50)
    logger.info(f"📊 RESULTADO DOS TESTES: {passed}/{total} passaram")
    
    if passed == total:
        logger.info("🎉 TODOS OS TESTES PASSARAM! O bot está pronto para uso.")
        return True
    else:
        logger.error(f"❌ {total - passed} teste(s) falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)