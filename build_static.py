"""
Сборка статической версии для GitHub Pages.

Запуск:
    python build_static.py

Результат: папка docs/ с готовым index.html и файлами стилей/скриптов.
GitHub Pages не умеет запускать Flask, поэтому для него мы просто
сохраняем уже готовую HTML-страницу.
"""

import shutil
from pathlib import Path

from app import app

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def build() -> None:
    # Включаем режим статической страницы: форма подписки будет
    # показывать демо-сообщение, а не отправлять данные на сервер.
    app.config["STATIC_MODE"] = True

    with app.test_client() as client:
        response = client.get("/")

    if response.status_code != 200:
        raise RuntimeError(f"Не удалось отрендерить страницу: HTTP {response.status_code}")

    html = response.get_data(as_text=True)

    # Flask отдаёт пути вида /static/style.css. На GitHub Pages проект
    # открывается по адресу /neurostart-ai-digest/, поэтому делаем пути
    # относительными: static/style.css.
    html = html.replace('href="/static/', 'href="static/')
    html = html.replace('src="/static/', 'src="static/')

    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)

    DOCS_DIR.mkdir()
    shutil.copytree(BASE_DIR / "static", DOCS_DIR / "static")
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")

    # Пустой .nojekyll просит GitHub Pages не обрабатывать файлы через Jekyll.
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")

    print("Готово: docs/index.html")
    print("Папку docs/ можно коммитить и публиковать на GitHub Pages.")


if __name__ == "__main__":
    build()
