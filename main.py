import feedparser
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram данные не найдены")
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
        if r.status_code == 200:
            print("✅ Сообщение успешно отправлено в Telegram")
        else:
            print(f"❌ Telegram error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

def main():
    print(f"[{datetime.now().strftime('%H:%M')}] Запуск US News Bot")

    message = f"<b>🇺🇸 Свежие новости США</b>\n"
    message += f"<i>{datetime.now().strftime('%d %B %H:%M')}</i>\n\n"

    # Основные категории для американской аудитории
    categories = [
        "U.S. news",
        "Politics",
        "World news", 
        "Business",
        "Technology",
        "Entertainment"
    ]

    for i, category in enumerate(categories, 1):
        encoded = requests.utils.quote(category)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        articles = []
        
        for entry in feed.entries[:5]:   # по 5 новостей на категорию
            title = entry.title[:120]
            if len(entry.title) > 120:
                title += "..."
            articles.append(f"• <a href='{entry.link}'>{title}</a>")
        
        if articles:
            message += f"<b>{i}. {category}</b>\n" + "\n".join(articles) + "\n\n"

    send_to_telegram(message)
    print("Работа завершена.")

if __name__ == "__main__":
    main()
