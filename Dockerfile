FROM python:3.12-slim

WORKDIR /work

COPY app app
COPY requirements.txt .
COPY alembic.ini .
COPY pyproject.toml .
COPY alembic alembic
COPY test test

RUN pip install --no-cache-dir --upgrade -r requirements.txt
