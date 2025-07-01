FROM python:3.9-slim

# Instala curl y herramientas básicas
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cache_worker.py .

CMD ["python", "cache_worker.py"]