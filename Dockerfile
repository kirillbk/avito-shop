FROM python:3.12-slim

COPY app /work/app
COPY requirements.txt /work
COPY alembic.ini /work
COPY pyproject.toml /work
COPY alembic /work/alembic
COPY test /work/test

WORKDIR /work

RUN pip install --no-cache-dir --upgrade -r requirements.txt
