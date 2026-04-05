# Отчётогенератор

Веб-сервис для генерации документов из Markdown и Jupyter Notebook.  
Стек: **FastAPI** + **pdfkit** + **nbconvert** + **pandoc**

## Требования

- Python 3.10+
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) — установить в `C:\Program Files\wkhtmltopdf\` (для Windows)
- pandoc — установить с [pandoc.org](https://pandoc.org/installing.html)
- [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref/releases/latest) — скачать `pandoc-crossref-Windows.7z`, распаковать и положить `pandoc-crossref.exe` в папку `bin` проекта
- TeX Live или MiKTeX (для PDF через xelatex)
- Шаблон `latex_authentic` в папке `templates/`

## Установка и запуск
```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
# Открыть: http://localhost:8000
```

## Что умеет

- Markdown → PDF (через pdfkit)
- Jupyter Notebook (.ipynb) → PDF (через nbconvert + latex_authentic)
- Pandoc Markdown → PDF / HTML / DOCX (через pandoc + xelatex)

## API эндпоинты

| Метод | URL                  | Описание                        |
|-------|----------------------|---------------------------------|
| GET   | `/`                  | Веб-интерфейс                   |
| POST  | `/generate`          | Markdown → PDF                  |
| POST  | `/generate-notebook` | Jupyter Notebook → PDF          |
| POST  | `/generate-pandoc`   | Pandoc Markdown → PDF/HTML/DOCX |
| GET   | `/health`            | Проверка состояния сервиса      |
| GET   | `/docs`              | Swagger UI (документация)       |

## Структура проекта
```
project/
├── main.py
├── requirements.txt
├── Dockerfile
├── bin/
│   └── pandoc-crossref.exe
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    ├── index.html
    └── latex_authentic/
```