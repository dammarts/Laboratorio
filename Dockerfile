FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .

RUN grep -v "locust" requirements.txt > requirements-prod.txt && \
    pip install --no-cache-dir -r requirements-prod.txt && \
    rm requirements-prod.txt

COPY backend/ .

ENV APP_ENV=production

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
