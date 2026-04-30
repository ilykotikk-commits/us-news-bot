import feedparser
import requests
import os
from datetime import datetime

try:
    from newspaper import Article
    from newspaper import Config
    NEWSPAPER_OK = True
except:
    NEWSPAPER_OK = False

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
            print("✅ Успешно отправлено!")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def get_summary(url):
    if not NEWSPAPER_OK:
        return "Не удалось извлечь текст статьи."
    try:
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0'
        config.request_timeout = 10
        
        article = Article(url, config=config)
        article.download()
        article.parse()
        article.nlp()
        
        summary = article.summary.strip()
        if len(summary) > 420:   # оптимально для 30 сек видео
            summary = summary[:417] + "..."
        return summary if summary else "Короткая новость без детального саммари."
    except:
        return "Не удалось загрузить полную статью."

def main():
    print(f"[{datetime.now().strftime('%H:%M')}] Запуск парсера выжимок...")

    message = f"<b>🇺🇸 Топ новости США — выжимки для видео</b>\n"
    message += f"<i>{datetime.now().strftime('%d %B %H:%M')}</i>\n\n"

    categories = ["U.S. news", "Politics", "Business", "Technology", "World news"]

    for cat in categories:
        encoded = requests.utils.quote(cat)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        count = 0

        message += f"<b>→ {cat}</b>\n\n"

        for entry in feed.entries[:3]:          # по 3 новости на категорию
            if not entry.title or len(entry.title) < 15:
                continue
                
            title = entry.title[:130]
            summary = get_summary(entry.link)
            
            message += f"<b>{title}</b>\n"
            message += f"{summary}\n\n"
            
            count += 1
            if count >= 3:
                break

    send_to_telegram(message)
    print("Скрипт завершён.")

if __name__ == "__main__":
    main()
