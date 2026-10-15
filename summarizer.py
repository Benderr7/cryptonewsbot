# Сводка новостей через нейронку (любой OpenAI-совместимый API: Gemini, Groq, DeepSeek...)
import os

from openai import OpenAI

MAX_ITEMS = 60  # больше новостей в один запрос не отправляем

PROMPT = """Ты редактор крипто-канала. Ниже новости за последние часы из разных источников.
Сделай сводку на русском:
- выбери 5-7 самых важных событий, одинаковые новости из разных источников объедини в одну;
- мусор (рекламу, розыгрыши, мелкие переводы китов) пропусти;
- каждый пункт: эмодзи, <b>суть в одной фразе</b>, ещё 1-2 предложения, ссылка на источник <a href="URL">источник</a>;
- в начале одна строка-заголовок, например: <b>Крипто-сводка</b>.
Форматирование только HTML-тегами <b>, <i>, <a>. Без Markdown, без других тегов.
Вся сводка не длиннее 3500 символов.

Новости:
{news}"""


def _providers():
    """Список нейронок из .env: основная и запасная (если указана)."""
    result = []
    for prefix in ("LLM", "FALLBACK"):
        key = os.getenv(f"{prefix}_API_KEY")
        if key:
            result.append((os.getenv(f"{prefix}_BASE_URL"), key, os.getenv(f"{prefix}_MODEL")))
    return result


def summarize(items):
    """Отдаёт новости нейронке, возвращает готовый текст поста."""
    news = "\n\n".join(
        f"[{it['source']}] {it['title']}\n{it['text'][:300]}\nURL: {it['url']}"
        for it in items[:MAX_ITEMS]
    )

    providers = _providers()
    if not providers:
        raise RuntimeError("В .env не указан ни один LLM_API_KEY")

    last_error = None
    for base_url, key, model in providers:
        try:
            client = OpenAI(base_url=base_url, api_key=key, timeout=120)
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": PROMPT.format(news=news)}],
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            # Основная нейронка упала или лимит кончился, пробуем запасную
            print(f"[!] {model}: {e}")
            last_error = e
    raise RuntimeError(f"Все нейронки недоступны: {last_error}")
