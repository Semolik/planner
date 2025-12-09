#!/usr/bin/env bash
cd /app/api
alembic upgrade head
alembic check
python3 ./scripts/pre_start.py
cd /app
uvicorn api.main:app --host 0.0.0.0 --reload --port 8000
