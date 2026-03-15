# RAG System для поиска по документации

Система вопросов-ответов по PDF/DOCX документам с использованием GigaChat API.

## Возможности

- Загрузка PDF и DOCX файлов
- Векторный поиск с эмбеддингами
- Генерация ответов через GigaChat
- Оценка качества ответов

## Установка

```bash
git clone https://github.com/your-username/rag-project.git
cd rag-project

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

Настройка API

1. Зарегистрируйтесь на https://developers.sber.ru
2. Создайте проект в разделе GigaChat API
3. Скопируйте Authorization Key
4. Создайте файл .env в корне проекта:

GIGACHAT_AUTH_KEY=ваш_ключ