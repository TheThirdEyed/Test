FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \ 
    build-essential     curl     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

RUN mkdir -p storage/uploads storage/extracted

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
