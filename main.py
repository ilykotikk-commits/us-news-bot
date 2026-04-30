import feedparser
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    if len(text.strip()) < 50:
        print("Сообщение слишком короткое")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "parse_mode": "HTML",
        "text": text[:3900]
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        print(f"Telegram status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Отправлено успешно!")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def main():
    print(f"[{datetime.now().strftime('%H:%M')}] Запуск парсера...")

    message = f"<b>🇺🇸 Топ новости США — короткие выжимки</b>\n"
    message += f"<i>{datetime.now().strftime('%d %B %H:%M')}</i>\n\n"

    # Берём самые популярные категории
    categories = ["U.S. news", "Politics", "Business", "Technology"]

    for cat in categories:
        encoded = requests.utils.quote(cat)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        count = 0

        message += f"<b>→ {cat}</b>\n\n"

        for entry in feed.entries[:4]:   # максимум 4 новости на категорию
            if not entry.title or len(entry.title) < 20:
                continue

            title = entry.title.strip()

            # Простая выжимка из заголовка + описание (description часто содержит саммари)
            summary = ""
            if hasattr(entry, 'description') and entry.description:
                # Берём первые 2-3 предложения из description
                desc = entry.description.replace('<b>', '').replace('</b>', '').strip()
                summary = desc[:380] + "..." if len(desc) > 380 else desc

            if not summary:
                summary = "Короткая новость без детального описания."

            message += f"<b>{title}</b>\n"
            message += f"{summary}\n\n"

            count += 1
            if count >= 3:        # берём только 3 новости на категорию
                break

    send_to_telegram(message)
    print("Скрипт завершён.")

if __name__ == "__main__":
    main()
