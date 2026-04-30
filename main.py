import feedparser
import requests
from datetime import datetime
import os

# Для выжимки статей
try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    print("newspaper3k не установлен. Будем использовать только заголовки.")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    if len(text.strip()) < 30:
        print("Сообщение слишком короткое")
        return
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
            print("✅ Сообщение отправлено!")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def get_summary(url):
    """Делает короткую выжимку статьи"""
    if not NEWSPAPER_AVAILABLE:
        return "Нет возможности сделать summary (библиотека не установлена)"
    try:
        article = Article(url, language='en')
        article.download()
        article.parse()
        article.nlp()
        summary = article.summary.strip()
        # Обрезаем до разумной длины для видео
        if len(summary) > 380:
            summary = summary[:377] + "..."
        return summary if summary else "Не удалось извлечь summary."
    except:
        return "Не удалось загрузить статью."

def main():
    print(f"[{datetime.now().strftime('%H:%M')}] Запуск парсера выжимок...")

    message = f"<b>🇺🇸 Топ новости США — выжимки</b>\n"
    message += f"<i>{datetime.now().strftime('%d %B %H:%M')}</i>\n\n"

    categories = ["U.S. news", "Politics", "Business", "Technology", "World news"]

    for cat in categories:
        encoded = requests.utils.quote(cat)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        articles_found = 0

        message += f"<b>{cat}</b>\n"

        for entry in feed.entries[:3]:   # по 3 самые свежие на категорию
            if not entry.title or len(entry.title) < 20:
                continue
                
            title = entry.title[:140]
            summary = get_summary(entry.link)
            
            message += f"• <b>{title}</b>\n"
            message += f"{summary}\n\n"
            
            articles_found += 1
            if articles_found >= 3:
                break

        if articles_found == 0:
            message += "Нет данных\n\n"

    send_to_telegram(message)
    print("Скрипт завершён.")

if __name__ == "__main__":
    main()
