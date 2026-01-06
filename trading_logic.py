import ccxt
from groq import Groq
import os
import math
import time
import json

class ScalpingBot:
    def __init__(self, api_key=None, api_secret=None, exchange_id='binance'):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.exchange_id = exchange_id
        if api_key and api_secret:
            exchange_class = getattr(ccxt, exchange_id)
            self.exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        else:
            self.exchange = ccxt.binance()

    def get_top_volume_pairs(self, limit=20):
        try:
            tickers = self.exchange.fetch_tickers()
            sorted_tickers = sorted(
                [t for t in tickers.values() if t['quoteVolume'] and t['symbol'].endswith('/USDT')],
                key=lambda x: x['quoteVolume'],
                reverse=True
            )
            return [t['symbol'] for t in sorted_tickers[:limit]]
        except Exception:
            return ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

    def calculate_indicators(self, symbol):
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='5m', limit=50)
        closes = [x[4] for x in ohlcv]
        
        # RSI
        period = 14
        deltas = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss))) if avg_loss != 0 else 100

        # Bollinger Bands
        sma = sum(closes[-20:]) / 20
        variance = sum((x - sma) ** 2 for x in closes[-20:]) / 20
        stdev = math.sqrt(variance)
        
        return {
            "symbol": symbol,
            "price": closes[-1],
            "rsi": rsi,
            "bb_upper": sma + (2 * stdev),
            "bb_lower": sma - (2 * stdev),
            "bb_mid": sma
        }

    def get_ai_decision(self, data):
        prompt = f"""
        [SYSTEM: EXPERT SCALPER]
        Analyse {data['symbol']} à {data['price']} USDT.
        Indicateurs: RSI={data['rsi']:.2f}, BB_Upper={data['bb_upper']:.2f}, BB_Lower={data['bb_lower']:.2f}.
        
        Règles:
        1. Si RSI > 70 et prix proche BB_Upper -> SELL possible.
        2. Si RSI < 30 et prix proche BB_Lower -> BUY possible.
        3. Si volatilité extrême ou incertitude -> WAIT.
        
        Réponds UNIQUEMENT en JSON:
        {{"decision": "BUY" | "SELL" | "WAIT", "reason": "...", "confidence": 0-100}}
        """
        try:
            completion = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except:
            return {"decision": "WAIT", "reason": "Erreur IA"}

    def execute_trade(self, symbol, side, amount_usdt):
        # 1. Vérification du solde
        balance = self.exchange.fetch_balance()
        free_usdt = balance['free']['USDT']
        
        # 2. Calcul de la taille (Max 5% du capital)
        max_risk_amount = free_usdt * 0.05
        trade_amount = min(amount_usdt, max_risk_amount)
        
        if trade_amount < 10: # Minimum Binance
            return "Solde insuffisant pour respecter la gestion du risque."

        # 3. Exécution de l'ordre principal
        price = self.exchange.fetch_ticker(symbol)['last']
        amount = trade_amount / price
        
        order = self.exchange.create_order(symbol, 'market', side, amount)
        entry_price = order['price'] or price
        
        # 4. Placement simultané SL (-1%) et TP (+2%)
        sl_price = entry_price * 0.99 if side == 'buy' else entry_price * 1.01
        tp_price = entry_price * 1.02 if side == 'buy' else entry_price * 0.98
        
        self.exchange.create_order(symbol, 'limit', 'sell' if side == 'buy' else 'buy', amount, sl_price, {'stopPrice': sl_price})
        self.exchange.create_order(symbol, 'limit', 'sell' if side == 'buy' else 'buy', amount, tp_price)
        
        return f"Trade {side.upper()} exécuté sur {symbol}. Entrée: {entry_price}, SL: {sl_price}, TP: {tp_price}"
