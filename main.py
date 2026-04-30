import feedparser
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    if len(text.strip()) < 100:
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
            print("✅ Сообщение успешно отправлено!")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def clean_text(text):
    if not text:
        return ""
    return text.replace('<b>', '').replace('</b>', '').replace('&nbsp;', ' ').strip()

def main():
    print(f"[{datetime.now().strftime('%H:%M')}] Запуск парсера выжимок...")

    message = f"<b>🇺🇸 Топ новости США — короткие выжимки</b>\n"
    message += f"<i>{datetime.now().strftime('%d %B %H:%M')}</i>\n\n"

    categories = ["U.S. news", "Politics", "Business", "Technology", "World news"]

    for cat in categories:
        encoded = requests.utils.quote(cat)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        count = 0

        message += f"<b>→ {cat}</b>\n\n"

        for entry in feed.entries[:3]:   # 3 новости на категорию
            if not entry.title or len(entry.title) < 15:
                continue

            title = clean_text(entry.title)
            summary = ""

            # Берём description — часто там уже есть хорошая выжимка
            if hasattr(entry, 'description') and entry.description:
                summary = clean_text(entry.description)
                # Обрезаем до удобной длины для видео (примерно 300-400 символов)
                if len(summary) > 420:
                    summary = summary[:417] + "..."

            if not summary or len(summary) < 30:
                summary = "Важная новость дня."

            message += f"<b>{title}</b>\n"
            message += f"{summary}\n\n"

            count += 1
            if count >= 3:
                break

    send_to_telegram(message)
    print("Скрипт завершён.")

if __name__ == "__main__":
    main()
