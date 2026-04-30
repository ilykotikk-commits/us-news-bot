import feedparser
import requests
import os
from datetime import datetime

# ================== НАСТРОЙКИ ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram не настроен")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
        "text": text[:3900]  # ограничение Telegram
    }
    
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"Telegram status: {r.status_code}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

# Популярные категории новостей США
CATEGORIES = [
    "Top stories",
    "World news",
    "U.S. news",
    "Politics",
    "Technology",
    "Business",
    "Entertainment"
]

def get_google_news(category="Top stories", num=6):
    query = requests.utils.quote(category)
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    articles = []
    for entry in feed.entries[:num]:
        title = entry.title[:110] + "..." if len(entry.title) > 110 else entry.title
        articles.append(f"• <a href='{entry.link}'>{title}</a>")
    return articles

# Главная функция
def main():
    print(f"[{datetime.now().strftime('%H:%M')}] Запуск US News Bot...")

    message = f"<b>🔥 Свежие новости США</b>\n"
    message += f"<i>{datetime.now().strftime('%d %B %H:%M')}</i>\n\n"

    for i, cat in enumerate(CATEGORIES, 1):
        news = get_google_news(cat, num=4)
        message += f"<b>{i}. {cat}</b>\n"
        message += "\n".join(news) + "\n\n"

    send_to_telegram(message)
    print("✅ Сообщение отправлено (или попытка сделана)")

if __name__ == "__main__":
    main()
