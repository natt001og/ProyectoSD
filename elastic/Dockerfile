# elastic/Dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install pymongo elasticsearch

CMD ["python", "indexar.py"]
