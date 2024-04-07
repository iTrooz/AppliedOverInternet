# Inspired from https://stackoverflow.com/a/54763270
FROM python:3.11.5-slim-bookworm

ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-interaction --no-ansi

COPY server.py /app
COPY templates /app/templates

ENTRYPOINT [ "gunicorn" ]
CMD [ "server:app", "-b", "0.0.0.0:5000"]
