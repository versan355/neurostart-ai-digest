"""
НЕЙРОСТАРТ — AI-дайджест для новичков.

Запуск:
    python app.py

Дальше открыть в браузере: http://127.0.0.1:5000
"""

import re
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)

# Секретный ключ нужен, чтобы Flask мог показывать flash-сообщения
# (зелёная плашка «Готово!» после отправки формы).
app.secret_key = "neurostart-demo-key"

BASE_DIR = Path(__file__).resolve().parent
SUBSCRIBERS_FILE = BASE_DIR / "subscribers.txt"

ISSUE_DATE = "26 октября 2026"

# ---------------------------------------------------------------------------
# ФИЛЬТРЫ
# slug — техническое имя (используется в HTML и JavaScript),
# title — то, что видит человек.
# ---------------------------------------------------------------------------
CATEGORIES = [
    {"slug": "all", "title": "Все"},
    {"slug": "tools", "title": "Инструменты"},
    {"slug": "guides", "title": "Гайды"},
    {"slug": "courses", "title": "Курсы"},
]

# ---------------------------------------------------------------------------
# КАРТОЧКИ ДАЙДЖЕСТА
# Чтобы добавить новую карточку — скопируйте любой словарь ниже
# и поменяйте значения. Менять HTML и CSS не нужно.
# accent: lime | violet | cyan | pink (цвет подсветки карточки)
# ---------------------------------------------------------------------------
MATERIALS = [
    {
        "title": "ChatGPT: первый диалог",
        "description": "Самый простой вход в мир ИИ: чат, который пишет, объясняет и спорит. Начните со своей настоящей задачи — например, попросите переписать письмо короче.",
        "url": "https://chatgpt.com",
        "category": "tools",
        "category_title": "Инструмент",
        "duration": "10 минут",
        "level": "Новичок",
        "tags": ["чат", "тексты", "старт"],
        "accent": "lime",
    },
    {
        "title": "Claude: длинные тексты",
        "description": "Спокойный ассистент, который хорошо держит большой контекст. Удобен, когда нужно разобрать договор, конспект или статью на двадцать страниц.",
        "url": "https://claude.ai",
        "category": "tools",
        "category_title": "Инструмент",
        "duration": "12 минут",
        "level": "Новичок",
        "tags": ["документы", "анализ"],
        "accent": "pink",
    },
    {
        "title": "NotebookLM: ИИ по вашим файлам",
        "description": "Загрузите конспекты или PDF — и получите ответы строго по своим материалам, со ссылками на страницы. Лучший способ учиться, не доверяя ИИ на слово.",
        "url": "https://notebooklm.google.com",
        "category": "tools",
        "category_title": "Инструмент",
        "duration": "8 минут",
        "level": "Новичок",
        "tags": ["учёба", "PDF", "источники"],
        "accent": "cyan",
    },
    {
        "title": "Perplexity: поиск с источниками",
        "description": "Поисковик, который сам читает ссылки и показывает, откуда взял ответ. Хорошая замена обычному поиску, когда важны факты, а не красивые формулировки.",
        "url": "https://www.perplexity.ai",
        "category": "tools",
        "category_title": "Инструмент",
        "duration": "7 минут",
        "level": "Новичок",
        "tags": ["поиск", "факты"],
        "accent": "violet",
    },
    {
        "title": "Стратегии промптов от Google",
        "description": "Официальный гид: как ставить задачу, чтобы модель не угадывала. Примеры рабочих промптов и разбор типичных ошибок — без воды и мотивации.",
        "url": "https://ai.google.dev/gemini-api/docs/prompting-strategies",
        "category": "guides",
        "category_title": "Гайд",
        "duration": "15 минут",
        "level": "База",
        "tags": ["промпты", "практика"],
        "accent": "cyan",
    },
    {
        "title": "Prompt engineering от OpenAI",
        "description": "Короткая методичка: структура промпта, роли, примеры. Полезна, если хочется перейти от «напиши текст» к результатам, которые можно предсказать.",
        "url": "https://platform.openai.com/docs/guides/prompt-engineering",
        "category": "guides",
        "category_title": "Гайд",
        "duration": "20 минут",
        "level": "База",
        "tags": ["промпты", "OpenAI"],
        "accent": "lime",
    },
    {
        "title": "Elements of AI: основы бесплатно",
        "description": "Курс университета Хельсинки: что такое ИИ, где он помогает, а где вредит. Без кода и сложной математики — для тех, кто хочет понять, а не заучить.",
        "url": "https://www.elementsofai.com",
        "category": "courses",
        "category_title": "Курс",
        "duration": "6 часов",
        "level": "Новичок",
        "tags": ["основы", "бесплатно"],
        "accent": "violet",
    },
    {
        "title": "Hugging Face: курс по LLM",
        "description": "Пошаговый курс о больших языковых моделях: от токенов до собственных мини-проектов. Для тех, кто уже понял идею и хочет заглянуть под капот.",
        "url": "https://huggingface.co/learn/llm-course/chapter1/1",
        "category": "courses",
        "category_title": "Курс",
        "duration": "8 часов",
        "level": "Средний",
        "tags": ["LLM", "код", "Python"],
        "accent": "pink",
    },
    {
        "title": "AI for Everyone: ИИ для работы",
        "description": "Курс Эндрю Ына для не-технарей: как встроить ИИ в процессы и не наделать ошибок. Можно слушать бесплатно, без сертификата.",
        "url": "https://www.coursera.org/learn/ai-for-everyone",
        "category": "courses",
        "category_title": "Курс",
        "duration": "6 часов",
        "level": "Новичок",
        "tags": ["работа", "стратегия"],
        "accent": "lime",
    },
]

# ---------------------------------------------------------------------------
# БОЛЬШАЯ КАРТОЧКА «ВЫБОР РЕДАКЦИИ»
# ---------------------------------------------------------------------------
FEATURED = {
    "label": "Выбор редакции",
    "title": "Промпт-инжиниринг: полный гайд на русском",
    "description": "Лучший бесплатный учебник по общению с ИИ: от простых вопросов до цепочек рассуждений, с примерами на русском. Прочитайте вводную и главу о техниках — этого хватит, чтобы получать заметно лучшие ответы уже сегодня.",
    "url": "https://www.promptingguide.ai/ru",
    "source": "promptingguide.ai",
    "duration": "25 минут чтения",
    "level": "База",
    "tags": ["промпты", "ChatGPT", "практика"],
}


def count_by_category(slug: str) -> int:
    """Сколько карточек показывать для каждого фильтра."""
    if slug == "all":
        return len(MATERIALS)
    return sum(1 for item in MATERIALS if item["category"] == slug)


@app.route("/")
def index():
    """Главная страница: собираем все данные и отдаём шаблон."""
    categories = [
        {**category, "count": count_by_category(category["slug"])}
        for category in CATEGORIES
    ]

    return render_template(
        "index.html",
        materials=MATERIALS,
        featured=FEATURED,
        categories=categories,
        issue_date=ISSUE_DATE,
        year=datetime.now().year,
        static_mode=app.config.get("STATIC_MODE", False),
    )


@app.route("/subscribe", methods=["POST"])
def subscribe():
    """Приём формы подписки.

    Настоящую рассылку здесь никто не отправляет: адрес просто
    дописывается в файл subscribers.txt рядом с app.py.
    """
    email = request.form.get("email", "").strip().lower()

    # Простая проверка: что-то@что-то.что-то
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        flash("Кажется, в адресе опечатка. Проверьте и попробуйте ещё раз.", "error")
        return redirect(url_for("index") + "#subscribe")

    with SUBSCRIBERS_FILE.open("a", encoding="utf-8") as file:
        file.write(email + "\n")

    flash("Готово! Адрес сохранён. Это учебный проект, поэтому письма пока не отправляются.", "success")
    return redirect(url_for("index") + "#subscribe")


if __name__ == "__main__":
    # debug=True перезапускает сервер после каждого сохранения файла.
    # Для настоящего сайта в интернете этот режим нужно выключить.
    # Порт 5050 выбран потому, что 5000 на некоторых системах занят.
    app.run(debug=True, port=5050)
