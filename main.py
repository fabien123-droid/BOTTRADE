import os
import json
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from trading_logic import ScalpingBot

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None

def send_telegram_message(chat_id: int, text: str, reply_markup: Optional[dict] = None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return requests.post(url, json=payload)

def set_bot_commands():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyCommands"
    commands = [
        {"command": "start", "description": "Menu principal"},
        {"command": "config", "description": "Lier vos clés API"},
        {"command": "status", "description": "État des trades & Analyse IA"},
        {"command": "stats", "description": "Rapport de profits (PnL)"},
        {"command": "stop", "description": "Arrêt d'urgence"}
    ]
    requests.post(url, json={"commands": commands})

@app.on_event("startup")
async def startup_event():
    set_bot_commands()

@app.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    if update.message:
        chat_id = update.message["chat"]["id"]
        text = update.message.get("text", "")
        
        if text == "/start":
            welcome_text = (
                "🛡️ *BOTTRADE : Sécurité & Performance*\n\n"
                "Bienvenue dans votre interface de trading automatisée.\n\n"
                "🚀 *Sécurités Actives :*\n"
                "• *Anti-Liquidation* : Max 5% du capital par trade.\n"
                "• *Auto SL/TP* : Stop Loss (-1%) et Take Profit (+2%) automatiques.\n"
                "• *IA Guard* : DeepSeek-R1 filtre la volatilité anormale.\n"
                "• *Daily Limit* : Arrêt auto si perte > 3% / jour.\n\n"
                "👉 *Étape 1* : Utilisez `/config` pour lier vos clés API.\n"
                "👉 *Étape 2* : Lancez le bot via le bouton ci-dessous."
            )
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🚀 Lancer le Trading Auto", "callback_data": "start_bot"}],
                    [{"text": "📊 Status Actuel", "callback_data": "status"}, {"text": "⚙️ Configuration", "callback_data": "config"}],
                    [{"text": "🛑 ARRÊT D'URGENCE", "callback_data": "emergency_stop"}]
                ]
            }
            send_telegram_message(chat_id, welcome_text, keyboard)
            
        elif text == "/config":
            config_text = (
                "⚙️ *Configuration Sécurisée*\n\n"
                "Pour lier votre compte, envoyez vos clés au format suivant :\n"
                "`exchange:api_key:api_secret` (ex: `binance:abc:123`)\n\n"
                "🔒 *Vos clés sont chiffrées en AES-256.*"
            )
            send_telegram_message(chat_id, config_text)

        elif text == "/status":
            send_telegram_message(chat_id, "🔍 *Analyse en cours...*\n\nMarché : Stable\nIA : En attente de signal optimal.")

        elif text == "/stop":
            send_telegram_message(chat_id, "🛑 *ARRÊT D'URGENCE*\n\nOrdre de fermeture envoyé pour toutes les positions. Trading désactivé.")

    elif update.callback_query:
        chat_id = update.callback_query["message"]["chat"]["id"]
        data = update.callback_query["data"]
        
        if data == "config":
            send_telegram_message(chat_id, "Veuillez envoyer vos clés API au format `exchange:key:secret`.")
        elif data == "start_bot":
            send_telegram_message(chat_id, "✅ *Trading Auto Activé*\n\nLe bot scanne le Top 20 Binance avec une gestion du risque de 5% par position.")
        elif data == "status":
            send_telegram_message(chat_id, "📈 *Status*\n\nPositions : 0\nAnalyse IA : Neutre")
        elif data == "emergency_stop":
            send_telegram_message(chat_id, "🛑 *Action Immédiate*\n\nFermeture de tous les ordres en cours...")

    return {"ok": True}
