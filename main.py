import feedparser
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    print("=== DEBUG TELEGRAM ===")
    print(f"Token length: {len(TELEGRAM_TOKEN) if TELEGRAM_TOKEN else 0}")
    print(f"Chat ID raw: '{TELEGRAM_CHAT_ID}' (type: {type(TELEGRAM_CHAT_ID)})")
    
    if not TELEGRAM_TOKEN:
        print("❌ TOKEN отсутствует!")
        return
    if not TELEGRAM_CHAT_ID:
        print("❌ CHAT_ID отсутствует или пустой!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "parse_mode": "HTML",
        "text": text.strip()[:3900]
    }
    
    print(f"Отправляем текст длиной: {len(payload['text'])} символов")
    
    try:
        r = requests.post(url, json=payload, timeout=20)
        print(f"Status Code: {r.status_code}")
        print(f"Ответ Telegram: {r.text}")
    except Exception as e:
        print(f"Исключение: {e}")

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] === ЗАПУСК ТЕСТА ===")
    
    test_message = f"<b>🔥 Тест от {datetime.now().strftime('%d.%m %H:%M')}</b>\n\n"
    test_message += "Это тестовое сообщение.\n"
    test_message += "Если ты его видишь — бот работает корректно."

    send_to_telegram(test_message)
    print("=== СКРИПТ ЗАВЕРШЁН ===")

if __name__ == "__main__":
    main()
