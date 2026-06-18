FROM python:3.12-slim

WORKDIR /app

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         default-mysql-client \
#     && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY ./app /app/app

CMD ["poetry", "run", "python", "app/speed_test.py"]