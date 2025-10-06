"""
Cliente para API da Paradex
Implementa conexão REST e WebSocket para market making
"""

import asyncio
import json
import hmac
import hashlib
import time
import base64
from typing import Dict, List, Optional, Any
import aiohttp
import websockets
from datetime import datetime, timedelta
import logging

from config import API_CONFIG, SECURITY_CONFIG

class ParadexClient:
    def __init__(self):
        self.api_key = API_CONFIG['api_key']
        self.secret_key = API_CONFIG['secret_key']
        self.passphrase = API_CONFIG['passphrase']
        self.base_url = API_CONFIG['base_url']
        self.websocket_url = API_CONFIG['websocket_url']
        self.session = None
        self.websocket = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.websocket:
            await self.websocket.close()
    
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = '') -> str:
        """Gera assinatura HMAC para autenticação"""
        message = timestamp + method + path + body
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    def _get_headers(self, method: str, path: str, body: str = '') -> Dict[str, str]:
        """Gera headers de autenticação"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, path, body)
        
        return {
            'PARADEX-ACCESS-KEY': self.api_key,
            'PARADEX-ACCESS-SIGN': signature,
            'PARADEX-ACCESS-TIMESTAMP': timestamp,
            'PARADEX-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Faz requisição HTTP para a API"""
        url = f"{self.base_url}{endpoint}"
        body = json.dumps(data) if data else ''
        headers = self._get_headers(method, endpoint, body)
        
        try:
            async with self.session.request(
                method, url, headers=headers, data=body, 
                timeout=aiohttp.ClientTimeout(total=SECURITY_CONFIG['connection_timeout'])
            ) as response:
                result = await response.json()
                if response.status >= 400:
                    self.logger.error(f"API Error {response.status}: {result}")
                    raise Exception(f"API Error: {result}")
                return result
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            raise
    
    # Métodos da API REST
    
    async def get_account_balance(self) -> Dict:
        """Obtém saldo da conta"""
        return await self._make_request('GET', '/api/v1/account/balance')
    
    async def get_trading_fees(self) -> Dict:
        """Obtém taxas de trading"""
        return await self._make_request('GET', '/api/v1/trading/fees')
    
    async def get_market_data(self, symbol: str) -> Dict:
        """Obtém dados de mercado para um símbolo"""
        return await self._make_request('GET', f'/api/v1/market/ticker?symbol={symbol}')
    
    async def get_orderbook(self, symbol: str, depth: int = 20) -> Dict:
        """Obtém livro de ordens"""
        return await self._make_request('GET', f'/api/v1/market/orderbook?symbol={symbol}&depth={depth}')
    
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> Dict:
        """Obtém trades recentes"""
        return await self._make_request('GET', f'/api/v1/market/trades?symbol={symbol}&limit={limit}')
    
    async def get_klines(self, symbol: str, interval: str = '1m', limit: int = 100) -> Dict:
        """Obtém dados de candlestick"""
        return await self._make_request('GET', f'/api/v1/market/klines?symbol={symbol}&interval={interval}&limit={limit}')
    
    async def place_order(self, symbol: str, side: str, order_type: str, 
                         quantity: float, price: float = None, 
                         time_in_force: str = 'GTC') -> Dict:
        """Coloca uma ordem"""
        order_data = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': str(quantity),
            'timeInForce': time_in_force
        }
        
        if price:
            order_data['price'] = str(price)
        
        return await self._make_request('POST', '/api/v1/trading/orders', order_data)
    
    async def cancel_order(self, order_id: str) -> Dict:
        """Cancela uma ordem"""
        return await self._make_request('DELETE', f'/api/v1/trading/orders/{order_id}')
    
    async def get_open_orders(self, symbol: str = None) -> Dict:
        """Obtém ordens abertas"""
        endpoint = '/api/v1/trading/orders/open'
        if symbol:
            endpoint += f'?symbol={symbol}'
        return await self._make_request('GET', endpoint)
    
    async def get_order_history(self, symbol: str = None, limit: int = 100) -> Dict:
        """Obtém histórico de ordens"""
        endpoint = f'/api/v1/trading/orders/history?limit={limit}'
        if symbol:
            endpoint += f'&symbol={symbol}'
        return await self._make_request('GET', endpoint)
    
    async def get_positions(self) -> Dict:
        """Obtém posições abertas"""
        return await self._make_request('GET', '/api/v1/trading/positions')
    
    # Métodos WebSocket
    
    async def connect_websocket(self, callback):
        """Conecta ao WebSocket para dados em tempo real"""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            self.logger.info("WebSocket conectado com sucesso")
            
            # Subscribe para dados de mercado
            subscribe_msg = {
                "method": "subscribe",
                "params": {
                    "channels": ["ticker", "orderbook", "trades"]
                }
            }
            await self.websocket.send(json.dumps(subscribe_msg))
            
            # Loop de recebimento de mensagens
            async for message in self.websocket:
                data = json.loads(message)
                await callback(data)
                
        except Exception as e:
            self.logger.error(f"Erro no WebSocket: {e}")
            raise
    
    async def subscribe_to_ticker(self, symbol: str, callback):
        """Subscribe para dados de ticker específico"""
        subscribe_msg = {
            "method": "subscribe",
            "params": {
                "channels": [f"ticker.{symbol}"]
            }
        }
        await self.websocket.send(json.dumps(subscribe_msg))
    
    async def subscribe_to_orderbook(self, symbol: str, callback):
        """Subscribe para livro de ordens específico"""
        subscribe_msg = {
            "method": "subscribe",
            "params": {
                "channels": [f"orderbook.{symbol}"]
            }
        }
        await self.websocket.send(json.dumps(subscribe_msg))
    
    # Métodos utilitários
    
    async def get_current_price(self, symbol: str) -> float:
        """Obtém preço atual de um símbolo"""
        try:
            ticker = await self.get_market_data(symbol)
            return float(ticker['last'])
        except Exception as e:
            self.logger.error(f"Erro ao obter preço atual: {e}")
            return 0.0
    
    async def get_best_bid_ask(self, symbol: str) -> tuple:
        """Obtém melhor bid e ask"""
        try:
            orderbook = await self.get_orderbook(symbol, 1)
            best_bid = float(orderbook['bids'][0][0]) if orderbook['bids'] else 0.0
            best_ask = float(orderbook['asks'][0][0]) if orderbook['asks'] else 0.0
            return best_bid, best_ask
        except Exception as e:
            self.logger.error(f"Erro ao obter bid/ask: {e}")
            return 0.0, 0.0
    
    async def calculate_spread(self, symbol: str) -> float:
        """Calcula spread atual"""
        bid, ask = await self.get_best_bid_ask(symbol)
        if bid > 0 and ask > 0:
            return (ask - bid) / bid
        return 0.0