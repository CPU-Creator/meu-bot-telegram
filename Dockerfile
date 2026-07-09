FROM python:3.12-slim

WORKDIR /app

# system deps for Pillow and others
RUN apt-get update && apt-get install -y build-essential libjpeg-dev zlib1g-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot_promocoes.py"]
