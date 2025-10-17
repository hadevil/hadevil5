"""
Arquivo principal para executar o Long&Short Bot
"""
import asyncio
import argparse
import logging
import sys
from long_short_bot import LongShortBot
from dashboard import app
import threading

def setup_logging(level=logging.INFO):
    """Configura logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('long_short_bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_dashboard():
    """Executa dashboard em thread separada"""
    app.run_server(debug=False, host="0.0.0.0", port=8050)

async def run_bot_only():
    """Executa apenas o bot"""
    bot = LongShortBot()
    await bot.start()

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Long&Short Bot')
    parser.add_argument('--mode', choices=['bot', 'dashboard', 'both'], 
                       default='both', help='Modo de execução')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Nível de log')
    
    args = parser.parse_args()
    
    # Configurar logging
    log_level = getattr(logging, args.log_level.upper())
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Iniciando em modo: {args.mode}")
    
    try:
        if args.mode == 'bot':
            # Executar apenas o bot
            asyncio.run(run_bot_only())
            
        elif args.mode == 'dashboard':
            # Executar apenas o dashboard
            logger.info("Iniciando dashboard em http://localhost:8050")
            run_dashboard()
            
        elif args.mode == 'both':
            # Executar bot e dashboard
            logger.info("Iniciando bot e dashboard...")
            logger.info("Dashboard disponível em http://localhost:8050")
            
            # Iniciar dashboard em thread separada
            dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
            dashboard_thread.start()
            
            # Executar bot
            asyncio.run(run_bot_only())
    
    except KeyboardInterrupt:
        logger.info("Interrupção recebida, finalizando...")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()