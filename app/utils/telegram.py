import requests
from dotenv import load_dotenv
import os
import re

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram_message(message : str):
    try:
        message = escape_markdown(message)
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


def escape_markdown(text):
    """Helper function to escape Markdown special characters"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)        