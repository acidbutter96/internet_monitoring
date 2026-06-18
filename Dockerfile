FROM python:3.12-slim

WORKDIR /app

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         default-mysql-client \
#     && rm -rf /var/lib/apt/lists/*

COPY ./app /app

RUN pip install --no-cache-dir poetry

# COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create true \
    && poetry install --no-root


CMD ["poetry", "run", "python", "speed_test.py"]