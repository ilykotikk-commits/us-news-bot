import feedparser
import requests
import os
from datetime import datetime
import html

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    if not text or len(text.strip()) < 20:
        print("❌ Сообщение слишком короткое, пропускаем")
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
            print(f"Ошибка Telegram: {r.text[:500]}")
        else:
            print("✅ Сообщение успешно отправлено!")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def escape_html(text):
    """Экранируем специальные HTML символы"""
    return html.escape(text) if text else ""

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск парсера новостей США...")

    message = f"<b>🇺🇸 Новости США</b>\n"
    message += f"<i>{datetime.now().strftime('%d %B %H:%M')}</i>\n\n"

    categories = ["U.S.", "Politics", "Business", "Technology", "World"]

    total = 0

    for cat in categories:
        encoded = requests.utils.quote(cat)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        articles = []

        for entry in feed.entries[:5]:
            if entry.title and len(entry.title) > 10:
                safe_title = escape_html(entry.title[:118])
                if len(entry.title) > 118:
                    safe_title += "..."
                
                article_line = f'• <a href="{entry.link}">{safe_title}</a>'
                articles.append(article_line)
                total += 1

        if articles:
            message += f"<b>{cat}</b>\n" + "\n".join(articles) + "\n\n"

    print(f"Всего собрано статей: {total}")

    send_to_telegram(message)
    print("Скрипт завершён.")

if __name__ == "__main__":
    main()
