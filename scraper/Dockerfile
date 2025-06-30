FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper.py .

# Mantiene el contenedor vivo para poder ejecutar comandos dentro
CMD ["tail", "-f", "/dev/null"]
