# crypto-digest

Telegram-бот, который раз в несколько часов собирает криптоновости, делает из них короткую сводку и постит в канал.

**Как работает:**
1. Забирает свежие новости из RSS (CoinDesk, Cointelegraph, Decrypt, The Block, ForkLog) и открытых TG-каналов (через веб-превью `t.me/s/...`).
2. Отбрасывает новости, которые уже были в прошлых сводках (SQLite).
3. Отдаёт всё нейронке (любой OpenAI-совместимый API, по умолчанию Gemini), она выбирает 5-7 главных событий и склеивает дубли.
4. Постит сводку в канал с HTML-разметкой и ссылками на источники.

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # и заполнить ключи
```

В `.env` нужны:
- `BOT_TOKEN` — токен от @BotFather, бота добавить админом в канал;
- `CHANNEL_ID` — `@username` канала или его числовой id;
- `LLM_API_KEY` — ключ Gemini (бесплатный, в Google AI Studio);
- `FALLBACK_*` — запасная нейронка, можно не заполнять.

```bash
python sources.py      # проверить сбор новостей
python main.py --dry   # сводка в консоль, в канал ничего не уходит
python main.py --once  # одна сводка в канал и выход
python main.py         # работа по расписанию
```

## Настройка

Всё в `config.py`: список RSS-лент, TG-каналов и интервал сводки (`DIGEST_INTERVAL_HOURS`).

## Стек

Python, aiogram 3, APScheduler, feedparser, BeautifulSoup, openai, SQLite.
