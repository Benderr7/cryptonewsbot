# Сбор новостей из RSS-лент и открытых TG-каналов
import calendar
from datetime import datetime, timedelta, timezone

import feedparser
import requests
from bs4 import BeautifulSoup

import config

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 15  # секунд на один запрос


def clean_html(html):
    """Убирает HTML-теги, оставляет чистый текст."""
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


def fetch_rss(name, url):
    """Читает одну RSS-ленту, возвращает список новостей."""
    # Качаем через requests с User-Agent, иначе некоторые сайты отдают 403
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    feed = feedparser.parse(resp.content)

    items = []
    for entry in feed.entries:
        parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        if not parsed:
            continue
        # published_parsed идёт в UTC, переводим в datetime
        published = datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)
        items.append({
            "source": name,
            "title": entry.get("title", ""),
            "text": clean_html(entry.get("summary", ""))[:500],
            "url": entry.get("link", ""),
            "published": published,
        })
    return items


def fetch_tg_channel(username):
    """Читает последние посты канала через веб-превью t.me/s/<username>."""
    resp = requests.get(f"https://t.me/s/{username}", headers=HEADERS, timeout=TIMEOUT)
    soup = BeautifulSoup(resp.text, "html.parser")

    items = []
    for msg in soup.select(".tgme_widget_message"):
        text_tag = msg.select_one(".tgme_widget_message_text")
        time_tag = msg.select_one("time[datetime]")
        if not text_tag or not time_tag:
            continue  # пост без текста (только картинка/видео) пропускаем

        text = text_tag.get_text(" ", strip=True)
        items.append({
            "source": f"@{username}",
            "title": text[:100],  # у постов нет заголовка, берём начало текста
            "text": text[:500],
            "url": f"https://t.me/{msg['data-post']}",  # data-post = "канал/номер"
            "published": datetime.fromisoformat(time_tag["datetime"]),
        })
    return items


def collect(hours=config.DIGEST_INTERVAL_HOURS):
    """Собирает новости со всех источников за последние `hours` часов."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    all_items = []

    jobs = [(name, fetch_rss, (name, url)) for name, url in config.RSS_FEEDS.items()]
    jobs += [(f"@{ch}", fetch_tg_channel, (ch,)) for ch in config.TG_CHANNELS]

    for name, func, args in jobs:
        try:
            items = func(*args)
        except Exception as e:
            # Один упавший источник не должен ломать всю сводку
            print(f"[!] {name}: ошибка {e}")
            continue
        fresh = [it for it in items if it["published"] >= since]
        print(f"[ok] {name}: всего {len(items)}, свежих {len(fresh)}")
        all_items += fresh

    all_items.sort(key=lambda it: it["published"], reverse=True)
    return all_items


if __name__ == "__main__":
    # Ручная проверка: печатаем новости за последние 2 часа
    news = collect()
    print(f"\nИтого свежих новостей: {len(news)}\n")
    for it in news:
        print(f"{it['published']:%H:%M} | {it['source']} | {it['title']}\n    {it['url']}")
