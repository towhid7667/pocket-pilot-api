import requests
from dotenv import load_dotenv
import os

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram_message(message : str):
    try:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": message,
            "parse_mode": "Markdown"
            }
        response = requests.post(TELEGRAM_API_URL, json=payload)
        response.raise_for_status()
        print("Telegram message sent successfully!")
    except Exception as error:
        print(f"A Telegram error occurred: {error}")    