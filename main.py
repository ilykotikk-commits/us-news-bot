import feedparser
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "parse_mode": "HTML",
        "text": text[:3900]
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"Telegram status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Успешно отправлено в Telegram")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def clean(text):
    if not text:
        return ""
    return text.replace("<b>", "").replace("</b>", "").replace("&nbsp;", " ").strip()

def main():
    print(f"[{datetime.now().strftime('%H:%M')}] Запуск парсера...")

    message = f"<b>🇺🇸 Топ новости США — выжимки</b>\n"
    message += f"<i>{datetime.now().strftime('%d %B %H:%M')}</i>\n\n"

    categories = ["U.S. news", "Politics", "Business", "Technology"]

    for cat in categories:
        encoded = requests.utils.quote(cat)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)

        message += f"<b>→ {cat}</b>\n\n"

        count = 0
        for entry in feed.entries[:3]:   # 3 новости на категорию
            if not entry.title:
                continue

            title = clean(entry.title)
            summary = clean(getattr(entry, 'description', ''))

            # Если description пустой или очень короткий — используем заголовок
            if len(summary) < 50:
                summary = "Важная новость, требующая внимания."

            message += f"<b>{title}</b>\n{summary}\n\n"
            count += 1
            if count >= 3:
                break

    send_to_telegram(message)
    print("Скрипт завершён.")

if __name__ == "__main__":
    main()
