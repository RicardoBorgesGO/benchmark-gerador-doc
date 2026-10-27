FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install ".[app]"

COPY apps ./apps
COPY benchmark ./benchmark

EXPOSE 8501

CMD ["streamlit", "run", "apps/streamlit/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
