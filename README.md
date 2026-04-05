# Отчётогенератор

Веб-сервис для генерации PDF из Markdown и Jupyter Notebook.  
Стек: **FastAPI** + **pdfkit** + **nbconvert**

## Требования

- Python 3.10+
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) — установить в `C:\Program Files\wkhtmltopdf\`
- Jupyter + шаблон `latex_authentic` в папке `templates/`

## Установка и запуск

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Запустить сервер
python -m uvicorn main:app --reload

# 3. Открыть в браузере
# http://localhost:8000
```

## Что умеет

- Принимает Markdown через веб-форму и генерирует PDF
- Поддерживает таблицы, блоки кода, списки, изображения
- Принимает `.ipynb` файл и конвертирует в PDF через nbconvert
- При ошибке возвращает сообщение и не падает

## API эндпоинты

| Метод | URL                  | Описание                          |
|-------|----------------------|-----------------------------------|
| GET   | `/`                  | Веб-интерфейс                     |
| POST  | `/generate`          | Markdown + картинки → PDF         |
| POST  | `/generate-notebook` | Jupyter Notebook (.ipynb) → PDF   |
| GET   | `/health`            | Проверка состояния сервиса        |
| GET   | `/docs`              | Автодокументация (Swagger UI)     |

## Структура проекта

```
project/
├── main.py
├── requirements.txt
└── templates/
    ├── index.html
    └── latex_authentic/   ← шаблон для nbconvert
```
