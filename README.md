
# Planner — запуск и настройка
<img width="1920" height="1080" alt="Снимок экрана 2025-12-17 в 01 10 41" src="https://github.com/user-attachments/assets/65e967eb-dc9d-46c9-8af1-a1479b614af4" />

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
<img width="1920" height="1080" alt="Снимок экрана 2025-12-17 в 01 10 41" src="https://github.com/user-attachments/assets/efb58f49-0194-469d-8785-1665e826b2ea" />
<img width="1920" height="1080" alt="Снимок экрана 2025-12-17 в 01 10 50" src="https://github.com/user-attachments/assets/5dfe8cef-fa4e-4cd9-a2c9-f07ad757ec15" />
<img width="1920" height="1080" alt="Снимок экрана 2025-12-17 в 01 11 48" src="https://github.com/user-attachments/assets/9a1e39d5-763d-4473-890f-ba10e0caf716" />
<img width="1920" height="1080" alt="Снимок экрана 2025-12-17 в 01 11 55" src="https://github.com/user-attachments/assets/876fdd18-7ff1-42e4-b4bb-173b4a3efc90" />
<img width="1920" height="1080" alt="Снимок экрана 2025-12-17 в 01 11 12" src="https://github.com/user-attachments/assets/e2e28f9b-61f2-41dd-b643-cc1176f2f3e9" />
<img width="1920" height="1080" alt="Снимок экрана 2025-12-17 в 01 11 19" src="https://github.com/user-attachments/assets/a55ff160-548c-49bb-b3a2-145581a571a8" />
<img width="1920" height="1080" alt="Снимок экрана 2025-12-17 в 01 11 32" src="https://github.com/user-attachments/assets/a58e5201-a301-43f2-bbd1-d3ee67944d79" />
