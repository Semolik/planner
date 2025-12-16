# Planner — запуск и настройка

Этот проект состоит из backend (FastAPI + Postgres) и frontend (Nuxt, статическая сборка на nginx). Ниже — пошаговая настройка окружения, запуск и описание ключевых особенностей.

## 1. Переменные окружения (.env)

Институты создаются автоматически при первом запуске. Главное — корректно заполнить `.env`.

- Возьмите шаблон `./.env.example` и скопируйте его в `.env`:

```
cp .env.example .env
```

- Для фронтенда аналогично используйте `./web/.env.example`:

```
cp web/.env.example web/.env
```

Далее отредактируйте значения под ваше окружение.

## 2. Запуск в режиме разработки

Есть два варианта:

- Минимальный (в Docker поднимается только база данных, API и фронт запускаются локально):
  1) База данных в Docker:
     ```bash
     docker compose -f docker-compose-dev.yml up -d database
     ```
  2) API локально (Python 3.11):
     ```bash
     cd api
     python -m pip install --upgrade pip
     pip install -r requirements.txt
     python run.py
     ```
  3) Фронт локально (Node.js 22):
     ```bash
     cd web
     npm i
     npm run dev
     ```

- Полный (бэкенд и база в Docker):
  ```bash
  docker compose -f docker-compose-dev-full.yml up -d --build
  ```

После старта:
- API: `http://localhost:${API_PORT}`
- WEB: `http://localhost:${WEB_PORT}`

### Версии окружения
- Node.js: 22 (как в `web/Dockerfile`)
- Python: 3.11 (как в `api/Dockerfile`)

## 3. Продакшн‑сборка и запуск

Фронтенд собирается в статический сайт и отдаётся через nginx. Сервис `web` проксирует запросы `/api` на `api:8000`.

Запуск:

```
docker compose -f docker-compose-prod.yml up -d --build
```

Порты:
- `api` → `${API_PORT}:8000`
- `web` → `${WEB_PORT}:80`

## 4. Первоначальная инициализация и пользователи

- Первый зарегистрированный пользователь автоматически получает роль администратора.
- Институты создаются автоматически на основе настроек инициализации.

## 5. Структура проекта

- `api/` — FastAPI, Alembic, CRUD, endpoints, схемы
- `web/` — Nuxt SPA, статическая сборка, nginx Dockerfile
- `uploads/` — файлы и изображения (монтируются в контейнер API)
- `docker-compose-*.yml` — сценарии запуска сервисов

## 6. Клиент для API (генерация)

В папке `web` доступна генерация API‑клиента из OpenAPI:

```
cd web
npm run generate-client-dev
```

По умолчанию фронт в браузере обращается к backend по относительному пути `/api` (nginx проксирует на `api:8000`).

## 7. Скриншоты



