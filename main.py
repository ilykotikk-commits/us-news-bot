import feedparser
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    if not text or len(text.strip()) < 10:
        print("❌ Пропускаем отправку — сообщение слишком короткое или пустое")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
        "text": text[:3900]
    }
    
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"Telegram status: {r.status_code}")
        if r.status_code != 200:
            print(f"Ошибка Telegram: {r.text}")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Запуск парсера...")

    message = f"<b>🇺🇸 Новости США</b>\n<i>{datetime.now().strftime('%d %B %H:%M')}</i>\n\n"

    categories = ["U.S.", "Politics", "Business", "Technology", "World"]

    total_articles = 0

    for category in categories:
        encoded = requests.utils.quote(category)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        
        print(f"Загружаем: {category} → {rss_url}")
        
        feed = feedparser.parse(rss_url)
        print(f"Найдено записей: {len(feed.entries)}")

        articles = []
        for entry in feed.entries[:6]:
            if entry.title and len(entry.title) > 15:
                title = entry.title[:115] + "..." if len(entry.title) > 115 else entry.title
                articles.append(f"• <a href='{entry.link}'>{title}</a>")
                total_articles += 1

        if articles:
            message += f"<b>{category}</b>\n" + "\n".join(articles) + "\n\n"

    print(f"Всего собрано статей: {total_articles}")

    if total_articles == 0:
        message += "Пока новостей мало. Попробуем позже.\n"

    send_to_telegram(message)
    print("Скрипт завершён.")

if __name__ == "__main__":
    main()
