FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
COPY backend ./backend
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --only main

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "rest_api.main:app", "--host", "0.0.0.0", "--port", "8000"]