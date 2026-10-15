# Бот: раз в N часов собирает новости, делает сводку и постит в канал
#   python main.py        - запуск по расписанию
#   python main.py --dry  - один прогон, сводка печатается в консоль, в канал не постится
import asyncio
import os
import sys
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

import config
import db
from sources import collect
from summarizer import summarize

load_dotenv()


async def make_digest(bot=None):
    """Один цикл: собрать -> отфильтровать -> сводка -> пост."""
    print(f"\n=== Сводка {datetime.now():%d.%m %H:%M} ===")
    # Сбор и нейронка работают синхронно, выносим в поток, чтобы не блокировать бота
    items = await asyncio.to_thread(collect)
    items = db.filter_new(items)
    if not items:
        print("Новых новостей нет, пропускаем")
        return

    text = await asyncio.to_thread(summarize, items)

    if bot is None:  # режим --dry
        print(text)
        return

    try:
        await bot.send_message(os.getenv("CHANNEL_ID"), text, parse_mode="HTML",
                               disable_web_page_preview=True)
    except TelegramBadRequest:
        # Нейронка могла сломать HTML-разметку, шлём простым текстом
        await bot.send_message(os.getenv("CHANNEL_ID"), text, disable_web_page_preview=True)
    db.mark_sent(items)
    print(f"Опубликовано, новостей в сводке: {len(items)}")


async def main():
    db.init_db()

    if "--dry" in sys.argv:
        await make_digest()
        return

    bot = Bot(os.getenv("BOT_TOKEN"))
    scheduler = AsyncIOScheduler()
    # next_run_time=now: первая сводка сразу при запуске, дальше по интервалу
    scheduler.add_job(make_digest, "interval", hours=config.DIGEST_INTERVAL_HOURS,
                      args=[bot], next_run_time=datetime.now())
    scheduler.start()
    print(f"Бот запущен, сводка каждые {config.DIGEST_INTERVAL_HOURS} ч. Ctrl+C для остановки")
    await asyncio.Event().wait()  # просто держим программу живой


if __name__ == "__main__":
    asyncio.run(main())
